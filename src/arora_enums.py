from enum import Enum


class CircMod(Enum):
    AUX_SYN_DEG_ONLY = 3
    INDEP_SYN_DEG = 2
    UNIVERSAL_SYN_DEG = 1


class PinLocalizationRuleset(Enum):
    SIMPLE_INHERITANCE = 1
    IMPOSED = 2
