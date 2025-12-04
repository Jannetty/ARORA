from enum import Enum


class CircModEnum(Enum):
    UNIVERSAL_SYN_DEG = 1
    INDEP_SYN_DEG = 2
    AUX_SYN_DEG_ONLY = 3
    AUX_SYN_DEG_EXP = 4


class PinLocalizationRulesetEnum(Enum):
    SIMPLE_INHERITANCE = 1
    IMPOSED = 2
