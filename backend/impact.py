"""
impact.py – Impact analysis generator.
Produces structured impact analysis for any decision.
"""
from typing import Dict, Any, Optional
from schemas import ImpactAnalysis


# ─── Category-specific impact templates ──────────────────────────────────────

LAPTOP_IMPACTS = {
    "immediate": [
        "Meets your current software and workflow requirements.",
        "Fits within your stated budget range.",
        "Available from multiple vendors with standard warranty.",
    ],
    "cost_impact": [
        "One-time capital expense; total cost of ownership includes accessories and support.",
        "Budget accessories (charger, bag, mouse) may add ₹3,000–₹8,000 to initial cost.",
        "Annual software licenses (if needed) should be factored separately.",
    ],
    "long_term": [
        "A well-chosen laptop typically remains capable for 3–5 years of everyday use.",
        "For AI/ML and gaming workloads, computational demands will increase over time.",
        "Battery capacity typically degrades to ~80% of original capacity after 2–3 years.",
    ],
    "trade_offs": [
        "Higher performance often means higher weight and lower battery life.",
        "Budget models save money upfront but may require replacement sooner.",
        "Gaming laptops offer GPU power but are less portable for daily commuting.",
    ],
    "risks": [
        "Avoid purchasing refurbished without certified warranty.",
        "Physical damage voids most standard warranties.",
        "Software compatibility should be verified before purchase.",
    ],
    "maintenance": [
        "Clean cooling vents every 6–12 months for optimal thermal performance.",
        "Replace thermal paste every 2–3 years on gaming/performance laptops.",
        "Regular OS updates and antivirus essential for longevity.",
    ],
}

COMPANY_BULK_IMPACTS = {
    "immediate": [
        "Enables standardised hardware across the organisation.",
        "Reduces individual procurement complexity and negotiation overhead.",
        "Bulk purchasing often qualifies for vendor discounts of 5–15%.",
    ],
    "cost_impact": [
        "Capital expense spread across budget cycle; consider depreciation schedules.",
        "IT setup and imaging costs add approximately ₹1,000–₹3,000 per unit.",
        "Extended warranty for business use is strongly recommended (adds 10–15% to unit cost).",
    ],
    "long_term": [
        "3-year refresh cycles are typical for business hardware.",
        "Standardised fleet reduces IT support complexity and training costs.",
        "Consider resale value of current equipment to offset new purchase cost.",
    ],
    "trade_offs": [
        "Lower-spec units save upfront cost but may limit productivity for power users.",
        "Higher-spec units future-proof the investment but increase capital expenditure.",
        "Leasing provides flexibility but increases total cost of ownership over 3+ years.",
    ],
    "risks": [
        "Ensure vendor has capacity to deliver required quantity within your timeline.",
        "Verify warranty terms cover on-site service for business use.",
        "Plan for 5–10% spare units for immediate replacements.",
    ],
    "maintenance": [
        "Centralise device management using MDM (Mobile Device Management) software.",
        "Schedule quarterly maintenance windows for OS and security updates.",
        "Maintain hardware inventory records for lifecycle and warranty tracking.",
    ],
}

GENERIC_IMPACTS = {
    "immediate": [
        "Addresses your stated immediate need or problem.",
        "Implementation or adoption will require an initial adjustment period.",
    ],
    "cost_impact": [
        "Evaluate total cost of ownership, not just purchase price.",
        "Factor in ongoing maintenance or subscription costs.",
        "Consider resale value or reversibility if the decision does not work out.",
    ],
    "long_term": [
        "Consider how well this choice will scale with your evolving needs.",
        "Reassess the decision after 6–12 months of use.",
    ],
    "trade_offs": [
        "Every option involves trade-offs between cost, quality, and convenience.",
        "The recommended option best matches your stated priorities, but alternatives may suit different preferences.",
    ],
    "risks": [
        "Research vendor reliability and after-sales support before committing.",
        "Verify compatibility with your existing setup or environment.",
    ],
    "maintenance": [
        "Factor in time and cost of ongoing maintenance.",
        "Build a regular review schedule to ensure the decision continues to meet your needs.",
    ],
}

FISH_AQUARIUM_IMPACTS = {
    "immediate": [
        "Setting up a new aquarium requires 2–4 weeks of nitrogen cycle establishment before adding fish.",
        "Initial setup cost includes tank, filter, heater, lighting, substrate, and decorations.",
        "Research fish compatibility thoroughly before purchasing.",
    ],
    "cost_impact": [
        "Ongoing costs include fish food, water conditioners, electricity (heater, filter, light), and occasional medications.",
        "Water testing kits are essential; budget ₹2,500–₹3,500 for a reliable liquid test kit.",
        "Monthly maintenance cost typically ranges from ₹500–₹2,000 depending on tank size.",
    ],
    "long_term": [
        "Fish lifespans range from 2 years (some tetras) to 10–15 years (goldfish, cichlids).",
        "Filter media replacement and equipment upgrades are periodic long-term costs.",
        "Larger tanks are generally more stable and easier to maintain once established.",
    ],
    "trade_offs": [
        "Larger tanks cost more upfront but offer more stable water parameters and fish variety.",
        "Saltwater tanks are more complex and expensive but offer more variety.",
        "Some visually striking fish have complex care requirements not suitable for beginners.",
    ],
    "risks": [
        "New tank syndrome (ammonia/nitrite spike) is the most common cause of fish loss in new setups.",
        "Overstocking significantly increases waste load and disease risk.",
        "Always quarantine new fish for 2–4 weeks before introducing to the main tank.",
    ],
    "maintenance": [
        "Weekly 20–30% water changes are essential for water quality.",
        "Clean filter media monthly in old tank water (not tap water).",
        "Test water parameters weekly, especially in newly established tanks.",
    ],
}

RELATIONSHIP_IMPACTS = {
    "immediate": [
        "De-escalates emotional tension by honoring your friend's immediate boundary and request for space.",
        "Halts the cycle of panic texting, preventing words spoken out of fear of abandonment.",
        "Allows heightened physiological stress and adrenaline levels to cool down before any conversation.",
    ],
    "cost_impact": [
        "Zero financial cost — the investment is emotional patience, self-regulation, and boundary respect.",
        "Managing acute short-term anxiety during the waiting period is the key psychological cost.",
    ],
    "long_term": [
        "Friendships that learn to weather fights with mutual respect for boundaries become stronger and more durable.",
        "Reduces unhealthy emotional over-dependence: having one person as your sole emotional lifeline places unsustainable pressure on that relationship.",
        "Builds lasting conflict resolution maturity and self-reliance that benefits all future relationships.",
    ],
    "trade_offs": [
        "Giving space feels counter-intuitive when you feel lonely, but pursuing someone who asked for distance almost always pushes them further away.",
        "Short-term discomfort of waiting is traded for a significantly higher likelihood of successful reconciliation.",
    ],
    "risks": [
        "Prolonging silence indefinitely (beyond 7–10 days) without a gentle door-opener can cause emotional distance to harden.",
        "Over-apologizing or accepting unfair blame just out of fear of losing them creates toxic relationship imbalance.",
    ],
    "maintenance": [
        "Step 1: Observe 48–72 hours of total cooling-off space without calls or messages.",
        "Step 2: Reach out with a short, low-pressure message acknowledging their boundary and stating you value the friendship.",
        "Step 3: Actively engage in hobbies, community groups, or other friendships so you are not dependent on a single point of emotional connection.",
    ],
}

CATEGORY_IMPACT_MAP = {
    "laptop": LAPTOP_IMPACTS,
    "smartphone": {
        "immediate": ["Addresses your communication, entertainment and productivity needs.", "Check network compatibility (5G/4G bands) with your carrier."],
        "cost_impact": ["Consider total cost including accessories (case, screen protector, charger).", "Insurance adds ₹500–₹1,500/year but protects against damage."],
        "long_term": ["Android phones typically receive OS updates for 3–4 years; iPhones for 5–6 years.", "Battery capacity typically degrades to ~80% after 2–3 years of heavy use."],
        "trade_offs": ["Android offers more customisation; iOS offers tighter ecosystem integration.", "Higher megapixel cameras do not always produce better photos — sensor size matters more."],
        "risks": ["Buy from authorised dealers to ensure warranty validity.", "Verify IMEI status before purchasing pre-owned devices."],
        "maintenance": ["Use a protective case and tempered glass screen protector.", "Charge between 20–80% to maximise battery longevity.", "Regular software updates improve security and performance."],
    },
    "company_bulk": COMPANY_BULK_IMPACTS,
    "fish_aquarium": FISH_AQUARIUM_IMPACTS,
    "pet": {
        "immediate": ["Research breed-specific needs, temperament, and compatibility with your living situation.", "Initial costs include pet, vaccinations, microchipping, bed, food, and accessories."],
        "cost_impact": ["Annual veterinary costs range from ₹5,000–₹25,000+ depending on species and health.", "Food, grooming, and supplies are ongoing monthly costs."],
        "long_term": ["Pets are long-term commitments (dogs: 10–15 years; cats: 12–18 years).", "Consider pet care arrangements for travel and emergencies."],
        "trade_offs": ["Puppies require intensive training; adult rescue pets may have established behaviours.", "High-energy breeds require more exercise and time commitment."],
        "risks": ["Verify breeder or shelter credentials before adopting.", "Ensure all family members are comfortable and not allergic before committing."],
        "maintenance": ["Regular vaccinations, deworming, and vet check-ups are essential.", "Groom, exercise, and socialise pets regularly for their wellbeing."],
    },
    "relationship": RELATIONSHIP_IMPACTS,
    "personal": RELATIONSHIP_IMPACTS,
    "health": {
        "immediate": [
            "Replenishes fluids and vital electrolytes (sodium, potassium) to prevent acute dehydration and fatigue.",
            "Reduces intestinal motility and mechanical irritation with low-residue, bland foods (BRAT protocol).",
            "Soothes the gastric lining and helps ease abdominal cramping within 4–12 hours.",
        ],
        "cost_impact": [
            "Low-cost recovery: ORS sachets (₹5–₹20), bananas, white rice, and plain toast cost under ₹100.",
            "Early oral rehydration eliminates the risk and heavy expense of emergency room IV fluid admission.",
        ],
        "long_term": [
            "Protects intestinal barrier integrity and prepares gut for gradual microflora repopulation.",
            "Helps pinpoint whether acute diarrhea was triggered by food intolerance, viral bug, or contaminated water.",
        ],
        "trade_offs": [
            "Bland BRAT food lacks flavor and variety, but trades taste for immediate bowel stabilization.",
            "Total food restriction/starvation is counter-productive; small sips of electrolytes and starch maintain gut lining cells.",
        ],
        "risks": [
            "RED FLAG WARNING: Consult a physician immediately if you have high fever (>102°F/39°C), bloody/black stool, severe unremitting abdominal pain, or dehydration signs (dry mouth, dizziness, dark urine).",
            "Avoid taking over-the-counter anti-diarrheal pills (e.g. Loperamide) if bacterial infection or fever is suspected without doctor guidance.",
        ],
        "maintenance": [
            "Phase 1 (Hours 0–12): Sip ORS, electrolyte water, or clear salted broth every 15–30 minutes.",
            "Phase 2 (Hours 12–36): Introduce BRAT diet foods (Bananas, white Rice, Applesauce, plain dry Toast, boiled potatoes).",
            "Phase 3 (Hours 36–72): Slowly reintroduce plain curd (probiotics) and light soups; strictly avoid dairy, oily curries, caffeine, and raw salad for 4–5 days.",
        ],
    },
}


def generate_impact(
    category: str,
    recommendation: str,
    answers: Dict[str, Any],
    bulk_summary: Optional[Dict[str, Any]] = None,
) -> ImpactAnalysis:
    """Generate a structured impact analysis."""
    cat = category.lower().strip()
    template = CATEGORY_IMPACT_MAP.get(cat, GENERIC_IMPACTS)

    immediate = list(template.get("immediate", GENERIC_IMPACTS["immediate"]))
    cost_impact = list(template.get("cost_impact", GENERIC_IMPACTS["cost_impact"]))
    long_term = list(template.get("long_term", GENERIC_IMPACTS["long_term"]))
    trade_offs = list(template.get("trade_offs", GENERIC_IMPACTS["trade_offs"]))
    risks = list(template.get("risks", GENERIC_IMPACTS["risks"]))
    maintenance = list(template.get("maintenance", GENERIC_IMPACTS["maintenance"]))

    # Personalise with budget if provided
    budget = answers.get("budget") or answers.get("total_budget") or 0
    try:
        budget = float(budget)
    except (TypeError, ValueError):
        budget = 0

    if budget > 0 and cat == "laptop":
        cost_impact.insert(0, f"Your stated budget of ₹{budget:,.0f} allows for adequate options in the mid-range segment." if budget < 80000 else f"Your stated budget of ₹{budget:,.0f} provides access to premium configurations.")

    if bulk_summary and cat == "company_bulk":
        qty = bulk_summary.get("quantity", 1)
        total = bulk_summary.get("estimated_total", "")
        remaining = bulk_summary.get("remaining_budget", "")
        cost_impact.insert(0, f"Estimated total for {qty} units: {total}.")
        if remaining and remaining != "N/A":
            cost_impact.insert(1, f"Estimated remaining budget: {remaining}.")

    return ImpactAnalysis(
        immediate=immediate,
        cost_impact=cost_impact,
        long_term=long_term,
        trade_offs=trade_offs,
        risks=risks,
        maintenance=maintenance,
    )
