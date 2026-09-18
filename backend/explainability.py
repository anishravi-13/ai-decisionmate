"""
explainability.py – Factor-based explanation generator.
Produces human-readable explanations of decision factors.
"""
from typing import List, Dict, Any
from schemas import FactorScore


def generate_explanation(
    factors: List[FactorScore],
    recommendation: str,
    category: str,
    answers: Dict[str, Any],
) -> str:
    """Generate a plain-English explanation of the recommendation."""
    if not factors:
        return "The recommendation is based on your stated requirements."

    # Sort factors by score descending
    sorted_factors = sorted(factors, key=lambda f: f.score, reverse=True)
    top = sorted_factors[:3]

    top_names = [f.label for f in top]
    strong = [f for f in top if f.score >= 75]
    weak = [f for f in sorted_factors if f.score < 60]

    if len(strong) >= 2:
        strength_phrase = f"Your **{top_names[0]}** and **{top_names[1]}** were the strongest factors."
    elif len(strong) == 1:
        strength_phrase = f"Your **{top_names[0]}** was the primary determining factor."
    else:
        strength_phrase = "The recommendation is based on a balanced evaluation of all factors."

    # Category-specific context
    context_map = {
        "laptop": f"For a laptop decision, performance, budget, and portability are typically the most critical factors.",
        "smartphone": f"For a smartphone decision, budget, camera requirements, and OS preference are key.",
        "company_bulk": f"For a bulk purchase, per-unit budget, warranty, and total cost fit are critical.",
        "fish_aquarium": f"Tank size, water type, and experience level are the primary compatibility factors.",
        "pet": f"Lifestyle compatibility, care commitment, and budget are the main pet selection factors.",
        "education": f"Accreditation, career alignment, and cost-to-benefit ratio drive this recommendation.",
        "career": f"This decision is influenced by market demand, skill alignment, and financial readiness.",
        "relationship": f"In interpersonal disputes, respecting explicit boundaries and allowing emotional cooling-off are the highest-leverage strategies to preserve the relationship.",
        "personal": f"For personal decisions, emotional safety, personal boundaries, and support network health are vital.",
        "general": f"The recommendation reflects the best match across your stated criteria.",
    }
    context = context_map.get(category, context_map["general"])

    # Limitations mention
    limitation = ""
    if weak:
        limitation = (
            f" Note that **{weak[0].label}** scored lower — "
            "this represents a trade-off in the recommendation."
        )

    return f"{strength_phrase} {context}{limitation}"


def compute_factor_contributions(
    raw_scores: Dict[str, float],
    weights: Dict[str, float],
) -> List[FactorScore]:
    """
    Compute weighted factor contributions and normalize to percentage display.
    raw_scores: {factor_name: raw_score 0-100}
    weights: {factor_name: weight 0-1}
    Returns FactorScore list sorted by contribution descending.
    """
    label_map = {
        "budget_match": "Budget Compatibility",
        "performance_match": "Performance Match",
        "usage_match": "Usage Fit",
        "portability_match": "Portability",
        "battery_match": "Battery Priority",
        "gaming_match": "Gaming Capability",
        "ai_ml_match": "AI/ML Capability",
        "os_preference": "OS Preference",
        "brand_preference": "Brand Preference",
        "requirements_match": "Requirements Match",
        "budget_per_unit": "Budget per Unit",
        "total_cost_fit": "Total Cost Fit",
        "warranty_match": "Warranty Coverage",
        "delivery_feasibility": "Delivery Feasibility",
        "preference_match": "Preference Alignment",
        "feasibility": "Practical Feasibility",
        "requirement_match": "Requirement Match",
        "boundary_respect": "Respect for Stated Boundaries",
        "deescalation": "Emotional De-escalation Priority",
        "relationship_longevity": "Relationship Value & Longevity",
        "support_system": "Mitigation of Over-dependence",
        "communication_timing": "Non-Defensive Timing",
        "space_fit": "Living Space Compatibility",
        "activity_fit": "Exercise & Activity Match",
        "time_fit": "Care & Grooming Commitment",
        "budget_fit": "Maintenance Cost Fit",
        "temperament_fit": "Temperament & Lifestyle Fit",
    }

    desc_map = {
        "budget_match": "How well the recommendation fits your stated budget",
        "performance_match": "Alignment with your performance requirements",
        "usage_match": "Suitability for your primary use case",
        "portability_match": "Weight and portability requirements match",
        "battery_match": "Battery life alignment with your needs",
        "gaming_match": "Gaming performance requirements match",
        "ai_ml_match": "Machine learning workload support",
        "requirements_match": "Alignment with stated requirements",
        "budget_per_unit": "Unit price fit within total budget allocation",
        "total_cost_fit": "Total purchase cost vs. available budget",
        "warranty_match": "Warranty terms match organisational needs",
        "delivery_feasibility": "Delivery timeline compatibility",
        "boundary_respect": "Honoring his explicit request not to talk prevents further escalation and emotional pushback",
        "deescalation": "Allowing heat and adrenaline from the fight to cool before attempting any conversation",
        "relationship_longevity": "Protecting the core friendship rather than forcing a rushed, panicked resolution",
        "support_system": "Addressing the vulnerability of having a single emotional anchor by broadening support",
        "communication_timing": "Ensuring your eventual outreach is thoughtful, calm, and pressure-free",
        "space_fit": "Compatibility between the breed's size/energy and your home square footage",
        "activity_fit": "Match between the breed's daily exercise demand and your physical activity level",
        "time_fit": "Sufficient daily availability for walking, mental stimulation, and coat grooming",
        "budget_fit": "Alignment between expected monthly food, grooming, and vet costs and your budget",
        "temperament_fit": "How naturally the breed's inherent behavioral traits integrate into your household",
    }

    factors = []
    for name, score in raw_scores.items():
        weight = weights.get(name, 1.0 / len(raw_scores))
        weighted = score * weight
        factors.append(FactorScore(
            factor=name,
            score=round(score),
            label=label_map.get(name, name.replace("_", " ").title()),
            description=desc_map.get(name, "Contributing factor to recommendation"),
        ))

    factors.sort(key=lambda f: f.score, reverse=True)
    return factors
