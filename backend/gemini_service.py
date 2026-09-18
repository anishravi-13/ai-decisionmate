"""
gemini_service.py – Full Google Gemini Generative AI Integration for AI DecisionMate.
Powers both Free-Text ("Ask AI") and Guided Questionnaires with ultra-clear explainable analytics.
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List
import httpx

from config import settings
from schemas import DecisionResult, FactorScore, ImpactAnalysis, AlternativeOption, ProductCard

logger = logging.getLogger(__name__)

GEMINI_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-2.5-pro",
]

def get_active_gemini_key(user_key: Optional[str] = None) -> Optional[str]:
    """Retrieve Gemini API key from parameter, settings, or environment."""
    if user_key and user_key.strip():
        return user_key.strip()
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
        return settings.GEMINI_API_KEY.strip()
    env_key = os.getenv("GEMINI_API_KEY", "")
    if env_key.strip():
        return env_key.strip()
    return None


SYSTEM_PROMPT = """You are AI DecisionMate, an advanced Explainable AI Decision Support System (EDSS).
Your goal is to guide users to make high-confidence, real-world decisions by providing crystal-clear, structured analytics.

COMMUNICATION PRINCIPLES:
1. MAXIMUM CLARITY: Speak in plain, warm, and highly actionable English. Explain technical or complex ideas so any beginner immediately understands them.
2. CONCRETE SPECIFICS: Never give generic advice. Provide exact model recommendations, concrete steps, dietary rules, scripts for conversations, or financial benchmarks.
3. EXPLAINABILITY: Every factor score (0-100) must have a clear 1-2 sentence description explaining what it means and why this score was assigned.
4. ACTIONABLE IMPACT: Provide immediate next steps (what to do right now), honest trade-offs, financial/time costs, and long-term trajectory.

Always return ONLY a valid JSON object matching the requested schema. No markdown formatting around the outer output, no conversational preambles.
"""

def _call_gemini_json(prompt: str, key: str) -> Optional[Dict[str, Any]]:
    """Helper to query Gemini models with automatic fallback across supported versions."""
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{SYSTEM_PROMPT}\n\n{prompt}"}]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.3,
            "maxOutputTokens": 2048,
        }
    }

    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        try:
            with httpx.Client(timeout=25.0) as client:
                res = client.post(url, json=payload, headers={"Content-Type": "application/json"})
                if res.status_code == 200:
                    resp_json = res.json()
                    candidates = resp_json.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            raw_text = parts[0].get("text", "")
                            cleaned = raw_text.strip()
                            if cleaned.startswith("```json"):
                                cleaned = cleaned[7:]
                            elif cleaned.startswith("```"):
                                cleaned = cleaned[3:]
                            if cleaned.endswith("```"):
                                cleaned = cleaned[:-3]
                            return json.loads(cleaned.strip())
                else:
                    logger.warning(f"Gemini model {model} returned HTTP {res.status_code}: {res.text[:150]}")
        except Exception as e:
            logger.warning(f"Gemini model {model} attempt failed: {e}")

    return None


def analyze_with_gemini(
    query: str,
    api_key: Optional[str] = None,
    location: Optional[str] = None,
) -> Optional[DecisionResult]:
    """Analyze open-ended free text questions with Gemini AI."""
    key = get_active_gemini_key(api_key)
    if not key:
        return None

    prompt = f"""User Decision Query: "{query}"
User Location: "{location or 'Not specified'}"

Please synthesize the definitive Explainable Decision Support System (EDSS) guidance for this query.
Make the recommendation exceptionally clear, practical, structured, and easy for the user to understand.

Output JSON with this schema:
{{
  "category": "Clear category (e.g. Career & Education, Health & Nutrition, Relationships, Tech, Finance, Life Decision)",
  "recommendation": "Direct, empathetic, and actionable recommendation with specific next steps.",
  "confidence": 92.0,
  "confidence_band": "HIGH",
  "confidence_explanation": "Plain English rationale of why this confidence level was assigned.",
  "factors": [
    {{
      "factor": "snake_case_key",
      "score": 90.0,
      "label": "Easy to Understand Factor Label",
      "description": "Clear 1-2 sentence explanation of what this measures and why this score was awarded."
    }}
  ],
  "explanation": "A structured 2-3 paragraph plain-English explanation breaking down the rationale and trade-offs.",
  "impact": {{
    "immediate": ["Specific action for today", "Second immediate step"],
    "cost_impact": ["Clear estimate of financial, time, or emotional cost"],
    "long_term": ["Expected outcome 6-18 months out"],
    "trade_offs": ["What is sacrificed or compromised with this choice"],
    "risks": ["Key vulnerabilities to watch and mitigate"],
    "maintenance": ["Ongoing habit or review frequency needed"]
  }},
  "alternatives": [
    {{
      "name": "Alternative Option Name",
      "score": 75.0,
      "key_advantage": "Main advantage",
      "key_tradeoff": "Main trade-off",
      "estimated_price": "Cost or effort"
    }}
  ],
  "follow_up_questions": [
    "Clarifying question 1",
    "Clarifying question 2",
    "Clarifying question 3"
  ],
  "nearby_available": false,
  "nearby_message": null
}}
"""
    data = _call_gemini_json(prompt, key)
    if not data:
        return None

    return _build_decision_result(data, query, "general")


def analyze_guided_with_gemini(
    category: str,
    answers: Dict[str, Any],
    location: Optional[str] = None,
) -> Optional[DecisionResult]:
    """Analyze structured guided questionnaire answers with Gemini AI."""
    key = get_active_gemini_key()
    if not key:
        return None

    cat_title = category.replace("_", " ").title()

    # Format user questionnaire answers cleanly
    formatted_answers = []
    for k, v in answers.items():
        if k in ["query", "location"]:
            continue
        if v is not None and v != "" and v != []:
            label = k.replace("_", " ").title()
            if isinstance(v, list):
                val_str = ", ".join(str(item).replace("_", " ").title() for item in v)
            elif isinstance(v, (int, float)) and "budget" in k.lower():
                val_str = f"₹{v:,.0f}"
            else:
                val_str = str(v).replace("_", " ").title()
            formatted_answers.append(f"- {label}: {val_str}")

    answers_text = "\n".join(formatted_answers) if formatted_answers else "Standard defaults"

    prompt = f"""The user completed the Guided Decision Questionnaire for category: '{cat_title}'.
Their specific requirements and constraints:
{answers_text}
User Location: "{location or 'Not specified'}"

Synthesize the ultimate Explainable Decision Support System (EDSS) recommendation for this user.
Write in crystal-clear, friendly, and authoritative English.
For physical products (e.g. Laptop, Phone, Aquarium, Office Gear), name exact models/specs matching their budget.
For life/pets/health/career decisions, provide exact action plans and clear factor explanations.

Output JSON with this schema:
{{
  "category": "{cat_title}",
  "recommendation": "Direct, highly specific primary recommendation naming exact models/protocols/actions.",
  "confidence": 94.0,
  "confidence_band": "HIGH",
  "confidence_explanation": "Explanation of data alignment with user constraints.",
  "factors": [
    {{
      "factor": "snake_case_key",
      "score": 92.0,
      "label": "Clear Factor Label",
      "description": "Clear 1-2 sentence description explaining the score for this specific requirement."
    }}
  ],
  "explanation": "2-3 paragraphs of structured rationale explaining why this option best satisfies their questionnaire answers.",
  "impact": {{
    "immediate": ["Immediate step 1", "Immediate step 2"],
    "cost_impact": ["Cost/budget alignment analysis"],
    "long_term": ["Long-term value and lifespan"],
    "trade_offs": ["Key compromise made compared to alternatives"],
    "risks": ["Potential pitfalls to avoid"],
    "maintenance": ["Ongoing maintenance or upkeep required"]
  }},
  "alternatives": [
    {{
      "name": "Alternative Option Name",
      "score": 80.0,
      "key_advantage": "Main advantage",
      "key_tradeoff": "Key compromise",
      "estimated_price": "Price or effort"
    }}
  ],
  "follow_up_questions": [
    "Clarifying question 1",
    "Clarifying question 2",
    "Clarifying question 3"
  ],
  "nearby_available": {str(category in ["laptop", "smartphone", "pet", "fish_aquarium", "office_equipment", "health"]).lower()},
  "nearby_message": "Local stores and clinics are available for physical testing and consultation."
}}
"""
    data = _call_gemini_json(prompt, key)
    if not data:
        return None

    result = _build_decision_result(data, f"Guided {cat_title}", category)
    result.category = category

    # Attach demo catalog products where relevant
    try:
        from product_catalog import get_products_for_category
        budget_val = float(answers.get("budget", 0) or answers.get("total_budget", 0) or 0)
        quantity_val = int(answers.get("quantity", 1) or 1)
        from decision_engine import _generate_product_cards
        cards = _generate_product_cards(category, answers, budget_val, quantity_val)
        if cards:
            result.products = cards
    except Exception:
        pass

    return result


def _build_decision_result(data: Dict[str, Any], query_context: str, fallback_cat: str) -> DecisionResult:
    """Build a validated DecisionResult object from parsed Gemini JSON."""
    factors = []
    for f in data.get("factors", []):
        factors.append(FactorScore(
            factor=str(f.get("factor", "factor_score")),
            score=float(f.get("score", 80.0)),
            label=str(f.get("label", "Decision Factor")),
            description=str(f.get("description", "Evaluation metric")),
        ))

    if not factors:
        factors = [
            FactorScore(factor="requirement_fit", score=90.0, label="Requirement Match", description="How thoroughly this meets your stated criteria"),
            FactorScore(factor="practical_feasibility", score=85.0, label="Practical Feasibility", description="Ease and realism of execution"),
            FactorScore(factor="risk_mitigation", score=88.0, label="Risk Management", description="Protection against downsides and regrets"),
            FactorScore(factor="long_term_value", score=86.0, label="Long-Term Value", description="Durability of this choice over time"),
        ]

    alternatives = []
    for a in data.get("alternatives", []):
        alternatives.append(AlternativeOption(
            name=str(a.get("name", "Alternative Option")),
            score=float(a.get("score", 75.0)),
            key_advantage=str(a.get("key_advantage", "Viable alternative choice")),
            key_tradeoff=str(a.get("key_tradeoff", "Different trade-off profile")),
            estimated_price=a.get("estimated_price"),
        ))

    raw_impact = data.get("impact", {})
    impact = ImpactAnalysis(
        immediate=list(raw_impact.get("immediate", ["Immediate step defined."])),
        cost_impact=list(raw_impact.get("cost_impact", ["Cost evaluated."])),
        long_term=list(raw_impact.get("long_term", ["Long-term value evaluated."])),
        trade_offs=list(raw_impact.get("trade_offs", ["Trade-offs balanced."])),
        risks=list(raw_impact.get("risks", ["Risks identified."])),
        maintenance=list(raw_impact.get("maintenance", ["Upkeep noted."])),
    )

    conf_score = float(data.get("confidence", 90.0))
    conf_band = str(data.get("confidence_band", "HIGH" if conf_score >= 80 else "MEDIUM")).upper()

    return DecisionResult(
        recommendation=str(data.get("recommendation", "Proceed with a structured approach.")),
        confidence=conf_score,
        confidence_band=conf_band,
        confidence_explanation=str(data.get("confidence_explanation", "Analyzed using Gemini AI factor evaluation.")),
        factors=factors,
        explanation=str(data.get("explanation", "Synthesized using multi-criteria factor analysis.")),
        impact=impact,
        alternatives=alternatives,
        products=[],
        nearby_available=bool(data.get("nearby_available", False)),
        nearby_message=data.get("nearby_message"),
        category=str(data.get("category", fallback_cat)),
        quantity=None,
        bulk_summary=None,
        follow_up_questions=list(data.get("follow_up_questions", [
            "What is your highest priority constraint?",
            "What is your timeline for implementation?",
            "What is your backup plan if circumstances change?"
        ])),
    )
