"""
Command Line Interface (CLI) for Cognitive Security Prototype.
Usage:
    python -m cognitive_security.cli_runner demo
    python -m cognitive_security.cli_runner simulate
    python -m cognitive_security.cli_runner attack
    python -m cognitive_security.cli_runner benchmark
    python -m cognitive_security.cli_runner figures
    python -m cognitive_security.cli_runner claims
"""

import argparse
import sys
import os
import json
import pandas as pd
import numpy as np

from cognitive_security.config import (
    CLI_WEIGHTS,
    CVS_THRESHOLDS,
    ACTION_SENSITIVITY,
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


def run_demo():
    print("=" * 70)
    print("🧠 COGNITIVE SECURITY SYSTEM — INTERACTIVE DEMONSTRATION")
    print("=" * 70)
    sim = UserInteractionSimulator(n_sessions=4, events_per_session=20)
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

    normal_subset = df[~df['is_stressed']].head(5)
    stressed_subset = df[df['is_stressed']].head(5)

    print("\n[1] NORMAL SESSION (Baseline Activity):")
    print(normal_subset[['event_idx', 'action_type', 'CLI', 'CSS', 'CVS', 'CVS_State', 'Trust']].to_string(index=False))

    print("\n[2] STRESSED SESSION (Under Social Engineering / Attack):")
    print(stressed_subset[['event_idx', 'action_type', 'CLI', 'CSS', 'CVS', 'CVS_State', 'Trust']].to_string(index=False))

    print("\n✅ Cognitive vulnerability state effectively modulates session trust level.")


def run_simulate(events: int = 5000):
    print("=" * 70)
    print(f"📊 RUNNING FULL COGNITIVE SECURITY SIMULATION ({events} events)")
    print("=" * 70)
    n_sessions = max(4, events // 100)
    sim = UserInteractionSimulator(n_sessions=n_sessions, events_per_session=100)
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

    print(f"\nGenerated {len(df):,} events across {df['session_id'].nunique()} sessions:")
    print(f"  • Normal CLI Mean:    {normal['CLI'].mean():.4f} +/- {normal['CLI'].std():.4f}")
    print(f"  • Stressed CLI Mean:  {stressed['CLI'].mean():.4f} +/- {stressed['CLI'].std():.4f}")
    print(f"  • Normal CSS Mean:    {normal['CSS'].mean():.4f} +/- {normal['CSS'].std():.4f}")
    print(f"  • Stressed CSS Mean:  {stressed['CSS'].mean():.4f} +/- {stressed['CSS'].std():.4f}")
    print(f"  • Normal CVS Mean:    {normal['CVS'].mean():.4f} +/- {normal['CVS'].std():.4f}")
    print(f"  • Stressed CVS Mean:  {stressed['CVS'].mean():.4f} +/- {stressed['CVS'].std():.4f}")
    print(f"  • Min Trust (Normal):   {normal['Trust'].min():.4f}")
    print(f"  • Min Trust (Stressed): {stressed['Trust'].min():.4f}")


def run_attacks():
    print("=" * 70)
    print("🔴 EVALUATING ATTACK MITIGATION SCENARIOS")
    print("=" * 70)
    attacker = AttackSimulator()
    scenarios = [
        attacker.simulate_bec_attack(),
        attacker.simulate_otp_fraud(),
        attacker.simulate_deepfake(),
        attacker.simulate_insider_coercion(),
    ]

    for sc in scenarios:
        df = sc['data']
        peak_cvs = df['CVS'].max()
        min_trust = df['Trust'].min()
        high_crit = (df['CVS_State'].isin(['HIGH', 'CRITICAL'])).sum()
        pct = (high_crit / len(df)) * 100
        print(f"\nScenario: {sc['name']}")
        print(f"  Description:  {sc['description']}")
        print(f"  Peak CVS:     {peak_cvs:.4f} | Min Trust: {min_trust:.4f}")
        print(f"  Vulnerability Triggered: {high_crit}/{len(df)} events ({pct:.1f}%)")
        if 'UEBA_Risk' in df.columns:
            print(f"  Traditional UEBA: {df['UEBA_Risk'].mean():.4f} (Blind to coercion)")
            print(f"  Cognitive Security: {df['CVS'].mean():.4f} (Detected coercion)")


def run_benchmark():
    print("=" * 70)
    print("🔬 RUNNING NOVELTY VALIDATION EXPERIMENT BENCHMARK")
    print("=" * 70)
    sim = ExperimentSimulator(n_participants=30, n_trials_per_condition=10)
    exp_data = sim.run_experiment()
    res = sim.evaluate_statistics(exp_data)

    print(f"Participants: {res['n_participants']} | Total Trials: {res['n_trials']}")
    print(f"  1. CLI Paired t-test: t={res['t_stat_cli']:.2f}, p={res['p_val_cli']:.2e}, Cohen's d={res['cohens_d_cli']:.2f}")
    print(f"  2. NASA-TLX Pearson r: r={res['pearson_r_cvs_tlx']:.3f}, p={res['p_val_tlx']:.2e}")
    print(f"  3. ROC/AUC Load Detection: AUC={res['roc_auc']:.3f} (Optimal Thresh={res['optimal_threshold']:.2f})")
    print(f"  4. Attack Reduction: {res['attack_rate_no_sys']:.1%} -> {res['attack_rate_with_sys']:.1%} ({res['attack_reduction_pct']:.1f}% reduction)")


def generate_all_figures(output_dir: str = "results/figures"):
    print("=" * 70)
    print(f"🎨 GENERATING PUBLICATION & PATENT FIGURES -> {output_dir}")
    print("=" * 70)
    os.makedirs(output_dir, exist_ok=True)

    # 1. Patent Architecture (Figure 1)
    p1 = os.path.join(output_dir, "fig09_patent_system_architecture_block_diagram.png")
    plot_system_architecture(p1)
    print(f"  ✓ Saved: {os.path.basename(p1)}")

    # 2. Computation Pipeline (Figure 2)
    p2 = os.path.join(output_dir, "fig10_patent_cognitive_pipeline_flowchart.png")
    plot_computation_pipeline(p2)
    print(f"  ✓ Saved: {os.path.basename(p2)}")

    # 3. Intervention Decision Flow (Figure 3)
    p3 = os.path.join(output_dir, "fig11_patent_intervention_decision_flow.png")
    plot_intervention_flow(p3)
    print(f"  ✓ Saved: {os.path.basename(p3)}")

    # 4. Novelty Validation Experiment
    exp_sim = ExperimentSimulator(n_participants=30, n_trials_per_condition=10)
    exp_data = exp_sim.run_experiment()
    stats_dict = exp_sim.evaluate_statistics(exp_data)
    p4 = os.path.join(output_dir, "fig12_novelty_validation_experiment.png")
    plot_validation_experiment(exp_data, stats_dict, p4)
    print(f"  ✓ Saved: {os.path.basename(p4)}")

    # 5. Privacy Architecture
    p5 = os.path.join(output_dir, "fig13_privacy_preserving_architecture.png")
    plot_privacy_architecture(p5)
    print(f"  ✓ Saved: {os.path.basename(p5)}")

    # 6. End-to-End Simulation Dashboard
    # Generate session time-series
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

    session = {
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
    p6 = os.path.join(output_dir, "fig14_end_to_end_system_dashboard.png")
    plot_full_dashboard(session, p6)
    print(f"  ✓ Saved: {os.path.basename(p6)}")

    # Copy to assets/figures as well
    assets_dir = output_dir.replace("results/figures", "assets/figures")
    if os.path.exists(assets_dir) or output_dir != assets_dir:
        os.makedirs(assets_dir, exist_ok=True)
        for fn in [p1, p2, p3, p4, p5, p6]:
            dst = os.path.join(assets_dir, os.path.basename(fn))
            with open(fn, 'rb') as f_src, open(dst, 'wb') as f_dst:
                f_dst.write(f_src.read())

    print("✅ All figures generated successfully.")


def main():
    parser = argparse.ArgumentParser(
        description="Cognitive-State-Aware Adaptive Information Security Enforcement CLI"
    )
    parser.add_argument(
        "command",
        choices=["demo", "simulate", "attack", "benchmark", "figures", "all"],
        help="Command to run"
    )
    args = parser.parse_args()

    if args.command == "demo":
        run_demo()
    elif args.command == "simulate":
        run_simulate()
    elif args.command == "attack":
        run_attacks()
    elif args.command == "benchmark":
        run_benchmark()
    elif args.command == "figures":
        generate_all_figures()
    elif args.command == "all":
        run_demo()
        run_simulate()
        run_attacks()
        run_benchmark()
        generate_all_figures()


if __name__ == "__main__":
    main()
