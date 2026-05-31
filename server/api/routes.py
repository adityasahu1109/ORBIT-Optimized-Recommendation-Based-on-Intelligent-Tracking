"""
API routes — thin controllers that delegate to services.
No business logic here, just request handling and response formatting.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.db.engine import get_db
from server.api.schemas import (
    InteractionCreate,
    RecommendationRequest,
    RecommendationResponse,
    SearchResponse,
)

# These will be injected by main.py after engine initialization
_recommendation_service = None
_search_engine = None
_interaction_service = None
_product_service = None


def set_services(recommendation_svc, search_eng, interaction_svc, product_svc):
    """Called once at startup to inject service references."""
    global _recommendation_service, _search_engine, _interaction_service, _product_service
    _recommendation_service = recommendation_svc
    _search_engine = search_eng
    _interaction_service = interaction_svc
    _product_service = product_svc


router = APIRouter(prefix="/api")


# ──────────────────────────────────────────────
# INTERACTIONS
# ──────────────────────────────────────────────

@router.post("/interactions")
def log_interaction(data: InteractionCreate, db: Session = Depends(get_db)):
    """Log a user-product interaction."""
    _interaction_service.log_interaction(
        db=db,
        user_id=data.user_id,
        product_id=data.product_id,
        interaction_type=data.interaction_type.value,
    )
    return {"status": "success", "message": "Interaction logged"}


# ──────────────────────────────────────────────
# RECOMMENDATIONS
# ──────────────────────────────────────────────

@router.post("/recommend", response_model=RecommendationResponse)
def get_recommendations(req: RecommendationRequest, db: Session = Depends(get_db)):
    """
    Get personalized recommendations for a user.
    If `product_id_viewed` is set, returns content-based similar items.
    """
    result = _recommendation_service.get_recommendations(
        db=db,
        user_id=req.user_id,
        product_id_viewed=req.product_id_viewed,
        n=req.n_recommendations,
    )
    return result


# ──────────────────────────────────────────────
# SEARCH
# ──────────────────────────────────────────────

@router.get("/search", response_model=SearchResponse)
def search_products(query: str = ""):
    """Search products by keyword with TF-IDF relevance scoring."""
    if not query.strip():
        return {"query": query, "results": []}

    results = _search_engine.search(query, k=40)
    return {"query": query, "results": results}


# ──────────────────────────────────────────────
# PRODUCTS
# ──────────────────────────────────────────────

@router.get("/products/{asin}")
def get_product(asin: str):
    """Get a single product by ASIN."""
    product = _product_service.get_product(asin)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {asin} not found")
    return product
