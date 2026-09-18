"""
whatif.py – What-if analysis engine.
Re-runs the decision engine with modified parameters and detects recommendation changes.
"""
from typing import Dict, Any, Optional, Tuple
from schemas import DecisionResult


def run_whatif(
    category: str,
    original_input: Dict[str, Any],
    changes: Dict[str, Any],
) -> Tuple[DecisionResult, bool, str]:
    """
    Apply changes to original input and re-run decision engine.
    Returns (new_result, recommendation_changed, change_explanation)
    """
    from decision_engine import run_decision_engine

    # Merge changes into original input
    modified = dict(original_input)
    modified.update(changes)

    # Run engine with modified input
    original_rec = original_input.get("recommendation", "")
    new_result = run_decision_engine(category, modified)

    # Detect if recommendation changed
    rec_changed = (
        original_rec != new_result.recommendation and
        original_rec != ""
    )

    # Generate explanation of why it changed
    change_explanation = _explain_change(changes, original_input, rec_changed)

    return new_result, rec_changed, change_explanation


def _explain_change(
    changes: Dict[str, Any],
    original: Dict[str, Any],
    changed: bool,
) -> str:
    """Generate a plain English explanation of what changed and why."""
    if not changes:
        return "No changes were applied."

    parts = []
    for key, new_val in changes.items():
        old_val = original.get(key)
        label = key.replace("_", " ").title()
        if old_val is not None and old_val != new_val:
            parts.append(f"{label} changed from {old_val} to {new_val}")
        else:
            parts.append(f"{label} set to {new_val}")

    change_str = "; ".join(parts)

    if changed:
        return (
            f"Your recommendation changed because: {change_str}. "
            "The modified parameters shift the optimal option to a different candidate."
        )
    else:
        return (
            f"Changes applied: {change_str}. "
            "The core recommendation remains the same, but confidence and factor scores have been updated."
        )
