"""Tests for fishflow.common.support module."""

import numpy as np
import pandas as pd
import pytest

from fishflow.common.support import (
    log_likelihood_member,
    prob_members,
    build_model_matrices,
    compute_support,
    compute_mixtures
)


class TestLogLikelihoodMember:
    """Tests for log_likelihood_member function."""

    def test_basic_computation(self):
        """Test basic likelihood computation."""
        # Simple case: 2 decisions, 2 choices each
        reference_model = np.array([
            [0.5, 0.5],
            [0.5, 0.5]
        ])
        model = np.array([
            [0.8, 0.2],
            [0.3, 0.7]
        ])
        selections = np.array([
            [1, 0],
            [0, 1]
        ])

        # At epsilon=1, should use model only
        ll = log_likelihood_member(1.0, reference_model, model, selections)
        expected = np.log(0.8) + np.log(0.7)
        assert np.isclose(ll, expected)

        # At epsilon=0, should use reference only
        ll = log_likelihood_member(0.0, reference_model, model, selections)
        expected = np.log(0.5) + np.log(0.5)
        assert np.isclose(ll, expected)

    def test_epsilon_validation(self):
        """Test epsilon bounds validation."""
        ref = np.array([[0.5, 0.5]])
        model = np.array([[0.8, 0.2]])
        sel = np.array([[1, 0]])

        with pytest.raises(ValueError, match="epsilon must be between 0 and 1"):
            log_likelihood_member(-0.1, ref, model, sel)

        with pytest.raises(ValueError, match="epsilon must be between 0 and 1"):
            log_likelihood_member(1.5, ref, model, sel)

    def test_shape_validation(self):
        """Test shape compatibility validation."""
        ref = np.array([[0.5, 0.5]])
        model = np.array([[0.8, 0.2, 0.0]])  # Wrong shape
        sel = np.array([[1, 0]])

        with pytest.raises(ValueError, match="same shape"):
            log_likelihood_member(0.5, ref, model, sel)


class TestProbMembers:
    """Tests for prob_members function."""

    def test_uniform_prior(self):
        """Test with uniform prior."""
        reference_model = np.array([[0.5, 0.5]])
        model = np.array([[0.9, 0.1]])
        selections = np.array([[1, 0]])
        epsilons = np.array([0.0, 0.5, 1.0])

        posteriors = prob_members(
            reference_model, model, selections, epsilons
        )

        assert len(posteriors) == 3
        assert np.isclose(posteriors.sum(), 1.0)
        assert np.all(posteriors >= 0)

        # Model matches data better, so higher epsilon should have higher probability
        assert posteriors[2] > posteriors[0]

    def test_custom_prior(self):
        """Test with custom prior."""
        reference_model = np.array([[0.5, 0.5]])
        model = np.array([[0.9, 0.1]])
        selections = np.array([[1, 0]])
        epsilons = np.array([0.0, 1.0])
        prior = np.array([0.9, 0.1])  # Strong prior for reference model

        posteriors = prob_members(
            reference_model, model, selections, epsilons, prior
        )

        assert np.isclose(posteriors.sum(), 1.0)

    def test_epsilon_ordering(self):
        """Test that epsilons must be sorted."""
        ref = np.array([[0.5, 0.5]])
        model = np.array([[0.9, 0.1]])
        sel = np.array([[1, 0]])
        epsilons = np.array([1.0, 0.0, 0.5])  # Not sorted

        with pytest.raises(ValueError, match="sorted"):
            prob_members(ref, model, sel, epsilons)


class TestBuildModelMatrices:
    """Tests for build_model_matrices function."""

    def test_basic_matrix_building(self):
        """Test basic matrix construction."""
        model_df = pd.DataFrame({
            '_decision': [1, 1, 2, 2],
            '_choice': ['A', 'B', 'A', 'B'],
            'probability': [0.8, 0.2, 0.3, 0.7]
        })

        reference_df = pd.DataFrame({
            '_decision': [1, 1, 2, 2],
            '_choice': ['A', 'B', 'A', 'B'],
            'probability': [0.5, 0.5, 0.5, 0.5]
        })

        selections_df = pd.DataFrame({
            '_decision': [1, 2],
            '_choice': ['A', 'B']
        })

        model_mat, ref_mat, sel_mat = build_model_matrices(
            model_df, reference_df, selections_df
        )

        assert model_mat.shape == (2, 2)
        assert ref_mat.shape == (2, 2)
        assert sel_mat.shape == (2, 2)

        # Check selection matrix
        assert sel_mat[0, 0] == 1  # Decision 1, choice A
        assert sel_mat[0, 1] == 0
        assert sel_mat[1, 0] == 0
        assert sel_mat[1, 1] == 1  # Decision 2, choice B

    def test_missing_columns(self):
        """Test error on missing columns."""
        bad_df = pd.DataFrame({'_decision': [1], 'wrong': ['A']})
        ref_df = pd.DataFrame({
            '_decision': [1],
            '_choice': ['A'],
            'probability': [0.5]
        })
        sel_df = pd.DataFrame({'_decision': [1], '_choice': ['A']})

        with pytest.raises(ValueError, match="must have columns"):
            build_model_matrices(bad_df, ref_df, sel_df)

    def test_mismatched_keys(self):
        """Test error when model and reference have different keys."""
        model_df = pd.DataFrame({
            '_decision': [1],
            '_choice': ['A'],
            'probability': [0.8]
        })

        reference_df = pd.DataFrame({
            '_decision': [2],  # Different decision
            '_choice': ['A'],
            'probability': [0.5]
        })

        selections_df = pd.DataFrame({'_decision': [1], '_choice': ['A']})

        with pytest.raises(ValueError, match="same.*pairs"):
            build_model_matrices(model_df, reference_df, selections_df)


class TestComputeSupport:
    """Tests for compute_support function."""

    def test_integration(self):
        """Test full support computation pipeline."""
        model_df = pd.DataFrame({
            '_decision': [1, 1, 2, 2],
            '_choice': ['A', 'B', 'A', 'B'],
            'probability': [0.9, 0.1, 0.2, 0.8]
        })

        reference_df = pd.DataFrame({
            '_decision': [1, 1, 2, 2],
            '_choice': ['A', 'B', 'A', 'B'],
            'probability': [0.5, 0.5, 0.5, 0.5]
        })

        selections_df = pd.DataFrame({
            '_decision': [1, 2],
            '_choice': ['A', 'B']
        })

        epsilons = np.linspace(0, 1, 11)

        support = compute_support(model_df, reference_df, selections_df, epsilons)

        assert len(support) == len(epsilons)
        assert np.isclose(support.sum(), 1.0)
        assert np.all(support >= 0)


class TestComputeMixtures:
    """Tests for compute_mixtures function."""

    def test_basic_mixture_computation(self):
        """Test basic mixture computation."""
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

        epsilons = np.array([0.0, 0.5, 1.0])

        mixtures = compute_mixtures(model_df, reference_df, epsilons)

        # Should have 2 choices * 3 epsilons = 6 rows
        assert len(mixtures) == 6

        # Check that we have correct columns
        assert '_decision' in mixtures.columns
        assert '_choice' in mixtures.columns
        assert 'epsilon' in mixtures.columns
        assert 'probability' in mixtures.columns

        # Check that probabilities sum to 1 for each (decision, epsilon)
        for eps in epsilons:
            subset = mixtures[mixtures['epsilon'] == eps]
            for decision in subset['_decision'].unique():
                dec_subset = subset[subset['_decision'] == decision]
                assert np.isclose(dec_subset['probability'].sum(), 1.0)

    def test_epsilon_extremes(self):
        """Test mixture computation at epsilon extremes."""
        model_df = pd.DataFrame({
            '_decision': [1, 1],
            '_choice': ['A', 'B'],
            'probability': [0.8, 0.2],
            'context': ['x', 'x']
        })

        reference_df = pd.DataFrame({
            '_decision': [1, 1],
            '_choice': ['A', 'B'],
            'probability': [0.4, 0.6],
            'context': ['x', 'x']
        })

        epsilons = np.array([0.0, 1.0])

        mixtures = compute_mixtures(model_df, reference_df, epsilons)

        # At epsilon=0, should match reference model
        eps0 = mixtures[mixtures['epsilon'] == 0.0]
        assert np.isclose(
            eps0[eps0['_choice'] == 'A']['probability'].values[0],
            0.4
        )

        # At epsilon=1, should match complex model
        eps1 = mixtures[mixtures['epsilon'] == 1.0]
        assert np.isclose(
            eps1[eps1['_choice'] == 'A']['probability'].values[0],
            0.8
        )

        # Check that context columns are preserved
        assert 'context' in mixtures.columns

    def test_context_preservation(self):
        """Test that additional context columns are preserved."""
        model_df = pd.DataFrame({
            '_decision': [1],
            '_choice': ['A'],
            'probability': [1.0],
            'depth': [10.0],
            'time': ['2023-01-01']
        })

        reference_df = pd.DataFrame({
            '_decision': [1],
            '_choice': ['A'],
            'probability': [1.0],
            'depth': [10.0],
            'time': ['2023-01-01']
        })

        epsilons = np.array([0.5])

        mixtures = compute_mixtures(model_df, reference_df, epsilons)

        assert 'depth' in mixtures.columns
        assert 'time' in mixtures.columns
