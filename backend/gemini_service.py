"""
gemini_service.py – Integration with Google Gemini API for arbitrary real-world queries.
Produces structured Explainable Decision Support System (EDSS) outputs matching DecisionResult schema.
"""
import os
import json
import logging
from typing import Optional, Dict, Any
import httpx

from config import settings
from schemas import DecisionResult, FactorScore, ImpactAnalysis, AlternativeOption

logger = logging.getLogger(__name__)

GEMINI_MODELS = [
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-pro",
]

def get_active_gemini_key(user_key: Optional[str] = None) -> Optional[str]:
    """Retrieve Gemini API key from user parameter, settings, or environment."""
    if user_key and user_key.strip():
        return user_key.strip()
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
        return settings.GEMINI_API_KEY.strip()
    env_key = os.getenv("GEMINI_API_KEY", "")
    if env_key.strip():
        return env_key.strip()
    return None


SYSTEM_PROMPT = """You are AI DecisionMate, a world-class Explainable AI Decision Support System (EDSS).
Your mission is to help users make high-stakes, everyday, ethical, financial, relational, technical, or personal decisions.

Unlike ordinary chat bots that produce unstructured text essays, you provide structured, auditable, explainable decision analytics:
1. A direct, clear, highly practical, empathetic, and actionable primary recommendation tailored to their situation.
2. 4 to 5 quantifiable factor scores (0-100) reflecting the critical dimensions of the decision (e.g. Feasibility, Long-Term Well-Being, Cost/Resource Efficiency, Risk Mitigation, Alignment).
3. A calibrated confidence score (0-100) and confidence band (HIGH / MEDIUM / LOW) explaining data sufficiency.
4. An explainability rationale justifying the factor weights and recommendations.
5. A comprehensive 6-dimension impact analysis:
   - immediate: short-term outcomes / actions
   - cost_impact: financial, emotional, or time costs
   - long_term: 1 to 2 year trajectory
   - trade_offs: compromises and sacrifices required
   - risks: downsides or vulnerabilities to watch
   - maintenance: ongoing habits, reviews, or upkeep
6. 2 to 3 distinct, realistic alternative paths with scores and trade-offs.
7. 3 smart follow-up clarifying questions.

Return ONLY a valid JSON object matching the requested schema. No markdown backticks, no preamble, only pure JSON.
"""

def analyze_with_gemini(
    query: str,
    api_key: Optional[str] = None,
    location: Optional[str] = None,
) -> Optional[DecisionResult]:
    """
    Call Google Gemini REST API to analyze any free-text decision.
    Returns DecisionResult if successful, or None if unavailable/error.
    """
    key = get_active_gemini_key(api_key)
    if not key:
        logger.info("No Gemini API key found. Falling back to local decision engine.")
        return None

    prompt = f"""Analyze this decision query thoroughly:
User Question: "{query}"
User Location: "{location or 'Not specified'}"

Generate the complete Explainable Decision Support System output as JSON with this exact structure:
{{
  "category": "Descriptive category name (e.g. Life & Personal, Career & Education, Health & Nutrition, Tech & Gadgets, Finance, Relationship)",
  "recommendation": "A detailed, direct, practical, and empathetic primary recommendation with specific actionable steps.",
  "confidence": 90.0,
  "confidence_band": "HIGH",
  "confidence_explanation": "Why this confidence level was assigned based on clarity of user input.",
  "factors": [
    {{
      "factor": "snake_case_key",
      "score": 88.0,
      "label": "Human Readable Factor Label",
      "description": "Explanation of how this factor influences the decision"
    }}
  ],
  "explanation": "A structured 2-3 paragraph explanation justifying the decision logic, factor weights, and trade-offs.",
  "impact": {{
    "immediate": ["Immediate outcome 1", "Immediate outcome 2"],
    "cost_impact": ["Cost/Resource impact 1"],
    "long_term": ["Long term impact 1", "Long term impact 2"],
    "trade_offs": ["Trade off 1", "Trade off 2"],
    "risks": ["Potential risk 1", "Potential risk 2"],
    "maintenance": ["Ongoing habit or review 1"]
  }},
  "alternatives": [
    {{
      "name": "Alternative Option Name",
      "score": 82.0,
      "key_advantage": "Main advantage over primary recommendation",
      "key_tradeoff": "Main drawback or trade-off",
      "estimated_price": "Cost or effort estimate"
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

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{SYSTEM_PROMPT}\n\n{prompt}"}]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.35,
            "maxOutputTokens": 2048,
        }
    }

    # Try model endpoints in order
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
                            return _parse_gemini_json(raw_text, query)
                else:
                    logger.warning(f"Gemini model {model} returned status {res.status_code}: {res.text[:200]}")
        except Exception as e:
            logger.warning(f"Failed to query Gemini model {model}: {e}")

    logger.warning("All Gemini model attempts failed or timed out. Falling back to local decision engine.")
    return None


def _parse_gemini_json(raw_text: str, original_query: str) -> Optional[DecisionResult]:
    """Clean and parse JSON from Gemini into a valid DecisionResult."""
    try:
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)

        # Parse factors
        factors = []
        for f in data.get("factors", []):
            factors.append(FactorScore(
                factor=str(f.get("factor", "factor_score")),
                score=float(f.get("score", 75.0)),
                label=str(f.get("label", "Evaluation Factor")),
                description=str(f.get("description", "")),
            ))

        if not factors:
            factors = [
                FactorScore(factor="alignment", score=85.0, label="Requirement Alignment", description="Fit with your core goal"),
                FactorScore(factor="feasibility", score=80.0, label="Feasibility", description="Ease of implementation"),
                FactorScore(factor="risk_control", score=82.0, label="Risk Control", description="Safety and risk mitigation"),
            ]

        # Parse alternatives
        alternatives = []
        for a in data.get("alternatives", []):
            alternatives.append(AlternativeOption(
                name=str(a.get("name", "Alternative Option")),
                score=float(a.get("score", 70.0)),
                key_advantage=str(a.get("key_advantage", "Viable secondary approach")),
                key_tradeoff=str(a.get("key_tradeoff", "Different trade-off balance")),
                estimated_price=a.get("estimated_price"),
            ))

        # Parse impact
        raw_impact = data.get("impact", {})
        impact = ImpactAnalysis(
            immediate=list(raw_impact.get("immediate", ["Clarifies next immediate actionable step."])),
            cost_impact=list(raw_impact.get("cost_impact", ["Requires dedicated focus and time commitment."])),
            long_term=list(raw_impact.get("long_term", ["Builds long-term resilience and positive outcome."])),
            trade_offs=list(raw_impact.get("trade_offs", ["Requires prioritizing this path over alternatives."])),
            risks=list(raw_impact.get("risks", ["Inconsistency or premature abandonment of the plan."])),
            maintenance=list(raw_impact.get("maintenance", ["Review progress weekly and adjust as needed."])),
        )

        conf_score = float(data.get("confidence", 88.0))
        conf_band = str(data.get("confidence_band", "HIGH" if conf_score >= 80 else "MEDIUM")).upper()

        return DecisionResult(
            recommendation=str(data.get("recommendation", "Consider your options carefully.")),
            confidence=conf_score,
            confidence_band=conf_band,
            confidence_explanation=str(data.get("confidence_explanation", "Analyzed with Gemini Explainable AI based on your query requirements.")),
            factors=factors,
            explanation=str(data.get("explanation", "This recommendation was synthesized using multi-criteria factor analysis.")),
            impact=impact,
            alternatives=alternatives,
            products=[],
            nearby_available=bool(data.get("nearby_available", False)),
            nearby_message=data.get("nearby_message"),
            category=str(data.get("category", "General Decision")),
            quantity=None,
            bulk_summary=None,
            follow_up_questions=list(data.get("follow_up_questions", [
                "What is your primary constraint (time, budget, or emotion)?",
                "What would be your ideal outcome in 6 months?",
                "Do you have a backup plan if initial steps encounter resistance?"
            ])),
        )
    except Exception as e:
        logger.error(f"Failed to parse Gemini output into DecisionResult: {e}. Raw text: {raw_text[:300]}")
        return None
