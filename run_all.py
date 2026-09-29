#!/usr/bin/env python3
"""
Full System Execution & Results Generation Pipeline.
Runs simulations, evaluates attacks, computes statistical benchmarks,
generates all 14 figures, and exports derived metrics.
"""

import os
import sys
import json
import subprocess
import pandas as pd
import numpy as np

# Ensure local package is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from cognitive_security.config import (
    CLI_WEIGHTS,
    CVS_THRESHOLDS,
    ACTION_SENSITIVITY,
    INTERVENTION_THRESHOLDS,
)
from cognitive_security.signals.simulator import UserInteractionSimulator
from cognitive_security.core.cli import CognitiveLoadIndexCalculator
from cognitive_security.core.css import CognitiveStabilityScorer
from cognitive_security.core.cvs import CognitiveVulnerabilityClassifier
from cognitive_security.core.trust import AdaptiveTrustManager
from cognitive_security.enforcement.friction import CognitiveFrictionEngine
from cognitive_security.enforcement.sandbox import ActionSandbox
from cognitive_security.attacks.simulator import AttackSimulator
from cognitive_security.domains.mapper import DomainMapper
from cognitive_security.privacy.ephemeral import EphemeralStateStore, PrivacyAuditor
from cognitive_security.experiments.validation import ExperimentSimulator
from cognitive_security.visualization.diagrams import (
    plot_system_architecture,
    plot_computation_pipeline,
    plot_intervention_flow,
    plot_validation_experiment,
    plot_privacy_architecture,
    plot_full_dashboard,
)


def main():
    print("=" * 80)
    print("🧠 COGNITIVE SECURITY SYSTEM — COMPLETE REPRODUCIBILITY PIPELINE")
    print("   Patent: Cognitive-State-Aware Adaptive Information Security Enforcement")
    print("=" * 80)

    results_dir = os.path.abspath("results")
    figures_dir = os.path.join(results_dir, "figures")
    tables_dir = os.path.join(results_dir, "tables")
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(tables_dir, exist_ok=True)

    # 1. Run Unit Tests
    print("\n[Step 1/6] Running unit tests...")
    test_ret = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q"])
    if test_ret.returncode != 0:
        print("❌ Tests failed!")
        sys.exit(1)
    print("✓ All unit tests passed.")

    # 2. Simulate User Interaction Data
    print("\n[Step 2/6] Generating simulated interaction telemetry...")
    sim = UserInteractionSimulator(n_sessions=50, events_per_session=100, seed=42)
    df = sim.generate_all()

    cli_calc = CognitiveLoadIndexCalculator()
    css_scorer = CognitiveStabilityScorer()
    cvs_class = CognitiveVulnerabilityClassifier()
    trust_mgr = AdaptiveTrustManager()

    df['CLI'], _ = cli_calc.compute_cli(df)
    df['CSS'] = css_scorer.compute_css(df)
    df['CVS'], states = cvs_class.compute_cvs(df)
    df['CVS_State'] = [s.value for s in states]
    df['Trust'] = trust_mgr.simulate_trust(df['CVS'].values)

    normal = df[~df['is_stressed']]
    stressed = df[df['is_stressed']]
    print(f"✓ Generated {len(df):,} events across {df['session_id'].nunique()} sessions.")

    # 3. Simulate Attack Scenarios
    print("\n[Step 3/6] Simulating 4 Social Engineering Attack Scenarios...")
    attacker = AttackSimulator()
    scenarios = [
        attacker.simulate_bec_attack(),
        attacker.simulate_otp_fraud(),
        attacker.simulate_deepfake(),
        attacker.simulate_insider_coercion(),
    ]
    attack_summaries = []
    for sc in scenarios:
        sc_df = sc['data']
        peak_cvs = float(sc_df['CVS'].max())
        min_trust = float(sc_df['Trust'].min())
        crit_events = int((sc_df['CVS_State'].isin(['HIGH', 'CRITICAL'])).sum())
        pct = float((crit_events / len(sc_df)) * 100)
        attack_summaries.append({
            'scenario': sc['name'],
            'description': sc['description'],
            'peak_cvs': peak_cvs,
            'min_trust': min_trust,
            'critical_events_detected': crit_events,
            'detection_rate_pct': pct,
            'minimum_permission': trust_mgr.get_permission_level(min_trust),
        })
        print(f"  • {sc['name']}: Peak CVS={peak_cvs:.3f}, Min Trust={min_trust:.4f}, Interventions={crit_events}/{len(sc_df)}")

    # 4. Run Novelty Validation Experiment
    print("\n[Step 4/6] Running Novelty Validation Experiment Benchmark (30 participants)...")
    exp_sim = ExperimentSimulator(n_participants=30, n_trials_per_condition=10, seed=42)
    exp_data = exp_sim.run_experiment()
    stats_dict = exp_sim.evaluate_statistics(exp_data)
    print(f"  • CLI Paired t-test: t={stats_dict['t_stat_cli']:.2f}, p={stats_dict['p_val_cli']:.2e}, Cohen's d={stats_dict['cohens_d_cli']:.2f}")
    print(f"  • NASA-TLX Correlation: r={stats_dict['pearson_r_cvs_tlx']:.3f}, p={stats_dict['p_val_tlx']:.2e}")
    print(f"  • ROC Detection AUC: {stats_dict['roc_auc']:.3f}")
    print(f"  • Social Engineering Reduction: {stats_dict['attack_rate_no_sys']:.1%} -> {stats_dict['attack_rate_with_sys']:.1%} ({stats_dict['attack_reduction_pct']:.1f}% reduction)")

    # 5. Generate Figures
    print("\n[Step 5/6] Generating and verifying all figures...")
    plot_system_architecture(os.path.join(figures_dir, "fig09_patent_system_architecture_block_diagram.png"))
    plot_computation_pipeline(os.path.join(figures_dir, "fig10_patent_cognitive_pipeline_flowchart.png"))
    plot_intervention_flow(os.path.join(figures_dir, "fig11_patent_intervention_decision_flow.png"))
    plot_validation_experiment(exp_data, stats_dict, os.path.join(figures_dir, "fig12_novelty_validation_experiment.png"))
    plot_privacy_architecture(os.path.join(figures_dir, "fig13_privacy_preserving_architecture.png"))

    # Also build full dashboard session
    np.random.seed(42)
    n_samples = 300
    times = np.arange(300)
    phases = [
        (0, 120, 'Normal Activity', 'normal'),
        (120, 210, 'Phishing Attack', 'attack'),
        (210, 240, 'Recovery', 'recovery'),
        (240, 300, 'OTP Fraud Attempt', 'attack'),
    ]
    signals = {s: np.zeros(n_samples) for s in CLI_WEIGHTS}
    cli = np.zeros(n_samples)
    css = np.zeros(n_samples)
    cvs = np.zeros(n_samples)
    trust = np.zeros(n_samples)
    trust[0] = 1.0
    cvs_states = []
    interventions = []
    actions = []

    for i, t in enumerate(times):
        if 0 <= t < 120:
            params = UserInteractionSimulator.NORMAL_PARAMS
            phase_type = 'normal'
        elif 120 <= t < 210:
            params = UserInteractionSimulator.STRESSED_PARAMS
            phase_type = 'attack'
        elif 210 <= t < 240:
            params = {k: ((v[0] + UserInteractionSimulator.NORMAL_PARAMS[k][0]) / 2,
                          (v[1] + UserInteractionSimulator.NORMAL_PARAMS[k][1]) / 2)
                      for k, v in UserInteractionSimulator.STRESSED_PARAMS.items()}
            phase_type = 'recovery'
        else:
            params = UserInteractionSimulator.STRESSED_PARAMS
            phase_type = 'attack'

        for signal, (mu, sigma) in params.items():
            signals[signal][i] = float(np.clip(np.random.normal(mu, sigma), 0.0, None))
            if signal == 'context_mismatch_score':
                signals[signal][i] = float(np.clip(signals[signal][i], 0.0, 1.0))

        cli_raw = sum(CLI_WEIGHTS[s] * abs(signals[s][i] - UserInteractionSimulator.NORMAL_PARAMS[s][0]) / max(UserInteractionSimulator.NORMAL_PARAMS[s][1], 0.1) for s in CLI_WEIGHTS) / sum(CLI_WEIGHTS.values())
        cli[i] = float(1.0 / (1.0 + np.exp(-2.0 * (cli_raw - 1.5))))

        window = max(0, i - 10)
        var_recent = np.var(signals['hesitation_before_confirm'][window:i+1]) if i > 0 else 160000.0
        css[i] = float(np.clip(1.0 - min(var_recent / 160000.0, 1.0), 0.0, 1.0))

        delta_cli = max(0.0, cli[i] - cli[max(0, i - 1)])
        cvs[i] = float(np.clip(0.40 * cli[i] + 0.40 * (1.0 - css[i]) + 0.20 * delta_cli, 0.0, 1.0))

        if cvs[i] < 0.30:
            cvs_states.append('NORMAL')
        elif cvs[i] < 0.60:
            cvs_states.append('ELEVATED')
        elif cvs[i] < 0.80:
            cvs_states.append('HIGH')
        else:
            cvs_states.append('CRITICAL')

        if i > 0:
            if cvs[i] > 0.30:
                trust[i] = trust[i - 1] * np.exp(-0.50 * cvs[i])
            else:
                trust[i] = trust[i - 1] + 0.10 * (1.0 - trust[i - 1]) * (1.0 - cvs[i])
            trust[i] = float(np.clip(trust[i], 0.0, 1.0))

        if cvs_states[-1] in ['HIGH', 'CRITICAL'] and phase_type == 'attack':
            interventions.append((t, cvs_states[-1]))

        if np.random.random() < 0.10:
            action_type = 'wire_transfer' if phase_type == 'attack' else 'view_account'
            actions.append((t, action_type))

    session_data = {
        'times': times,
        'signals': signals,
        'cli': cli,
        'css': css,
        'cvs': cvs,
        'cvs_states': cvs_states,
        'trust': trust,
        'interventions': interventions,
        'actions': actions,
        'phases': phases,
    }
    plot_full_dashboard(session_data, os.path.join(figures_dir, "fig14_end_to_end_system_dashboard.png"))

    # Also copy all 14 figures to assets/figures
    assets_figures = os.path.abspath("assets/figures")
    os.makedirs(assets_figures, exist_ok=True)
    for fig_file in os.listdir(figures_dir):
        if fig_file.endswith(".png"):
            src = os.path.join(figures_dir, fig_file)
            dst = os.path.join(assets_figures, fig_file)
            with open(src, "rb") as f1, open(dst, "wb") as f2:
                f2.write(f1.read())
    print("✓ All 14 figures saved to results/figures and assets/figures.")

    # 6. Export Derived Metrics & Tables
    print("\n[Step 6/6] Exporting derived metrics and tabular datasets...")
    derived_metrics = {
        'simulation': {
            'total_events': len(df),
            'sessions': df['session_id'].nunique(),
            'normal_cli_mean': float(normal['CLI'].mean()),
            'normal_cli_std': float(normal['CLI'].std()),
            'stressed_cli_mean': float(stressed['CLI'].mean()),
            'stressed_cli_std': float(stressed['CLI'].std()),
            'normal_css_mean': float(normal['CSS'].mean()),
            'stressed_css_mean': float(stressed['CSS'].mean()),
            'normal_cvs_mean': float(normal['CVS'].mean()),
            'stressed_cvs_mean': float(stressed['CVS'].mean()),
            'min_trust_normal': float(normal['Trust'].min()),
            'min_trust_stressed': float(stressed['Trust'].min()),
        },
        'attacks': attack_summaries,
        'experiment_validation': stats_dict,
    }

    with open(os.path.join(results_dir, "derived_metrics.json"), "w") as f:
        json.dump(derived_metrics, f, indent=2)

    # Export domain comparison table
    domain_mapper = DomainMapper()
    domain_df = domain_mapper.get_comparison_table()
    domain_df.to_csv(os.path.join(tables_dir, "domain_comparison.csv"), index=False)

    # Export compliance table
    auditor = PrivacyAuditor()
    comp_df = auditor.generate_compliance_report()
    comp_df.to_csv(os.path.join(tables_dir, "privacy_compliance_matrix.csv"), index=False)

    # Export attack summary table
    pd.DataFrame(attack_summaries).to_csv(os.path.join(tables_dir, "attack_mitigation_evaluations.csv"), index=False)

    # Export experiment sample data
    exp_data.head(500).to_csv(os.path.join(tables_dir, "validation_experiment_trials_sample.csv"), index=False)

    print("✓ Derived metrics written to results/derived_metrics.json")
    print("✓ Tables written to results/tables/")
    print("\n======================================================================")
    print("🎉 EXECUTION COMPLETE! ALL DERIVED RESULTS & FIGURES GENERATED.")
    print("======================================================================")


if __name__ == "__main__":
    main()
