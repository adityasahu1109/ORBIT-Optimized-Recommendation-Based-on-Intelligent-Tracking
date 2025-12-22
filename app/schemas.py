from pydantic import BaseModel
from typing import List, Optional

# --- INPUT SCHEMAS (Data coming IN) ---

class InteractionCreate(BaseModel):
    user_id: str
    product_id: str
    interaction_type: str  # 'view', 'click', 'add_to_cart', 'purchase'

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "1001",
                "product_id": "B07BR3F9N6",
                "interaction_type": "click"
            }
        }

class RecommendationRequest(BaseModel):
    user_id: str
    product_id_viewed: Optional[str] = None # Optional: Only if they are looking at a product right now
    n_recommendations: int = 10

# --- OUTPUT SCHEMAS (Data going OUT) ---

class ProductResponse(BaseModel):
    asin: str
    title: str
    category: str
    price: float
    imgUrl: str = ""      # <--- Ensure this exists
    stars: float = 0.0    # <--- Ensure this exists
    reviews: int = 0      # <--- Ensure this exists
    score: float
    reason: str  # Explain WHY we recommended this (e.g., "Popularity", "Because you viewed X")

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[ProductResponse]