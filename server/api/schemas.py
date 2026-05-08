"""
Pydantic schemas for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# ──────────────────────────────────────────────
# ENUMS
# ──────────────────────────────────────────────

class InteractionType(str, Enum):
    view = "view"
    click = "click"
    add_to_cart = "add_to_cart"
    purchase = "purchase"


# ──────────────────────────────────────────────
# INPUT SCHEMAS
# ──────────────────────────────────────────────

class InteractionCreate(BaseModel):
    user_id: str = Field(..., examples=["1001"])
    product_id: str = Field(..., examples=["B07BR3F9N6"])
    interaction_type: InteractionType = Field(..., examples=["click"])


class RecommendationRequest(BaseModel):
    user_id: str = Field(..., examples=["1001"])
    product_id_viewed: Optional[str] = Field(
        None,
        description="If set, returns content-based similar products.",
        examples=["B07BR3F9N6"],
    )
    n_recommendations: int = Field(10, ge=1, le=50)


# ──────────────────────────────────────────────
# OUTPUT SCHEMAS
# ──────────────────────────────────────────────

class ProductResponse(BaseModel):
    asin: str
    title: str
    category: str
    price: float
    imgUrl: str = ""
    stars: float = 0.0
    reviews: int = 0
    score: float
    reason: str


class RecommendationResponse(BaseModel):
    user_id: str
    strategy: str  # "cold_start", "personalized", "content_based"
    recommendations: list[ProductResponse]


class SearchResultItem(BaseModel):
    asin: str
    title: str
    categoryName: str
    price: float
    stars: float = 0.0
    reviews: int = 0
    imgUrl: str = ""
    relevance_score: float = 0.0
    quality_score: float = 0.0
    score: float = 0.0


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
