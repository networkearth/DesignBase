"""
Unit tests for support module.
"""

import unittest
import numpy as np
import pandas as pd
from fishflow.common.support import (
    log_likelihood_member,
    prob_members,
    build_model_matrices,
    compute_support,
    compute_mixtures
)


class TestLogLikelihoodMember(unittest.TestCase):
    """Test log_likelihood_member function."""

    def setUp(self):
        """Set up test fixtures."""
        # Simple 2x2 matrices for testing
        self.reference_matrix = np.array([
            [0.7, 0.3],
            [0.6, 0.4]
        ])
        self.model_matrix = np.array([
            [0.4, 0.6],
            [0.3, 0.7]
        ])
        self.selections_matrix = np.array([
            [1, 0],
            [0, 1]
        ])

    def test_epsilon_zero(self):
        """Test that epsilon=0 uses only reference model."""
        ll = log_likelihood_member(
            0.0, self.reference_matrix, self.model_matrix, self.selections_matrix
        )
        # Should get log(0.7) + log(0.4)
        expected = np.log(0.7) + np.log(0.4)
        self.assertAlmostEqual(ll, expected)

    def test_epsilon_one(self):
        """Test that epsilon=1 uses only non-reference model."""
        ll = log_likelihood_member(
            1.0, self.reference_matrix, self.model_matrix, self.selections_matrix
        )
        # Should get log(0.4) + log(0.7)
        expected = np.log(0.4) + np.log(0.7)
        self.assertAlmostEqual(ll, expected)

    def test_invalid_epsilon(self):
        """Test that invalid epsilon raises ValueError."""
        with self.assertRaises(ValueError):
            log_likelihood_member(
                1.5, self.reference_matrix, self.model_matrix, self.selections_matrix
            )

        with self.assertRaises(ValueError):
            log_likelihood_member(
                -0.1, self.reference_matrix, self.model_matrix, self.selections_matrix
            )

    def test_mismatched_shapes(self):
        """Test that mismatched matrix shapes raise ValueError."""
        bad_matrix = np.array([[0.5, 0.5, 0.0]])

        with self.assertRaises(ValueError):
            log_likelihood_member(
                0.5, self.reference_matrix, bad_matrix, self.selections_matrix
            )


class TestProbMembers(unittest.TestCase):
    """Test prob_members function."""

    def setUp(self):
        """Set up test fixtures."""
        self.reference_matrix = np.array([
            [0.7, 0.3],
            [0.6, 0.4]
        ])
        self.model_matrix = np.array([
            [0.4, 0.6],
            [0.3, 0.7]
        ])
        self.selections_matrix = np.array([
            [1, 0],
            [0, 1]
        ])
        self.epsilons = np.array([0.0, 0.5, 1.0])

    def test_uniform_prior(self):
        """Test that result sums to 1 with uniform prior."""
        probs = prob_members(
            self.reference_matrix,
            self.model_matrix,
            self.selections_matrix,
            self.epsilons
        )
        self.assertAlmostEqual(probs.sum(), 1.0)
        self.assertEqual(len(probs), len(self.epsilons))

    def test_custom_prior(self):
        """Test with custom prior probabilities."""
        prior = np.array([0.5, 0.3, 0.2])
        probs = prob_members(
            self.reference_matrix,
            self.model_matrix,
            self.selections_matrix,
            self.epsilons,
            prior_probs=prior
        )
        self.assertAlmostEqual(probs.sum(), 1.0)

    def test_invalid_prior(self):
        """Test that invalid prior raises ValueError."""
        # Prior doesn't sum to 1
        bad_prior = np.array([0.3, 0.3, 0.3])
        with self.assertRaises(ValueError):
            prob_members(
                self.reference_matrix,
                self.model_matrix,
                self.selections_matrix,
                self.epsilons,
                prior_probs=bad_prior
            )

    def test_empty_epsilons(self):
        """Test that empty epsilons raises ValueError."""
        with self.assertRaises(ValueError):
            prob_members(
                self.reference_matrix,
                self.model_matrix,
                self.selections_matrix,
                np.array([])
            )


class TestBuildModelMatrices(unittest.TestCase):
    """Test build_model_matrices function."""

    def setUp(self):
        """Set up test fixtures."""
        self.model_df = pd.DataFrame({
            '_decision': [1, 1, 2, 2],
            '_choice': ['A', 'B', 'A', 'B'],
            'probability': [0.4, 0.6, 0.3, 0.7]
        })
        self.reference_df = pd.DataFrame({
            '_decision': [1, 1, 2, 2],
            '_choice': ['A', 'B', 'A', 'B'],
            'probability': [0.7, 0.3, 0.6, 0.4]
        })
        self.selections_df = pd.DataFrame({
            '_decision': [1, 2],
            '_choice': ['A', 'B']
        })

    def test_basic_functionality(self):
        """Test basic matrix construction."""
        model_mat, ref_mat, sel_mat = build_model_matrices(
            self.model_df, self.reference_df, self.selections_df
        )

        # Check shapes
        self.assertEqual(model_mat.shape, (2, 2))
        self.assertEqual(ref_mat.shape, (2, 2))
        self.assertEqual(sel_mat.shape, (2, 2))

        # Check selections matrix
        self.assertTrue(np.allclose(sel_mat.sum(axis=1), 1.0))

    def test_missing_columns(self):
        """Test that missing columns raise ValueError."""
        bad_df = pd.DataFrame({
            '_decision': [1, 1],
            '_choice': ['A', 'B']
        })
        with self.assertRaises(ValueError):
            build_model_matrices(bad_df, self.reference_df, self.selections_df)

    def test_mismatched_pairs(self):
        """Test that mismatched decision-choice pairs raise ValueError."""
        bad_ref = pd.DataFrame({
            '_decision': [1, 1, 3, 3],
            '_choice': ['A', 'B', 'A', 'B'],
            'probability': [0.7, 0.3, 0.6, 0.4]
        })
        with self.assertRaises(ValueError):
            build_model_matrices(self.model_df, bad_ref, self.selections_df)


class TestComputeSupport(unittest.TestCase):
    """Test compute_support function."""

    def setUp(self):
        """Set up test fixtures."""
        self.model_df = pd.DataFrame({
            '_decision': [1, 1, 2, 2],
            '_choice': ['A', 'B', 'A', 'B'],
            'probability': [0.4, 0.6, 0.3, 0.7]
        })
        self.reference_df = pd.DataFrame({
            '_decision': [1, 1, 2, 2],
            '_choice': ['A', 'B', 'A', 'B'],
            'probability': [0.7, 0.3, 0.6, 0.4]
        })
        self.selections_df = pd.DataFrame({
            '_decision': [1, 2],
            '_choice': ['A', 'B']
        })
        self.epsilons = np.array([0.0, 0.5, 1.0])

    def test_basic_functionality(self):
        """Test basic support computation."""
        support = compute_support(
            self.model_df,
            self.reference_df,
            self.selections_df,
            self.epsilons
        )

        # Should return array of same length as epsilons
        self.assertEqual(len(support), len(self.epsilons))

        # Should sum to 1
        self.assertAlmostEqual(support.sum(), 1.0)

        # All values should be non-negative
        self.assertTrue(np.all(support >= 0))


class TestComputeMixtures(unittest.TestCase):
    """Test compute_mixtures function."""

    def setUp(self):
        """Set up test fixtures."""
        self.model_df = pd.DataFrame({
            '_decision': [1, 1, 2, 2],
            '_choice': ['A', 'B', 'A', 'B'],
            'probability': [0.4, 0.6, 0.3, 0.7],
            'depth_bin': [1, 2, 1, 2]
        })
        self.reference_df = pd.DataFrame({
            '_decision': [1, 1, 2, 2],
            '_choice': ['A', 'B', 'A', 'B'],
            'probability': [0.7, 0.3, 0.6, 0.4],
            'depth_bin': [1, 2, 1, 2]
        })
        self.epsilons = np.array([0.0, 1.0])

    def test_basic_functionality(self):
        """Test basic mixture computation."""
        mixtures = compute_mixtures(
            self.model_df,
            self.reference_df,
            self.epsilons
        )

        # Should have rows for each (decision, choice, epsilon) combination
        expected_rows = len(self.model_df) * len(self.epsilons)
        self.assertEqual(len(mixtures), expected_rows)

        # Should have required columns
        required_cols = ['_decision', '_choice', 'epsilon', 'probability']
        for col in required_cols:
            self.assertIn(col, mixtures.columns)

        # Should preserve context columns
        self.assertIn('depth_bin', mixtures.columns)

    def test_probability_normalization(self):
        """Test that probabilities sum to 1 per decision and epsilon."""
        mixtures = compute_mixtures(
            self.model_df,
            self.reference_df,
            self.epsilons
        )

        # Group by decision and epsilon, check probabilities sum to 1
        for (decision, epsilon), group in mixtures.groupby(['_decision', 'epsilon']):
            prob_sum = group['probability'].sum()
            self.assertAlmostEqual(prob_sum, 1.0, places=10)

    def test_epsilon_zero(self):
        """Test that epsilon=0 returns reference model probabilities."""
        mixtures = compute_mixtures(
            self.model_df,
            self.reference_df,
            np.array([0.0])
        )

        # Check that probabilities match reference model
        for _, row in mixtures.iterrows():
            ref_prob = self.reference_df[
                (self.reference_df['_decision'] == row['_decision']) &
                (self.reference_df['_choice'] == row['_choice'])
            ]['probability'].iloc[0]
            self.assertAlmostEqual(row['probability'], ref_prob)

    def test_epsilon_one(self):
        """Test that epsilon=1 returns non-reference model probabilities."""
        mixtures = compute_mixtures(
            self.model_df,
            self.reference_df,
            np.array([1.0])
        )

        # Check that probabilities match model
        for _, row in mixtures.iterrows():
            model_prob = self.model_df[
                (self.model_df['_decision'] == row['_decision']) &
                (self.model_df['_choice'] == row['_choice'])
            ]['probability'].iloc[0]
            self.assertAlmostEqual(row['probability'], model_prob)


if __name__ == '__main__':
    unittest.main()
