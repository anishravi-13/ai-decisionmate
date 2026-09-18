"""
main.py – FastAPI application entry point.
AI DecisionMate — Explainable AI Decision Support System
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import traceback

from config import settings
from database import init_db, get_db
from schemas import (
    AnalyzeRequest, AnalyzeResponse,
    GuidedAnalyzeRequest,
    WhatIfRequest, WhatIfResponse,
    ProductRequest, ProductCard,
    NearbyRequest, NearbyResponse,
    HistoryItem, HistoryDetail,
    CounterfactualRequest, CounterfactualResponse,
    ImpactRequest, ImpactAnalysis,
    HealthResponse,
    DecisionResult,
)

# ─── App Initialisation ───────────────────────────────────────────────────────

app = FastAPI(
    title="AI DecisionMate API",
    description="Explainable AI Decision Support System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Auto-create database tables on first startup."""
    init_db()


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Check API and database health."""
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "error"
    return HealthResponse(status="ok", version="1.0.0", database=db_status)


# ─── Analyze (Free-text) ──────────────────────────────────────────────────────

@app.post("/analyze", response_model=AnalyzeResponse, tags=["Decision"])
def analyze(req: AnalyzeRequest, db: Session = Depends(get_db)):
    """Analyze a free-text decision query."""
    try:
        from decision_engine import analyze_free_text
        from history import create_history_entry

        result = analyze_free_text(req.query)

        # Persist to history
        entry = create_history_entry(
            db=db,
            category=result.category,
            user_query=req.query,
            input_data={"query": req.query, "location": req.location},
            result=result,
        )

        return AnalyzeResponse(success=True, result=result, history_id=entry.id)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )


# ─── Guided Analyze ───────────────────────────────────────────────────────────

@app.post("/guided-analyze", response_model=AnalyzeResponse, tags=["Decision"])
def guided_analyze(req: GuidedAnalyzeRequest, db: Session = Depends(get_db)):
    """Analyze a guided questionnaire-based decision."""
    try:
        from decision_engine import run_decision_engine
        from history import create_history_entry

        answers = dict(req.answers)
        if req.quantity:
            answers["quantity"] = req.quantity
        if req.location:
            answers["location"] = req.location

        result = run_decision_engine(req.category, answers)

        entry = create_history_entry(
            db=db,
            category=req.category,
            user_query=f"Guided: {req.category}",
            input_data=answers,
            result=result,
        )

        return AnalyzeResponse(success=True, result=result, history_id=entry.id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Guided analysis failed: {str(e)}")


# ─── What-If Analysis ─────────────────────────────────────────────────────────

@app.post("/whatif", response_model=WhatIfResponse, tags=["Decision"])
def whatif(req: WhatIfRequest):
    """Run what-if analysis with modified parameters."""
    try:
        from whatif import run_whatif

        new_result, rec_changed, explanation = run_whatif(
            category=req.category,
            original_input=req.original_request,
            changes=req.changes,
        )

        return WhatIfResponse(
            success=True,
            result=new_result,
            changed_because=explanation,
            recommendation_changed=rec_changed,
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"What-if analysis failed: {str(e)}")


# ─── Products ─────────────────────────────────────────────────────────────────

@app.post("/products", response_model=List[ProductCard], tags=["Products"])
def products(req: ProductRequest):
    """Get product recommendations from demo catalog."""
    try:
        from product_catalog import get_products_for_category
        from decision_engine import _compute_product_match, _generate_why_match, _generate_product_tradeoffs

        raw = get_products_for_category(
            req.category,
            budget=req.budget,
            quantity=req.quantity or 1,
        )

        answers: Dict[str, Any] = {}
        if req.budget:
            answers["budget"] = req.budget
        if req.requirements:
            answers["requirements"] = req.requirements
        if req.filters:
            answers.update(req.filters)

        cards = []
        for p in raw[:8]:
            match = _compute_product_match(p, answers, req.category)
            why = _generate_why_match(p, answers, req.category, match)
            tradeoffs = _generate_product_tradeoffs(p, req.category)
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

        cards.sort(key=lambda c: c.match_pct, reverse=True)
        return cards

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Product search failed: {str(e)}")


# ─── Nearby ───────────────────────────────────────────────────────────────────

@app.post("/nearby", response_model=NearbyResponse, tags=["Nearby"])
def nearby(req: NearbyRequest):
    """Search for nearby businesses. Falls back gracefully if no API key."""
    try:
        from business_search import search_nearby_businesses

        response = search_nearby_businesses(
            category=req.category,
            location=req.location,
            radius_km=req.radius_km or 10.0,
        )
        return response

    except Exception as e:
        traceback.print_exc()
        return NearbyResponse(
            success=False,
            businesses=[],
            live_data=False,
            message="",
            error=f"Nearby search encountered an error: {str(e)}",
        )


# ─── History ──────────────────────────────────────────────────────────────────

@app.get("/history", response_model=List[HistoryItem], tags=["History"])
def get_history(db: Session = Depends(get_db)):
    """Get all decision history."""
    try:
        from history import get_all_history
        return get_all_history(db)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch history: {str(e)}")


@app.get("/history/{history_id}", response_model=HistoryDetail, tags=["History"])
def get_history_item(history_id: int, db: Session = Depends(get_db)):
    """Get a single history item by ID."""
    try:
        from history import get_history_by_id
        item = get_history_by_id(db, history_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"History item {history_id} not found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch history item: {str(e)}")


@app.delete("/history/{history_id}", tags=["History"])
def delete_history_item(history_id: int, db: Session = Depends(get_db)):
    """Delete a single history item."""
    try:
        from history import delete_history_by_id
        deleted = delete_history_by_id(db, history_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"History item {history_id} not found")
        return {"success": True, "message": f"History item {history_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete history item: {str(e)}")


@app.delete("/history", tags=["History"])
def delete_all_history_endpoint(db: Session = Depends(get_db)):
    """Delete all history entries."""
    try:
        from history import delete_all_history
        count = delete_all_history(db)
        return {"success": True, "message": f"Deleted {count} history entries"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete history: {str(e)}")


# ─── Counterfactual ───────────────────────────────────────────────────────────

@app.post("/counterfactual", response_model=CounterfactualResponse, tags=["Decision"])
def counterfactual(req: CounterfactualRequest):
    """
    Simple counterfactual: find minimum input change that flips the recommendation.
    Clearly labeled as estimated what-if scenario.
    """
    try:
        from decision_engine import run_decision_engine, detect_category

        cat = req.category.lower()
        current_input = dict(req.current_input)
        current_rec = req.current_recommendation

        # For relationship / personal categories
        if cat in ["relationship", "personal"]:
            if current_input.get("asked_for_space") in ["yes", True] or current_input.get("boundary_requested") in ["yes", True]:
                trial_input = dict(current_input)
                trial_input["asked_for_space"] = "no"
                trial_input["boundary_requested"] = "no"
                result = run_decision_engine(cat, trial_input)
                if result.recommendation != current_rec:
                    change_required = {
                        "factor": "stated_boundary",
                        "current_value": "Boundary requested ('do not talk')",
                        "suggested_value": "No boundary set / Communication open",
                        "change": "If he had not explicitly asked for space, reaching out sooner for open dialogue would be recommended instead of a 3-5 day cooling-off wait.",
                    }
                    new_rec = result.recommendation
                    found = True

            if not found and current_input.get("fault_attribution") != "mostly_mine":
                trial_input = dict(current_input)
                trial_input["fault_attribution"] = "mostly_mine"
                trial_input["asked_for_space"] = "no"
                result = run_decision_engine(cat, trial_input)
                if result.recommendation != current_rec:
                    change_required = {
                        "factor": "fault_attribution",
                        "current_value": current_input.get("fault_attribution", "mutual"),
                        "suggested_value": "Clear personal mistake / ownership",
                        "change": "If the fight was caused primarily by your mistake, taking direct ownership via a brief apology would take precedence over waiting.",
                    }
                    new_rec = result.recommendation
                    found = True

        # Try incrementally changing budget
        if not found and "budget" in current_input and current_input["budget"]:
            original_budget = float(current_input["budget"])
            step = original_budget * 0.1  # 10% increments

            for i in range(1, 6):  # Up to 5 steps
                trial_input = dict(current_input)
                trial_input["budget"] = original_budget + (step * i)
                result = run_decision_engine(cat, trial_input)

                if result.recommendation != current_rec:
                    increase = step * i
                    change_required = {
                        "factor": "budget",
                        "current_value": f"₹{original_budget:,.0f}",
                        "suggested_value": f"₹{original_budget + increase:,.0f}",
                        "change": f"+₹{increase:,.0f}",
                    }
                    new_rec = result.recommendation
                    found = True
                    break

        if not found:
            # Try changing performance priority
            perf_levels = ["low", "medium", "high"]
            current_perf = current_input.get("performance_priority", "medium")
            try:
                idx = perf_levels.index(str(current_perf).lower())
            except ValueError:
                idx = 1

            if idx < len(perf_levels) - 1:
                trial_input = dict(current_input)
                trial_input["performance_priority"] = perf_levels[idx + 1]
                result = run_decision_engine(cat, trial_input)
                if result.recommendation != current_rec:
                    change_required = {
                        "factor": "performance_priority",
                        "current_value": current_perf,
                        "suggested_value": perf_levels[idx + 1],
                        "change": f"Increase performance priority to '{perf_levels[idx + 1]}'",
                    }
                    new_rec = result.recommendation
                    found = True

        if not found:
            description = (
                "No single parameter change within tested ranges produced a different recommendation. "
                "Your current requirements strongly align with the existing recommendation. "
                "This is an estimated what-if scenario and does not guarantee specific outcomes."
            )
            return CounterfactualResponse(
                success=True,
                change_required=None,
                description=description,
                new_recommendation=None,
            )

        description = (
            f"Estimated what-if scenario: If you change {change_required['factor'].replace('_', ' ')} "
            f"from {change_required['current_value']} to {change_required['suggested_value']}, "
            f"the recommendation may shift to a different option. "
            "This is an estimated scenario — actual outcomes depend on market availability and other factors."
        )

        return CounterfactualResponse(
            success=True,
            change_required=change_required,
            description=description,
            new_recommendation=new_rec,
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Counterfactual analysis failed: {str(e)}")


# ─── Impact ───────────────────────────────────────────────────────────────────

@app.post("/impact", response_model=ImpactAnalysis, tags=["Decision"])
def impact_analysis(req: ImpactRequest):
    """Get detailed impact analysis for a recommendation."""
    try:
        from impact import generate_impact

        result = generate_impact(
            category=req.category,
            recommendation=req.recommendation,
            answers=req.input_data,
            bulk_summary=None,
        )
        return result

    except Exception as e:
        traceback.print_exc()
# ─── Static Frontend (Unified 1-Server Mode) ──────────────────────────────────

import os
from fastapi.staticfiles import StaticFiles

frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
