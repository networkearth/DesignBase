"""
Support computation for Bayesian model interpolation.

This module implements functions for computing the posterior support of model
mixtures given observed data. The approach uses Bayesian model averaging across
a family of interpolated models ranging from a simple reference model to a more
complex model.
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
    Compute the log likelihood of data given a mixture model member.

    This function computes the log likelihood for a specific value of epsilon,
    which controls the interpolation between a reference model (epsilon=0) and
    a more complex model (epsilon=1).

    Args:
        epsilon: Mixing parameter between 0 and 1. When epsilon=0, uses only
            the reference model. When epsilon=1, uses only the non-reference model.
        reference_model_matrix: An N_D x N_C matrix (G_B) with probabilities for
            each choice in each decision for the reference model.
        model_matrix: An N_D x N_C matrix (G_H) with probabilities for each choice
            in each decision for the non-reference model.
        selections_matrix: A binary N_D x N_C matrix (C) indicating which choice
            was selected for each decision (sum of each row = 1).

    Returns:
        The log likelihood of the observed data given the mixture model defined
        by epsilon.

    Raises:
        ValueError: If epsilon is not in [0, 1] or if matrix dimensions don't match.
    """
    if not 0 <= epsilon <= 1:
        raise ValueError(f"epsilon must be in [0, 1], got {epsilon}")

    if reference_model_matrix.shape != model_matrix.shape:
        raise ValueError(
            f"reference_model_matrix shape {reference_model_matrix.shape} "
            f"must match model_matrix shape {model_matrix.shape}"
        )

    if reference_model_matrix.shape != selections_matrix.shape:
        raise ValueError(
            f"Model matrix shape {reference_model_matrix.shape} must match "
            f"selections_matrix shape {selections_matrix.shape}"
        )

    # Compute odds: O = epsilon * G_H + (1 - epsilon) * G_B
    odds = epsilon * model_matrix + (1 - epsilon) * reference_model_matrix

    # Compute probabilities: G_epsilon = odds / row_sum(odds)
    row_sums = odds.sum(axis=1, keepdims=True)

    # Avoid division by zero
    if np.any(row_sums == 0):
        raise ValueError("Row sums in odds matrix contain zeros")

    probabilities = odds / row_sums

    # Get probability of selected choices: element-wise multiply and sum rows
    selected_probs = (probabilities * selections_matrix).sum(axis=1)

    # Avoid log(0)
    if np.any(selected_probs <= 0):
        raise ValueError("Selected probabilities contain non-positive values")

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
    Compute the posterior likelihood of each mixture model member.

    This function computes P(epsilon_i | D) for each epsilon in the epsilons array,
    where D is the observed data. It uses a numerically stable approach based on
    log-likelihoods.

    Args:
        reference_model_matrix: An N_D x N_C matrix (G_B) with probabilities for
            each choice in each decision for the reference model.
        model_matrix: An N_D x N_C matrix (G_H) with probabilities for each choice
            in each decision for the non-reference model.
        selections_matrix: A binary N_D x N_C matrix (C) indicating which choice
            was selected for each decision.
        epsilons: Array of epsilon values ranging from 0 to 1. Each defines a
            member of the model family.
        prior_probs: Optional prior probabilities P(epsilon_i) for each epsilon.
            Defaults to uniform distribution if not provided.

    Returns:
        Array of posterior probabilities P(epsilon_i | D) with the same shape
        as epsilons.

    Raises:
        ValueError: If inputs are invalid or have incompatible shapes.
    """
    if len(epsilons) == 0:
        raise ValueError("epsilons array must not be empty")

    if not np.all((epsilons >= 0) & (epsilons <= 1)):
        raise ValueError("All epsilon values must be in [0, 1]")

    # Default to uniform prior if not provided
    if prior_probs is None:
        prior_probs = np.ones(len(epsilons)) / len(epsilons)

    if len(prior_probs) != len(epsilons):
        raise ValueError(
            f"prior_probs length {len(prior_probs)} must match "
            f"epsilons length {len(epsilons)}"
        )

    if not np.isclose(prior_probs.sum(), 1.0):
        raise ValueError(f"prior_probs must sum to 1, got {prior_probs.sum()}")

    # Compute log likelihoods for each epsilon
    log_likelihoods = np.array([
        log_likelihood_member(eps, reference_model_matrix, model_matrix, selections_matrix)
        for eps in epsilons
    ])

    # Compute L_i = log(P(epsilon_i)) + log_likelihood_i
    log_posteriors = np.log(prior_probs) + log_likelihoods

    # Use the first (minimum epsilon) as the reference for numerical stability
    # r_i = exp(L_i - L_0)
    log_reference = log_posteriors[0]
    log_ratios = log_posteriors - log_reference
    ratios = np.exp(log_ratios)

    # Normalize: P(epsilon_i | D) = r_i / sum(r_j)
    posterior_probs = ratios / ratios.sum()

    return posterior_probs


def build_model_matrices(
    model_df: pd.DataFrame,
    reference_model_df: pd.DataFrame,
    selections_df: pd.DataFrame
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Transform dataframes into matrices for support computation.

    This function converts prediction dataframes into the matrix format required
    by log_likelihood_member and prob_members functions.

    Args:
        model_df: DataFrame with columns ['_decision', '_choice', 'probability']
            for the non-reference model predictions.
        reference_model_df: DataFrame with columns ['_decision', '_choice', 'probability']
            for the reference model predictions.
        selections_df: DataFrame with columns ['_decision', '_choice'] containing
            only the actually selected choices (one per decision).

    Returns:
        Tuple of (model_matrix, reference_model_matrix, selections_matrix) where:
        - model_matrix (G_H): N_D x N_C matrix of model probabilities
        - reference_model_matrix (G_B): N_D x N_C matrix of reference probabilities
        - selections_matrix (C): N_D x N_C binary matrix of selections

    Raises:
        ValueError: If dataframes have incompatible structures.
    """
    # Validate required columns
    required_cols = ['_decision', '_choice', 'probability']
    for df, name in [(model_df, 'model_df'), (reference_model_df, 'reference_model_df')]:
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"{name} must have columns {required_cols}")

    if not all(col in selections_df.columns for col in ['_decision', '_choice']):
        raise ValueError("selections_df must have columns ['_decision', '_choice']")

    # Check that model_df and reference_model_df have the same decision-choice pairs
    model_pairs = set(zip(model_df['_decision'], model_df['_choice']))
    ref_pairs = set(zip(reference_model_df['_decision'], reference_model_df['_choice']))

    if model_pairs != ref_pairs:
        raise ValueError(
            "model_df and reference_model_df must have the same "
            "(_decision, _choice) pairs"
        )

    # Get all unique decisions and choices
    decisions = sorted(model_df['_decision'].unique())
    choices = sorted(model_df['_choice'].unique())

    n_decisions = len(decisions)
    n_choices = len(choices)

    # Create decision and choice index mappings
    decision_to_idx = {d: i for i, d in enumerate(decisions)}
    choice_to_idx = {c: i for i, c in enumerate(choices)}

    # Initialize matrices
    model_matrix = np.zeros((n_decisions, n_choices))
    reference_model_matrix = np.zeros((n_decisions, n_choices))
    selections_matrix = np.zeros((n_decisions, n_choices))

    # Fill model matrix
    for _, row in model_df.iterrows():
        d_idx = decision_to_idx[row['_decision']]
        c_idx = choice_to_idx[row['_choice']]
        model_matrix[d_idx, c_idx] = row['probability']

    # Fill reference model matrix
    for _, row in reference_model_df.iterrows():
        d_idx = decision_to_idx[row['_decision']]
        c_idx = choice_to_idx[row['_choice']]
        reference_model_matrix[d_idx, c_idx] = row['probability']

    # Fill selections matrix
    for _, row in selections_df.iterrows():
        if row['_decision'] not in decision_to_idx:
            raise ValueError(
                f"Decision {row['_decision']} in selections_df not found in model_df"
            )
        if row['_choice'] not in choice_to_idx:
            raise ValueError(
                f"Choice {row['_choice']} in selections_df not found in model_df"
            )

        d_idx = decision_to_idx[row['_decision']]
        c_idx = choice_to_idx[row['_choice']]
        selections_matrix[d_idx, c_idx] = 1

    # Validate selections matrix (each row should sum to 1)
    row_sums = selections_matrix.sum(axis=1)
    if not np.allclose(row_sums, 1.0):
        invalid_decisions = [decisions[i] for i, s in enumerate(row_sums) if not np.isclose(s, 1.0)]
        raise ValueError(
            f"Each decision must have exactly one selection. "
            f"Invalid decisions: {invalid_decisions}"
        )

    return model_matrix, reference_model_matrix, selections_matrix


def compute_support(
    model_df: pd.DataFrame,
    reference_model_df: pd.DataFrame,
    selections_df: pd.DataFrame,
    epsilons: np.ndarray
) -> np.ndarray:
    """
    Compute support for a model mixture from dataframes.

    This is a convenience wrapper that combines build_model_matrices and
    prob_members to compute posterior support directly from dataframes.

    Args:
        model_df: DataFrame with columns ['_decision', '_choice', 'probability']
            for the non-reference model.
        reference_model_df: DataFrame with columns ['_decision', '_choice', 'probability']
            for the reference model.
        selections_df: DataFrame with columns ['_decision', '_choice'] for
            actually selected choices.
        epsilons: Array of epsilon values from 0 to 1 defining the model mixture.

    Returns:
        Array of posterior likelihoods P(epsilon_i | D) for each epsilon.

    Raises:
        ValueError: If inputs are invalid.
    """
    # Build matrices from dataframes
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
    Compute mixture model predictions across all epsilons.

    This function creates a dataframe containing predictions for every model
    in the mixture family, interpolating between the reference and non-reference
    models according to the epsilon values.

    Args:
        model_df: DataFrame with columns ['_decision', '_choice', 'probability']
            and potentially additional context columns.
        reference_model_df: DataFrame with columns ['_decision', '_choice', 'probability']
            with the same structure as model_df.
        epsilons: Array of epsilon values from 0 to 1.

    Returns:
        DataFrame with columns ['_decision', '_choice', 'epsilon', 'probability']
        plus any additional context columns from the input dataframes. Contains
        rows for every combination of (decision, choice, epsilon).

    Raises:
        ValueError: If inputs are invalid or incompatible.
    """
    # Validate inputs
    if not all(col in model_df.columns for col in ['_decision', '_choice', 'probability']):
        raise ValueError("model_df must have columns ['_decision', '_choice', 'probability']")

    if not all(col in reference_model_df.columns for col in ['_decision', '_choice', 'probability']):
        raise ValueError(
            "reference_model_df must have columns ['_decision', '_choice', 'probability']"
        )

    if not np.all((epsilons >= 0) & (epsilons <= 1)):
        raise ValueError("All epsilon values must be in [0, 1]")

    # Rename probability columns to distinguish them
    model_df_temp = model_df.rename(columns={'probability': 'prob_model'})
    reference_df_temp = reference_model_df.rename(columns={'probability': 'prob_reference'})

    # Join the two dataframes on _decision and _choice
    merged = model_df_temp.merge(
        reference_df_temp[['_decision', '_choice', 'prob_reference']],
        on=['_decision', '_choice'],
        how='inner'
    )

    # Get context columns (everything except the key columns and probabilities)
    context_cols = [
        col for col in merged.columns
        if col not in ['_decision', '_choice', 'prob_model', 'prob_reference']
    ]

    # Cross join with epsilons
    epsilon_df = pd.DataFrame({'epsilon': epsilons})
    epsilon_df['_merge_key'] = 1
    merged['_merge_key'] = 1

    mixtures = merged.merge(epsilon_df, on='_merge_key', how='outer')
    mixtures = mixtures.drop('_merge_key', axis=1)

    # Compute odds: O = epsilon * G_H + (1 - epsilon) * G_B
    mixtures['odds'] = (
        mixtures['epsilon'] * mixtures['prob_model'] +
        (1 - mixtures['epsilon']) * mixtures['prob_reference']
    )

    # Compute sum of odds per decision and epsilon
    odds_sums = mixtures.groupby(['_decision', 'epsilon'])['odds'].transform('sum')

    # Compute probability: odds / sum(odds)
    mixtures['probability'] = mixtures['odds'] / odds_sums

    # Select and order final columns
    final_cols = ['_decision', '_choice', 'epsilon', 'probability'] + context_cols
    result = mixtures[final_cols]

    return result
