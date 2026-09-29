"""
Cognitive Friction Injection Engine.
Patent Reference: Claim 1(vi), Claim 6(g)-(h), Claim 7, Block 400/430.

Intervention Strategies:
- ForcedDelay (cool-off delay proportional to CVS)
- MandatorySummary (text description of user intent)
- StepDecomposition (atomic confirmation steps)
- UISimplification (suppress urgency cues)
"""

from dataclasses import dataclass
from typing import List

from cognitive_security.config import INTERVENTION_THRESHOLDS


@dataclass
class SecurityIntervention:
    intervention_type: str
    details: str
    delay_seconds: float = 0.0
    requires_summary: bool = False
    decomposition_steps: int = 1
    ui_simplified: bool = False


class CognitiveFrictionEngine:
    """
    Selects and parameterizes cognitive friction interventions based on
    effective risk: R_effective = Action_Sensitivity * (1 + CVS_score).
    """

    def select_friction(
        self,
        cvs_state: str,
        action_sensitivity: float,
        cvs_score: float
    ) -> List[SecurityIntervention]:
        """
        Select appropriate friction strategies based on computed risk level.
        """
        r_effective = action_sensitivity * (1.0 + cvs_score)
        interventions: List[SecurityIntervention] = []

        if r_effective < INTERVENTION_THRESHOLDS['allow']:
            return [SecurityIntervention('ALLOW', 'Action permitted under standard baseline controls')]

        if r_effective < INTERVENTION_THRESHOLDS['friction']:
            delay = 5 + int(15 * cvs_score)
            interventions.append(SecurityIntervention(
                'ForcedDelay', f'Cool-off timer: {delay}s', delay_seconds=float(delay)
            ))

        elif r_effective < INTERVENTION_THRESHOLDS['decay']:
            delay = 10 + int(20 * cvs_score)
            interventions.append(SecurityIntervention(
                'ForcedDelay', f'Cool-off timer: {delay}s', delay_seconds=float(delay)
            ))
            interventions.append(SecurityIntervention(
                'MandatorySummary',
                'User must describe the intended action and recipient verification',
                requires_summary=True
            ))
            steps = 3 + int(cvs_score * 2)
            interventions.append(SecurityIntervention(
                'StepDecomposition',
                f'Action broken into {steps} atomic confirmation steps',
                decomposition_steps=steps
            ))

        elif r_effective < INTERVENTION_THRESHOLDS['defer']:
            interventions = [
                SecurityIntervention('ForcedDelay', 'Cool-off timer: 30s', delay_seconds=30.0),
                SecurityIntervention('MandatorySummary', 'Mandatory multi-field action summary', requires_summary=True),
                SecurityIntervention('StepDecomposition', 'Action decomposed into 5 atomic steps', decomposition_steps=5),
                SecurityIntervention('UISimplification', 'Urgency cues and aggressive countdowns suppressed', ui_simplified=True),
                SecurityIntervention('ActionDeferral', 'Action queued for 30-minute cooling delay'),
            ]
        else:
            interventions = [
                SecurityIntervention('BLOCK', 'Action blocked — Cognitive Vulnerability State Critical'),
                SecurityIntervention('ChannelEscalation', 'Routed to secondary out-of-band human approver'),
                SecurityIntervention('SessionRestriction', 'Session permissions dynamically reduced to read-only'),
            ]

        return interventions
