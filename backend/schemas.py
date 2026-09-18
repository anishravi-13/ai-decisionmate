from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# ─── Request Schemas ────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=2000, description="Free-text decision query")
    location: Optional[str] = Field(None, max_length=200)

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class GuidedAnalyzeRequest(BaseModel):
    category: str = Field(..., description="Decision category")
    answers: Dict[str, Any] = Field(default_factory=dict)
    location: Optional[str] = Field(None, max_length=200)
    quantity: Optional[int] = Field(None, ge=1, le=10000)

    @field_validator("category")
    @classmethod
    def category_valid(cls, v: str) -> str:
        valid = [
            "laptop", "smartphone", "pc_components", "pet", "fish_aquarium",
            "education", "career", "travel", "home", "vehicle",
            "office_equipment", "product_purchase", "company_bulk", "relationship",
            "personal", "general",
        ]
        if v.lower() not in valid:
            raise ValueError(f"Category must be one of: {valid}")
        return v.lower()


class WhatIfRequest(BaseModel):
    original_request: Dict[str, Any] = Field(..., description="Original request data")
    changes: Dict[str, Any] = Field(..., description="Changed parameters")
    category: str = Field(..., description="Decision category")


class ProductRequest(BaseModel):
    category: str = Field(..., max_length=100)
    budget: Optional[float] = Field(None, ge=0, le=100_000_000)
    quantity: Optional[int] = Field(1, ge=1, le=10000)
    requirements: Optional[List[str]] = Field(default_factory=list)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class NearbyRequest(BaseModel):
    category: str = Field(..., max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    radius_km: Optional[float] = Field(10.0, ge=1.0, le=100.0)


class CounterfactualRequest(BaseModel):
    category: str = Field(..., max_length=100)
    current_input: Dict[str, Any] = Field(...)
    current_recommendation: str = Field(..., max_length=500)
    target_change: Optional[str] = Field(None, max_length=200)


class ImpactRequest(BaseModel):
    category: str = Field(..., max_length=100)
    recommendation: str = Field(..., max_length=500)
    input_data: Dict[str, Any] = Field(...)
    quantity: Optional[int] = Field(1, ge=1)


# ─── Response Schemas ────────────────────────────────────────────────────────

class FactorScore(BaseModel):
    factor: str
    score: float = Field(..., ge=0.0, le=100.0)
    label: str
    description: str


class AlternativeOption(BaseModel):
    name: str
    score: float
    key_advantage: str
    key_tradeoff: str
    estimated_price: Optional[str] = None


class ImpactAnalysis(BaseModel):
    immediate: List[str]
    cost_impact: List[str]
    long_term: List[str]
    trade_offs: List[str]
    risks: List[str]
    maintenance: List[str]


class ProductCard(BaseModel):
    id: str
    name: str
    price: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    image_url: Optional[str] = None
    specs: Dict[str, Any] = Field(default_factory=dict)
    match_pct: float = Field(0.0, ge=0.0, le=100.0)
    why_match: str
    trade_offs: List[str] = Field(default_factory=list)
    link: Optional[str] = None
    demo_data: bool = True


class DecisionResult(BaseModel):
    recommendation: str
    confidence: float = Field(..., ge=0.0, le=100.0)
    confidence_band: str  # LOW / MEDIUM / HIGH
    confidence_explanation: str
    factors: List[FactorScore]
    explanation: str
    impact: ImpactAnalysis
    alternatives: List[AlternativeOption]
    products: List[ProductCard] = Field(default_factory=list)
    nearby_available: bool = False
    nearby_message: Optional[str] = None
    category: str
    quantity: Optional[int] = None
    bulk_summary: Optional[Dict[str, Any]] = None
    follow_up_questions: List[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    success: bool
    result: Optional[DecisionResult] = None
    history_id: Optional[int] = None
    error: Optional[str] = None


class WhatIfResponse(BaseModel):
    success: bool
    result: Optional[DecisionResult] = None
    changed_because: Optional[str] = None
    recommendation_changed: bool = False
    error: Optional[str] = None


class CounterfactualResponse(BaseModel):
    success: bool
    change_required: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    new_recommendation: Optional[str] = None
    error: Optional[str] = None


class HistoryItem(BaseModel):
    id: int
    timestamp: datetime
    category: str
    user_query: Optional[str] = None
    recommendation: Optional[str] = None
    confidence: Optional[float] = None
    confidence_band: Optional[str] = None

    model_config = {"from_attributes": True}


class HistoryDetail(BaseModel):
    id: int
    timestamp: datetime
    category: str
    user_query: Optional[str] = None
    input_data: Dict[str, Any] = Field(default_factory=dict)
    recommendation: Optional[str] = None
    confidence: Optional[float] = None
    confidence_band: Optional[str] = None
    factors: List[Dict[str, Any]] = Field(default_factory=list)
    result: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str


class NearbyBusiness(BaseModel):
    name: str
    category: str
    address: Optional[str] = None
    phone: Optional[str] = None
    rating: Optional[float] = None
    distance_km: Optional[float] = None
    note: str = "Demo data"


class NearbyResponse(BaseModel):
    success: bool
    businesses: List[NearbyBusiness] = Field(default_factory=list)
    live_data: bool = False
    message: str = ""
    error: Optional[str] = None
