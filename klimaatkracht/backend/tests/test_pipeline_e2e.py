"""End-to-end pipeline test (Layer 6 from the plan).

Steps:
1. Operations data ingested for 5 chapters (seed fixture)
2. Buyer commits with allocation preferences
3. Allocation engine routes commitment
4. Attribution computed against actual operations data
5. Report generated with verified numbers

If this test is green, the full data flow produces numbers consistent with
the simulation seed's `expected_totals`. If it fails, demo numbers are wrong.
"""

from datetime import date

from sqlalchemy.orm import Session

from app.models import Buyer, Commitment, OperationsRecord
from app.services.pipeline import run_full_pipeline
from tests.fixtures import load_simulation_seed


def _ingest_operations_from_seed(db: Session, seed: dict) -> None:
    for chapter in seed["chapters"]:
        total_kg = sum(chapter["category_breakdown"].values())
        db.add(
            OperationsRecord(
                chapter_id=chapter["id"],
                period_start=date.fromisoformat(chapter["period_start"]),
                period_end=date.fromisoformat(chapter["period_end"]),
                submission_method="csv_upload",
                total_kg=total_kg,
                category_breakdown=chapter["category_breakdown"],
                households_served=chapter["households_quarter"],
                distribution_count=65,
                transport_km=2400,
                refrigeration_kwh=3850,
                operational_cost_eur=chapter["quarterly_cost_eur"],
            )
        )
    db.commit()


def _create_buyer_and_commitment(db: Session, seed: dict) -> Commitment:
    buyer = Buyer(
        id="corp-x-buyer",
        name="Corporation X",
        industry="Financial Services",
        contact_email="reporting@corp-x.example",
        employees_count=1200,
        turnover_eur_m=540,
        csrd_in_scope=True,
    )
    db.add(buyer)
    commitment = Commitment(
        id="corp-x-commit",
        buyer_id=buyer.id,
        fund_id="demo-fund-q1-2026",
        amount_eur=seed["corp_x_commitment_eur"],
        allocation_preferences=seed["corp_x_preferences"],
        rationale="Blended preference for dual climate and social impact.",
    )
    db.add(commitment)
    db.commit()
    return commitment


class TestEndToEndPipeline:
    def test_full_pipeline_corp_x(self, seeded_db: Session):
        seed = load_simulation_seed("q1_2026")
        _ingest_operations_from_seed(seeded_db, seed)
        commitment = _create_buyer_and_commitment(seeded_db, seed)

        result = run_full_pipeline(
            db=seeded_db,
            commitment=commitment,
            coefficients=seed["coefficients"],
            period_start=date(2026, 1, 6),
            period_end=date(2026, 3, 30),
            methodology_version=seed["methodology_version"],
        )

        expected = seed["expected_totals"]
        # Totals must hit simulation seed within 1%
        assert (
            abs(result.total_net_avoided_kgco2e / 1000 - expected["corp_x_attributed_tco2e"])
            / expected["corp_x_attributed_tco2e"]
            < 0.01
        )
        assert (
            abs(result.total_food_rescued_kg - expected["corp_x_attributed_food_kg"])
            / expected["corp_x_attributed_food_kg"]
            < 0.01
        )
        assert (
            abs(
                result.total_households_supported
                - expected["corp_x_attributed_households"]
            )
            / expected["corp_x_attributed_households"]
            < 0.01
        )

        assert "Quarterly Impact Report — Corporation X" in result.report_markdown
        assert "VB-AMS-OOST" in result.report_markdown
        assert "Methodology" in result.report_markdown

    def test_pipeline_persists_attribution_rows(self, seeded_db: Session):
        from sqlalchemy import select

        from app.models import AttributionRow

        seed = load_simulation_seed("q1_2026")
        _ingest_operations_from_seed(seeded_db, seed)
        commitment = _create_buyer_and_commitment(seeded_db, seed)
        run_full_pipeline(
            db=seeded_db,
            commitment=commitment,
            coefficients=seed["coefficients"],
            period_start=date(2026, 1, 6),
            period_end=date(2026, 3, 30),
            methodology_version=seed["methodology_version"],
        )

        rows = (
            seeded_db.execute(
                select(AttributionRow).where(AttributionRow.commitment_id == commitment.id)
            )
            .scalars()
            .all()
        )
        assert len(rows) == 5
        for row in rows:
            assert 0 <= float(row.attribution_factor) <= 1.0

    def test_pipeline_idempotent_numerics(self, seeded_db: Session):
        """Running the pipeline a second time produces identical totals
        (drives Invariant 4 — report regeneration is numerically stable).
        """
        seed = load_simulation_seed("q1_2026")
        _ingest_operations_from_seed(seeded_db, seed)
        commitment = _create_buyer_and_commitment(seeded_db, seed)

        first = run_full_pipeline(
            db=seeded_db,
            commitment=commitment,
            coefficients=seed["coefficients"],
            period_start=date(2026, 1, 6),
            period_end=date(2026, 3, 30),
            methodology_version=seed["methodology_version"],
        )

        # Wipe attributions so the second run rebuilds them. Real production
        # would refuse to overwrite; the test is exercising the recompute path.
        from sqlalchemy import delete

        from app.models import Allocation, AttributionRow, Report

        seeded_db.execute(delete(AttributionRow).where(AttributionRow.commitment_id == commitment.id))
        seeded_db.execute(delete(Allocation).where(Allocation.commitment_id == commitment.id))
        seeded_db.execute(delete(Report).where(Report.commitment_id == commitment.id))
        seeded_db.commit()

        second = run_full_pipeline(
            db=seeded_db,
            commitment=commitment,
            coefficients=seed["coefficients"],
            period_start=date(2026, 1, 6),
            period_end=date(2026, 3, 30),
            methodology_version=seed["methodology_version"],
        )
        assert abs(first.total_net_avoided_kgco2e - second.total_net_avoided_kgco2e) < 1e-3
        assert abs(first.total_food_rescued_kg - second.total_food_rescued_kg) < 1e-3
