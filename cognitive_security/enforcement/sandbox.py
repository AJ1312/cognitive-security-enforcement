"""
Action Sandboxing & Deferral Engine.
Patent Reference: Claim 1(vi), Claim 8, Claim 15, Block 433.
"""

from typing import Dict, Any, List
import numpy as np

from cognitive_security.config import ACTION_SENSITIVITY


class ActionSandbox:
    """
    Manages deferred, sandboxed, and escalated actions.
    Evaluates real-time risk, applies cooling queues or sandboxing,
    and records execution metrics.
    """

    def __init__(self):
        self.queue: List[Dict[str, Any]] = []
        self.metrics: Dict[str, int] = {
            'deferred': 0,
            'confirmed': 0,
            'abandoned': 0,
            'sandboxed': 0,
            'escalated': 0,
            'allowed': 0,
            'blocked': 0,
        }

    def process_action(
        self,
        action_type: str,
        cvs_score: float,
        trust_level: float
    ) -> Dict[str, Any]:
        """
        Process an action through risk-based routing.
        Returns:
            Dictionary with outcome ('ALLOWED', 'DEFERRED_CONFIRMED', 'DEFERRED_ABANDONED',
            'SANDBOXED', 'BLOCKED_ESCALATED') and action metadata.
        """
        sensitivity = ACTION_SENSITIVITY.get(action_type, 0.50)
        r_effective = sensitivity * (1.0 + cvs_score)

        if r_effective < 0.40:
            self.metrics['allowed'] += 1
            return {
                'outcome': 'ALLOWED',
                'action': action_type,
                'r_effective': r_effective,
                'trust': trust_level,
            }
        elif r_effective < 1.00:
            self.metrics['deferred'] += 1
            # 70% probability legitimate user confirms calmly after friction,
            # 30% attacker/coerced user abandons under friction
            if np.random.random() < 0.70:
                self.metrics['confirmed'] += 1
                return {
                    'outcome': 'DEFERRED_CONFIRMED',
                    'action': action_type,
                    'r_effective': r_effective,
                    'trust': trust_level,
                }
            else:
                self.metrics['abandoned'] += 1
                return {
                    'outcome': 'DEFERRED_ABANDONED',
                    'action': action_type,
                    'r_effective': r_effective,
                    'trust': trust_level,
                }
        elif r_effective < 1.50:
            self.metrics['sandboxed'] += 1
            return {
                'outcome': 'SANDBOXED',
                'action': action_type,
                'r_effective': r_effective,
                'trust': trust_level,
            }
        else:
            self.metrics['blocked'] += 1
            self.metrics['escalated'] += 1
            return {
                'outcome': 'BLOCKED_ESCALATED',
                'action': action_type,
                'r_effective': r_effective,
                'trust': trust_level,
            }
