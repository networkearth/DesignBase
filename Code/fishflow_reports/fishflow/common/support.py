"""
Support computation for Bayesian model interpolation.

This module implements functions for computing the support (posterior probability)
of model mixtures using Bayesian model interpolation between a complex model and
a simpler reference model.
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple


def log_likelihood_member(
    epsilon: float,
    reference_model_matrix: np.ndarray,
    model_matrix: np.ndarray,
    selections_matrix: np.ndarray
) -> float:
    """
    Compute log likelihood of data given a specific mixture model.

    For a given epsilon, this computes the log likelihood of the observed
    selections given a mixture model that interpolates between a reference
    model and a more complex model.

    Args:
        epsilon: Float between 0 and 1, the mixture parameter where
            epsilon=1 means trust the complex model fully, epsilon=0 means
            trust the reference model fully.
        reference_model_matrix: Array of shape (N_D, N_C) containing
            probabilities for each choice in each decision for the reference model.
        model_matrix: Array of shape (N_D, N_C) containing probabilities
            for each choice in each decision for the complex model.
        selections_matrix: Binary array of shape (N_D, N_C) indicating which
            choice was selected for each decision (one 1 per row, rest 0s).

    Returns:
        Log likelihood of the observed data given the mixture model defined by epsilon.

    Raises:
        ValueError: If inputs have incompatible shapes or invalid values.
    """
    # Validate inputs
    if not 0 <= epsilon <= 1:
        raise ValueError(f"epsilon must be between 0 and 1, got {epsilon}")

    if reference_model_matrix.shape != model_matrix.shape:
        raise ValueError("reference_model_matrix and model_matrix must have same shape")

    if reference_model_matrix.shape != selections_matrix.shape:
        raise ValueError("selections_matrix must have same shape as model matrices")

    # Compute mixture odds: O = epsilon * G_H + (1 - epsilon) * G_B
    odds = epsilon * model_matrix + (1 - epsilon) * reference_model_matrix

    # Normalize to get probabilities: divide each element by its row sum
    row_sums = odds.sum(axis=1, keepdims=True)

    # Avoid division by zero
    if np.any(row_sums == 0):
        raise ValueError("Row sums of odds cannot be zero")

    probabilities = odds / row_sums

    # Extract probabilities for selected choices
    selected_probs = (probabilities * selections_matrix).sum(axis=1)

    # Avoid log(0)
    if np.any(selected_probs <= 0):
        raise ValueError("Selected probabilities must be positive")

    # Compute log likelihood
    log_likelihood = np.log(selected_probs).sum()

    return log_likelihood


def prob_members(
    reference_model_matrix: np.ndarray,
    model_matrix: np.ndarray,
    selections_matrix: np.ndarray,
    epsilons: np.ndarray,
    prior_probs: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Compute posterior probabilities for each model in a mixture family.

    This efficiently computes the posterior probability P(epsilon_i | D) for
    each mixture model defined by epsilon_i, given observed data D.

    Args:
        reference_model_matrix: Array of shape (N_D, N_C) containing
            probabilities for each choice in each decision for the reference model.
        model_matrix: Array of shape (N_D, N_C) containing probabilities
            for each choice in each decision for the complex model.
        selections_matrix: Binary array of shape (N_D, N_C) indicating which
            choice was selected for each decision.
        epsilons: Array of epsilon values (0 to 1, sorted low to high) defining
            the mixture family members.
        prior_probs: Optional array of prior probabilities for each epsilon.
            Defaults to uniform prior if not provided.

    Returns:
        Array of posterior probabilities P(epsilon_i | D) for each epsilon_i.

    Raises:
        ValueError: If inputs are invalid or incompatible.
    """
    # Validate inputs
    if not np.all((epsilons >= 0) & (epsilons <= 1)):
        raise ValueError("All epsilon values must be between 0 and 1")

    if not np.all(epsilons[:-1] <= epsilons[1:]):
        raise ValueError("epsilons must be sorted in ascending order")

    n_epsilons = len(epsilons)

    # Set default uniform prior if not provided
    if prior_probs is None:
        prior_probs = np.ones(n_epsilons) / n_epsilons

    if len(prior_probs) != n_epsilons:
        raise ValueError("prior_probs must have same length as epsilons")

    if not np.isclose(prior_probs.sum(), 1.0):
        raise ValueError("prior_probs must sum to 1")

    # Compute log likelihoods for each epsilon
    log_likelihoods = np.zeros(n_epsilons)
    for i, epsilon in enumerate(epsilons):
        log_likelihoods[i] = log_likelihood_member(
            epsilon, reference_model_matrix, model_matrix, selections_matrix
        )

    # Add log priors
    log_priors = np.log(prior_probs)
    log_posteriors_unnormalized = log_priors + log_likelihoods

    # Use log-sum-exp trick for numerical stability
    # Subtract maximum to prevent overflow
    max_log_posterior = log_posteriors_unnormalized.max()

    # Compute ratios relative to maximum
    ratios = np.exp(log_posteriors_unnormalized - max_log_posterior)

    # Normalize to get posterior probabilities
    posteriors = ratios / ratios.sum()

    return posteriors


def build_model_matrices(
    model_df: pd.DataFrame,
    reference_model_df: pd.DataFrame,
    selections_df: pd.DataFrame
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Build matrices for model comparison from dataframes.

    Converts dataframes with decision-choice-probability structure into
    matrix format suitable for efficient likelihood computation.

    Args:
        model_df: DataFrame with columns '_decision', '_choice', 'probability'
            for the complex model.
        reference_model_df: DataFrame with columns '_decision', '_choice',
            'probability' for the reference model.
        selections_df: DataFrame with columns '_decision', '_choice' containing
            only the actually selected choices (one per decision).

    Returns:
        Tuple of (model_matrix, reference_model_matrix, selections_matrix)
        where each matrix has shape (N_D, N_C).

    Raises:
        ValueError: If inputs are invalid or incompatible.
    """
    # Validate required columns
    required_cols_model = {'_decision', '_choice', 'probability'}
    required_cols_selection = {'_decision', '_choice'}

    if not required_cols_model.issubset(model_df.columns):
        raise ValueError(f"model_df must have columns {required_cols_model}")

    if not required_cols_model.issubset(reference_model_df.columns):
        raise ValueError(f"reference_model_df must have columns {required_cols_model}")

    if not required_cols_selection.issubset(selections_df.columns):
        raise ValueError(f"selections_df must have columns {required_cols_selection}")

    # Check that model_df and reference_model_df have same decision-choice pairs
    model_keys = set(zip(model_df['_decision'], model_df['_choice']))
    ref_keys = set(zip(reference_model_df['_decision'], reference_model_df['_choice']))

    if model_keys != ref_keys:
        raise ValueError("model_df and reference_model_df must have same (_decision, _choice) pairs")

    # Get unique decisions and choices
    decisions = sorted(model_df['_decision'].unique())
    all_choices = sorted(model_df['_choice'].unique())

    # Create index mappings
    decision_to_idx = {d: i for i, d in enumerate(decisions)}
    choice_to_idx = {c: i for i, c in enumerate(all_choices)}

    n_decisions = len(decisions)
    n_choices = len(all_choices)

    # Initialize matrices
    model_matrix = np.zeros((n_decisions, n_choices))
    reference_model_matrix = np.zeros((n_decisions, n_choices))
    selections_matrix = np.zeros((n_decisions, n_choices))

    # Fill model matrices
    for _, row in model_df.iterrows():
        i = decision_to_idx[row['_decision']]
        j = choice_to_idx[row['_choice']]
        model_matrix[i, j] = row['probability']

    for _, row in reference_model_df.iterrows():
        i = decision_to_idx[row['_decision']]
        j = choice_to_idx[row['_choice']]
        reference_model_matrix[i, j] = row['probability']

    # Fill selections matrix
    for _, row in selections_df.iterrows():
        if row['_decision'] not in decision_to_idx:
            raise ValueError(f"Decision {row['_decision']} in selections not found in model data")
        if row['_choice'] not in choice_to_idx:
            raise ValueError(f"Choice {row['_choice']} in selections not found in model data")

        i = decision_to_idx[row['_decision']]
        j = choice_to_idx[row['_choice']]
        selections_matrix[i, j] = 1

    # Validate selections matrix (exactly one selection per decision)
    row_sums = selections_matrix.sum(axis=1)
    if not np.all(row_sums == 1):
        raise ValueError("Each decision must have exactly one selected choice")

    return model_matrix, reference_model_matrix, selections_matrix


def compute_support(
    model_df: pd.DataFrame,
    reference_model_df: pd.DataFrame,
    selections_df: pd.DataFrame,
    epsilons: np.ndarray
) -> np.ndarray:
    """
    Compute support (posterior probability) for model mixture family.

    This is a convenience wrapper that combines build_model_matrices and
    prob_members to compute support directly from dataframes.

    Args:
        model_df: DataFrame with columns '_decision', '_choice', 'probability'
            for the complex model.
        reference_model_df: DataFrame with columns '_decision', '_choice',
            'probability' for the reference model.
        selections_df: DataFrame with columns '_decision', '_choice' containing
            only the actually selected choices (one per decision).
        epsilons: Array of epsilon values (0 to 1) defining the mixture family.

    Returns:
        Array of posterior probabilities (support) for each epsilon value.

    Raises:
        ValueError: If inputs are invalid or incompatible.
    """
    # Build matrices
    model_matrix, reference_model_matrix, selections_matrix = build_model_matrices(
        model_df, reference_model_df, selections_df
    )

    # Compute posterior probabilities
    support = prob_members(
        reference_model_matrix,
        model_matrix,
        selections_matrix,
        epsilons
    )

    return support


def compute_mixtures(
    model_df: pd.DataFrame,
    reference_model_df: pd.DataFrame,
    epsilons: np.ndarray
) -> pd.DataFrame:
    """
    Compute mixture probabilities across all decisions and choices.

    Creates a dataframe with mixture probabilities for every combination of
    decision, choice, and epsilon value in the mixture family.

    Args:
        model_df: DataFrame with columns '_decision', '_choice', 'probability'
            for the complex model. May contain additional context columns.
        reference_model_df: DataFrame with columns '_decision', '_choice',
            'probability' for the reference model. May contain additional context columns.
        epsilons: Array of epsilon values (0 to 1) defining the mixture family.

    Returns:
        DataFrame with columns '_decision', '_choice', 'epsilon', 'probability'
        plus any additional columns from the input dataframes. Contains one row
        for each combination of decision, choice, and epsilon.

    Raises:
        ValueError: If inputs are invalid or incompatible.
    """
    # Validate inputs
    required_cols = {'_decision', '_choice', 'probability'}
    if not required_cols.issubset(model_df.columns):
        raise ValueError(f"model_df must have columns {required_cols}")
    if not required_cols.issubset(reference_model_df.columns):
        raise ValueError(f"reference_model_df must have columns {required_cols}")

    # Merge the two models
    merged = model_df.merge(
        reference_model_df[['_decision', '_choice', 'probability']],
        on=['_decision', '_choice'],
        suffixes=('_model', '_reference')
    )

    # Rename probability columns for clarity
    merged = merged.rename(columns={
        'probability_model': 'prob_model',
        'probability_reference': 'prob_reference'
    })

    # If there was already a 'probability' column without suffix, handle it
    if 'probability' in merged.columns:
        merged = merged.drop('probability', axis=1)

    # Cross join with epsilons
    epsilon_df = pd.DataFrame({'epsilon': epsilons})
    epsilon_df['_key'] = 1
    merged['_key'] = 1

    mixtures = merged.merge(epsilon_df, on='_key').drop('_key', axis=1)

    # Compute mixture odds: epsilon * prob_model + (1 - epsilon) * prob_reference
    mixtures['odds'] = (
        mixtures['epsilon'] * mixtures['prob_model'] +
        (1 - mixtures['epsilon']) * mixtures['prob_reference']
    )

    # Compute sum of odds per (decision, epsilon) group
    odds_sums = mixtures.groupby(['_decision', 'epsilon'])['odds'].transform('sum')

    # Compute mixture probability
    mixtures['probability'] = mixtures['odds'] / odds_sums

    # Clean up temporary columns
    mixtures = mixtures.drop(['prob_model', 'prob_reference', 'odds'], axis=1)

    # Reorder columns: keys first, then epsilon, probability, then any other context
    key_cols = ['_decision', '_choice', 'epsilon', 'probability']
    other_cols = [c for c in mixtures.columns if c not in key_cols]
    mixtures = mixtures[key_cols + other_cols]

    return mixtures
