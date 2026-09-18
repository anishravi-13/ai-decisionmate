"""
decision_engine.py – Hybrid decision engine.
Uses keyword extraction + weighted scoring for each category.
Works completely offline. No external AI API required.
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from schemas import FactorScore, AlternativeOption, DecisionResult, ImpactAnalysis, ProductCard
from product_catalog import get_products_for_category, DEMO_LAPTOPS, DEMO_PHONES


# ─── Category Detection ───────────────────────────────────────────────────────

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "laptop": ["laptop", "notebook", "macbook", "chromebook", "lenovo", "hp laptop", "dell laptop", "asus laptop", "coding laptop", "gaming laptop"],
    "smartphone": ["phone", "smartphone", "mobile", "iphone", "android", "samsung", "oneplus", "redmi", "pixel"],
    "pc_components": ["desktop", "pc", "cpu", "gpu", "motherboard", "ram", "processor", "graphics card", "build a pc", "custom pc"],
    "pet": ["dog", "cat", "pet", "puppy", "kitten", "bird", "hamster", "rabbit", "animal food", "pet supplies"],
    "fish_aquarium": ["fish", "aquarium", "tank", "betta", "goldfish", "tetra", "freshwater", "saltwater", "reef", "aquatic"],
    "education": ["course", "degree", "college", "university", "study", "learn", "certification", "mba", "engineering", "skill"],
    "career": ["job", "career", "switch career", "resign", "promotion", "freelance", "business idea", "startup", "work"],
    "travel": ["travel", "trip", "vacation", "flight", "hotel", "tourism", "destination", "holiday", "visa", "backpack"],
    "home": ["home", "house", "apartment", "furniture", "appliance", "refrigerator", "washing machine", "sofa", "tv", "air conditioner"],
    "vehicle": ["car", "bike", "motorcycle", "scooter", "electric vehicle", "ev", "suv", "sedan", "vehicle"],
    "office_equipment": ["office", "printer", "monitor", "keyboard", "mouse", "desk", "chair", "scanner", "projector"],
    "company_bulk": ["company", "bulk", "enterprise", "employees", "units", "corporate", "office purchase", "fleet", "wholesale", "25 laptops", "50 units"],
    "product_purchase": ["buy", "purchase", "recommend", "which one should", "best product", "best option"],
    "relationship": [
        "friend", "friendship", "fight", "argument", "relationship", "breakup", "partner", "boyfriend", "girlfriend",
        "conflict", "apologize", "apology", "family", "parent", "colleague", "coworker", "roommate", "dating",
        "talk to him", "talk to her", "not to talk", "not talking", "lonely", "alone", "disagreement", "broke up",
        "ignore me", "ignoring me", "blocked me", "silent treatment", "reconcile", "reconciliation", "forgive",
        "forgiveness", "boundary", "boundaries", "all i have", "close to me", "best friend"
    ],
    "personal": [
        "personal dilemma", "mental health", "habit", "stress", "routine", "burnout", "work life balance",
        "life decision", "self improvement", "guilt", "anxiety"
    ],
    "health": [
        "diarrhea", "diarrhoea", "loose motion", "stomach", "stomach ache", "food poisoning",
        "vomiting", "vomit", "nausea", "fever", "headache", "cold", "flu", "cough", "indigestion",
        "what should i eat", "what to eat", "what shoulod i eat", "diet", "nutrition", "dehydration",
        "ors", "electrolyte", "infection", "medicine", "doctor", "allergy", "cramps", "sick",
        "illness", "gastroenteritis", "gastric", "acidity", "constipation"
    ],
}


def detect_category(text: str) -> str:
    """Detect decision category from free text."""
    text_lower = text.lower()
    scores: Dict[str, int] = {cat: 0 for cat in CATEGORY_KEYWORDS}

    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[cat] += 2 if len(kw.split()) > 1 else 1

    best = max(scores, key=lambda k: scores[k])
    if scores[best] == 0:
        return "general"
    return best


# ─── Entity Extraction ────────────────────────────────────────────────────────

def extract_budget(text: str) -> Optional[float]:
    """Extract budget in INR from text."""
    patterns = [
        r"₹\s*([\d,]+(?:\.\d+)?)\s*(?:lakh|lac|l\b)",
        r"rs\.?\s*([\d,]+(?:\.\d+)?)\s*(?:lakh|lac|l\b)",
        r"inr\s*([\d,]+(?:\.\d+)?)\s*(?:lakh|lac|l\b)",
        r"budget\s+(?:of\s+|is\s+)?₹?\s*([\d,]+(?:\.\d+)?)\s*(?:lakh|lac|l\b)",
        r"₹\s*([\d,]+(?:\.\d+)?)",
        r"rs\.?\s*([\d,]+(?:\.\d+)?)",
        r"budget\s+(?:of\s+|is\s+)?([\d,]+(?:\.\d+)?)",
        r"under\s+([\d,]+(?:\.\d+)?)",
        r"below\s+([\d,]+(?:\.\d+)?)",
        r"([\d,]+)\s*(?:rupees|inr)",
    ]
    text_lower = text.lower()
    for pat in patterns:
        m = re.search(pat, text_lower)
        if m:
            val_str = m.group(1).replace(",", "")
            val = float(val_str)
            # Check if "lakh" was in the original pattern match context
            window = text_lower[max(0, m.start() - 5):m.end() + 10]
            if "lakh" in window or "lac" in window or "l " in window:
                val *= 100000
            return val
    return None


def extract_quantity(text: str) -> Optional[int]:
    """Extract quantity from text."""
    patterns = [
        r"(\d+)\s+(?:units|laptops|phones|computers|devices|items|pieces)",
        r"(?:quantity|qty|count)\s+(?:of\s+)?(\d+)",
        r"for\s+(\d+)\s+(?:employees|users|people|staff)",
        r"(\d+)\s+(?:employees|users|people|staff)",
    ]
    for pat in patterns:
        m = re.search(pat, text.lower())
        if m:
            return int(m.group(1))
    return None


def extract_requirements(text: str) -> List[str]:
    """Extract requirement keywords from text."""
    requirement_terms = [
        "gaming", "programming", "coding", "office", "student", "professional",
        "lightweight", "portable", "long battery", "fast", "powerful", "budget",
        "ai", "machine learning", "ml", "data science", "video editing",
        "graphic design", "photography", "music", "travel", "outdoor",
        "beginner", "expert", "advanced", "basic",
    ]
    text_lower = text.lower()
    found = [term for term in requirement_terms if term in text_lower]
    return found


def extract_relationship_entities(text: str) -> Dict[str, Any]:
    """Extract interpersonal/relationship factors from free text."""
    text_lower = text.lower()
    entities: Dict[str, Any] = {}

    # Check if boundary / space was requested
    if any(k in text_lower for k in [
        "not to talk", "don't talk", "dont talk", "do not talk",
        "leave me alone", "space", "blocked", "ignoring me", "silent treatment"
    ]):
        entities["asked_for_space"] = "yes"
        entities["boundary_requested"] = "yes"
    else:
        entities["asked_for_space"] = "no"
        entities["boundary_requested"] = "no"

    # Check emotional stakes / isolation
    if any(k in text_lower for k in [
        "all i have", "only friend", "no one else", "nobody else",
        "so lonely", "alone", "can't lose", "cant lose", "only one"
    ]):
        entities["emotional_dependency"] = "high"
    elif any(k in text_lower for k in ["best friend", "very close", "really close", "important to me"]):
        entities["emotional_dependency"] = "medium"
    else:
        entities["emotional_dependency"] = "moderate"

    # Conflict intensity
    if any(k in text_lower for k in ["fight", "huge fight", "screaming", "angry", "furious", "hurtful"]):
        entities["conflict_intensity"] = "high"
    elif any(k in text_lower for k in ["argument", "disagreement", "misunderstanding", "upset"]):
        entities["conflict_intensity"] = "medium"
    else:
        entities["conflict_intensity"] = "low"

    # Responsibility attribution
    if any(k in text_lower for k in ["my fault", "i messed up", "i made a mistake", "i regret"]):
        entities["fault_attribution"] = "mostly_mine"
    elif any(k in text_lower for k in ["his fault", "her fault", "their fault", "unfair to me"]):
        entities["fault_attribution"] = "mostly_theirs"
    else:
        entities["fault_attribution"] = "mutual_or_unclear"

    entities["cooling_off_days"] = 3
    return entities


def extract_pet_entities(text: str) -> Dict[str, Any]:
    """Extract pet type, mentioned breed, and lifestyle constraints from text."""
    text_lower = text.lower()
    entities: Dict[str, Any] = {}

    known_breeds = {
        "golden retriever": "golden_retriever",
        "golden": "golden_retriever",
        "labrador retriever": "labrador",
        "labrador": "labrador",
        "lab": "labrador",
        "german shepherd": "german_shepherd",
        "gsd": "german_shepherd",
        "beagle": "beagle",
        "shih tzu": "shih_tzu",
        "shihtzu": "shih_tzu",
        "pug": "pug",
        "indie": "indie_desi",
        "indian pariah": "indie_desi",
        "desi dog": "indie_desi",
        "desi": "indie_desi",
        "french bulldog": "french_bulldog",
        "frenchie": "french_bulldog",
        "persian cat": "persian_cat",
        "persian": "persian_cat",
        "domestic shorthair": "domestic_shorthair",
        "siamese cat": "siamese_cat",
        "siamese": "siamese_cat",
    }

    for phrase, b_id in known_breeds.items():
        if phrase in text_lower:
            entities["breed_choice"] = b_id
            entities["selected_breed"] = b_id
            break

    if any(k in text_lower for k in ["dog", "puppy", "pup", "canine"]):
        entities["pet_type"] = "dog"
    elif any(k in text_lower for k in ["cat", "kitten", "kitty"]):
        entities["pet_type"] = "cat"

    if any(k in text_lower for k in ["small apartment", "studio", "1bhk", "compact flat"]):
        entities["living_situation"] = "apartment_small"
    elif any(k in text_lower for k in ["apartment", "flat", "2bhk", "3bhk"]):
        entities["living_situation"] = "apartment_large"
    elif any(k in text_lower for k in ["house with garden", "garden", "yard", "backyard", "farmhouse"]):
        entities["living_situation"] = "house_garden"
    elif any(k in text_lower for k in ["house", "bungalow"]):
        entities["living_situation"] = "house_no_garden"

    if any(k in text_lower for k in ["active", "running", "jogging", "trekking", "athletic"]):
        entities["activity_level"] = "high"
    elif any(k in text_lower for k in ["moderate", "normal walks", "daily walk"]):
        entities["activity_level"] = "medium"
    elif any(k in text_lower for k in ["low", "relaxed", "indoor", "lazy", "busy"]):
        entities["activity_level"] = "low"

    return entities


def extract_health_entities(text: str) -> Dict[str, Any]:
    """Extract health condition, symptoms, and dietary intent from free text."""
    text_lower = text.lower()
    entities: Dict[str, Any] = {}

    # Condition detection
    if any(k in text_lower for k in ["diarrhea", "diarrhoea", "loose motion", "watery stool"]):
        entities["condition"] = "diarrhea"
    elif any(k in text_lower for k in ["vomit", "vomiting", "nausea"]):
        entities["condition"] = "nausea_vomiting"
    elif any(k in text_lower for k in ["fever", "chills", "high temp"]):
        entities["condition"] = "fever"
    elif any(k in text_lower for k in ["acidity", "heartburn", "acid reflux"]):
        entities["condition"] = "acidity"
    elif any(k in text_lower for k in ["constipation", "bloating"]):
        entities["condition"] = "constipation"
    else:
        entities["condition"] = "stomach_upset"

    # Red flag symptoms detection
    if any(k in text_lower for k in ["blood", "bloody", "black stool", "faint", "dizziness", "severe pain", "103", "102"]):
        entities["red_flags"] = "yes"
    else:
        entities["red_flags"] = "no"

    # Duration
    if any(k in text_lower for k in ["just started", "today", "hours"]):
        entities["duration"] = "under_24h"
    elif any(k in text_lower for k in ["2 days", "yesterday", "3 days", "few days"]):
        entities["duration"] = "1_to_3_days"
    elif any(k in text_lower for k in ["week", "chronic", "long time"]):
        entities["duration"] = "over_3_days"
    else:
        entities["duration"] = "under_24h"

    # Hydration risk
    if any(k in text_lower for k in ["thirsty", "dry mouth", "weak", "tired", "fatigue", "dizzy"]):
        entities["dehydration_risk"] = "high"
    else:
        entities["dehydration_risk"] = "medium"

    return entities


# ─── Per-Category Scoring ─────────────────────────────────────────────────────

def score_laptop(answers: Dict[str, Any]) -> Tuple[List[FactorScore], float]:
    """Score laptop decision factors."""
    budget = answers.get("budget", 0) or 0
    usage = answers.get("usage", "general")
    ram_req = answers.get("ram_requirement", "8gb")
    performance = answers.get("performance_priority", "medium")
    gaming = answers.get("gaming_requirement", "no")
    ai_ml = answers.get("ai_ml_requirement", "no")
    portability = answers.get("portability", "medium")
    battery = answers.get("battery_priority", "medium")
    os_pref = answers.get("os_preference", "any")

    # Normalise to scores 0-100
    perf_map = {"low": 30, "medium": 60, "high": 90}
    usage_map = {
        "basic": 1, "student": 2, "programming": 3, "office": 2,
        "gaming": 5, "video_editing": 4, "ai_ml": 5, "general": 2,
    }
    usage_score = usage_map.get(str(usage).lower(), 2)

    perf_score = perf_map.get(str(performance).lower(), 60)
    port_score = {"low": 30, "medium": 60, "high": 90}.get(str(portability).lower(), 60)
    bat_score = {"low": 30, "medium": 60, "high": 90}.get(str(battery).lower(), 60)

    budget_fit = 75
    if budget > 0:
        if budget >= 80000:
            budget_fit = 95
        elif budget >= 55000:
            budget_fit = 80
        elif budget >= 35000:
            budget_fit = 65
        else:
            budget_fit = 50

    gaming_req_score = 90 if str(gaming).lower() in ["yes", "true", "1"] else 40
    ai_ml_score = 85 if str(ai_ml).lower() in ["yes", "true", "1"] else 40

    factors = [
        FactorScore(factor="budget_match", score=round(budget_fit), label="Budget Compatibility",
                    description="How well the recommendation fits your stated budget"),
        FactorScore(factor="performance_match", score=round(perf_score), label="Performance Match",
                    description="Alignment with your performance requirements"),
        FactorScore(factor="usage_match", score=round(min(usage_score * 18, 100)), label="Usage Fit",
                    description="Suitability for your primary use case"),
        FactorScore(factor="portability_match", score=round(port_score), label="Portability",
                    description="Weight and portability requirements match"),
        FactorScore(factor="battery_match", score=round(bat_score), label="Battery Priority",
                    description="Battery life alignment with your needs"),
    ]
    if str(gaming).lower() in ["yes", "true", "1"]:
        factors.append(FactorScore(factor="gaming_match", score=round(gaming_req_score), label="Gaming Requirement",
                                   description="Gaming capability match"))
    if str(ai_ml).lower() in ["yes", "true", "1"]:
        factors.append(FactorScore(factor="ai_ml_match", score=round(ai_ml_score), label="AI/ML Capability",
                                   description="Machine learning workload support"))

    avg = sum(f.score for f in factors) / len(factors)
    return factors, round(avg)


def score_company_bulk(answers: Dict[str, Any]) -> Tuple[List[FactorScore], float]:
    budget = float(answers.get("total_budget", 0) or 0)
    quantity = int(answers.get("quantity", 1) or 1)
    product_cat = answers.get("product_category", "laptop")
    perf_req = answers.get("performance_requirements", "medium")
    warranty = answers.get("warranty_importance", "medium")
    delivery = answers.get("delivery_requirements", "standard")

    unit_budget = budget / max(quantity, 1)

    budget_fit = 75
    if unit_budget >= 70000:
        budget_fit = 95
    elif unit_budget >= 50000:
        budget_fit = 80
    elif unit_budget >= 35000:
        budget_fit = 65
    else:
        budget_fit = 50

    perf_score = {"low": 40, "medium": 70, "high": 90}.get(str(perf_req).lower(), 70)
    warranty_score = {"low": 40, "medium": 70, "high": 95}.get(str(warranty).lower(), 70)
    delivery_score = {"urgent": 60, "standard": 85, "flexible": 95}.get(str(delivery).lower(), 85)

    factors = [
        FactorScore(factor="budget_per_unit", score=round(budget_fit), label="Budget per Unit",
                    description="Unit price fit within total budget allocation"),
        FactorScore(factor="total_cost_fit", score=round(budget_fit), label="Total Cost Fit",
                    description="Total purchase cost vs. available budget"),
        FactorScore(factor="requirements_match", score=round(perf_score), label="Requirements Match",
                    description="Alignment with stated performance/feature requirements"),
        FactorScore(factor="warranty_match", score=round(warranty_score), label="Warranty Coverage",
                    description="Warranty terms match organisational needs"),
        FactorScore(factor="delivery_feasibility", score=round(delivery_score), label="Delivery Feasibility",
                    description="Delivery timeline compatibility"),
    ]
    avg = sum(f.score for f in factors) / len(factors)
    return factors, round(avg)


def score_relationship(answers: Dict[str, Any]) -> Tuple[List[FactorScore], float]:
    """Score interpersonal and relationship decision factors."""
    asked_for_space = str(answers.get("asked_for_space", answers.get("boundary_requested", "no"))).lower() in ["yes", "true", "1"]
    dependency = str(answers.get("emotional_dependency", "medium")).lower()
    conflict = str(answers.get("conflict_intensity", "high")).lower()
    cooling_days = int(answers.get("cooling_off_days", 3) or 3)
    fault = str(answers.get("fault_attribution", "mutual_or_unclear")).lower()

    # Factor 1: Respect for Stated Boundaries
    boundary_score = 92 if asked_for_space else 70

    # Factor 2: Emotional De-escalation & Cooling Off
    if conflict == "high":
        deescalate_score = 90 if cooling_days >= 2 else 55
    elif conflict == "medium":
        deescalate_score = 80
    else:
        deescalate_score = 65

    # Factor 3: Relationship Longevity & Core Value
    longevity_score = 86 if dependency in ["high", "medium"] else 75

    # Factor 4: Support System Health & Independence
    support_score = 82 if dependency == "high" else 68

    # Factor 5: Non-Defensive Communication Timing
    comm_score = 78 if cooling_days >= 2 else 52

    factors = [
        FactorScore(
            factor="boundary_respect",
            score=round(boundary_score),
            label="Respect for Stated Boundaries",
            description="Honoring his explicit request not to talk prevents further escalation and emotional pushback",
        ),
        FactorScore(
            factor="deescalation",
            score=round(deescalate_score),
            label="Emotional De-escalation Priority",
            description="Allowing heat and adrenaline from the fight to cool down before attempting any conversation",
        ),
        FactorScore(
            factor="relationship_longevity",
            score=round(longevity_score),
            label="Relationship Value & Longevity",
            description="Protecting the core friendship rather than forcing a rushed, panicked resolution",
        ),
        FactorScore(
            factor="support_system",
            score=round(support_score),
            label="Mitigation of Over-dependence",
            description="Addressing the vulnerability of having a single emotional anchor by broadening support",
        ),
        FactorScore(
            factor="communication_timing",
            score=round(comm_score),
            label="Non-Defensive Timing",
            description="Ensuring your eventual outreach is thoughtful, calm, and pressure-free",
        ),
    ]
    avg = sum(f.score for f in factors) / len(factors)
    return factors, round(avg)


BREED_PROFILES: Dict[str, Dict[str, Any]] = {
    "golden_retriever": {
        "name": "Golden Retriever",
        "type": "dog",
        "size": "Large (25–34 kg)",
        "ideal_space": "house_garden",
        "energy": "high",
        "grooming": "high",
        "min_budget": 4000,
        "temperament": "Extremely friendly, gentle, eager to please, family favorite",
        "pros": "Loving nature, gentle with children, highly trainable",
        "cons": "Heavy shedding, requires 1.5–2 hours daily exercise, challenging in small apartments without strict walking routine",
    },
    "labrador": {
        "name": "Labrador Retriever",
        "type": "dog",
        "size": "Large (27–36 kg)",
        "ideal_space": "house_garden",
        "energy": "high",
        "grooming": "medium",
        "min_budget": 3500,
        "temperament": "Outgoing, loyal, playful, enthusiastic companion",
        "pros": "Loyal, easy to train, patient with kids",
        "cons": "High energy in youth, requires frequent exercise, prone to obesity without active routines",
    },
    "german_shepherd": {
        "name": "German Shepherd",
        "type": "dog",
        "size": "Large (30–40 kg)",
        "ideal_space": "house_garden",
        "energy": "high",
        "grooming": "medium",
        "min_budget": 4500,
        "temperament": "Intelligent, protective, confident, highly trainable work dog",
        "pros": "Superb protection, highly loyal, excels in obedience",
        "cons": "Requires experienced handling, strict socialization, and continuous mental stimulation",
    },
    "beagle": {
        "name": "Beagle",
        "type": "dog",
        "size": "Medium (9–11 kg)",
        "ideal_space": "apartment_large",
        "energy": "medium",
        "grooming": "low",
        "min_budget": 3000,
        "temperament": "Curious, affectionate, playful, scent-driven",
        "pros": "Compact size, short easy-care coat, friendly personality",
        "cons": "Loud howling/baying if bored, stubborn when tracking scents",
    },
    "shih_tzu": {
        "name": "Shih Tzu",
        "type": "dog",
        "size": "Small (4–7 kg)",
        "ideal_space": "apartment_small",
        "energy": "low",
        "grooming": "high",
        "min_budget": 3000,
        "temperament": "Affectionate, happy, outgoing, relaxed lap dog",
        "pros": "Flourishes in small apartments, minimal barking, low outdoor exercise demand",
        "cons": "Requires daily coat brushing and professional grooming every 6–8 weeks",
    },
    "pug": {
        "name": "Pug",
        "type": "dog",
        "size": "Small (6–8 kg)",
        "ideal_space": "apartment_small",
        "energy": "low",
        "grooming": "low",
        "min_budget": 2500,
        "temperament": "Loving, comical, quiet, docile companion",
        "pros": "Ideal for small apartments and low-activity lifestyles, gentle with all ages",
        "cons": "Sensitive to Indian summer heat (brachycephalic breathing), heavy seasonal shedding",
    },
    "french_bulldog": {
        "name": "French Bulldog",
        "type": "dog",
        "size": "Small (9–13 kg)",
        "ideal_space": "apartment_small",
        "energy": "low",
        "grooming": "low",
        "min_budget": 4500,
        "temperament": "Quiet, friendly, alert, low-barking companion",
        "pros": "Rarely barks, thrives indoors, compact build",
        "cons": "High purchase price and vet care, sensitive to high heat",
    },
    "indie_desi": {
        "name": "Indian Pariah / Indie (Desi Dog)",
        "type": "dog",
        "size": "Medium (15–25 kg)",
        "ideal_space": "apartment_small",
        "energy": "medium",
        "grooming": "low",
        "min_budget": 1500,
        "temperament": "Exceptionally hardy, loyal, smart, naturally immune",
        "pros": "Naturally acclimated to Indian climate, virtually zero genetic diseases, low maintenance, noble rescue",
        "cons": "Needs early puppy socialization to curb territorial alertness",
    },
    "persian_cat": {
        "name": "Persian Cat",
        "type": "cat",
        "size": "Medium (3–5 kg)",
        "ideal_space": "apartment_small",
        "energy": "low",
        "grooming": "high",
        "min_budget": 2500,
        "temperament": "Quiet, sweet, gentle indoor cat",
        "pros": "Zero outdoor exercise needed, very quiet, peaceful companion",
        "cons": "Requires daily brushing to prevent matting and regular eye cleaning",
    },
    "domestic_shorthair": {
        "name": "Domestic Shorthair / Indie Cat",
        "type": "cat",
        "size": "Medium (3–5 kg)",
        "ideal_space": "apartment_small",
        "energy": "medium",
        "grooming": "low",
        "min_budget": 1200,
        "temperament": "Playful, independent, affectionate, resilient",
        "pros": "Low maintenance, robust health, easily adapts to any home size",
        "cons": "Independent spirit; needs scratch posts to protect furniture",
    },
    "siamese_cat": {
        "name": "Siamese Cat",
        "type": "cat",
        "size": "Medium (3–4.5 kg)",
        "ideal_space": "apartment_small",
        "energy": "high",
        "grooming": "low",
        "min_budget": 2500,
        "temperament": "Very vocal, social, curious, highly engaged",
        "pros": "Acts like a puppy, communicative and interactive companion",
        "cons": "Can become noisy or distressed if left alone for extended hours",
    },
}


def _find_best_matching_breed(living: str, activity: str, time_comm: str, monthly_budget: float, pet_type: str = "dog") -> Dict[str, Any]:
    """Select the best matching breed for user constraints."""
    target_type = "cat" if str(pet_type).lower() == "cat" else "dog"
    candidates = [b for b in BREED_PROFILES.values() if b["type"] == target_type]

    def score_candidate(b: Dict[str, Any]) -> float:
        s = 100.0
        # Space match
        if living == "apartment_small" and b["ideal_space"] == "house_garden":
            s -= 35
        elif living == "apartment_large" and b["ideal_space"] == "house_garden":
            s -= 15
        # Activity match
        if activity == "low" and b["energy"] == "high":
            s -= 30
        elif activity == "high" and b["energy"] == "high":
            s += 15
        # Time match
        if time_comm == "low" and b["grooming"] == "high":
            s -= 25
        # Budget match
        if monthly_budget > 0 and monthly_budget < b["min_budget"]:
            s -= 20
        return s

    candidates.sort(key=score_candidate, reverse=True)
    return candidates[0] if candidates else BREED_PROFILES["indie_desi"]


def score_pet(answers: Dict[str, Any]) -> Tuple[List[FactorScore], float]:
    """Score pet breed compatibility factors."""
    breed_key = answers.get("breed_choice", answers.get("selected_breed", "recommend"))
    living = str(answers.get("living_situation", "apartment_large")).lower()
    activity = str(answers.get("activity_level", "medium")).lower()
    time_comm = str(answers.get("time_commitment", "medium")).lower()
    monthly_budget = float(answers.get("budget", 0) or 0)
    pet_type = answers.get("pet_type", "dog")

    if breed_key and breed_key != "recommend" and breed_key in BREED_PROFILES:
        profile = BREED_PROFILES[breed_key]
    else:
        profile = _find_best_matching_breed(living, activity, time_comm, monthly_budget, pet_type)

    # 1. Space Compatibility Score
    if living == "apartment_small":
        if profile["ideal_space"] == "house_garden":
            space_score = 55
        elif profile["ideal_space"] == "apartment_large":
            space_score = 75
        else:
            space_score = 95
    elif living == "apartment_large":
        if profile["ideal_space"] == "house_garden":
            space_score = 70
        else:
            space_score = 90
    else:  # house with or without garden
        space_score = 95

    # 2. Activity / Exercise Match
    energy = profile.get("energy", "medium")
    if activity == "high":
        act_score = 95 if energy == "high" else 80
    elif activity == "medium":
        act_score = 88 if energy in ["medium", "low"] else 68
    else:  # low activity
        act_score = 92 if energy == "low" else (65 if energy == "medium" else 48)

    # 3. Care & Grooming Time Commitment
    grooming = profile.get("grooming", "medium")
    if time_comm == "high":
        time_score = 95
    elif time_comm == "medium":
        time_score = 85 if grooming != "high" else 72
    else:  # low time
        time_score = 88 if grooming == "low" else 50

    # 4. Monthly Maintenance & Vet Budget Fit
    min_b = profile.get("min_budget", 2500)
    if monthly_budget == 0:
        budget_score = 75
    elif monthly_budget >= min_b * 1.2:
        budget_score = 95
    elif monthly_budget >= min_b:
        budget_score = 85
    else:
        budget_score = max(40, round((monthly_budget / min_b) * 75))

    # 5. Temperament & Lifestyle Fit
    temp_score = round((space_score * 0.35) + (act_score * 0.35) + (time_score * 0.30))

    factors = [
        FactorScore(
            factor="space_fit",
            score=round(space_score),
            label="Living Space Compatibility",
            description=f"Alignment of {profile['name']}'s size and energy with your living space",
        ),
        FactorScore(
            factor="activity_fit",
            score=round(act_score),
            label="Exercise & Activity Match",
            description=f"Match between {profile['name']}'s daily exercise needs and your activity routine",
        ),
        FactorScore(
            factor="time_fit",
            score=round(time_score),
            label="Care & Grooming Commitment",
            description=f"Daily availability for grooming, exercise, and attention for a {profile['name']}",
        ),
        FactorScore(
            factor="budget_fit",
            score=round(budget_score),
            label="Maintenance Cost Fit",
            description=f"Estimated monthly upkeep (~Rs. {min_b:,}) vs your stated budget",
        ),
        FactorScore(
            factor="temperament_fit",
            score=round(temp_score),
            label="Temperament & Lifestyle Fit",
            description=f"How naturally {profile['name']}'s personality integrates into your household",
        ),
    ]
    avg = sum(f.score for f in factors) / len(factors)
    return factors, round(avg)


def score_health(answers: Dict[str, Any]) -> Tuple[List[FactorScore], float]:
    """Score health recovery, hydration, and nutritional safety factors."""
    condition = answers.get("condition", "diarrhea")
    duration = answers.get("duration", "under_24h")
    dehydration_risk = answers.get("dehydration_risk", "medium")
    has_red_flags = answers.get("red_flags", "no") == "yes"

    # 1. Hydration & Electrolyte Replacement (Crucial clinical priority)
    hydration_score = 98 if dehydration_risk == "high" else 92

    # 2. Digestive Rest & Low-Fibre Bland Diet (BRAT)
    digestive_score = 94

    # 3. Stool-Binding Capability (Pectin, Starches)
    binding_score = 90 if condition == "diarrhea" else 75

    # 4. Irritant Avoidance (Eliminating milk/dairy, chili, fried, coffee)
    irritant_score = 92

    # 5. Clinical Safety & Red Flag Screening
    safety_score = 60 if has_red_flags or duration == "over_3_days" else 90

    factors = [
        FactorScore(
            factor="hydration_priority",
            score=round(hydration_score),
            label="Hydration & Electrolyte Balance",
            description="Crucial priority: replacing fluids, potassium, and sodium lost through frequent bowel movements",
        ),
        FactorScore(
            factor="digestive_rest",
            score=round(digestive_score),
            label="Digestive Rest & Bland Diet",
            description="Resting inflamed gut mucosa with easily digestible, low-residue, non-irritating starches",
        ),
        FactorScore(
            factor="stool_binding",
            score=round(binding_score),
            label="Stool-Binding Capability",
            description="Utilizing soluble fibre (pectin from bananas/applesauce) and simple starches to firm stool",
        ),
        FactorScore(
            factor="irritant_avoidance",
            score=round(irritant_score),
            label="Irritant Avoidance",
            description="Strictly eliminating dairy/lactose, greasy fried foods, chili spices, and caffeine that trigger gut spasms",
        ),
        FactorScore(
            factor="medical_safety",
            score=round(safety_score),
            label="Clinical Safety & Monitoring",
            description="Evaluating red flag symptoms that require clinical diagnosis rather than home diet care",
        ),
    ]
    avg = sum(f.score for f in factors) / len(factors)
    return factors, round(avg)


def score_general(category: str, answers: Dict[str, Any]) -> Tuple[List[FactorScore], float]:
    """Generic scoring for any category."""
    budget = answers.get("budget", 0) or 0
    requirements = answers.get("requirements", [])
    if isinstance(requirements, str):
        requirements = [requirements]
    pref_count = len(requirements)

    budget_score = 70 if budget == 0 else min(95, 60 + (budget / 10000))
    req_score = min(90, 50 + pref_count * 10)
    completeness = min(85, 40 + len([v for v in answers.values() if v]) * 8)

    factors = [
        FactorScore(factor="requirement_match", score=round(req_score), label="Requirement Match",
                    description="How well the options match your stated requirements"),
        FactorScore(factor="budget_match", score=round(min(budget_score, 100)), label="Budget Fit",
                    description="Price compatibility with your budget"),
        FactorScore(factor="preference_match", score=round(completeness), label="Preference Alignment",
                    description="Match with your stated preferences and priorities"),
        FactorScore(factor="feasibility", score=75, label="Practical Feasibility",
                    description="Real-world practicality of the recommendation"),
    ]
    avg = sum(f.score for f in factors) / len(factors)
    return factors, round(avg)


# ─── Confidence ────────────────────────────────────────────────────────────────

def compute_confidence(avg_score: float, answers: Dict[str, Any]) -> Tuple[float, str, str]:
    """Compute confidence band and explanation."""
    filled = sum(1 for v in answers.values() if v is not None and v != "" and v != 0)
    total = max(len(answers), 1)
    completeness_ratio = filled / total

    confidence = avg_score * (0.5 + 0.5 * completeness_ratio)
    confidence = round(min(confidence, 99), 1)

    if confidence >= 80:
        band = "HIGH"
        explanation = (
            "The recommendation is strongly supported because your requirements are "
            "clearly specified and consistently aligned with the scoring signals."
        )
    elif confidence >= 60:
        band = "MEDIUM"
        explanation = (
            "The recommendation has moderate confidence. Some requirements were not "
            "fully specified, which limits certainty. Consider providing more details "
            "for a more tailored recommendation."
        )
    else:
        band = "LOW"
        explanation = (
            "Confidence is low because important information is missing or the requirements "
            "are ambiguous. The recommendation is a best-guess given available information. "
            "Providing more detail will significantly improve accuracy."
        )
    return confidence, band, explanation


# ─── Recommendation Generation ────────────────────────────────────────────────

def generate_laptop_recommendation(answers: Dict[str, Any]) -> Dict[str, Any]:
    budget = float(answers.get("budget", 0) or 0)
    gaming = str(answers.get("gaming_requirement", "no")).lower() in ["yes", "true", "1"]
    ai_ml = str(answers.get("ai_ml_requirement", "no")).lower() in ["yes", "true", "1"]
    portability = str(answers.get("portability", "medium")).lower()
    usage = str(answers.get("usage", "general")).lower()

    rec_name = "Mid-range programming laptop"
    specific = None

    if budget > 0:
        if gaming and budget >= 100000:
            rec_name = "High-performance gaming laptop (RTX 4060 class)"
            specific = "ASUS ROG Strix G15 (RTX 4060)"
        elif gaming and budget >= 60000:
            rec_name = "Gaming laptop with dedicated GPU (RTX 3050 class)"
            specific = "HP Pavilion Gaming 15 (RTX 3050)"
        elif portability == "high" and budget >= 100000:
            rec_name = "Premium ultrabook"
            specific = "Dell XPS 13 or MacBook Air M2"
        elif ai_ml and budget >= 100000:
            rec_name = "High-performance laptop for AI/ML workloads"
            specific = "ASUS ROG Strix G15 (RTX 4060)"
        elif budget <= 35000:
            rec_name = "Budget laptop for everyday use"
            specific = "Acer Aspire 5 (AMD Ryzen 3)"
        elif budget <= 50000:
            rec_name = "Budget-friendly student laptop"
            specific = "Lenovo IdeaPad Slim 3"
        elif budget <= 65000:
            rec_name = "Mid-range laptop for programming"
            specific = "ASUS VivoBook 15 (Intel i5 12th Gen)"
        else:
            rec_name = "Professional-grade laptop"
            specific = "Dell XPS 13 or HP Envy"
    else:
        rec_name = "Mid-range laptop (₹50,000–₹70,000 range recommended for most users)"

    if specific:
        rec_name = f"{specific} — {rec_name}"
    return {"recommendation": rec_name, "category": "laptop"}


def generate_company_bulk_recommendation(answers: Dict[str, Any]) -> Dict[str, Any]:
    budget = float(answers.get("total_budget", 0) or 0)
    quantity = int(answers.get("quantity", 1) or 1)
    product_cat = str(answers.get("product_category", "laptop")).lower()
    perf_req = str(answers.get("performance_requirements", "medium")).lower()

    unit_budget = budget / max(quantity, 1)

    if product_cat in ["laptop", "computer", "notebook"]:
        if perf_req == "high" and unit_budget >= 80000:
            rec = "Dell Latitude / HP EliteBook — Business-class laptops with enterprise warranty"
        elif unit_budget >= 55000:
            rec = "Lenovo ThinkPad E-series or HP ProBook — Mid-range business laptops"
        elif unit_budget >= 40000:
            rec = "HP Pavilion / Lenovo IdeaPad — Value business laptops"
        else:
            rec = "Acer Aspire / Lenovo IdeaPad — Budget business laptops"
    else:
        rec = f"Business-grade {product_cat} — procurement recommended through authorized distributor"

    # Estimated costs
    estimated_unit = unit_budget * 0.9 if unit_budget > 0 else 50000
    estimated_total = estimated_unit * quantity
    remaining = budget - estimated_total if budget > 0 else 0

    summary = {
        "quantity": quantity,
        "product_category": product_cat,
        "estimated_unit_price": f"₹{estimated_unit:,.0f} (est.)",
        "estimated_total": f"₹{estimated_total:,.0f} (est.)",
        "total_budget": f"₹{budget:,.0f}" if budget > 0 else "Not specified",
        "remaining_budget": f"₹{max(remaining, 0):,.0f} (est.)" if budget > 0 else "N/A",
        "note": "All prices are estimates. Actual prices will vary by vendor and negotiation.",
    }
    return {"recommendation": rec, "category": "company_bulk", "bulk_summary": summary}


def generate_relationship_recommendation(answers: Dict[str, Any], query: str = "") -> Dict[str, Any]:
    asked_for_space = str(answers.get("asked_for_space", answers.get("boundary_requested", "no"))).lower() in ["yes", "true", "1"]
    dependency = str(answers.get("emotional_dependency", "medium")).lower()
    conflict = str(answers.get("conflict_intensity", "high")).lower()
    cooling_days = int(answers.get("cooling_off_days", 3) or 3)
    fault = str(answers.get("fault_attribution", "mutual_or_unclear")).lower()

    if asked_for_space:
        if dependency == "high":
            rec = (
                f"Observe a {cooling_days}–5 day cooling-off period to honor his explicit boundary, followed by a concise, "
                "pressure-free reconciliation text — while immediately taking steps to broaden your emotional support network."
            )
        else:
            rec = (
                f"Respect his boundary with a {cooling_days}–4 day cooling-off period, then reach out with a sincere, "
                "calm message leaving the door open without demanding an immediate reply."
            )
    else:
        if fault == "mostly_mine":
            rec = (
                "Send a brief, sincere apology taking direct ownership of your mistake without excuses or defensiveness, "
                "and give him time to absorb it."
            )
        else:
            rec = (
                "Suggest an informal, calm conversation in a neutral setting to clear the air, share how much you value him, "
                "and listen openly to his perspective."
            )

    return {"recommendation": rec, "category": "relationship"}


def generate_pet_recommendation(answers: Dict[str, Any], query: str = "") -> Dict[str, Any]:
    """Generate breed-specific recommendation for pet category."""
    breed_key = answers.get("breed_choice", answers.get("selected_breed", "recommend"))
    living = str(answers.get("living_situation", "apartment_large")).lower()
    activity = str(answers.get("activity_level", "medium")).lower()
    time_comm = str(answers.get("time_commitment", "medium")).lower()
    monthly_budget = float(answers.get("budget", 0) or 0)
    pet_type = answers.get("pet_type", "dog")

    if breed_key and breed_key != "recommend" and breed_key in BREED_PROFILES:
        profile = BREED_PROFILES[breed_key]
        factors, avg_score = score_pet(answers)
        fit_label = (
            "Excellent Match" if avg_score >= 80
            else ("Moderate Fit with Considerations" if avg_score >= 65 else "Challenging Lifestyle Fit")
        )

        rec = (
            f"Selected Breed Analysis: {profile['name']} ({profile['size']}) — {fit_label}. "
            f"Known for being {profile['temperament'].lower()}. "
            f"Strengths: {profile['pros']}. "
            f"Lifestyle Note: {profile['cons']}."
        )
    else:
        profile = _find_best_matching_breed(living, activity, time_comm, monthly_budget, pet_type)
        rec = (
            f"Recommended Breed: {profile['name']} ({profile['size']}) — Ideal Companion for Your Lifestyle. "
            f"Known for being {profile['temperament'].lower()}. "
            f"Key Advantages: {profile['pros']}. "
            f"Care Requirement: {profile['cons']}."
        )

    return {"recommendation": rec, "category": "pet"}


def generate_health_recommendation(answers: Dict[str, Any], query: str = "") -> Dict[str, Any]:
    """Generate clinical nutrition & recovery guidance for acute health symptoms."""
    condition = answers.get("condition", "diarrhea")
    has_red_flags = answers.get("red_flags", "no") == "yes"
    duration = answers.get("duration", "under_24h")

    if has_red_flags or duration == "over_3_days":
        rec = (
            "Medical Evaluation Recommended: Please consult a physician promptly. "
            "For immediate home care: Sip Oral Rehydration Salts (ORS) continuously to avoid dehydration. "
            "Do NOT take self-prescribed anti-motility drugs (e.g. Loperamide) if fever or severe pain is present."
        )
    elif condition == "diarrhea":
        rec = (
            "Adopt the BRAT Diet Protocol (Bananas, White Rice, Applesauce, Plain Toast) paired with continuous Oral Rehydration Solution (ORS). "
            "Take frequent, small sips of coconut water, salted rice congee (kanji), or clear broths. "
            "Strictly avoid: Milk/dairy, spicy seasonings, oily/fried foods, caffeine, and artificial sweeteners for 3–5 days."
        )
    elif condition == "nausea_vomiting":
        rec = (
            "Allow the stomach to settle with 1–2 hours of gut rest, then take tiny ice chips or cold electrolyte sips. "
            "Gradually introduce plain saltine crackers, boiled potato, and ginger tea once fluid is tolerated."
        )
    elif condition == "acidity":
        rec = (
            "Eat small, non-acidic meals: Oatmeal, ripe bananas, boiled vegetables, and cold milk/almond milk. "
            "Avoid citrus fruits, tomatoes, fried snacks, coffee, and lying down within 3 hours after eating."
        )
    else:
        rec = (
            "Follow a gentle restorative diet: Sip warm electrolyte broths, eat small portions of steamed rice or dry toast, "
            "and rest your digestive system while monitoring symptoms."
        )

    return {"recommendation": rec, "category": "health"}


def generate_general_recommendation(category: str, answers: Dict[str, Any], query: str = "") -> Dict[str, Any]:
    recs = {
        "fish_aquarium": "Start with a 40–75 litre freshwater tank with beginner-friendly fish such as Neon Tetras or Guppies",
        "education": "Evaluate course accreditation, placement record, and skill alignment with your career goal before enrolling.",
        "career": "Conduct a structured self-assessment of skills, interests, market demand, and financial runway before switching.",
        "travel": "Plan 2–4 months ahead for international travel. Compare transport costs, accommodation, and visa requirements.",
        "home": "Evaluate total cost of ownership (purchase + installation + maintenance) and energy efficiency ratings.",
        "vehicle": "Compare EMI affordability, fuel/running cost, insurance, and resale value. Test-drive before deciding.",
        "personal": "Prioritize emotional self-regulation, respect clear personal boundaries, and build a balanced support circle.",
        "general": "Based on your stated requirements, evaluate options systematically against your primary criteria.",
    }
    rec = recs.get(category, f"Based on your requirements, a careful evaluation across the key decision factors is recommended.")
    return {"recommendation": rec, "category": category}


# ─── Main Engine ──────────────────────────────────────────────────────────────

def run_decision_engine(category: str, answers: Dict[str, Any], query: str = "") -> DecisionResult:
    """Main decision engine. Returns a full DecisionResult."""
    from explainability import generate_explanation
    from impact import generate_impact

    cat = category.lower().strip()

    # Score
    if cat == "laptop":
        factors, avg_score = score_laptop(answers)
        rec_data = generate_laptop_recommendation(answers)
    elif cat == "company_bulk":
        factors, avg_score = score_company_bulk(answers)
        rec_data = generate_company_bulk_recommendation(answers)
    elif cat in ["relationship", "personal"]:
        factors, avg_score = score_relationship(answers)
        rec_data = generate_relationship_recommendation(answers, query)
    elif cat == "pet":
        factors, avg_score = score_pet(answers)
        rec_data = generate_pet_recommendation(answers, query)
    elif cat == "health":
        factors, avg_score = score_health(answers)
        rec_data = generate_health_recommendation(answers, query)
    else:
        factors, avg_score = score_general(cat, answers)
        rec_data = generate_general_recommendation(cat, answers, query)

    recommendation = rec_data["recommendation"]
    bulk_summary = rec_data.get("bulk_summary")

    # Confidence
    confidence, conf_band, conf_explanation = compute_confidence(avg_score, answers)

    # Explanation
    explanation = generate_explanation(factors, recommendation, cat, answers)

    # Impact
    impact = generate_impact(cat, recommendation, answers, rec_data.get("bulk_summary"))

    # Alternatives
    alternatives = _generate_alternatives(cat, answers, avg_score)

    # Products
    budget = answers.get("budget") or answers.get("total_budget") or 0
    try:
        budget = float(budget)
    except (TypeError, ValueError):
        budget = 0
    quantity = answers.get("quantity", 1) or 1
    products = _generate_product_cards(cat, answers, budget, quantity)

    # Quantity
    qty = answers.get("quantity", 1)

    # Follow-up questions for low confidence
    follow_up = []
    if confidence < 60:
        follow_up = _generate_follow_up_questions(cat, answers)

    return DecisionResult(
        recommendation=recommendation,
        confidence=confidence,
        confidence_band=conf_band,
        confidence_explanation=conf_explanation,
        factors=factors,
        explanation=explanation,
        impact=impact,
        alternatives=alternatives,
        products=products,
        nearby_available=cat in ["pet", "fish_aquarium", "laptop", "smartphone", "office_equipment", "relationship", "personal", "health"],
        nearby_message=(
            "Discover local 24/7 pharmacies, medical clinics, and hospitals."
            if cat == "health"
            else (
                "Discover local counseling centers, community support groups, and social meetup clubs."
                if cat in ["relationship", "personal"]
                else "Use the 'Find Nearby' feature to discover local shops."
            )
        ),
        category=cat,
        quantity=int(qty) if qty else 1,
        bulk_summary=bulk_summary,
        follow_up_questions=follow_up,
    )


def _generate_alternatives(category: str, answers: Dict[str, Any], base_score: float) -> List[AlternativeOption]:
    """Generate alternative recommendations."""
    cat = category.lower()

    if cat == "laptop":
        budget = float(answers.get("budget", 0) or 0)
        gaming = str(answers.get("gaming_requirement", "no")).lower() in ["yes", "true", "1"]
        return [
            AlternativeOption(
                name="Higher-budget option with better performance",
                score=round(min(base_score + 8, 99)),
                key_advantage="Significantly better performance and future-proofing",
                key_tradeoff="Higher upfront cost",
                estimated_price=f"₹{int(budget * 1.3):,} (est.)" if budget > 0 else "₹15,000–₹30,000 more",
            ),
            AlternativeOption(
                name="Lower-budget option for basic needs",
                score=round(max(base_score - 10, 40)),
                key_advantage="Lower cost, sufficient for basic tasks",
                key_tradeoff="Less RAM, slower processor, may feel limiting in 2–3 years",
                estimated_price=f"₹{int(budget * 0.7):,} (est.)" if budget > 0 else "₹10,000–₹20,000 less",
            ),
            AlternativeOption(
                name="Refurbished/certified pre-owned model",
                score=round(max(base_score - 5, 50)),
                key_advantage="Same performance at 20–30% lower price",
                key_tradeoff="Limited warranty, cosmetic wear, shorter product life",
                estimated_price="20–30% below new retail (est.)",
            ),
        ]
    elif cat == "company_bulk":
        quantity = int(answers.get("quantity", 1) or 1)
        budget = float(answers.get("total_budget", 0) or 0)
        return [
            AlternativeOption(
                name="Lease/rental model instead of purchase",
                score=round(base_score - 5),
                key_advantage="Lower upfront cost, easier upgrades, included maintenance",
                key_tradeoff="Higher long-term cost if retained >3 years",
                estimated_price="~20–30% of purchase price per year (est.)",
            ),
            AlternativeOption(
                name="Split-tier purchasing (mixed spec)",
                score=round(base_score + 3),
                key_advantage="Right-sized cost — higher spec only for power users",
                key_tradeoff="More complex procurement and support",
                estimated_price=f"Potentially ₹{int(budget * 0.85 / max(quantity, 1)):,}/unit avg (est.)" if budget > 0 else "Varies",
            ),
            AlternativeOption(
                name="Refurbished business-grade fleet",
                score=round(base_score - 12),
                key_advantage="30–40% cost saving, certified quality",
                key_tradeoff="Shorter lifecycle, limited warranty, no latest features",
                estimated_price="30–40% below new (est.)",
            ),
        ]
    elif cat in ["relationship", "personal"]:
        return [
            AlternativeOption(
                name="Patient De-escalation (Wait 48–72h, then send a warm, zero-pressure door-opener)",
                score=round(min(base_score + 5, 95)),
                key_advantage="Honors his boundary, lowers emotional defenses, and maximizes probability of genuine reconciliation",
                key_tradeoff="Requires managing your acute anxiety and loneliness during the waiting period",
                estimated_price="Emotional patience required (Zero financial cost)",
            ),
            AlternativeOption(
                name="Single Immediate Accountability Note (One calm text acknowledging his boundary, then radio silence)",
                score=round(max(base_score - 8, 55)),
                key_advantage="Lets him know immediately that you care and respect his space before silence sets in",
                key_tradeoff="Risk that sending any message immediately might still irritate him if emotions are at peak boiling point",
                estimated_price="Zero cost",
            ),
            AlternativeOption(
                name="Focus on Self-Grounding & Support Diversification (Shift focus outward for 7–10 days)",
                score=round(max(base_score - 3, 60)),
                key_advantage="Directly cures the single-point-of-failure vulnerability ('he is all I have') and restores your self-worth",
                key_tradeoff="Friendship repair is delayed until you achieve emotional stability",
                estimated_price="Community / hobby involvement",
            ),
        ]
    elif cat == "pet":
        breed_key = answers.get("breed_choice", answers.get("selected_breed", "recommend"))
        if breed_key == "golden_retriever":
            return [
                AlternativeOption(
                    name="Indian Pariah / Indie (Desi Dog) — Highly Resilient",
                    score=round(min(base_score + 8, 96)),
                    key_advantage="Naturally adapted to Indian climate, zero genetic health issues, substantially lower vet and grooming expenses",
                    key_tradeoff="Requires active puppy socialization",
                    estimated_price="Adoption fee: ₹0 / Monthly: ~₹1,500",
                ),
                AlternativeOption(
                    name="Beagle — Compact Hound Companion",
                    score=round(base_score + 3),
                    key_advantage="Medium compact build, deeply affectionate with families, significantly easier to manage in flats",
                    key_tradeoff="Scent-driven hound; needs on-leash walking",
                    estimated_price="Monthly upkeep: ~₹3,000",
                ),
                AlternativeOption(
                    name="Shih Tzu — Low Exercise Apartment Dog",
                    score=round(base_score - 2),
                    key_advantage="Thrives in smaller apartments, rarely barks, very gentle outdoor exercise demand",
                    key_tradeoff="Requires daily coat brushing and professional grooming every 6–8 weeks",
                    estimated_price="Monthly upkeep: ~₹3,000",
                ),
            ]
        elif breed_key == "labrador":
            return [
                AlternativeOption(
                    name="Golden Retriever — Similar Family Temperament",
                    score=round(base_score),
                    key_advantage="Wonderfully gentle with children, highly receptive to positive reinforcement",
                    key_tradeoff="Heavier seasonal coat shedding than Labradors",
                    estimated_price="Monthly upkeep: ~₹4,000",
                ),
                AlternativeOption(
                    name="Indian Pariah / Indie — Robust & Climate-Resilient",
                    score=round(min(base_score + 6, 95)),
                    key_advantage="Remarkably hardy, high natural immunity, minimal grooming needs",
                    key_tradeoff="May be alert and protective of home boundaries",
                    estimated_price="Adoption: ₹0 / Monthly: ~₹1,500",
                ),
                AlternativeOption(
                    name="Beagle — Smaller Footprint",
                    score=round(base_score + 2),
                    key_advantage="More manageable size for suburban and apartment living",
                    key_tradeoff="Vocal baying if left unexercised",
                    estimated_price="Monthly upkeep: ~₹3,000",
                ),
            ]
        else:
            return [
                AlternativeOption(
                    name="Indian Pariah / Indie (Desi Rescue Dog)",
                    score=round(min(base_score + 5, 95)),
                    key_advantage="Low maintenance, naturally adapted to local weather, high resistance to common diseases",
                    key_tradeoff="Requires early socialization",
                    estimated_price="Free adoption / ~₹1,500 monthly",
                ),
                AlternativeOption(
                    name="Shih Tzu or Pug (Compact Companion)",
                    score=round(base_score),
                    key_advantage="Thrives in flats, calm demeanor, ideal for moderate or low activity owners",
                    key_tradeoff="Special care needed in summer heat (Pugs) or coat care (Shih Tzus)",
                    estimated_price="Monthly: ~₹2,500–₹3,000",
                ),
                AlternativeOption(
                    name="Domestic Shorthair Cat (Low Maintenance Alternative)",
                    score=round(base_score + 4),
                    key_advantage="Self-grooming, litter-box trained, zero daily walking requirement",
                    key_tradeoff="Independent nature; needs indoor scratching furniture",
                    estimated_price="Monthly: ~₹1,200",
                ),
            ]
    elif cat == "health":
        return [
            AlternativeOption(
                name="BRAT Protocol + ORS Rehydration (Clinical Standard Home Care)",
                score=round(min(base_score + 5, 96)),
                key_advantage="Clinically proven to firm stool, replace vital potassium/sodium, and avoid gut irritation",
                key_tradeoff="Bland taste; limited nutritional diversity during the initial 24–48 hours",
                estimated_price="Under ₹100 (Bananas, rice, bread, ORS)",
            ),
            AlternativeOption(
                name="Liquid-Only Fasting & Electrolyte Loading (First 6–12 Hours)",
                score=round(base_score - 2),
                key_advantage="Provides complete mechanical rest to inflamed intestinal walls",
                key_tradeoff="Prolonged fasting (>12h) can weaken intestinal enterocytes; solid food should be phased in soon",
                estimated_price="ORS & coconut water: ~₹50",
            ),
            AlternativeOption(
                name="Immediate Clinical Outpatient Consultation / Stool Test",
                score=round(max(base_score - 6, 65)),
                key_advantage="Pinpoints bacterial vs viral etiology; allows targeted prescription if fever or severe cramps develop",
                key_tradeoff="Requires clinic visit and consultation fee",
                estimated_price="Clinic consultation: ₹300–₹800",
            ),
        ]
    else:
        return [
            AlternativeOption(
                name="Conservative / lower-risk option",
                score=round(max(base_score - 8, 40)),
                key_advantage="Lower risk, easier to reverse",
                key_tradeoff="Potentially lower upside",
            ),
            AlternativeOption(
                name="Premium / higher-investment option",
                score=round(min(base_score + 5, 95)),
                key_advantage="Better quality, longer lifespan, more features",
                key_tradeoff="Higher initial investment required",
            ),
            AlternativeOption(
                name="Gradual / phased approach",
                score=round(base_score),
                key_advantage="Spread cost, learn as you go, lower commitment",
                key_tradeoff="Slower progress, may cost more over time",
            ),
        ]


def _generate_product_cards(category: str, answers: Dict[str, Any], budget: float, quantity: int) -> List[ProductCard]:
    """Generate product cards from demo catalog."""
    from product_catalog import get_products_for_category
    products = get_products_for_category(category, budget if budget > 0 else None, quantity)
    cards = []
    for p in products[:5]:  # Top 5
        # Compute match percentage
        match = _compute_product_match(p, answers, category)
        why = _generate_why_match(p, answers, category, match)
        tradeoffs = _generate_product_tradeoffs(p, category)
        cards.append(ProductCard(
            id=p["id"],
            name=p["name"],
            price=p.get("price"),
            rating=p.get("rating"),
            specs=p.get("specs", {}),
            match_pct=match,
            why_match=why,
            trade_offs=tradeoffs,
            demo_data=True,
        ))
    # Sort by match
    cards.sort(key=lambda c: c.match_pct, reverse=True)
    return cards


def _compute_product_match(product: Dict[str, Any], answers: Dict[str, Any], category: str) -> float:
    """Compute a match percentage for a product."""
    score = 60.0  # Base
    cat = category.lower()

    if cat == "laptop":
        budget = float(answers.get("budget", 0) or 0)
        gaming = str(answers.get("gaming_requirement", "no")).lower() in ["yes", "true", "1"]
        ai_ml = str(answers.get("ai_ml_requirement", "no")).lower() in ["yes", "true", "1"]
        portability = str(answers.get("portability", "medium")).lower()

        price = product.get("price_num", 0)
        if budget > 0 and price > 0:
            if price <= budget:
                score += 15
            elif price <= budget * 1.1:
                score += 5
            else:
                score -= 20

        if gaming and product.get("gaming", 0) >= 3:
            score += 15
        elif gaming and product.get("gaming", 0) < 2:
            score -= 10

        if ai_ml and product.get("ai_ml", 0) >= 3:
            score += 10
        if portability == "high" and product.get("portability", 3) >= 4:
            score += 10
        elif portability == "high" and product.get("portability", 3) <= 2:
            score -= 10

    return round(min(max(score, 0), 100), 1)


def _generate_why_match(product: Dict[str, Any], answers: Dict[str, Any], category: str, match: float) -> str:
    reasons = []
    if match >= 80:
        reasons.append("Strongly aligns with your requirements")
    elif match >= 65:
        reasons.append("Good overall match for your stated needs")
    else:
        reasons.append("Partial match — consider alternatives")

    budget = float(answers.get("budget", 0) or 0)
    price = product.get("price_num", 0)
    if budget > 0 and price > 0 and price <= budget:
        reasons.append("fits within your budget")
    if product.get("gaming", 0) >= 3 and str(answers.get("gaming_requirement", "no")).lower() in ["yes", "true"]:
        reasons.append("has dedicated gaming GPU")
    if product.get("portability", 3) >= 4:
        reasons.append("is highly portable")

    return "; ".join(reasons).capitalize() + "."


def _generate_product_tradeoffs(product: Dict[str, Any], category: str) -> List[str]:
    tradeoffs = []
    if category == "laptop":
        if product.get("gaming", 0) >= 3:
            tradeoffs.append("Heavier than ultrabooks; limited battery life under gaming load")
        if product.get("portability", 3) >= 4:
            tradeoffs.append("Compact screen may feel small for extended sessions")
        if product.get("performance_tier", 3) <= 2:
            tradeoffs.append("May struggle with heavy multitasking or demanding applications in 2–3 years")
    return tradeoffs or ["Review full spec sheet before purchasing"]


def _generate_follow_up_questions(category: str, answers: Dict[str, Any]) -> List[str]:
    """Generate follow-up questions to improve confidence."""
    questions_map = {
        "laptop": [
            "What is your approximate budget (in ₹)?",
            "What will be your primary use? (e.g., programming, gaming, office work)",
            "Do you prefer Windows, macOS, or Linux?",
            "How important is portability?",
        ],
        "company_bulk": [
            "How many units are required?",
            "What is the total budget?",
            "What will employees primarily use these devices for?",
            "Is a business warranty important?",
        ],
        "relationship": [
            "Did your friend give a specific reason for being upset?",
            "How long ago did the fight occur?",
            "Do you have other friends, family, or someone to talk to right now?",
        ],
        "personal": [
            "What is the main challenge you are facing right now?",
            "What outcome would make you feel most at peace?",
            "Who can support you during this time?",
        ],
        "pet": [
            "What type of home do you live in? (e.g. small apartment, house with yard)",
            "How much daily time can you dedicate to walking and grooming?",
            "Do you have a specific breed in mind or want a recommendation?",
        ],
        "health": [
            "How many days have you been experiencing these digestive symptoms?",
            "Are you able to keep oral fluids down without vomiting?",
            "Do you have any high fever (>102°F / 38.9°C), blood in stool, or severe sharp abdominal pain?",
        ],
        "general": [
            "What is your budget or financial constraint?",
            "What are your top 3 requirements or priorities?",
            "What is your timeline for this decision?",
        ],
    }
    return questions_map.get(category, questions_map["general"])[:3]


def analyze_free_text(query: str) -> DecisionResult:
    """Parse free text and run decision engine."""
    category = detect_category(query)
    budget = extract_budget(query)
    quantity = extract_quantity(query)
    requirements = extract_requirements(query)

    answers: Dict[str, Any] = {
        "query": query,
        "requirements": requirements,
    }
    if budget:
        answers["budget"] = budget
        answers["total_budget"] = budget
    if quantity:
        answers["quantity"] = quantity

    # Extract specific requirements for laptop
    if category == "laptop":
        if any(k in query.lower() for k in ["gaming", "game"]):
            answers["gaming_requirement"] = "yes"
        if any(k in query.lower() for k in ["ai", "ml", "machine learning", "deep learning"]):
            answers["ai_ml_requirement"] = "yes"
        if any(k in query.lower() for k in ["portable", "lightweight", "travel", "slim"]):
            answers["portability"] = "high"
        if any(k in query.lower() for k in ["programming", "coding", "developer", "python", "cse"]):
            answers["usage"] = "programming"

    if category == "company_bulk" and quantity:
        answers["quantity"] = quantity

    # Extract specific entities for relationship and personal
    if category in ["relationship", "personal"]:
        rel_entities = extract_relationship_entities(query)
        answers.update(rel_entities)

    # Extract specific entities for pet
    if category == "pet":
        pet_entities = extract_pet_entities(query)
        answers.update(pet_entities)

    # Extract specific entities for health
    if category == "health":
        health_entities = extract_health_entities(query)
        answers.update(health_entities)

    return run_decision_engine(category, answers, query)
