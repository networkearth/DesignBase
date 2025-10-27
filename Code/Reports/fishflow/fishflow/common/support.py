"""
Support functions for Bayesian model interpolation.

This module implements functions for computing support for model mixtures
using Bayesian model interpolation techniques.
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple


def log_likelihood_member(
    epsilon: float,
    reference_model_matrix: np.ndarray,
    model_matrix: np.ndarray,
    selections_matrix: np.ndarray,
) -> float:
    """
    Compute log likelihood of data given a distribution family member.

    This function computes the log likelihood of observed data D given a specific
    member of the distribution family defined by blending a reference model and
    a hypothesis model with parameter epsilon.

    Args:
        epsilon: Mixing parameter between 0 and 1. When epsilon=0, uses only
            reference model. When epsilon=1, uses only the hypothesis model.
        reference_model_matrix: Array of shape (N_D, N_C) with probabilities
            for each choice in each decision for the reference model (G_B).
        model_matrix: Array of shape (N_D, N_C) with probabilities for each
            choice in each decision for the hypothesis model (G_H).
        selections_matrix: Binary array of shape (N_D, N_C) indicating which
            choice was selected for each decision. Each row sums to exactly 1.

    Returns:
        Log likelihood of the data given the distribution family member
        defined by epsilon, G_B, and G_H.

    Raises:
        ValueError: If epsilon is not between 0 and 1, or if input shapes don't match.
        ValueError: If selections_matrix rows don't sum to 1 (within tolerance).
    """
    # Input validation
    if not 0 <= epsilon <= 1:
        raise ValueError(f"epsilon must be between 0 and 1, got {epsilon}")

    if reference_model_matrix.shape != model_matrix.shape:
        raise ValueError(
            f"Reference model shape {reference_model_matrix.shape} doesn't match "
            f"model shape {model_matrix.shape}"
        )

    if reference_model_matrix.shape != selections_matrix.shape:
        raise ValueError(
            f"Model shape {reference_model_matrix.shape} doesn't match "
            f"selections shape {selections_matrix.shape}"
        )

    # Check that selections are valid (each row sums to 1)
    row_sums = selections_matrix.sum(axis=1)
    if not np.allclose(row_sums, 1.0, atol=1e-6):
        raise ValueError(
            "Each row of selections_matrix must sum to exactly 1 "
            f"(found sums ranging from {row_sums.min()} to {row_sums.max()})"
        )

    # Compute odds: O = epsilon * G_H + (1 - epsilon) * G_B
    odds = epsilon * model_matrix + (1 - epsilon) * reference_model_matrix

    # Normalize odds to probabilities: G_epsilon = odds / row_sum(odds)
    row_sums = odds.sum(axis=1, keepdims=True)
    # Add small epsilon to avoid division by zero
    probabilities = odds / (row_sums + 1e-10)

    # Extract probabilities for selected choices: G_epsilon * C (element-wise)
    selected_probs = probabilities * selections_matrix

    # Get probability per decision (sum over choices, since only one is selected)
    decision_probs = selected_probs.sum(axis=1)

    # Add small epsilon to avoid log(0)
    decision_probs = np.maximum(decision_probs, 1e-10)

    # Compute log likelihood: sum of log probabilities
    log_likelihood = np.sum(np.log(decision_probs))

    return log_likelihood


def prob_members(
    reference_model_matrix: np.ndarray,
    model_matrix: np.ndarray,
    selections_matrix: np.ndarray,
    epsilons: np.ndarray,
    prior_probs: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Compute posterior probabilities for each model in a family of mixture models.

    This function efficiently computes P(epsilon_i | D) for each epsilon_i,
    representing the likelihood of each model in the family given observed data.

    Args:
        reference_model_matrix: Array of shape (N_D, N_C) with probabilities
            for each choice in each decision for the reference model (G_B).
        model_matrix: Array of shape (N_D, N_C) with probabilities for each
            choice in each decision for the hypothesis model (G_H).
        selections_matrix: Binary array of shape (N_D, N_C) indicating which
            choice was selected for each decision.
        epsilons: Ordered array (low to high) of floats between 0 and 1 inclusive,
            defining the family of models.
        prior_probs: Optional array of prior probabilities for each epsilon.
            Defaults to uniform prior if not provided.

    Returns:
        Array of posterior probabilities P(epsilon_i | D) for each epsilon_i.

    Raises:
        ValueError: If epsilons are not sorted or not in [0, 1].
        ValueError: If prior_probs length doesn't match epsilons.
    """
    # Input validation
    if not np.all((epsilons >= 0) & (epsilons <= 1)):
        raise ValueError("All epsilon values must be between 0 and 1")

    if not np.all(epsilons[:-1] <= epsilons[1:]):
        raise ValueError("Epsilons must be sorted in ascending order")

    if prior_probs is None:
        prior_probs = np.ones(len(epsilons)) / len(epsilons)
    elif len(prior_probs) != len(epsilons):
        raise ValueError(
            f"prior_probs length {len(prior_probs)} doesn't match "
            f"epsilons length {len(epsilons)}"
        )

    # Normalize prior probabilities
    prior_probs = prior_probs / prior_probs.sum()

    # Compute log likelihood for each epsilon
    log_likelihoods = np.zeros(len(epsilons))
    for i, epsilon in enumerate(epsilons):
        log_likelihoods[i] = log_likelihood_member(
            epsilon, reference_model_matrix, model_matrix, selections_matrix
        )

    # Compute log prior + log likelihood
    log_posteriors = np.log(prior_probs + 1e-10) + log_likelihoods

    # For numerical stability, compute ratios relative to minimum epsilon
    # L_k = log(P(epsilon_k)) + sum(log(P(D_j | epsilon_k)))
    L_k = log_posteriors[0]

    # Compute ratios: r_i = exp(L_i - L_k)
    ratios = np.exp(log_posteriors - L_k)

    # Normalize to get posterior probabilities
    posterior_probs = ratios / ratios.sum()

    return posterior_probs


def build_model_matrices(
    model_df: pd.DataFrame,
    reference_model_df: pd.DataFrame,
    selections_df: pd.DataFrame,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Build matrices for model comparison from dataframes.

    Converts dataframes with decision-choice-probability structure into
    matrices suitable for use with prob_members function.

    Args:
        model_df: DataFrame with columns ['_decision', '_choice', 'probability']
            giving modeled probabilities for the hypothesis model.
        reference_model_df: DataFrame with columns ['_decision', '_choice', 'probability']
            giving modeled probabilities for the reference model.
        selections_df: DataFrame with columns ['_decision', '_choice'] containing
            only the actually selected choices (one per decision).

    Returns:
        Tuple of (model_matrix, reference_model_matrix, selection_matrix):
            - model_matrix: G_H for prob_members (N_D x N_C)
            - reference_model_matrix: G_B for prob_members (N_D x N_C)
            - selection_matrix: C for prob_members (N_D x N_C)

    Raises:
        ValueError: If model and reference model have different decision-choice pairs.
        ValueError: If selections contain decisions not in the model dataframes.
    """
    # Validate required columns
    required_model_cols = {"_decision", "_choice", "probability"}
    required_selection_cols = {"_decision", "_choice"}

    if not required_model_cols.issubset(model_df.columns):
        raise ValueError(f"model_df must contain columns: {required_model_cols}")

    if not required_model_cols.issubset(reference_model_df.columns):
        raise ValueError(
            f"reference_model_df must contain columns: {required_model_cols}"
        )

    if not required_selection_cols.issubset(selections_df.columns):
        raise ValueError(
            f"selections_df must contain columns: {required_selection_cols}"
        )

    # Sort both model dataframes
    model_df = model_df.sort_values(["_decision", "_choice"]).reset_index(drop=True)
    reference_model_df = reference_model_df.sort_values(
        ["_decision", "_choice"]
    ).reset_index(drop=True)

    # Verify both models have the same decision-choice pairs
    model_keys = model_df[["_decision", "_choice"]]
    ref_keys = reference_model_df[["_decision", "_choice"]]

    if not model_keys.equals(ref_keys):
        raise ValueError(
            "model_df and reference_model_df must have identical "
            "_decision and _choice pairs"
        )

    # Get unique decisions and choices for indexing
    decisions = model_df["_decision"].unique()
    decision_to_idx = {d: i for i, d in enumerate(decisions)}

    # Determine max number of choices per decision
    choices_per_decision = model_df.groupby("_decision").size()
    max_choices = choices_per_decision.max()

    # Initialize matrices
    n_decisions = len(decisions)
    model_matrix = np.zeros((n_decisions, max_choices))
    reference_model_matrix = np.zeros((n_decisions, max_choices))
    selection_matrix = np.zeros((n_decisions, max_choices))

    # Fill model matrices
    for decision in decisions:
        decision_idx = decision_to_idx[decision]
        model_subset = model_df[model_df["_decision"] == decision]

        for choice_idx, (_, row) in enumerate(model_subset.iterrows()):
            model_matrix[decision_idx, choice_idx] = row["probability"]

        ref_subset = reference_model_df[reference_model_df["_decision"] == decision]
        for choice_idx, (_, row) in enumerate(ref_subset.iterrows()):
            reference_model_matrix[decision_idx, choice_idx] = row["probability"]

    # Fill selection matrix
    for _, row in selections_df.iterrows():
        decision = row["_decision"]
        choice = row["_choice"]

        if decision not in decision_to_idx:
            raise ValueError(f"Selection decision {decision} not found in model data")

        decision_idx = decision_to_idx[decision]

        # Find which choice index this corresponds to
        model_subset = model_df[model_df["_decision"] == decision]
        choice_indices = model_subset["_choice"].tolist()

        if choice not in choice_indices:
            raise ValueError(
                f"Selection choice {choice} not found in model data "
                f"for decision {decision}"
            )

        choice_idx = choice_indices.index(choice)
        selection_matrix[decision_idx, choice_idx] = 1

    return model_matrix, reference_model_matrix, selection_matrix


def compute_support(
    model_df: pd.DataFrame,
    reference_model_df: pd.DataFrame,
    selections_df: pd.DataFrame,
    epsilons: np.ndarray,
) -> np.ndarray:
    """
    Compute support for a model mixture from dataframes.

    This is a convenience wrapper that builds matrices and computes posterior
    probabilities for a family of mixture models.

    Args:
        model_df: DataFrame with columns ['_decision', '_choice', 'probability']
            for the hypothesis model.
        reference_model_df: DataFrame with columns ['_decision', '_choice', 'probability']
            for the reference model.
        selections_df: DataFrame with columns ['_decision', '_choice'] containing
            only the actually selected choices.
        epsilons: Array of floats from 0 to 1 (inclusive) determining the
            density of the model mixture.

    Returns:
        Array of posterior probabilities (support) for each model in the mixture,
        in the same order as epsilons.

    Raises:
        ValueError: If input dataframes have incompatible structures.
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
    epsilons: np.ndarray,
) -> pd.DataFrame:
    """
    Compute mixture probabilities for all epsilon values.

    Creates a dataframe with probabilities for every model in the mixture
    across all decisions. The mixture is computed as:
    P_epsilon = (epsilon * G_H + (1 - epsilon) * G_B) / sum(odds)

    Args:
        model_df: DataFrame with columns ['_decision', '_choice', 'probability']
            for the hypothesis model. May contain additional context columns.
        reference_model_df: DataFrame with columns ['_decision', '_choice', 'probability']
            for the reference model. May contain additional context columns.
        epsilons: Array of floats from 0 to 1 (inclusive) defining the
            family of models.

    Returns:
        DataFrame with columns ['_decision', '_choice', 'epsilon', 'probability']
        and rows for every model in the mixture across all decisions.
        Additional columns from input dataframes are preserved.

    Raises:
        ValueError: If required columns are missing or dataframes are incompatible.
    """
    # Validate required columns
    required_cols = {"_decision", "_choice", "probability"}

    if not required_cols.issubset(model_df.columns):
        raise ValueError(f"model_df must contain columns: {required_cols}")

    if not required_cols.issubset(reference_model_df.columns):
        raise ValueError(f"reference_model_df must contain columns: {required_cols}")

    # Merge model and reference model dataframes
    merged = model_df.merge(
        reference_model_df,
        on=["_decision", "_choice"],
        suffixes=("_model", "_ref"),
        how="outer",
    )

    # Check for missing data
    if merged.isnull().any().any():
        raise ValueError(
            "model_df and reference_model_df must have identical "
            "_decision and _choice pairs"
        )

    # Cross join with epsilons
    merged["key"] = 1
    epsilon_df = pd.DataFrame({"epsilon": epsilons, "key": 1})
    mixtures = merged.merge(epsilon_df, on="key").drop("key", axis=1)

    # Compute odds: epsilon * G_H + (1 - epsilon) * G_B
    mixtures["odds"] = (
        mixtures["epsilon"] * mixtures["probability_model"]
        + (1 - mixtures["epsilon"]) * mixtures["probability_ref"]
    )

    # Compute sum of odds per decision and epsilon
    odds_sums = (
        mixtures.groupby(["_decision", "epsilon"])["odds"]
        .sum()
        .reset_index()
        .rename(columns={"odds": "odds_sum"})
    )

    # Merge back to get odds_sum for each row
    mixtures = mixtures.merge(odds_sums, on=["_decision", "epsilon"])

    # Compute probability: odds / odds_sum
    mixtures["probability"] = mixtures["odds"] / mixtures["odds_sum"]

    # Select final columns
    # Keep context columns from original model_df (excluding probability)
    context_cols = [
        c
        for c in model_df.columns
        if c not in ["_decision", "_choice", "probability"]
    ]
    final_cols = ["_decision", "_choice", "epsilon", "probability"] + context_cols

    # Get context columns from the original model_df
    if context_cols:
        mixtures = mixtures.merge(
            model_df[["_decision", "_choice"] + context_cols],
            on=["_decision", "_choice"],
            how="left",
        )

    result = mixtures[final_cols]

    return result
