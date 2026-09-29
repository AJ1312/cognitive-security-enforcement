"""Unit tests for core algorithms: CLI, CSS, CVS, and Trust."""

import pytest
import numpy as np
import pandas as pd

from cognitive_security.signals.simulator import UserInteractionSimulator
from cognitive_security.core.cli import CognitiveLoadIndexCalculator
from cognitive_security.core.css import CognitiveStabilityScorer
from cognitive_security.core.cvs import CVSState, CognitiveVulnerabilityClassifier
from cognitive_security.core.trust import AdaptiveTrustManager


@pytest.fixture
def sample_data():
    sim = UserInteractionSimulator(n_sessions=4, events_per_session=30, seed=42)
    return sim.generate_all()


def test_cli_calculator(sample_data):
    calc = CognitiveLoadIndexCalculator()
    cli, contribs = calc.compute_cli(sample_data)

    assert len(cli) == len(sample_data)
    assert len(contribs) == len(sample_data)
    assert cli.min() >= 0.0
    assert cli.max() <= 1.0


def test_css_scorer(sample_data):
    scorer = CognitiveStabilityScorer()
    css = scorer.compute_css(sample_data)

    assert len(css) == len(sample_data)
    assert css.min() >= 0.0
    assert css.max() <= 1.0


def test_cvs_classifier(sample_data):
    calc = CognitiveLoadIndexCalculator()
    scorer = CognitiveStabilityScorer()
    classifier = CognitiveVulnerabilityClassifier()

    sample_data['CLI'], _ = calc.compute_cli(sample_data)
    sample_data['CSS'] = scorer.compute_css(sample_data)

    cvs, states = classifier.compute_cvs(sample_data)

    assert len(cvs) == len(sample_data)
    assert len(states) == len(sample_data)
    assert cvs.min() >= 0.0
    assert cvs.max() <= 1.0
    assert all(isinstance(s, CVSState) for s in states)


def test_trust_manager():
    mgr = AdaptiveTrustManager(decay_alpha=0.5, recovery_lambda=0.1)

    # Test decay under critical CVS
    high_cvs = np.full(50, 0.90)
    decayed_trust = mgr.simulate_trust(high_cvs)
    assert decayed_trust[-1] < 0.05
    assert mgr.get_permission_level(decayed_trust[-1]) == 'suspended'

    # Test recovery under zero CVS
    calm_cvs = np.full(50, 0.10)
    recovered_trust = mgr.simulate_trust(calm_cvs)
    assert recovered_trust[-1] >= 0.90
    assert mgr.get_permission_level(recovered_trust[-1]) == 'full_access'
