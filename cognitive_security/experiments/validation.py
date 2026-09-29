"""
Novelty Validation Experiment Simulator.
Patent Reference: Section 12.

Simulates a cheap, reproducible within-subjects validation experiment:
- 30 participants
- Normal vs Cognitive Load conditions (n-back task)
- Social engineering cues in half of loaded trials
- Formal statistical validation: paired t-tests, Pearson correlation, Cohen's d, ROC/AUC
"""

from typing import Dict, Any
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_curve, auc

from cognitive_security.config import RANDOM_SEED


class ExperimentSimulator:
    """
    Simulates a validation experiment for patent novelty demonstration.
    Generates synthetic participant data matching expected distributions.
    """

    def __init__(self, n_participants: int = 30, n_trials_per_condition: int = 10, seed: int = RANDOM_SEED):
        self.n_participants = n_participants
        self.n_trials = n_trials_per_condition
        self.rng = np.random.RandomState(seed)

    def generate_nasa_tlx(self, condition: str) -> Dict[str, float]:
        """Generate NASA-TLX scores for a condition."""
        if condition == 'normal':
            return {
                'mental_demand': float(self.rng.uniform(20.0, 40.0)),
                'physical_demand': float(self.rng.uniform(5.0, 15.0)),
                'temporal_demand': float(self.rng.uniform(15.0, 35.0)),
                'performance': float(self.rng.uniform(70.0, 90.0)),
                'effort': float(self.rng.uniform(25.0, 45.0)),
                'frustration': float(self.rng.uniform(10.0, 30.0)),
            }
        else:  # loaded
            return {
                'mental_demand': float(self.rng.uniform(60.0, 85.0)),
                'physical_demand': float(self.rng.uniform(10.0, 25.0)),
                'temporal_demand': float(self.rng.uniform(55.0, 80.0)),
                'performance': float(self.rng.uniform(40.0, 65.0)),
                'effort': float(self.rng.uniform(60.0, 85.0)),
                'frustration': float(self.rng.uniform(50.0, 75.0)),
            }

    def simulate_participant(self, participant_id: int) -> pd.DataFrame:
        """Simulate one participant's trials across normal and loaded conditions."""
        records = []
        baseline_offset = float(self.rng.normal(0.0, 0.10))

        for trial in range(self.n_trials):
            for condition in ['normal', 'loaded']:
                cues = [False, True] if condition == 'loaded' else [False]
                for has_se_cue in cues:
                    if condition == 'normal':
                        cli = float(self.rng.normal(0.25 + baseline_offset, 0.08))
                        css = float(self.rng.normal(0.75 - baseline_offset * 0.5, 0.08))
                    else:
                        cli = float(self.rng.normal(0.65 + baseline_offset, 0.12))
                        css = float(self.rng.normal(0.45 - baseline_offset * 0.5, 0.12))

                        if has_se_cue:
                            cli += float(self.rng.uniform(0.10, 0.20))
                            css -= float(self.rng.uniform(0.05, 0.15))

                    cli = float(np.clip(cli, 0.0, 1.0))
                    css = float(np.clip(css, 0.0, 1.0))
                    cvs = 0.40 * cli + 0.40 * (1.0 - css) + 0.20 * max(0.0, cli - 0.30)
                    cvs = float(np.clip(cvs, 0.0, 1.0))

                    tlx = self.generate_nasa_tlx(condition)

                    # Attack success baseline (without system)
                    base_attack_success = 0.70 if (condition == 'loaded' and has_se_cue) else 0.05
                    attack_success_no_system = self.rng.random() < base_attack_success

                    # Attack success with cognitive friction system
                    if cvs > 0.50:
                        attack_success_with_system = self.rng.random() < 0.12
                    else:
                        attack_success_with_system = attack_success_no_system

                    records.append({
                        'participant_id': participant_id,
                        'trial': trial,
                        'condition': condition,
                        'has_se_cue': has_se_cue,
                        'CLI': cli,
                        'CSS': css,
                        'CVS': cvs,
                        'tlx_overall': float(np.mean(list(tlx.values()))),
                        'tlx_mental': tlx['mental_demand'],
                        'attack_success_no_system': attack_success_no_system,
                        'attack_success_with_system': attack_success_with_system,
                    })

        return pd.DataFrame(records)

    def run_experiment(self) -> pd.DataFrame:
        """Run complete multi-participant experiment simulation."""
        all_data = []
        for p in range(self.n_participants):
            all_data.append(self.simulate_participant(p))
        return pd.concat(all_data, ignore_index=True)

    def evaluate_statistics(self, exp_data: pd.DataFrame) -> Dict[str, Any]:
        """Compute all formal hypothesis testing metrics."""
        # 1. Paired t-test for CLI
        normal_cli = exp_data[exp_data['condition'] == 'normal'].groupby('participant_id')['CLI'].mean()
        loaded_cli = exp_data[exp_data['condition'] == 'loaded'].groupby('participant_id')['CLI'].mean()
        t_cli, p_cli = stats.ttest_rel(normal_cli, loaded_cli)
        d_cli = (loaded_cli.mean() - normal_cli.mean()) / np.sqrt((loaded_cli.std()**2 + normal_cli.std()**2) / 2)

        # 2. Pearson correlation with NASA-TLX
        corr_cvs_tlx, p_corr = stats.pearsonr(exp_data['CVS'], exp_data['tlx_overall'])

        # 3. ROC Analysis
        y_true = (exp_data['condition'] == 'loaded').astype(int)
        y_scores = exp_data['CVS']
        fpr, tpr, thresholds = roc_curve(y_true, y_scores)
        roc_auc = float(auc(fpr, tpr))
        optimal_idx = int(np.argmax(tpr - fpr))
        optimal_threshold = float(thresholds[optimal_idx])

        # 4. Attack prevention efficacy
        se_trials = exp_data[exp_data['has_se_cue'] == True]
        attack_rate_no_sys = float(se_trials['attack_success_no_system'].mean())
        attack_rate_with_sys = float(se_trials['attack_success_with_system'].mean())
        reduction = float((attack_rate_no_sys - attack_rate_with_sys) / attack_rate_no_sys * 100)

        return {
            'n_participants': int(exp_data['participant_id'].nunique()),
            'n_trials': len(exp_data),
            'cli_normal_mean': float(normal_cli.mean()),
            'cli_normal_std': float(normal_cli.std()),
            'cli_loaded_mean': float(loaded_cli.mean()),
            'cli_loaded_std': float(loaded_cli.std()),
            't_stat_cli': float(t_cli),
            'p_val_cli': float(p_cli),
            'cohens_d_cli': float(d_cli),
            'pearson_r_cvs_tlx': float(corr_cvs_tlx),
            'p_val_tlx': float(p_corr),
            'roc_auc': float(roc_auc),
            'optimal_threshold': float(optimal_threshold),
            'optimal_sensitivity': float(tpr[optimal_idx]),
            'optimal_specificity': float(1.0 - fpr[optimal_idx]),
            'attack_rate_no_sys': float(attack_rate_no_sys),
            'attack_rate_with_sys': float(attack_rate_with_sys),
            'attack_reduction_pct': float(reduction),
        }
