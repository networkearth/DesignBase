"""
Unit tests for support module functions.
"""

import pytest
import numpy as np
import pandas as pd
from fishflow.common.support import (
    log_likelihood_member,
    prob_members,
    build_model_matrices,
    compute_support,
    compute_mixtures
)


class TestLogLikelihoodMember:
    """Tests for log_likelihood_member function."""

    def test_epsilon_zero_uses_reference_model(self):
        """When epsilon=0, should use only reference model."""
        reference_matrix = np.array([[0.3, 0.7], [0.6, 0.4]])
        model_matrix = np.array([[0.8, 0.2], [0.1, 0.9]])
        selections = np.array([[1, 0], [0, 1]])

        ll = log_likelihood_member(0.0, reference_matrix, model_matrix, selections)

        # Should use reference model: log(0.3) + log(0.4)
        expected = np.log(0.3) + np.log(0.4)
        assert np.isclose(ll, expected)

    def test_epsilon_one_uses_target_model(self):
        """When epsilon=1, should use only target model."""
        reference_matrix = np.array([[0.3, 0.7], [0.6, 0.4]])
        model_matrix = np.array([[0.8, 0.2], [0.1, 0.9]])
        selections = np.array([[1, 0], [0, 1]])

        ll = log_likelihood_member(1.0, reference_matrix, model_matrix, selections)

        # Should use model: log(0.8) + log(0.9)
        expected = np.log(0.8) + np.log(0.9)
        assert np.isclose(ll, expected)

    def test_invalid_epsilon_raises_error(self):
        """Should raise error for epsilon outside [0, 1]."""
        reference_matrix = np.array([[0.5, 0.5]])
        model_matrix = np.array([[0.5, 0.5]])
        selections = np.array([[1, 0]])

        with pytest.raises(ValueError, match="epsilon must be in"):
            log_likelihood_member(-0.1, reference_matrix, model_matrix, selections)

        with pytest.raises(ValueError, match="epsilon must be in"):
            log_likelihood_member(1.5, reference_matrix, model_matrix, selections)

    def test_mismatched_shapes_raises_error(self):
        """Should raise error if matrix shapes don't match."""
        reference_matrix = np.array([[0.5, 0.5]])
        model_matrix = np.array([[0.5, 0.5], [0.5, 0.5]])
        selections = np.array([[1, 0]])

        with pytest.raises(ValueError, match="same shape"):
            log_likelihood_member(0.5, reference_matrix, model_matrix, selections)


class TestProbMembers:
    """Tests for prob_members function."""

    def test_uniform_prior_with_single_epsilon(self):
        """With one epsilon, should return probability 1.0."""
        reference_matrix = np.array([[0.3, 0.7], [0.6, 0.4]])
        model_matrix = np.array([[0.8, 0.2], [0.1, 0.9]])
        selections = np.array([[1, 0], [0, 1]])
        epsilons = np.array([0.5])

        probs = prob_members(reference_matrix, model_matrix, selections, epsilons)

        assert len(probs) == 1
        assert np.isclose(probs[0], 1.0)

    def test_probabilities_sum_to_one(self):
        """Posterior probabilities should sum to 1."""
        reference_matrix = np.array([[0.3, 0.7], [0.6, 0.4]])
        model_matrix = np.array([[0.8, 0.2], [0.1, 0.9]])
        selections = np.array([[1, 0], [0, 1]])
        epsilons = np.array([0.0, 0.5, 1.0])

        probs = prob_members(reference_matrix, model_matrix, selections, epsilons)

        assert np.isclose(probs.sum(), 1.0)

    def test_custom_prior(self):
        """Should respect custom prior probabilities."""
        reference_matrix = np.array([[0.5, 0.5]])
        model_matrix = np.array([[0.5, 0.5]])
        selections = np.array([[1, 0]])
        epsilons = np.array([0.0, 1.0])
        prior = np.array([0.9, 0.1])

        probs = prob_members(reference_matrix, model_matrix, selections, epsilons, prior)

        # With identical likelihoods, posterior should match prior
        assert np.allclose(probs, prior)


class TestBuildModelMatrices:
    """Tests for build_model_matrices function."""

    def test_basic_matrix_construction(self):
        """Should correctly construct matrices from dataframes."""
        model_df = pd.DataFrame({
            '_decision': [1, 1, 2, 2],
            '_choice': ['A', 'B', 'A', 'B'],
            'probability': [0.8, 0.2, 0.3, 0.7]
        })

        reference_df = pd.DataFrame({
            '_decision': [1, 1, 2, 2],
            '_choice': ['A', 'B', 'A', 'B'],
            'probability': [0.5, 0.5, 0.6, 0.4]
        })

        selections_df = pd.DataFrame({
            '_decision': [1, 2],
            '_choice': ['A', 'B']
        })

        model_matrix, ref_matrix, sel_matrix = build_model_matrices(
            model_df, reference_df, selections_df
        )

        assert model_matrix.shape == (2, 2)
        assert ref_matrix.shape == (2, 2)
        assert sel_matrix.shape == (2, 2)

        # Check values
        assert model_matrix[0, 0] == 0.8  # Decision 1, Choice A
        assert ref_matrix[1, 1] == 0.4  # Decision 2, Choice B

        # Check selections
        assert sel_matrix[0, 0] == 1  # Decision 1 selected A
        assert sel_matrix[1, 1] == 1  # Decision 2 selected B

    def test_missing_columns_raises_error(self):
        """Should raise error if required columns are missing."""
        model_df = pd.DataFrame({
            '_decision': [1],
            '_choice': ['A']
            # Missing 'probability'
        })

        reference_df = pd.DataFrame({
            '_decision': [1],
            '_choice': ['A'],
            'probability': [0.5]
        })

        selections_df = pd.DataFrame({
            '_decision': [1],
            '_choice': ['A']
        })

        with pytest.raises(ValueError, match="must have columns"):
            build_model_matrices(model_df, reference_df, selections_df)


class TestComputeSupport:
    """Tests for compute_support function."""

    def test_computes_support_correctly(self):
        """Should compute support across model family."""
        model_df = pd.DataFrame({
            '_decision': [1, 1],
            '_choice': ['A', 'B'],
            'probability': [0.8, 0.2]
        })

        reference_df = pd.DataFrame({
            '_decision': [1, 1],
            '_choice': ['A', 'B'],
            'probability': [0.5, 0.5]
        })

        selections_df = pd.DataFrame({
            '_decision': [1],
            '_choice': ['A']
        })

        epsilons = np.array([0.0, 0.5, 1.0])

        support = compute_support(model_df, reference_df, selections_df, epsilons)

        assert len(support) == 3
        assert np.isclose(support.sum(), 1.0)
        # Model predicts A better than reference, so epsilon=1 should have higher support
        assert support[2] > support[0]


class TestComputeMixtures:
    """Tests for compute_mixtures function."""

    def test_basic_mixture_computation(self):
        """Should compute mixture probabilities correctly."""
        model_df = pd.DataFrame({
            '_decision': [1, 1],
            '_choice': ['A', 'B'],
            'probability': [0.8, 0.2]
        })

        reference_df = pd.DataFrame({
            '_decision': [1, 1],
            '_choice': ['A', 'B'],
            'probability': [0.5, 0.5]
        })

        epsilons = np.array([0.0, 1.0])

        mixtures = compute_mixtures(model_df, reference_df, epsilons)

        # Should have 2 decisions * 2 choices * 2 epsilons = 4 rows
        assert len(mixtures) == 4

        # Check epsilon=0 uses reference model
        eps0 = mixtures[mixtures['epsilon'] == 0.0]
        assert np.isclose(eps0[eps0['_choice'] == 'A']['probability'].values[0], 0.5)

        # Check epsilon=1 uses target model
        eps1 = mixtures[mixtures['epsilon'] == 1.0]
        assert np.isclose(eps1[eps1['_choice'] == 'A']['probability'].values[0], 0.8)

    def test_probabilities_sum_to_one_per_decision_epsilon(self):
        """Probabilities should sum to 1 for each (decision, epsilon) group."""
        model_df = pd.DataFrame({
            '_decision': [1, 1, 1, 2, 2],
            '_choice': ['A', 'B', 'C', 'A', 'B'],
            'probability': [0.5, 0.3, 0.2, 0.7, 0.3]
        })

        reference_df = pd.DataFrame({
            '_decision': [1, 1, 1, 2, 2],
            '_choice': ['A', 'B', 'C', 'A', 'B'],
            'probability': [0.33, 0.33, 0.34, 0.6, 0.4]
        })

        epsilons = np.array([0.0, 0.25, 0.5, 0.75, 1.0])

        mixtures = compute_mixtures(model_df, reference_df, epsilons)

        # Check each (decision, epsilon) group sums to 1
        grouped = mixtures.groupby(['_decision', 'epsilon'])['probability'].sum()
        assert np.allclose(grouped.values, 1.0)

    def test_preserves_context_columns(self):
        """Should preserve additional context columns from input."""
        model_df = pd.DataFrame({
            '_decision': [1, 1],
            '_choice': ['A', 'B'],
            'probability': [0.8, 0.2],
            'datetime': ['2023-01-01', '2023-01-01'],
            'depth_bin': [0, 1]
        })

        reference_df = pd.DataFrame({
            '_decision': [1, 1],
            '_choice': ['A', 'B'],
            'probability': [0.5, 0.5],
            'datetime': ['2023-01-01', '2023-01-01'],
            'depth_bin': [0, 1]
        })

        epsilons = np.array([0.5])

        mixtures = compute_mixtures(model_df, reference_df, epsilons)

        assert 'datetime' in mixtures.columns
        assert 'depth_bin' in mixtures.columns
