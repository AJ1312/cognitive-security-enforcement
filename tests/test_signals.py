"""Unit tests for signals module."""

import pytest
import pandas as pd
import numpy as np

from cognitive_security.signals.simulator import UserInteractionSimulator
from cognitive_security.config import CLI_WEIGHTS


def test_signal_simulator_generation():
    sim = UserInteractionSimulator(n_sessions=4, events_per_session=25, seed=42)
    df = sim.generate_all()

    assert len(df) == 100
    assert df['session_id'].nunique() == 4
    assert set(CLI_WEIGHTS.keys()).issubset(set(df.columns))
    assert 'is_stressed' in df.columns
    assert 'action_type' in df.columns

    # Verify context mismatch score is bounded in [0, 1]
    assert df['context_mismatch_score'].min() >= 0.0
    assert df['context_mismatch_score'].max() <= 1.0

    # Verify hesitation is non-negative
    assert df['hesitation_before_confirm'].min() >= 50.0
