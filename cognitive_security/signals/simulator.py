"""
Telemetry simulator for non-biometric user interaction telemetry streams.
Generates realistic interaction events under baseline vs cognitive stress conditions.
Patent Reference: Claim 1(i), Claim 2, Block 200.
"""

import datetime
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from cognitive_security.config import (
    RANDOM_SEED,
    CLI_WEIGHTS,
    ACTION_SENSITIVITY,
)


class UserInteractionSimulator:
    """
    Generates realistic non-biometric interaction telemetry streams.
    Simulates both normal user behavior and behavior under cognitive stress
    (e.g., social engineering attack, urgency pressure, multitasking overload).
    """

    # Normal baseline distributions (mean, std)
    NORMAL_PARAMS: Dict[str, tuple] = {
        'read_to_decide_ratio':      (3.5, 0.8),    # seconds read per second deciding
        'click_acceleration':        (1.0, 0.3),    # clicks/5s window (normalized)
        'scroll_velocity':           (200.0, 60.0), # pixels/second
        're_read_count':             (0.3, 0.2),    # times per content block
        'hesitation_before_confirm': (1500.0, 400.0), # ms before confirm click
        'task_switch_frequency':     (0.5, 0.2),    # switches per minute
        'context_mismatch_score':    (0.1, 0.05),   # 0-1 scale
    }

    # Stressed / under-attack distributions
    STRESSED_PARAMS: Dict[str, tuple] = {
        'read_to_decide_ratio':      (0.8, 0.4),    # much less reading
        'click_acceleration':        (3.5, 1.2),    # frantic clicking
        'scroll_velocity':           (600.0, 200.0),# rapid scrolling
        're_read_count':             (2.0, 0.8),    # re-reading repeatedly
        'hesitation_before_confirm': (400.0, 200.0), # impulsive confirms
        'task_switch_frequency':     (4.0, 1.5),    # frequent window/tab switching
        'context_mismatch_score':    (0.7, 0.15),   # high context mismatch
    }

    ACTION_TYPES: List[str] = list(ACTION_SENSITIVITY.keys())

    def __init__(self, n_sessions: int = 50, events_per_session: int = 100, seed: int = RANDOM_SEED):
        self.n_sessions = n_sessions
        self.events_per_session = events_per_session
        self.rng = np.random.RandomState(seed)

    def _generate_session(self, session_id: int, user_id: str, stressed: bool) -> pd.DataFrame:
        params = self.STRESSED_PARAMS if stressed else self.NORMAL_PARAMS
        n = self.events_per_session

        data = {}
        for signal, (mu, sigma) in params.items():
            values = self.rng.normal(mu, sigma, n)
            # Clip to valid mathematical ranges
            if signal == 'context_mismatch_score':
                values = np.clip(values, 0.0, 1.0)
            elif signal == 'hesitation_before_confirm':
                values = np.clip(values, 50.0, 10000.0)
            else:
                values = np.clip(values, 0.0, None)
            data[signal] = values

        base_time = datetime.datetime(2026, 2, 8, 9, 0, 0)
        timestamps = [
            base_time + datetime.timedelta(seconds=float(i * self.rng.uniform(2.0, 8.0)))
            for i in range(n)
        ]

        action_weights = [
            0.30, 0.20, 0.10, 0.10, 0.05, 0.03, 0.05, 0.03, 0.02, 0.04, 0.02, 0.02, 0.02, 0.02
        ]
        actions = self.rng.choice(self.ACTION_TYPES, n, p=action_weights)

        df = pd.DataFrame(data)
        df['session_id'] = session_id
        df['user_id'] = user_id
        df['timestamp'] = timestamps
        df['action_type'] = actions
        df['is_stressed'] = stressed
        df['event_idx'] = list(range(n))
        return df

    def generate_all(self) -> pd.DataFrame:
        """Generate combined dataset across normal and stressed sessions."""
        frames = []
        n_normal = self.n_sessions // 2
        n_stressed = self.n_sessions - n_normal

        for i in range(n_normal):
            uid = f"user_{i % 10:03d}"
            frames.append(self._generate_session(i, uid, stressed=False))

        for i in range(n_stressed):
            uid = f"user_{i % 10:03d}"
            frames.append(self._generate_session(n_normal + i, uid, stressed=True))

        return pd.concat(frames, ignore_index=True)
