"""Unit tests for friction, sandbox, attacks, and privacy modules."""

import pytest
import time
from cognitive_security.enforcement.friction import CognitiveFrictionEngine, SecurityIntervention
from cognitive_security.enforcement.sandbox import ActionSandbox
from cognitive_security.attacks.simulator import AttackSimulator
from cognitive_security.privacy.ephemeral import EphemeralStateStore, PrivacyAuditor
from cognitive_security.domains.mapper import DomainMapper
from cognitive_security.experiments.validation import ExperimentSimulator


def test_cognitive_friction_engine():
    engine = CognitiveFrictionEngine()

    # Low sensitivity & normal state -> ALLOW
    interventions = engine.select_friction("NORMAL", action_sensitivity=0.1, cvs_score=0.1)
    assert any(i.intervention_type == 'ALLOW' for i in interventions)

    # High sensitivity & critical state -> BLOCK / ChannelEscalation
    interventions_crit = engine.select_friction("CRITICAL", action_sensitivity=0.9, cvs_score=0.9)
    assert any(i.intervention_type in ['BLOCK', 'ChannelEscalation'] for i in interventions_crit)


def test_action_sandbox():
    sandbox = ActionSandbox()

    res_allowed = sandbox.process_action("view_account", cvs_score=0.1, trust_level=0.9)
    assert res_allowed['outcome'] == 'ALLOWED'

    res_blocked = sandbox.process_action("delete_resource", cvs_score=0.95, trust_level=0.1)
    assert res_blocked['outcome'] == 'BLOCKED_ESCALATED'


def test_attack_simulator():
    attacker = AttackSimulator()
    bec = attacker.simulate_bec_attack()
    assert 'CLI' in bec['data'].columns
    assert 'CVS' in bec['data'].columns
    assert 'Trust' in bec['data'].columns
    assert bec['data']['Trust'].min() < 0.20


def test_privacy_store_and_auditor():
    store = EphemeralStateStore(default_ttl_seconds=1)
    store.put("key1", "value1")
    assert store.get("key1") == "value1"

    # Simulate TTL expiration
    store._store["key1"] = ("value1", time.time() - 1)
    assert store.get("key1") is None

    auditor = PrivacyAuditor()
    valid, _ = auditor.validate_output_schema({'cli': 0.5, 'cvs': 0.4})
    assert valid is True

    invalid, viols = auditor.validate_output_schema({'user_emotion': 'anxious', 'keystroke_content': 'secret'})
    assert invalid is False
    assert len(viols) == 2


def test_domain_mapper():
    mapper = DomainMapper()
    df = mapper.get_comparison_table()
    assert len(df) == 4
    assert 'Banking & Financial Services' in df['Domain'].values


def test_experiment_simulator():
    sim = ExperimentSimulator(n_participants=5, n_trials_per_condition=3, seed=42)
    data = sim.run_experiment()
    assert len(data) > 0
    stats_dict = sim.evaluate_statistics(data)
    assert stats_dict['roc_auc'] > 0.80
