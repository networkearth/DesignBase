"""
Unit tests for fishflow.common.support module.
"""

import pytest
import numpy as np
import pandas as pd
from fishflow.common.support import (
    log_likelihood_member,
    prob_members,
    build_model_matrices,
    compute_support,
    compute_mixtures,
)


class TestLogLikelihoodMember:
    """Tests for log_likelihood_member function."""

    def test_basic_computation(self):
        """Test basic log likelihood computation."""
        # Simple case: 2 decisions, 2 choices each
        reference_model = np.array([[0.5, 0.5], [0.6, 0.4]])
        model = np.array([[0.7, 0.3], [0.8, 0.2]])
        selections = np.array([[1, 0], [0, 1]])
        epsilon = 0.5

        result = log_likelihood_member(
            epsilon, reference_model, model, selections
        )

        # Should return a finite negative number
        assert isinstance(result, float)
        assert np.isfinite(result)
        assert result <= 0  # Log likelihood should be <= 0

    def test_epsilon_extremes(self):
        """Test that epsilon=0 uses reference model, epsilon=1 uses hypothesis model."""
        reference_model = np.array([[0.9, 0.1], [0.1, 0.9]])
        model = np.array([[0.1, 0.9], [0.9, 0.1]])
        selections = np.array([[1, 0], [0, 1]])

        # At epsilon=0, should use reference model
        ll_ref = log_likelihood_member(0.0, reference_model, model, selections)

        # At epsilon=1, should use hypothesis model
        ll_hyp = log_likelihood_member(1.0, reference_model, model, selections)

        # These should be different since the models are different
        assert ll_ref != ll_hyp

    def test_invalid_epsilon(self):
        """Test that invalid epsilon values raise errors."""
        reference_model = np.array([[0.5, 0.5]])
        model = np.array([[0.7, 0.3]])
        selections = np.array([[1, 0]])

        with pytest.raises(ValueError, match="epsilon must be between 0 and 1"):
            log_likelihood_member(-0.1, reference_model, model, selections)

        with pytest.raises(ValueError, match="epsilon must be between 0 and 1"):
            log_likelihood_member(1.5, reference_model, model, selections)

    def test_shape_mismatch(self):
        """Test that mismatched shapes raise errors."""
        reference_model = np.array([[0.5, 0.5]])
        model = np.array([[0.7, 0.3], [0.6, 0.4]])
        selections = np.array([[1, 0]])

        with pytest.raises(ValueError, match="doesn't match"):
            log_likelihood_member(0.5, reference_model, model, selections)


class TestProbMembers:
    """Tests for prob_members function."""

    def test_basic_computation(self):
        """Test basic posterior probability computation."""
        reference_model = np.array([[0.5, 0.5], [0.6, 0.4]])
        model = np.array([[0.7, 0.3], [0.8, 0.2]])
        selections = np.array([[1, 0], [0, 1]])
        epsilons = np.array([0.0, 0.5, 1.0])

        result = prob_members(
            reference_model, model, selections, epsilons
        )

        # Should return probabilities
        assert len(result) == len(epsilons)
        assert np.all(result >= 0)
        assert np.all(result <= 1)
        assert np.isclose(result.sum(), 1.0)

    def test_uniform_prior(self):
        """Test that default prior is uniform."""
        reference_model = np.array([[0.5, 0.5]])
        model = np.array([[0.5, 0.5]])
        selections = np.array([[1, 0]])
        epsilons = np.array([0.0, 0.5, 1.0])

        # With identical models, posterior should equal prior
        result = prob_members(
            reference_model, model, selections, epsilons
        )

        # Should be approximately uniform
        assert np.allclose(result, 1.0 / len(epsilons), atol=0.1)

    def test_custom_prior(self):
        """Test custom prior probabilities."""
        reference_model = np.array([[0.5, 0.5]])
        model = np.array([[0.5, 0.5]])
        selections = np.array([[1, 0]])
        epsilons = np.array([0.0, 1.0])
        prior = np.array([0.9, 0.1])

        result = prob_members(
            reference_model, model, selections, epsilons, prior_probs=prior
        )

        # With identical models, posterior should be close to prior
        assert result[0] > result[1]

    def test_unsorted_epsilons(self):
        """Test that unsorted epsilons raise error."""
        reference_model = np.array([[0.5, 0.5]])
        model = np.array([[0.7, 0.3]])
        selections = np.array([[1, 0]])
        epsilons = np.array([1.0, 0.0, 0.5])

        with pytest.raises(ValueError, match="sorted"):
            prob_members(reference_model, model, selections, epsilons)


class TestBuildModelMatrices:
    """Tests for build_model_matrices function."""

    def test_basic_conversion(self):
        """Test basic dataframe to matrix conversion."""
        model_df = pd.DataFrame(
            {
                "_decision": [1, 1, 2, 2],
                "_choice": ["A", "B", "A", "B"],
                "probability": [0.7, 0.3, 0.6, 0.4],
            }
        )

        reference_model_df = pd.DataFrame(
            {
                "_decision": [1, 1, 2, 2],
                "_choice": ["A", "B", "A", "B"],
                "probability": [0.5, 0.5, 0.5, 0.5],
            }
        )

        selections_df = pd.DataFrame(
            {"_decision": [1, 2], "_choice": ["A", "B"]}
        )

        model_matrix, ref_matrix, sel_matrix = build_model_matrices(
            model_df, reference_model_df, selections_df
        )

        # Check shapes
        assert model_matrix.shape == (2, 2)
        assert ref_matrix.shape == (2, 2)
        assert sel_matrix.shape == (2, 2)

        # Check that selections are binary
        assert np.all((sel_matrix == 0) | (sel_matrix == 1))
        assert np.all(sel_matrix.sum(axis=1) == 1)

    def test_mismatched_models(self):
        """Test that mismatched models raise error."""
        model_df = pd.DataFrame(
            {
                "_decision": [1, 1],
                "_choice": ["A", "B"],
                "probability": [0.7, 0.3],
            }
        )

        reference_model_df = pd.DataFrame(
            {
                "_decision": [1, 1],
                "_choice": ["A", "C"],
                "probability": [0.5, 0.5],
            }
        )

        selections_df = pd.DataFrame(
            {"_decision": [1], "_choice": ["A"]}
        )

        with pytest.raises(ValueError, match="identical"):
            build_model_matrices(model_df, reference_model_df, selections_df)


class TestComputeSupport:
    """Tests for compute_support function."""

    def test_end_to_end(self):
        """Test complete support computation."""
        model_df = pd.DataFrame(
            {
                "_decision": [1, 1, 2, 2],
                "_choice": ["A", "B", "A", "B"],
                "probability": [0.8, 0.2, 0.7, 0.3],
            }
        )

        reference_model_df = pd.DataFrame(
            {
                "_decision": [1, 1, 2, 2],
                "_choice": ["A", "B", "A", "B"],
                "probability": [0.5, 0.5, 0.5, 0.5],
            }
        )

        selections_df = pd.DataFrame(
            {"_decision": [1, 2], "_choice": ["A", "A"]}
        )

        epsilons = np.linspace(0, 1, 11)

        support = compute_support(
            model_df, reference_model_df, selections_df, epsilons
        )

        # Check properties
        assert len(support) == len(epsilons)
        assert np.all(support >= 0)
        assert np.all(support <= 1)
        assert np.isclose(support.sum(), 1.0)


class TestComputeMixtures:
    """Tests for compute_mixtures function."""

    def test_basic_mixture(self):
        """Test basic mixture computation."""
        model_df = pd.DataFrame(
            {
                "_decision": [1, 1],
                "_choice": ["A", "B"],
                "probability": [0.8, 0.2],
            }
        )

        reference_model_df = pd.DataFrame(
            {
                "_decision": [1, 1],
                "_choice": ["A", "B"],
                "probability": [0.5, 0.5],
            }
        )

        epsilons = np.array([0.0, 0.5, 1.0])

        mixtures = compute_mixtures(model_df, reference_model_df, epsilons)

        # Check structure
        assert "_decision" in mixtures.columns
        assert "_choice" in mixtures.columns
        assert "epsilon" in mixtures.columns
        assert "probability" in mixtures.columns

        # Should have 3 epsilon values × 2 choices = 6 rows
        assert len(mixtures) == 6

        # Check that probabilities sum to 1 per decision and epsilon
        grouped = mixtures.groupby(["_decision", "epsilon"])["probability"].sum()
        assert np.allclose(grouped.values, 1.0)

    def test_epsilon_extremes(self):
        """Test that epsilon=0 gives reference, epsilon=1 gives hypothesis."""
        model_df = pd.DataFrame(
            {
                "_decision": [1, 1],
                "_choice": ["A", "B"],
                "probability": [0.9, 0.1],
            }
        )

        reference_model_df = pd.DataFrame(
            {
                "_decision": [1, 1],
                "_choice": ["A", "B"],
                "probability": [0.3, 0.7],
            }
        )

        epsilons = np.array([0.0, 1.0])

        mixtures = compute_mixtures(model_df, reference_model_df, epsilons)

        # At epsilon=0, should match reference
        eps0 = mixtures[mixtures["epsilon"] == 0.0]
        eps0_A = eps0[eps0["_choice"] == "A"]["probability"].values[0]
        assert np.isclose(eps0_A, 0.3, atol=0.01)

        # At epsilon=1, should match hypothesis
        eps1 = mixtures[mixtures["epsilon"] == 1.0]
        eps1_A = eps1[eps1["_choice"] == "A"]["probability"].values[0]
        assert np.isclose(eps1_A, 0.9, atol=0.01)

    def test_context_preservation(self):
        """Test that additional context columns are preserved."""
        model_df = pd.DataFrame(
            {
                "_decision": [1, 1],
                "_choice": ["A", "B"],
                "probability": [0.8, 0.2],
                "depth_bin": [10.0, 20.0],
            }
        )

        reference_model_df = pd.DataFrame(
            {
                "_decision": [1, 1],
                "_choice": ["A", "B"],
                "probability": [0.5, 0.5],
                "depth_bin": [10.0, 20.0],
            }
        )

        epsilons = np.array([0.5])

        mixtures = compute_mixtures(model_df, reference_model_df, epsilons)

        # Context column should be preserved
        assert "depth_bin" in mixtures.columns
