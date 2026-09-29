"""
Attack Scenarios Simulator:
1. Business Email Compromise (BEC) - Urgent wire transfer
2. OTP / Payment Fraud (Vishing) - Phone call + banking portal
3. Deepfake Social Engineering - Synthetic authority impersonation
4. Insider Coercion - Legitimate user under external pressure
Patent Reference: Section 8, Claim 6, Claim 12.
"""

from typing import Dict, List, Any
import numpy as np
import pandas as pd

from cognitive_security.signals.simulator import UserInteractionSimulator
from cognitive_security.core.cli import CognitiveLoadIndexCalculator
from cognitive_security.core.css import CognitiveStabilityScorer
from cognitive_security.core.cvs import CognitiveVulnerabilityClassifier
from cognitive_security.core.trust import AdaptiveTrustManager
from cognitive_security.enforcement.friction import CognitiveFrictionEngine


class AttackSimulator:
    """Simulates complete attack scenarios with signal traces and system responses."""

    def __init__(self):
        self.cli_calc = CognitiveLoadIndexCalculator()
        self.css_scorer = CognitiveStabilityScorer()
        self.cvs_classifier = CognitiveVulnerabilityClassifier()
        self.trust_mgr = AdaptiveTrustManager()
        self.friction_eng = CognitiveFrictionEngine()

    def _create_scenario_data(
        self,
        phases: List[Dict[str, Any]],
        events_per_phase: int = 20,
        seed: int = 42
    ) -> pd.DataFrame:
        """Generate interaction data for a multi-phase attack scenario."""
        rng = np.random.RandomState(seed)
        all_events = []
        for phase_idx, phase in enumerate(phases):
            params = phase['params']
            for i in range(events_per_phase):
                event = {
                    'session_id': 0,
                    'user_id': 'victim_001',
                    'event_idx': phase_idx * events_per_phase + i,
                    'is_stressed': phase.get('stressed', False),
                    'action_type': phase.get('action', 'view_account'),
                    'phase': phase['name'],
                }
                for signal, (mu, sigma) in params.items():
                    event[signal] = float(np.clip(rng.normal(mu, sigma), 0.0, None))
                    if signal == 'context_mismatch_score':
                        event[signal] = float(np.clip(event[signal], 0.0, 1.0))
                all_events.append(event)

        return pd.DataFrame(all_events)

    def simulate_bec_attack(self) -> Dict[str, Any]:
        """Scenario 1: Business Email Compromise — Urgent wire transfer request."""
        phases = [
            {
                'name': 'Normal Work',
                'params': UserInteractionSimulator.NORMAL_PARAMS,
                'action': 'view_account',
                'stressed': False,
            },
            {
                'name': 'CEO Email Received',
                'params': {
                    'read_to_decide_ratio': (1.2, 0.3),
                    'click_acceleration': (2.5, 0.8),
                    'scroll_velocity': (450.0, 120.0),
                    're_read_count': (1.0, 0.5),
                    'hesitation_before_confirm': (600.0, 200.0),
                    'task_switch_frequency': (2.5, 0.8),
                    'context_mismatch_score': (0.6, 0.1),
                },
                'action': 'send_internal_msg',
                'stressed': True,
            },
            {
                'name': 'Wire Transfer Attempt',
                'params': {
                    'read_to_decide_ratio': (0.5, 0.2),
                    'click_acceleration': (4.0, 1.0),
                    'scroll_velocity': (700.0, 150.0),
                    're_read_count': (2.5, 0.8),
                    'hesitation_before_confirm': (300.0, 100.0),
                    'task_switch_frequency': (5.0, 1.5),
                    'context_mismatch_score': (0.85, 0.1),
                },
                'action': 'wire_transfer',
                'stressed': True,
            },
        ]

        df = self._create_scenario_data(phases, seed=101)
        df['CLI'], _ = self.cli_calc.compute_cli(df)
        df['CSS'] = self.css_scorer.compute_css(df)
        df['CVS'], states = self.cvs_classifier.compute_cvs(df)
        df['CVS_State'] = [s.value for s in states]
        df['Trust'] = self.trust_mgr.simulate_trust(df['CVS'].values)

        return {
            'data': df,
            'name': 'Business Email Compromise (BEC)',
            'description': 'CEO impersonation -> urgent executive wire transfer request',
        }

    def simulate_otp_fraud(self) -> Dict[str, Any]:
        """Scenario 2: OTP/Vishing — Phone call + banking portal manipulation."""
        phases = [
            {
                'name': 'Normal Banking',
                'params': UserInteractionSimulator.NORMAL_PARAMS,
                'action': 'view_account',
                'stressed': False,
            },
            {
                'name': 'Phone Call Begins',
                'params': {
                    'read_to_decide_ratio': (1.5, 0.5),
                    'click_acceleration': (1.8, 0.6),
                    'scroll_velocity': (350.0, 100.0),
                    're_read_count': (1.8, 0.6),
                    'hesitation_before_confirm': (2500.0, 800.0),
                    'task_switch_frequency': (6.0, 2.0),
                    'context_mismatch_score': (0.5, 0.15),
                },
                'action': 'view_account',
                'stressed': True,
            },
            {
                'name': 'OTP Entry Under Dictation',
                'params': {
                    'read_to_decide_ratio': (0.3, 0.1),
                    'click_acceleration': (3.0, 1.0),
                    'scroll_velocity': (500.0, 150.0),
                    're_read_count': (3.0, 1.0),
                    'hesitation_before_confirm': (3000.0, 1000.0),
                    'task_switch_frequency': (8.0, 2.0),
                    'context_mismatch_score': (0.9, 0.05),
                },
                'action': 'otp_submission',
                'stressed': True,
            },
        ]

        df = self._create_scenario_data(phases, seed=102)
        df['CLI'], _ = self.cli_calc.compute_cli(df)
        df['CSS'] = self.css_scorer.compute_css(df)
        df['CVS'], states = self.cvs_classifier.compute_cvs(df)
        df['CVS_State'] = [s.value for s in states]
        df['Trust'] = self.trust_mgr.simulate_trust(df['CVS'].values)

        return {
            'data': df,
            'name': 'OTP/Payment Fraud (Vishing)',
            'description': 'Urgent phone caller -> OTP dictation under duress',
        }

    def simulate_deepfake(self) -> Dict[str, Any]:
        """Scenario 3: Deepfake video call — credential sharing."""
        phases = [
            {
                'name': 'Normal Work',
                'params': UserInteractionSimulator.NORMAL_PARAMS,
                'action': 'view_account',
                'stressed': False,
            },
            {
                'name': 'Deepfake Video Call',
                'params': {
                    'read_to_decide_ratio': (0.8, 0.3),
                    'click_acceleration': (3.0, 1.0),
                    'scroll_velocity': (550.0, 180.0),
                    're_read_count': (0.5, 0.3),
                    'hesitation_before_confirm': (500.0, 200.0),
                    'task_switch_frequency': (3.0, 1.0),
                    'context_mismatch_score': (0.75, 0.1),
                },
                'action': 'change_credentials',
                'stressed': True,
            },
            {
                'name': 'Credential Sharing',
                'params': {
                    'read_to_decide_ratio': (0.4, 0.15),
                    'click_acceleration': (4.5, 1.2),
                    'scroll_velocity': (800.0, 200.0),
                    're_read_count': (0.2, 0.1),
                    'hesitation_before_confirm': (250.0, 100.0),
                    'task_switch_frequency': (4.0, 1.0),
                    'context_mismatch_score': (0.9, 0.05),
                },
                'action': 'change_credentials',
                'stressed': True,
            },
        ]

        df = self._create_scenario_data(phases, seed=103)
        df['CLI'], _ = self.cli_calc.compute_cli(df)
        df['CSS'] = self.css_scorer.compute_css(df)
        df['CVS'], states = self.cvs_classifier.compute_cvs(df)
        df['CVS_State'] = [s.value for s in states]
        df['Trust'] = self.trust_mgr.simulate_trust(df['CVS'].values)

        return {
            'data': df,
            'name': 'Deepfake Social Engineering',
            'description': 'Synthetic video executive impersonation -> credential hand-off',
        }

    def simulate_insider_coercion(self) -> Dict[str, Any]:
        """Scenario 4: Insider coercion — legitimate user under pressure."""
        phases = [
            {
                'name': 'Normal Access',
                'params': UserInteractionSimulator.NORMAL_PARAMS,
                'action': 'search_records',
                'stressed': False,
            },
            {
                'name': 'Under Coercion',
                'params': {
                    'read_to_decide_ratio': (1.0, 0.4),
                    'click_acceleration': (2.0, 0.7),
                    'scroll_velocity': (500.0, 150.0),
                    're_read_count': (2.5, 0.8),
                    'hesitation_before_confirm': (800.0, 300.0),
                    'task_switch_frequency': (4.5, 1.5),
                    'context_mismatch_score': (0.65, 0.15),
                },
                'action': 'search_records',
                'stressed': True,
            },
            {
                'name': 'Data Exfiltration',
                'params': {
                    'read_to_decide_ratio': (0.6, 0.2),
                    'click_acceleration': (3.5, 1.0),
                    'scroll_velocity': (650.0, 200.0),
                    're_read_count': (3.0, 1.0),
                    'hesitation_before_confirm': (400.0, 150.0),
                    'task_switch_frequency': (6.0, 2.0),
                    'context_mismatch_score': (0.8, 0.1),
                },
                'action': 'export_data',
                'stressed': True,
            },
        ]

        df = self._create_scenario_data(phases, seed=104)
        df['CLI'], _ = self.cli_calc.compute_cli(df)
        df['CSS'] = self.css_scorer.compute_css(df)
        df['CVS'], states = self.cvs_classifier.compute_cvs(df)
        df['CVS_State'] = [s.value for s in states]
        df['Trust'] = self.trust_mgr.simulate_trust(df['CVS'].values)

        # Baseline UEBA risk score that stays flat (traditional anomaly systems miss this)
        rng = np.random.RandomState(42)
        df['UEBA_Risk'] = rng.uniform(0.05, 0.15, len(df))

        return {
            'data': df,
            'name': 'Insider Coercion',
            'description': 'Legitimate authorized user coerced into bulk data exfiltration',
        }
