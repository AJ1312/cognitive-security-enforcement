"""
Cognitive Stability Score (CSS) Scorer.
Patent Reference: Claim 1(iii), Claim 4, Block 330.

Formula:
CSS(t) = 1.0 - (0.4 * Var_ratio + 0.35 * Action_Entropy + 0.25 * Reversal_Rate)
Optimized with NumPy vectorization for high-throughput streaming analysis.
"""

from collections import Counter
import numpy as np
import pandas as pd

from cognitive_security.config import (
    CSS_ROLLING_WINDOW,
    BASELINE_WINDOW_SIZE,
    ACTION_SENSITIVITY,
)


class CognitiveStabilityScorer:
    """
    Computes Cognitive Stability Score (CSS) from decision behavior consistency.
    CSS = 1.0 means perfectly stable, consistent interactions;
    CSS = 0.0 means erratic, chaotic behavior under duress.
    """

    def __init__(self, rolling_window: int = CSS_ROLLING_WINDOW):
        self.rolling_window = rolling_window
        self._max_entropy = float(np.log2(max(len(ACTION_SENSITIVITY), 2)))

    def _fast_action_entropy(self, actions_slice: np.ndarray) -> float:
        """Fast Shannon entropy computation over array slice."""
        n = len(actions_slice)
        if n == 0:
            return 0.0
        counts = Counter(actions_slice).values()
        probs = [c / n for c in counts]
        entropy = -sum(p * np.log2(p + 1e-10) for p in probs)
        return float(entropy / self._max_entropy)

    def compute_css(self, df: pd.DataFrame) -> pd.Series:
        """Compute CSS for each event using rolling window analysis."""
        css_values = np.zeros(len(df))
        session_col = 'session_id' if 'session_id' in df.columns else None

        session_ids = df[session_col].unique() if session_col else [0]

        for session_id in session_ids:
            if session_col:
                session = df[df[session_col] == session_id]
            else:
                session = df

            indices = session.index.values
            n_events = len(indices)

            has_hesitation = 'hesitation_before_confirm' in session.columns
            has_action = 'action_type' in session.columns

            hesitation_arr = session['hesitation_before_confirm'].values if has_hesitation else None
            action_arr = session['action_type'].values if has_action else None

            # Baseline hesitation variance from initial events
            if has_hesitation:
                baseline_hesitation = hesitation_arr[:BASELINE_WINDOW_SIZE]
                baseline_var = float(np.var(baseline_hesitation)) if len(baseline_hesitation) > 1 else 1.0
                baseline_var = max(baseline_var, 1e-6)
            else:
                baseline_var = 1.0

            for i in range(n_events):
                idx = indices[i]
                w_start = max(0, i - self.rolling_window)
                w_len = i - w_start + 1

                if w_len < 3:
                    css_values[idx] = 0.80  # Default baseline for small windows
                    continue

                # Sub-metric 1: Decision latency variance ratio
                if has_hesitation:
                    recent_var = float(np.var(hesitation_arr[w_start:i + 1]))
                    var_ratio = min(recent_var / baseline_var, 5.0) / 5.0
                else:
                    var_ratio = 0.20

                # Sub-metric 2: Action sequence entropy
                if has_action:
                    entropy = self._fast_action_entropy(action_arr[w_start:i + 1])
                else:
                    entropy = 0.20

                # Sub-metric 3: Action reversal rate
                if has_action and w_len > 2:
                    actions = action_arr[w_start:i + 1]
                    reversals = sum(
                        1 for j in range(2, len(actions))
                        if actions[j] == actions[j - 2] and actions[j] != actions[j - 1]
                    )
                    reversal_rate = reversals / max(len(actions) - 2, 1)
                else:
                    reversal_rate = 0.0

                css = 1.0 - (0.40 * var_ratio + 0.35 * entropy + 0.25 * reversal_rate)
                css_values[idx] = float(np.clip(css, 0.0, 1.0))

        return pd.Series(css_values, index=df.index)
