"""
Cognitive Load Index (CLI) Processor.
Patent Reference: Claim 1(ii), Claim 3, Block 320.

Formula:
CLI(t) = (1/N) * sum_i (w_i * |S_i(t) - mu_i| / sigma_i)
CLI_norm = sigmoid(2.0 * (CLI_raw - 1.5))
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy.special import expit

from cognitive_security.config import CLI_WEIGHTS, BASELINE_WINDOW_SIZE


class CognitiveLoadIndexCalculator:
    """
    Computes the Cognitive Load Index (CLI) from non-biometric interaction signals.
    CLI = weighted average of |z-scores| relative to per-user rolling baselines,
    projected into [0, 1] via sigmoid transform.
    """

    def __init__(
        self,
        weights: Dict[str, float] = None,
        baseline_window: int = BASELINE_WINDOW_SIZE
    ):
        self.weights = weights or CLI_WEIGHTS
        self.baseline_window = baseline_window
        self.baselines: Dict[str, Dict[str, Tuple[float, float]]] = {}

    def _compute_baseline(self, user_data: pd.DataFrame) -> Dict[str, Tuple[float, float]]:
        """Compute per-signal baseline mean and std from normal interaction history."""
        baseline = {}
        if 'is_stressed' in user_data.columns:
            normal_data = user_data[~user_data['is_stressed']]
        else:
            normal_data = user_data

        if len(normal_data) < 10:
            normal_data = user_data.head(self.baseline_window)

        for signal in self.weights:
            if signal in normal_data.columns:
                vals = normal_data[signal].values[:self.baseline_window]
                mu = float(np.mean(vals)) if len(vals) > 0 else 0.0
                sigma = float(np.std(vals)) if len(vals) > 1 else 1.0
                sigma = max(sigma, 1e-6)  # Prevent division by zero
                baseline[signal] = (mu, sigma)
            else:
                baseline[signal] = (0.0, 1.0)
        return baseline

    def compute_cli(self, df: pd.DataFrame) -> Tuple[pd.Series, List[Dict[str, float]]]:
        """
        Compute CLI for each event in the DataFrame.
        Returns:
            Tuple of (CLI series, list of per-signal weighted contributions)
        """
        cli_values = []
        contributions_all = []

        user_ids = df['user_id'].unique() if 'user_id' in df.columns else ['default_user']

        for user_id in user_ids:
            if 'user_id' in df.columns:
                user_mask = df['user_id'] == user_id
                user_data = df[user_mask].copy()
            else:
                user_mask = pd.Series(True, index=df.index)
                user_data = df.copy()

            baseline = self._compute_baseline(user_data)
            self.baselines[user_id] = baseline

            for _, row in user_data.iterrows():
                weighted_sum = 0.0
                weight_total = 0.0
                contribs = {}

                for signal, weight in self.weights.items():
                    if signal in row:
                        mu, sigma = baseline[signal]
                        z = abs((row[signal] - mu) / sigma)
                        weighted_sum += weight * z
                        weight_total += weight
                        contribs[signal] = float(weight * z)

                cli_raw = weighted_sum / weight_total if weight_total > 0 else 0.0
                # Sigmoid normalization to [0, 1]
                cli_norm = float(expit(2.0 * (cli_raw - 1.5)))
                cli_values.append(cli_norm)
                contributions_all.append(contribs)

        return pd.Series(cli_values, index=df.index), contributions_all
