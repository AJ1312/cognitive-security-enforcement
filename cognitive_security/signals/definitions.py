"""
Signal definitions and taxonomy for non-biometric telemetry.
Patent Reference: Claim 1(i), Claim 2.
"""

from enum import Enum


class SignalType(str, Enum):
    READ_TO_DECIDE_RATIO = "read_to_decide_ratio"
    CLICK_ACCELERATION = "click_acceleration"
    SCROLL_VELOCITY = "scroll_velocity"
    RE_READ_COUNT = "re_read_count"
    HESITATION_BEFORE_CONFIRM = "hesitation_before_confirm"
    TASK_SWITCH_FREQUENCY = "task_switch_frequency"
    CONTEXT_MISMATCH_SCORE = "context_mismatch_score"


class SessionType(str, Enum):
    NORMAL = "normal"
    STRESSED = "stressed"
    ATTACK = "attack"
    RECOVERY = "recovery"
