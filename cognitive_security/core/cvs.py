"""
Cognitive Vulnerability State (CVS) Classifier.
Patent Reference: Claim 1(iv), Claim 5, Claim 6(d)-(e), Block 340.

Formula:
CVS(t) = alpha * CLI(t) + beta * (1 - CSS(t)) + gamma * delta_CLI(t)
States: NORMAL (< 0.30) -> ELEVATED (< 0.60) -> HIGH (< 0.80) -> CRITICAL (<= 1.00)
"""

from enum import Enum
from typing import Tuple, List
import numpy as np
import pandas as pd

from cognitive_security.config import CVS_THRESHOLDS


class CVSState(str, Enum):
    NORMAL = "NORMAL"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CognitiveVulnerabilityClassifier:
    """
    Combines CLI (load) and CSS (stability) with rate-of-change sensitivity (delta_CLI)
    into the continuous Cognitive Vulnerability State (CVS) score and discrete states.
    """

    def __init__(self, alpha: float = 0.40, beta: float = 0.40, gamma: float = 0.20):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def classify_score(self, cvs: float) -> CVSState:
        """Map continuous CVS score [0, 1] to discrete CVSState enum."""
        if cvs < CVS_THRESHOLDS['normal']:
            return CVSState.NORMAL
        elif cvs < CVS_THRESHOLDS['elevated']:
            return CVSState.ELEVATED
        elif cvs < CVS_THRESHOLDS['high']:
            return CVSState.HIGH
        else:
            return CVSState.CRITICAL

    def compute_cvs(self, df: pd.DataFrame) -> Tuple[pd.Series, List[CVSState]]:
        """
        Compute continuous CVS series and list of discrete CVSState enums.
        """
        cvs_scores = np.zeros(len(df))
        cvs_states: List[CVSState] = []

        session_col = 'session_id' if 'session_id' in df.columns else None
        session_ids = df[session_col].unique() if session_col else [0]

        for session_id in session_ids:
            if session_col:
                mask = df[session_col] == session_id
                session = df[mask]
            else:
                mask = pd.Series(True, index=df.index)
                session = df

            indices = session.index
            cli_vals = session['CLI'].values
            css_vals = session['CSS'].values

            for i, idx in enumerate(indices):
                cli = cli_vals[i]
                instability = 1.0 - css_vals[i]
                delta_cli = max(cli_vals[i] - cli_vals[i - 1], 0.0) if i > 0 else 0.0

                cvs = self.alpha * cli + self.beta * instability + self.gamma * delta_cli
                cvs = float(np.clip(cvs, 0.0, 1.0))
                cvs_scores[idx] = cvs

                state = self.classify_score(cvs)
                cvs_states.append(state)

        return pd.Series(cvs_scores, index=df.index), cvs_states
