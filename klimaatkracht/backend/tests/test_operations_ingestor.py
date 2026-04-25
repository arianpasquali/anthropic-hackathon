"""Test contract: parse operational data submissions from food banks.
Accept CSV with category-level kg breakdown plus operational metadata.
Validate against business rules, surface errors clearly.
"""

from datetime import date
from io import BytesIO, StringIO

import pytest

from app.services.operations_ingestor import (
    OperationsRecord,
    ValidationError,
    parse_operations_csv,
    parse_operations_xlsx,
    validate_operations_record,
)

CSV_HEADER = (
    "chapter_id,period_start,period_end,"
    "fresh_produce_kg,bread_bakery_kg,dairy_kg,meat_processed_kg,"
    "ready_meals_kg,dry_goods_kg,canned_kg,frozen_kg,"
    "households_served,distribution_count,transport_km,refrigeration_kwh,"
    "operational_cost_eur"
)


class TestOperationsIngestor:
    def test_parse_well_formed_csv(self):
        csv_content = (
            CSV_HEADER + "\n"
            "VB-AMS-OOST,2026-01-06,2026-03-30,"
            "52000,29250,22750,9750,6500,26000,11375,4875,"
            "4940,65,2400,3850,58270"
        )
        records = parse_operations_csv(StringIO(csv_content))
        assert len(records) == 1
        r = records[0]
        assert r.chapter_id == "VB-AMS-OOST"
        assert r.period_start == date(2026, 1, 6)
        assert r.category_breakdown["fresh_produce"] == 52000
        assert r.households_served == 4940
        assert r.transport_km == 2400
        assert r.distribution_count == 65
        assert r.operational_cost_eur == 58270

    def test_parse_rejects_negative_kg(self):
        csv_content = (
            CSV_HEADER + "\n"
            "VB-AMS-OOST,2026-01-06,2026-03-30,"
            "-5000,29250,22750,9750,6500,26000,11375,4875,"
            "4940,65,2400,3850,58270"
        )
        with pytest.raises(ValidationError, match="negative"):
            parse_operations_csv(StringIO(csv_content))

    def test_parse_rejects_unknown_chapter(self):
        csv_content = (
            CSV_HEADER + "\n"
            "VB-FAKE-CHAPTER,2026-01-06,2026-03-30,"
            "1000,1000,1000,1000,1000,1000,1000,1000,"
            "100,10,100,100,1000"
        )
        with pytest.raises(ValidationError, match="unknown chapter"):
            parse_operations_csv(StringIO(csv_content))

    def test_parse_rejects_invalid_date(self):
        csv_content = (
            CSV_HEADER + "\n"
            "VB-AMS-OOST,not-a-date,2026-03-30,"
            "1000,1000,1000,1000,1000,1000,1000,1000,"
            "100,10,100,100,1000"
        )
        with pytest.raises(ValidationError, match="invalid date"):
            parse_operations_csv(StringIO(csv_content))

    def test_parse_rejects_overlapping_periods(self):
        existing = OperationsRecord(
            chapter_id="VB-AMS-OOST",
            period_start=date(2026, 1, 1),
            period_end=date(2026, 3, 31),
            category_breakdown={"fresh_produce": 1000.0},
            households_served=100,
        )
        new_record = OperationsRecord(
            chapter_id="VB-AMS-OOST",
            period_start=date(2026, 2, 1),
            period_end=date(2026, 4, 30),
            category_breakdown={"fresh_produce": 500.0},
            households_served=50,
        )
        with pytest.raises(ValidationError, match="[Oo]verlapping period"):
            validate_operations_record(new_record, existing=[existing])

    def test_validate_accepts_non_overlapping_period(self):
        existing = OperationsRecord(
            chapter_id="VB-AMS-OOST",
            period_start=date(2026, 1, 1),
            period_end=date(2026, 3, 31),
            category_breakdown={"fresh_produce": 1000.0},
            households_served=100,
        )
        new_record = OperationsRecord(
            chapter_id="VB-AMS-OOST",
            period_start=date(2026, 4, 1),
            period_end=date(2026, 6, 30),
            category_breakdown={"fresh_produce": 500.0},
            households_served=50,
        )
        validate_operations_record(new_record, existing=[existing])

    def test_validate_ignores_other_chapters(self):
        existing = OperationsRecord(
            chapter_id="VB-AMS-OOST",
            period_start=date(2026, 1, 1),
            period_end=date(2026, 3, 31),
            category_breakdown={"fresh_produce": 1000.0},
            households_served=100,
        )
        new_record = OperationsRecord(
            chapter_id="VB-RDM-ZUID",
            period_start=date(2026, 2, 1),
            period_end=date(2026, 4, 30),
            category_breakdown={"fresh_produce": 500.0},
            households_served=50,
        )
        validate_operations_record(new_record, existing=[existing])

    def test_parse_handles_empty_categories(self):
        """Categories not received this period default to 0."""
        csv_content = (
            CSV_HEADER + "\n"
            "VB-AMS-OOST,2026-01-06,2026-03-30,"
            "52000,29250,22750,0,0,26000,11375,0,"
            "4940,65,2400,3850,58270"
        )
        records = parse_operations_csv(StringIO(csv_content))
        assert records[0].category_breakdown["meat_processed"] == 0
        assert records[0].category_breakdown["frozen"] == 0
        assert records[0].total_kg == 141_375

    def test_excel_upload_supported(self):
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.append([
            "chapter_id", "period_start", "period_end",
            "fresh_produce_kg", "bread_bakery_kg", "dairy_kg",
            "meat_processed_kg", "ready_meals_kg", "dry_goods_kg",
            "canned_kg", "frozen_kg", "households_served",
            "distribution_count", "transport_km", "refrigeration_kwh",
            "operational_cost_eur",
        ])
        ws.append([
            "VB-AMS-OOST", "2026-01-06", "2026-03-30",
            52000, 29250, 22750, 9750, 6500, 26000, 11375, 4875,
            4940, 65, 2400, 3850, 58270,
        ])

        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)

        records = parse_operations_xlsx(buf)
        assert len(records) == 1
        assert records[0].chapter_id == "VB-AMS-OOST"
        assert records[0].category_breakdown["fresh_produce"] == 52000
        assert records[0].submission_method == "spreadsheet"
