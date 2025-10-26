"""
Support functions for computing Bayesian model mixtures and likelihood calculations.

This module implements the core mathematics for Bayesian Model Interpolation,
allowing us to compute support across a family of models that interpolate between
a reference model and a target model.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional


def log_likelihood_member(
    epsilon: float,
    reference_model_matrix: np.ndarray,
    model_matrix: np.ndarray,
    selections_matrix: np.ndarray
) -> float:
    """
    Compute the log likelihood of data given a specific mixture model member.

    This function computes the log likelihood for a model that interpolates between
    a reference model and a target model using the mixing parameter epsilon.

    Args:
        epsilon: Mixing parameter between 0 and 1. When epsilon=0, uses only the
            reference model. When epsilon=1, uses only the target model.
        reference_model_matrix: G_B matrix of shape (N_D, N_C) with probabilities
            for each choice in each decision for the reference model.
        model_matrix: G_H matrix of shape (N_D, N_C) with probabilities for each
            choice in each decision for the target model.
        selections_matrix: C matrix of shape (N_D, N_C), binary matrix indicating
            which choice was selected for each decision (row sum = 1).

    Returns:
        Log likelihood of the data given the mixture model defined by epsilon.

    Raises:
        ValueError: If epsilon is not in [0, 1] or if matrix shapes don't match.
    """
    # Validate inputs
    if not 0 <= epsilon <= 1:
        raise ValueError(f"epsilon must be in [0, 1], got {epsilon}")

    if reference_model_matrix.shape != model_matrix.shape:
        raise ValueError(
            f"Model matrices must have same shape. Got reference: {reference_model_matrix.shape}, "
            f"model: {model_matrix.shape}"
        )

    if reference_model_matrix.shape != selections_matrix.shape:
        raise ValueError(
            f"Selections matrix shape {selections_matrix.shape} must match model matrix "
            f"shape {reference_model_matrix.shape}"
        )

    # Compute odds: O = epsilon * G_H + (1 - epsilon) * G_B
    odds = epsilon * model_matrix + (1 - epsilon) * reference_model_matrix

    # Compute probabilities by normalizing odds: G_epsilon = odds / row_sum(odds)
    row_sums = odds.sum(axis=1, keepdims=True)

    # Avoid division by zero
    if np.any(row_sums == 0):
        raise ValueError("Encountered zero row sum in odds matrix")

    probabilities = odds / row_sums

    # Extract probabilities for selected choices: element-wise multiply with selections
    selected_probs = np.sum(probabilities * selections_matrix, axis=1)

    # Handle zero or negative probabilities (shouldn't happen with valid inputs)
    if np.any(selected_probs <= 0):
        raise ValueError("Encountered zero or negative probability for a selected choice")

    # Compute log likelihood
    log_likelihood = np.sum(np.log(selected_probs))

    return log_likelihood


def prob_members(
    reference_model_matrix: np.ndarray,
    model_matrix: np.ndarray,
    selections_matrix: np.ndarray,
    epsilons: np.ndarray,
    prior_probs: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Compute the posterior probability (likelihood) of each model in the mixture family.

    This implements numerically stable Bayesian inference over the family of mixture
    models defined by different epsilon values.

    Args:
        reference_model_matrix: G_B matrix of shape (N_D, N_C) with probabilities
            for each choice in each decision for the reference model.
        model_matrix: G_H matrix of shape (N_D, N_C) with probabilities for each
            choice in each decision for the target model.
        selections_matrix: C matrix of shape (N_D, N_C), binary matrix indicating
            which choice was selected for each decision.
        epsilons: Array of epsilon values (mixing parameters) defining the model family.
            Should be in [0, 1].
        prior_probs: Optional prior probabilities for each epsilon. If None, uses
            uniform prior. Must sum to 1.

    Returns:
        Array of posterior probabilities P(epsilon_i | D) for each epsilon, same
        length as epsilons array.

    Raises:
        ValueError: If inputs are invalid or shapes don't match.
    """
    # Validate epsilons
    epsilons = np.asarray(epsilons)
    if np.any(epsilons < 0) or np.any(epsilons > 1):
        raise ValueError("All epsilon values must be in [0, 1]")

    if len(epsilons) == 0:
        raise ValueError("epsilons array must not be empty")

    # Set up prior probabilities
    if prior_probs is None:
        prior_probs = np.ones(len(epsilons)) / len(epsilons)
    else:
        prior_probs = np.asarray(prior_probs)
        if len(prior_probs) != len(epsilons):
            raise ValueError(
                f"prior_probs length {len(prior_probs)} must match epsilons length {len(epsilons)}"
            )
        if not np.isclose(prior_probs.sum(), 1.0):
            raise ValueError(f"prior_probs must sum to 1, got {prior_probs.sum()}")
        if np.any(prior_probs < 0):
            raise ValueError("prior_probs must be non-negative")

    # Compute log likelihoods for all epsilons
    log_likelihoods = np.zeros(len(epsilons))
    for i, epsilon in enumerate(epsilons):
        log_likelihoods[i] = log_likelihood_member(
            epsilon, reference_model_matrix, model_matrix, selections_matrix
        )

    # Add log priors
    log_posteriors = np.log(prior_probs) + log_likelihoods

    # Use log-sum-exp trick for numerical stability
    # Find the maximum log posterior (use as reference)
    max_log_posterior = np.max(log_posteriors)

    # Compute ratios relative to maximum
    log_ratios = log_posteriors - max_log_posterior
    ratios = np.exp(log_ratios)

    # Normalize to get probabilities
    posterior_probs = ratios / np.sum(ratios)

    return posterior_probs


def build_model_matrices(
    model_df: pd.DataFrame,
    reference_model_df: pd.DataFrame,
    selections_df: pd.DataFrame
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Transform dataframes into matrices needed for likelihood computations.

    Args:
        model_df: DataFrame with columns '_decision', '_choice', 'probability' giving
            the modeled probabilities for each choice across each decision for the
            non-reference model.
        reference_model_df: DataFrame with columns '_decision', '_choice', 'probability'
            giving the modeled probabilities for each choice across each decision for
            the reference model.
        selections_df: DataFrame with columns '_decision', '_choice'. Only those choices
            that were actually selected in the observed data are present (one choice
            per decision).

    Returns:
        Tuple of (model_matrix, reference_model_matrix, selection_matrix):
            - model_matrix: G_H matrix of shape (N_D, N_C)
            - reference_model_matrix: G_B matrix of shape (N_D, N_C)
            - selection_matrix: C matrix of shape (N_D, N_C)

    Raises:
        ValueError: If dataframes don't have required columns or have mismatched decisions/choices.
    """
    # Validate required columns
    required_model_cols = {'_decision', '_choice', 'probability'}
    required_selection_cols = {'_decision', '_choice'}

    if not required_model_cols.issubset(model_df.columns):
        raise ValueError(f"model_df must have columns: {required_model_cols}")
    if not required_model_cols.issubset(reference_model_df.columns):
        raise ValueError(f"reference_model_df must have columns: {required_model_cols}")
    if not required_selection_cols.issubset(selections_df.columns):
        raise ValueError(f"selections_df must have columns: {required_selection_cols}")

    # Check that model and reference model have same decision/choice pairs
    model_pairs = set(zip(model_df['_decision'], model_df['_choice']))
    ref_pairs = set(zip(reference_model_df['_decision'], reference_model_df['_choice']))

    if model_pairs != ref_pairs:
        raise ValueError(
            "model_df and reference_model_df must have the same (_decision, _choice) pairs"
        )

    # Get unique decisions and choices
    all_decisions = sorted(model_df['_decision'].unique())
    all_choices = sorted(model_df['_choice'].unique())

    n_decisions = len(all_decisions)
    n_choices = len(all_choices)

    # Create decision and choice to index mappings
    decision_to_idx = {d: i for i, d in enumerate(all_decisions)}
    choice_to_idx = {c: i for i, c in enumerate(all_choices)}

    # Initialize matrices
    model_matrix = np.zeros((n_decisions, n_choices))
    reference_model_matrix = np.zeros((n_decisions, n_choices))
    selection_matrix = np.zeros((n_decisions, n_choices))

    # Fill model matrix
    for _, row in model_df.iterrows():
        i = decision_to_idx[row['_decision']]
        j = choice_to_idx[row['_choice']]
        model_matrix[i, j] = row['probability']

    # Fill reference model matrix
    for _, row in reference_model_df.iterrows():
        i = decision_to_idx[row['_decision']]
        j = choice_to_idx[row['_choice']]
        reference_model_matrix[i, j] = row['probability']

    # Fill selection matrix
    for _, row in selections_df.iterrows():
        decision = row['_decision']
        choice = row['_choice']

        if decision not in decision_to_idx:
            raise ValueError(f"Decision {decision} in selections_df not found in model_df")
        if choice not in choice_to_idx:
            raise ValueError(f"Choice {choice} in selections_df not found in model_df")

        i = decision_to_idx[decision]
        j = choice_to_idx[choice]
        selection_matrix[i, j] = 1

    # Validate selection matrix (each row should sum to 1)
    row_sums = selection_matrix.sum(axis=1)
    if not np.allclose(row_sums, 1.0):
        invalid_decisions = [all_decisions[i] for i in np.where(row_sums != 1)[0]]
        raise ValueError(
            f"Each decision must have exactly one selection. Invalid decisions: {invalid_decisions}"
        )

    return model_matrix, reference_model_matrix, selection_matrix


def compute_support(
    model_df: pd.DataFrame,
    reference_model_df: pd.DataFrame,
    selections_df: pd.DataFrame,
    epsilons: np.ndarray
) -> np.ndarray:
    """
    Compute support (posterior likelihood) for each model in the mixture family.

    This is a convenience wrapper that transforms dataframes to matrices and computes
    the posterior probabilities for each epsilon value.

    Args:
        model_df: DataFrame with columns '_decision', '_choice', 'probability' for
            the non-reference model.
        reference_model_df: DataFrame with columns '_decision', '_choice', 'probability'
            for the reference model.
        selections_df: DataFrame with columns '_decision', '_choice' containing only
            the actually selected choices (one per decision).
        epsilons: Array of mixing parameters (0 to 1) defining the model family.

    Returns:
        Array of posterior probabilities (support) for each model in the mixture,
        same length as epsilons.

    Raises:
        ValueError: If inputs are invalid.
    """
    # Build matrices
    model_matrix, reference_model_matrix, selection_matrix = build_model_matrices(
        model_df, reference_model_df, selections_df
    )

    # Compute posterior probabilities
    support = prob_members(
        reference_model_matrix, model_matrix, selection_matrix, epsilons
    )

    return support


def compute_mixtures(
    model_df: pd.DataFrame,
    reference_model_df: pd.DataFrame,
    epsilons: np.ndarray
) -> pd.DataFrame:
    """
    Compute mixture probabilities for all models in the family.

    For each epsilon value, this computes the interpolated probabilities between
    the reference model and target model predictions.

    Args:
        model_df: DataFrame with columns '_decision', '_choice', 'probability' (and
            optionally other context columns) for the target model.
        reference_model_df: DataFrame with columns '_decision', '_choice', 'probability'
            (and optionally other context columns) for the reference model.
        epsilons: Array of mixing parameters (0 to 1) defining the model family.

    Returns:
        DataFrame with columns '_decision', '_choice', 'epsilon', 'probability' and
        any other context columns from the input dataframes. Contains a row for every
        combination of (decision, choice, epsilon).

    Raises:
        ValueError: If inputs are invalid or dataframes have mismatched decision/choice pairs.
    """
    # Validate inputs
    required_cols = {'_decision', '_choice', 'probability'}
    if not required_cols.issubset(model_df.columns):
        raise ValueError(f"model_df must have columns: {required_cols}")
    if not required_cols.issubset(reference_model_df.columns):
        raise ValueError(f"reference_model_df must have columns: {required_cols}")

    epsilons = np.asarray(epsilons)
    if np.any(epsilons < 0) or np.any(epsilons > 1):
        raise ValueError("All epsilon values must be in [0, 1]")

    # Merge model and reference model dataframes
    # Keep all context columns from both dataframes
    merge_cols = ['_decision', '_choice']

    # Rename probability columns to distinguish them
    model_df_renamed = model_df.rename(columns={'probability': 'prob_model'})
    reference_df_renamed = reference_model_df.rename(columns={'probability': 'prob_reference'})

    # Merge on decision and choice
    merged = pd.merge(
        model_df_renamed,
        reference_df_renamed,
        on=merge_cols,
        how='inner',
        suffixes=('', '_ref')
    )

    # Check that we have the same number of rows (same decision/choice pairs)
    if len(merged) != len(model_df):
        raise ValueError(
            "model_df and reference_model_df must have the same (_decision, _choice) pairs"
        )

    # Cross join with epsilons
    merged['key'] = 1
    epsilon_df = pd.DataFrame({'epsilon': epsilons, 'key': 1})

    mixtures = pd.merge(merged, epsilon_df, on='key').drop('key', axis=1)

    # Compute odds: O = epsilon * prob_model + (1 - epsilon) * prob_reference
    mixtures['odds'] = (
        mixtures['epsilon'] * mixtures['prob_model'] +
        (1 - mixtures['epsilon']) * mixtures['prob_reference']
    )

    # Compute sum of odds per (decision, epsilon) group
    mixtures['sum_odds'] = mixtures.groupby(['_decision', 'epsilon'])['odds'].transform('sum')

    # Compute probability: odds / sum_odds
    mixtures['probability'] = mixtures['odds'] / mixtures['sum_odds']

    # Clean up temporary columns
    mixtures = mixtures.drop(['prob_model', 'prob_reference', 'odds', 'sum_odds'], axis=1)

    # Remove duplicate reference columns (those with _ref suffix)
    ref_cols = [col for col in mixtures.columns if col.endswith('_ref')]
    mixtures = mixtures.drop(ref_cols, axis=1)

    return mixtures
