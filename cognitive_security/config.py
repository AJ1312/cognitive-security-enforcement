"""
Global Configuration & Mathematical Constants.
Patent Reference: Claims 1, 3, 4, 5, 6, 9.
"""

from typing import Dict, List

# Core Hyperparameters & Seeds
RANDOM_SEED: int = 42
BASELINE_WINDOW_SIZE: int = 50          # Number of events for baseline computation
CSS_ROLLING_WINDOW: int = 10            # Rolling window for stability scoring
CVS_TTL_SECONDS: int = 60               # Ephemeral state time-to-live

# Signal weights for CLI computation (Claims 1(b), 3)
CLI_WEIGHTS: Dict[str, float] = {
    'read_to_decide_ratio': 0.20,
    'click_acceleration': 0.15,
    'scroll_velocity': 0.10,
    're_read_count': 0.10,
    'hesitation_before_confirm': 0.15,
    'task_switch_frequency': 0.15,
    'context_mismatch_score': 0.15,
}

# CVS thresholds for state classification (Claims 1(d), 5, 6(e))
CVS_THRESHOLDS: Dict[str, float] = {
    'normal': 0.30,
    'elevated': 0.60,
    'high': 0.80,
    'critical': 1.00,
}

# Trust model parameters (Claims 1(g), 6(d), 9)
TRUST_DECAY_ALPHA: float = 0.50          # Exponential decay rate
TRUST_RECOVERY_LAMBDA: float = 0.10      # Linear recovery rate (asymmetric, slower)

# Intervention thresholds for effective risk R_effective = Sensitivity * (1 + CVS)
INTERVENTION_THRESHOLDS: Dict[str, float] = {
    'allow': 0.40,
    'friction': 0.70,
    'decay': 1.00,
    'defer': 1.50,
    'block': float('inf'),
}

# Action sensitivity levels across general computing environments
ACTION_SENSITIVITY: Dict[str, float] = {
    'view_account': 0.1,
    'search_records': 0.1,
    'edit_profile': 0.3,
    'send_internal_msg': 0.3,
    'wire_transfer': 0.9,
    'change_credentials': 0.8,
    'add_payee': 0.7,
    'export_data': 0.8,
    'privilege_escalation': 0.9,
    'otp_submission': 0.6,
    'delete_resource': 0.9,
    'modify_iam_policy': 0.9,
    'dismiss_alert': 0.6,
    'modify_firewall': 0.8,
}

# Friction strategies (Claim 7)
FRICTION_STRATEGIES: List[str] = [
    'ForcedDelay',
    'MandatorySummary',
    'StepDecomposition',
    'UISimplification',
]
