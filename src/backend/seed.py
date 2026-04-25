"""Run with: python -m src.backend.seed"""
from datetime import date
from decimal import Decimal

from sqlmodel import Session, select

from src.backend.database import create_db_and_tables, engine
from src.backend.models.enums import (
    CounterfactualEnum, ImpactProfileEnum, RegionEnum, RoleEnum, SourceEnum,
)
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import Package
from src.backend.models.measurements import PeopleServed
from src.backend.models.user import User
from src.backend.services.auth import hash_password

FOODBANKS = [
    {"name": "Voedselbank Rotterdam", "city": "Rotterdam", "region": RegionEnum.west, "is_regional_dc": True,
     "co2e_kg": 1268740.0, "households": 3200},
    {"name": "Voedselbank Amsterdam", "city": "Amsterdam", "region": RegionEnum.randstad, "is_regional_dc": True,
     "co2e_kg": 1450000.0, "households": 4100},
    {"name": "Voedselbank Den Haag", "city": "Den Haag", "region": RegionEnum.west, "is_regional_dc": False,
     "co2e_kg": 890000.0, "households": 2500},
    {"name": "Voedselbank Utrecht", "city": "Utrecht", "region": RegionEnum.randstad, "is_regional_dc": False,
     "co2e_kg": 720000.0, "households": 1800},
    {"name": "Voedselbank Eindhoven", "city": "Eindhoven", "region": RegionEnum.zuidoost, "is_regional_dc": False,
     "co2e_kg": 650000.0, "households": 1600},
    {"name": "Voedselbank Tilburg", "city": "Tilburg", "region": RegionEnum.zuidoost, "is_regional_dc": True,
     "co2e_kg": 580000.0, "households": 1400},
    {"name": "Voedselbank Groningen", "city": "Groningen", "region": RegionEnum.noord, "is_regional_dc": True,
     "co2e_kg": 420000.0, "households": 1100},
    {"name": "Voedselbank Breda", "city": "Breda", "region": RegionEnum.zuidoost, "is_regional_dc": False,
     "co2e_kg": 390000.0, "households": 980},
    {"name": "Voedselbank Nijmegen", "city": "Nijmegen", "region": RegionEnum.oost, "is_regional_dc": False,
     "co2e_kg": 310000.0, "households": 820},
    {"name": "Voedselbank Zwolle", "city": "Zwolle", "region": RegionEnum.oost, "is_regional_dc": False,
     "co2e_kg": 270000.0, "households": 700},
]

PACKAGES = [
    {
        "name": "CO2 Impact Fund",
        "description": "Funds the 10 food banks with highest CO2e impact. Ideal for Scope 3 reporting.",
        "region": RegionEnum.randstad,
        "price_eur": 25000.0,
        "co2e_claim_kg": 800000.0,
        "impact_profile": ImpactProfileEnum.co2_focus,
        "top_n": 10,
    },
    {
        "name": "Social Reach Fund",
        "description": "Targets food banks serving the most households. Maximises social impact.",
        "region": RegionEnum.randstad,
        "price_eur": 15000.0,
        "co2e_claim_kg": 400000.0,
        "impact_profile": ImpactProfileEnum.social_focus,
        "top_n": 10,
    },
    {
        "name": "Balanced Impact Fund",
        "description": "Equal weighting of CO2e and social reach. Best for ESRS E5/S3 disclosure.",
        "region": RegionEnum.randstad,
        "price_eur": 50000.0,
        "co2e_claim_kg": 1500000.0,
        "impact_profile": ImpactProfileEnum.balanced,
        "top_n": 10,
    },
]


def seed():
    create_db_and_tables()
    with Session(engine) as session:
        if session.exec(select(Foodbank)).first():
            print("Already seeded, skipping.")
            return

        user = User(
            email="demo@acme.nl",
            hashed_password=hash_password("demo1234"),
            role=RoleEnum.corporate,
            org_name="ACME Nederland BV",
        )
        session.add(user)

        for fb_data in FOODBANKS:
            fb = Foodbank(
                name=fb_data["name"],
                city=fb_data["city"],
                region=fb_data["region"],
                is_regional_dc=fb_data["is_regional_dc"],
            )
            session.add(fb)
            session.flush()

            report = AnnualReport(
                foodbank_id=fb.id,
                year=2024,
                period_start=date(2024, 1, 1),
                period_end=date(2024, 12, 31),
                raw_file_path=f"data/{fb_data['city'].lower().replace(' ', '-')}-2024.pdf",
                ingestion_model="claude-sonnet-4-6",
            )
            session.add(report)
            session.flush()

            co2 = fb_data["co2e_kg"]
            frame = FrameResult(
                report_id=report.id,
                co2e_total_kg=co2,
                co2e_produce_kg=co2 * 0.365,
                co2e_meat_fish_kg=co2 * 0.240,
                co2e_dairy_eggs_kg=co2 * 0.151,
                co2e_dry_goods_kg=co2 * 0.144,
                co2e_bread_kg=co2 * 0.100,
                co2e_prepared_kg=0.0,
                counterfactual_route=CounterfactualEnum.incineration_energy_recovery,
                emission_factor_source="FAO Food Wastage Footprint 2013 + WRAP UK 2022",
                methodology_version="FRAME-NL-v1.0",
            )
            session.add(frame)

            people = PeopleServed(
                report_id=report.id,
                households_weekly=fb_data["households"],
                households_weekly_source=SourceEnum.extracted,
                households_weekly_method="extracted from annual report",
                individuals_total=int(fb_data["households"] * 2.3),
                individuals_total_source=SourceEnum.inferred_national_avg,
                individuals_total_method="CBS household size 2024",
                pct_under_18=0.37,
                pct_under_18_source=SourceEnum.inferred_national_avg,
                pct_under_18_method="NL national average Feiten & Cijfers 2024",
            )
            session.add(people)

            # FoodCategories — split rescued mass per FRAME taxonomy.
            # Approximate annual kg ≈ co2 / weighted EF (1.5) for demo purposes.
            est_kg = co2 / 1.5
            from src.backend.models.measurements import FoodCategories
            cats = FoodCategories(
                report_id=report.id,
                kg_produce=est_kg * 0.365, kg_produce_source=SourceEnum.extracted, kg_produce_method="annual report tonnage table",
                kg_meat_fish=est_kg * 0.060, kg_meat_fish_source=SourceEnum.extracted, kg_meat_fish_method="annual report tonnage table",
                kg_dairy_eggs=est_kg * 0.110, kg_dairy_eggs_source=SourceEnum.extracted, kg_dairy_eggs_method="annual report tonnage table",
                kg_dry_goods=est_kg * 0.220, kg_dry_goods_source=SourceEnum.extracted, kg_dry_goods_method="annual report tonnage table",
                kg_bread_bakery=est_kg * 0.180, kg_bread_bakery_source=SourceEnum.extracted, kg_bread_bakery_method="annual report tonnage table",
                kg_prepared=est_kg * 0.065, kg_prepared_source=SourceEnum.inferred_calculation, kg_prepared_method="residual category",
            )
            session.add(cats)

        for pkg_data in PACKAGES:
            pkg = Package(**pkg_data)
            session.add(pkg)

        session.commit()
        print("Seeded successfully.")
        print("Demo login: demo@acme.nl / demo1234")


if __name__ == "__main__":
    seed()
