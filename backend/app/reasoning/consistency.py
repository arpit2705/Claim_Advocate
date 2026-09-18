"""
consistency.py — Tallies agreement across 3 reasoning passes into a consistency_score.

The consistency_score is the fraction of passes that agree with the plurality verdict.
It is an agreement rate — NOT a probability or confidence measure.
Do not label or describe it as a probability anywhere.
"""
from __future__ import annotations

from collections import Counter
from typing import Any


def tally_consistency(pass_results: list[dict[str, Any]]) -> tuple[str, float, list[str]]:
    """
    Determines the plurality verdict and computes the agreement rate.

    Parameters
    ----------
    pass_results : list[dict[str, Any]]
        List of pass result dicts from run_three_pass_reasoning(). Each must
        have a "verdict" key.

    Returns
    -------
    tuple[str, float, list[str]]
        - final_verdict: plurality verdict string
        - consistency_score: fraction of passes agreeing with plurality (0.0–1.0)
        - pass_verdict_list: list of verdict strings from each pass (for audit trail)
    """
    if not pass_results:
        return "insufficient_evidence", 0.0, []

    verdicts = [p.get("verdict", "insufficient_evidence") for p in pass_results]
    counts = Counter(verdicts)
    plurality_verdict, plurality_count = counts.most_common(1)[0]
    consistency_score = plurality_count / len(pass_results)

    return plurality_verdict, consistency_score, verdicts


def select_best_pass(
    pass_results: list[dict[str, Any]],
    final_verdict: str,
) -> dict[str, Any]:
    """
    Selects the pass result that matches the final verdict and has the
    most detailed explanation (longest explanation string).

    Parameters
    ----------
    pass_results : list[dict[str, Any]]
        All three pass result dicts.
    final_verdict : str
        The plurality verdict chosen by tally_consistency().

    Returns
    -------
    dict[str, Any]
        The best matching pass result dict.
    """
    matching = [p for p in pass_results if p.get("verdict") == final_verdict]
    if not matching:
        # Fallback: return the first pass
        return pass_results[0] if pass_results else {}
    # Prefer the pass with the most detailed explanation
    return max(matching, key=lambda p: len(p.get("explanation", "")))
