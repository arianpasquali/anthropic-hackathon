import re

from src.backend.preprocessing.schemas import (
    DonationsExtraction,
    ExtractionResult,
    FoodCategoriesExtraction,
    FoodVolumeExtraction,
    OperationsExtraction,
    PeopleServedExtraction,
)


def _to_number(raw: str) -> float:
    return float(raw.replace(".", "").replace(",", ".").strip())


def _first(patterns: list[tuple[str, str]], text: str) -> tuple[float | int | None, str | None]:
    for pattern, method in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if not match:
            continue
        raw = match.group(1)
        value = _to_number(raw)
        if value.is_integer():
            return int(value), method.format(match=match.group(0).strip())
        return value, method.format(match=match.group(0).strip())
    return None, None


def _first_pct(patterns: list[tuple[str, str]], text: str) -> tuple[float | None, str | None]:
    value, evidence = _first(patterns, text)
    if value is None:
        return None, None
    return float(value) / 100.0, evidence


def _merge_section(
    primary: object,
    fallback: object,
    *,
    override_fields: set[str] | None = None,
) -> None:
    override_fields = override_fields or set()
    for field_name in type(primary).model_fields:
        fallback_value = getattr(fallback, field_name, None)
        if fallback_value is None:
            continue
        if field_name in override_fields or getattr(primary, field_name) is None:
            setattr(primary, field_name, fallback_value)


def merge_extraction_results(
    primary: ExtractionResult,
    fallback: ExtractionResult,
) -> ExtractionResult:
    _merge_section(
        primary.food_volume,
        fallback.food_volume,
        override_fields={
            "kg_received_total",
            "kg_via_national_dc",
            "waste_pct",
            "parcels_distributed",
            "avg_products_per_parcel",
            "pct_schijf_van_vijf",
        },
    )
    _merge_section(
        primary.food_categories,
        fallback.food_categories,
        override_fields={
            "kg_produce",
            "kg_meat_fish",
            "kg_dairy_eggs",
            "kg_dry_goods",
            "kg_bread_bakery",
            "kg_prepared",
        },
    )
    _merge_section(primary.people_served, fallback.people_served)
    _merge_section(primary.operations, fallback.operations)
    _merge_section(
        primary.donations,
        fallback.donations,
        override_fields={"food_dc_kg"},
    )
    return primary


def extract_all_regex(text: str) -> ExtractionResult:
    fv = FoodVolumeExtraction()
    fc = FoodCategoriesExtraction()
    don = DonationsExtraction()

    value, evidence = _first(
        [
            (
                r"(?:ontvingen we|ontvingen wij|ontvangen voedsel)[\s\S]{0,60}?([0-9][0-9\.\,]+)\s*kilo",
                "Regex exact phrase for total food received",
            ),
            (
                r"([0-9][0-9\.\,]+)\s*kilo\s+ontvangen voedsel",
                "Regex category card for total food received",
            ),
            (
                r"([0-9][0-9\.\,]+)\s*kilo levensmiddelen zijn verdeeld",
                "Regex exact phrase for food distributed/handled",
            ),
        ],
        text,
    )
    if value is not None:
        fv.kg_received_total = float(value)
        fv.kg_received_total_method = "regex"
        fv.kg_received_total_evidence = evidence
        fv.kg_received_total_confidence = 0.9

    value, evidence = _first(
        [
            (
                r"([0-9][0-9\.\,]+)\s*kilo[\s\S]{0,400}?via het regionale distributiecentrum",
                "Regex exact phrase for DC kilos",
            ),
            (
                r"([0-9][0-9\.\,]+)\s*kilo[\s\S]{0,400}?via (?:het )?(?:RDC|DC)",
                "Regex exact phrase for DC/RDC kilos",
            ),
        ],
        text,
    )
    if value is not None:
        fv.kg_via_national_dc = float(value)
        fv.kg_via_national_dc_method = "regex"
        fv.kg_via_national_dc_evidence = evidence
        fv.kg_via_national_dc_confidence = 0.95

        don.food_dc_kg = float(value)
        don.food_dc_kg_method = "regex"
        don.food_dc_kg_evidence = evidence
        don.food_dc_kg_confidence = 0.95

    value, evidence = _first(
        [
            (
                r"([0-9][0-9\.\,]+)\s+voedselpakketten uitgedeeld",
                "Regex exact phrase for parcels distributed",
            ),
            (
                r"([0-9][0-9\.\,]+)\s+(?:voedselpakketten|boodschappenpakketten)[^\n]{0,40}uitgedeeld",
                "Regex exact phrase for distributed packages",
            ),
            (
                r"in\s+\d{4}\s+verstrekten\s+wij[\s\S]{0,40}?in\s+totaal\s+ca\.\s*([0-9][0-9\.\,]+)\s+voedselpakketten",
                "Regex direct statement for yearly distributed parcels",
            ),
            (
                r"([0-9][0-9\.\,]+)\s+voedselpakketten[\s\S]{0,20}?uitgedeeld",
                "Regex stat card for distributed parcels",
            ),
        ],
        text,
    )
    if value is not None:
        fv.parcels_distributed = int(value)
        fv.parcels_distributed_method = "regex"
        fv.parcels_distributed_evidence = evidence
        fv.parcels_distributed_confidence = 0.95

    value, evidence = _first(
        [
            (
                r"gemiddeld\s+([0-9][0-9\.\,]*)\s+(?:verschillende\s+)?producten",
                "Regex exact phrase for average products per parcel",
            ),
            (
                r"ongeveer\s+([0-9][0-9\.\,]*)\s+producten per huishouden",
                "Regex exact phrase for average products per household",
            ),
            (
                r"gemiddeld\s+([0-9][0-9\.\,]*)\s+verschillende\s+producten",
                "Regex stat card for average products per parcel",
            ),
            (
                r"voedselpakket (?:bestond|bevat)[^\n]{0,40}?(?:circa|gemiddeld)\s+([0-9][0-9\.\,]*)\s+(?:artikelen|producten|consumenteneenheden)",
                "Regex direct statement for average products per parcel",
            ),
            (
                r"tweepersoonshuishouden kreeg gemiddeld\s+([0-9][0-9\.\,]*)",
                "Regex direct statement for average products per week",
            ),
        ],
        text,
    )
    if value is not None:
        fv.avg_products_per_parcel = float(value)
        fv.avg_products_per_parcel_method = "regex"
        fv.avg_products_per_parcel_evidence = evidence
        fv.avg_products_per_parcel_confidence = 0.85

    value, evidence = _first_pct(
        [
            (
                r"([0-9][0-9\.\,]*)\s*(?:%|procent)[\s\S]{0,40}?naar de stort",
                "Regex exact phrase for waste percentage",
            ),
        ],
        text,
    )
    if value is not None:
        fv.waste_pct = value
        fv.waste_pct_method = "regex"
        fv.waste_pct_evidence = evidence
        fv.waste_pct_confidence = 0.95

    value, evidence = _first_pct(
        [
            (
                r"([0-9][0-9\.\,]*)\s*(?:%|procent)\s+uit de schijf van vijf",
                "Regex direct statement for Schijf van Vijf share",
            ),
            (
                r"minimaal\s+([0-9][0-9\.\,]*)\s*(?:%|procent)\s+schijf van vijf producten",
                "Regex target statement for Schijf van Vijf share",
            ),
        ],
        text,
    )
    if value is not None:
        fv.pct_schijf_van_vijf = value
        fv.pct_schijf_van_vijf_method = "regex"
        fv.pct_schijf_van_vijf_evidence = evidence
        fv.pct_schijf_van_vijf_confidence = 0.85

    value, evidence = _first(
        [
            (
                r"ruim\s+€\s*([0-9][0-9\.\,]+)[\s,\-]*op jaarbasis",
                "Regex direct statement for annual food value",
            ),
            (
                r"totale waarde van het uitgeleverde voedsel ca\.\s*€\s*([0-9][0-9\.\,]+)",
                "Regex direct statement for total delivered food value",
            ),
            (
                r"geschatte winkelwaarde van een voedselpakket[^\n]{0,80}?€\s*([0-9][0-9\.\,]+)\s+per week",
                "Regex direct statement for weekly package value",
            ),
        ],
        text,
    )
    if value is not None:
        fv.food_value_eur = float(value)
        fv.food_value_eur_method = "regex"
        fv.food_value_eur_evidence = evidence
        fv.food_value_eur_confidence = 0.8

    triple_match = re.search(
        r"([0-9][0-9\.\,]+)\s*kilo\s+([0-9][0-9\.\,]+)\s*kilo\s+([0-9][0-9\.\,]+)\s*kilo\s+"
        r"\(aardappelen,[\s\S]{0,80}?\(vlees\s*&\s*vis\)[\s\S]{0,80}?\(zuivel\s*&\s*eieren\)",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if triple_match:
        fc.kg_produce = _to_number(triple_match.group(1))
        fc.kg_produce_method = "regex"
        fc.kg_produce_evidence = triple_match.group(0).strip()
        fc.kg_produce_confidence = 0.95
        fc.kg_meat_fish = _to_number(triple_match.group(2))
        fc.kg_meat_fish_method = "regex"
        fc.kg_meat_fish_evidence = triple_match.group(0).strip()
        fc.kg_meat_fish_confidence = 0.95
        fc.kg_dairy_eggs = _to_number(triple_match.group(3))
        fc.kg_dairy_eggs_method = "regex"
        fc.kg_dairy_eggs_evidence = triple_match.group(0).strip()
        fc.kg_dairy_eggs_confidence = 0.95

    patterns = {
        "kg_produce": [
            (
                r"([0-9][0-9\.\,]+)\s*kilo\s*\((?:aardappelen,\s*)?groente\s*&\s*fruit\)",
                "Regex category card for produce",
            ),
            (
                r"([0-9][0-9\.\,]+)\s*kilo verse groente en fruit",
                "Regex exact phrase for produce",
            ),
            (
                r"([0-9][0-9\.\,]+)\s*kg verse groenten?\s+en aardappelen",
                "Regex exact phrase for produce and potatoes",
            ),
        ],
        "kg_meat_fish": [
            (
                r"([0-9][0-9\.\,]+)\s*kilo\s*\(vlees\s*&\s*vis\)",
                "Regex category card for meat and fish",
            )
        ],
        "kg_dairy_eggs": [
            (
                r"([0-9][0-9\.\,]+)\s*kilo\s*\(zuivel\s*&\s*eieren\)",
                "Regex category card for dairy and eggs",
            )
        ],
        "kg_dry_goods": [
            (
                r"([0-9][0-9\.\,]+)\s*kg groenteconserven",
                "Regex exact phrase for canned pantry goods",
            )
        ],
    }

    for field_name, field_patterns in patterns.items():
        value, evidence = _first(field_patterns, text)
        if value is None:
            continue
        setattr(fc, field_name, float(value))
        setattr(fc, f"{field_name}_method", "regex")
        setattr(fc, f"{field_name}_evidence", evidence)
        setattr(fc, f"{field_name}_confidence", 0.9)

    return ExtractionResult(
        food_volume=fv,
        food_categories=fc,
        people_served=PeopleServedExtraction(),
        operations=OperationsExtraction(),
        donations=don,
    )
