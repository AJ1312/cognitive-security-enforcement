"""
Adaptive Trust Decay & Asymmetric Recovery Model.
Patent Reference: Claim 1(v), Claim 6(d), Claim 9, Claim 11(d), Block 410.

Decay:    T(t+1) = T(t) * exp(-alpha * CVS(t))
Recovery: T_recovery(t) = T(t) + lambda * (1 - T(t)) * (1 - CVS(t)) * dt
"""

from typing import Dict, Tuple
import numpy as np

from cognitive_security.config import TRUST_DECAY_ALPHA, TRUST_RECOVERY_LAMBDA


class AdaptiveTrustManager:
    """
    Manages session trust level with exponential decay and slower linear recovery.
    Asymmetric property ensures trust is fast to drop during suspicious/stressed activity,
    but requires sustained calm, consistent interaction to rebuild.
    """

    PERMISSION_LEVELS: Dict[str, Tuple[float, float]] = {
        'full_access': (0.80, 1.00),
        'restricted':  (0.50, 0.80),
        'read_only':   (0.30, 0.50),
        'suspended':   (0.00, 0.30),
    }

    def __init__(
        self,
        decay_alpha: float = TRUST_DECAY_ALPHA,
        recovery_lambda: float = TRUST_RECOVERY_LAMBDA
    ):
        self.alpha = decay_alpha
        self.lam = recovery_lambda

    def simulate_trust(self, cvs_series: np.ndarray, dt: float = 1.0) -> np.ndarray:
        """
        Simulate trust trajectory across time given CVS values.
        """
        n = len(cvs_series)
        trust = np.zeros(n)
        if n == 0:
            return trust

        trust[0] = 1.0  # Start fully trusted

        for t in range(1, n):
            cvs = float(cvs_series[t])
            if cvs > 0.30:  # Decay when vulnerable
                trust[t] = trust[t - 1] * np.exp(-self.alpha * cvs)
            else:  # Recover slowly when stable
                trust[t] = trust[t - 1] + self.lam * (1.0 - trust[t - 1]) * (1.0 - cvs) * dt
            trust[t] = float(np.clip(trust[t], 0.0, 1.0))

        return trust

    def get_permission_level(self, trust: float) -> str:
        """Map numeric trust score [0, 1] to permission tier."""
        for level, (low, high) in self.PERMISSION_LEVELS.items():
            if low <= trust <= high:
                return level
        return 'suspended'
