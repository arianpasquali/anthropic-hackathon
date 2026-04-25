from enum import Enum


class SourceEnum(str, Enum):
    extracted = "extracted"
    inferred_national_avg = "inferred_national_avg"
    inferred_category_split = "inferred_category_split"
    inferred_calculation = "inferred_calculation"
    manual = "manual"


class RoleEnum(str, Enum):
    corporate = "corporate"
    foodbank_op = "foodbank_op"
    admin = "admin"


class RegionEnum(str, Enum):
    noord = "noord"
    oost = "oost"
    zuidoost = "zuidoost"
    zuid = "zuid"
    west = "west"
    randstad = "randstad"


class StatusEnum(str, Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class CounterfactualEnum(str, Enum):
    incineration_energy_recovery = "incineration_energy_recovery"
    landfill = "landfill"
    composting = "composting"


class TemplateEnum(str, Enum):
    gri = "gri"
    csrd = "csrd"
    esrs_e1 = "esrs_e1"
    generic = "generic"


class ImpactProfileEnum(str, Enum):
    co2_focus = "co2_focus"
    social_focus = "social_focus"
    balanced = "balanced"
