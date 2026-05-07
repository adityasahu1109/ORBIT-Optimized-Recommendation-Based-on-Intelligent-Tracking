from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc  
from contextlib import asynccontextmanager
import pandas as pd

# Import our modules
from database import get_db, Interaction, SessionLocal
from app import schemas
from app.popularity import PopularityRecommender
from app.content_engine import ContentEngine
from app.collaborative_engine import CollaborativeEngine

# Global variables to hold our engines
engines = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- STARTUP: Loading Models ---")
    engines['popularity'] = PopularityRecommender()
    print("✅ Popularity Engine Loaded")
    engines['content'] = ContentEngine()
    print("✅ Content Engine Loaded")
    engines['collaborative'] = CollaborativeEngine()
    print("✅ Collaborative Engine Loaded")
    yield
    print("--- SHUTDOWN: Cleaning up ---")
    engines.clear()

# Initialize API
app = FastAPI(title="ORBIT Recommender API", lifespan=lifespan)

# --- CORS MIDDLEWARE ---
# This allows your React app (running on port 5173) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)
# -----------------------

# --- ENDPOINTS ---

@app.post("/log-interaction")
def log_user_interaction(data: schemas.InteractionCreate, db: Session = Depends(get_db)):
    new_interaction = Interaction(
        user_id=data.user_id,
        product_id=data.product_id,
        interaction_type=data.interaction_type
    )
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)
    return {"status": "success", "message": "Interaction logged"}

@app.post("/recommend", response_model=schemas.RecommendationResponse)
def get_recommendations(req: schemas.RecommendationRequest, db: Session = Depends(get_db)):
    user_id = req.user_id
    
    # ---------------------------------------------------------
    # SCENARIO 1: CONTEXT-AWARE (User is viewing a specific product)
    # ---------------------------------------------------------
    if req.product_id_viewed:
        print(f"User viewing {req.product_id_viewed} -> Using Content Engine")
        
        # Get similar items from Content Engine
        results = engines['content'].find_similar_products(req.product_id_viewed, k=req.n_recommendations)
        
        response_items = []
        for item in results:
            # We map the dictionary keys from ContentEngine to our Pydantic Schema
            response_items.append(schemas.ProductResponse(
                asin=item['asin'],
                title=item['title'],
                category=item.get('category', 'Unknown'), 
                price=item.get('price', 0.0),      
                imgUrl=item.get('imgUrl', ""),      
                stars=item.get('stars', 0.0),     
                reviews=item.get('reviews', 0),     
                score=item['score'],
                reason="Similar to viewed product"
            ))
        return {"user_id": user_id, "recommendations": response_items}

    # ---------------------------------------------------------
    # SCENARIO 2: PERSONALIZED HOMEPAGE (Popularity + Collaborative)
    # ---------------------------------------------------------
    print(f"Generating personalized feed for {user_id}...")
    
    # 1. Check user's last interaction to boost specific categories
    last_interaction = db.query(Interaction).filter(Interaction.user_id == user_id).order_by(desc(Interaction.timestamp)).first()
    
    boost_category = None
    if last_interaction:
        # Look up the product details of the last interacted item
        product_info = engines['popularity'].df[engines['popularity'].df['asin'] == last_interaction.product_id]
        if not product_info.empty:
            boost_category = product_info.iloc[0]['categoryName']
            print(f"User {user_id} intent: {boost_category}")

    # 2. Get Candidates (Top Popular Items)
    candidates = engines['popularity'].get_recommendations(k=50)
    
    # 3. If we have a category boost, inject more items from that category
    if boost_category:
        print(f"Injecting candidates from: {boost_category}")
        cat_items = engines['popularity'].df[engines['popularity'].df['categoryName'] == boost_category].head(50)
        # Fix: Ensure we include imgUrl and other details here too
        cat_candidates = cat_items[['asin', 'title', 'categoryName', 'price', 'stars', 'reviews', 'imgUrl']].to_dict(orient='records')
        candidates.extend(cat_candidates)

    # Deduplicate candidates
    unique_candidates = {item['asin']: item for item in candidates}.values()

    scored_candidates = []
    
    # 4. Score each candidate using the Collaborative Model (SVD)
    for item in unique_candidates:
        svd_score = engines['collaborative'].predict_score(user_id, item['asin'])
        
        bonus = 0
        reason = "Recommended for you"
        
        # Apply Bonus if it matches the boost category
        if boost_category and item['categoryName'] == boost_category:
            bonus = 1.5 
            reason = f"Because you viewed {boost_category}"
        
        final_score = svd_score + bonus
        
        scored_candidates.append({
            "asin": item['asin'],
            "title": item['title'],
            "category": item['categoryName'],
            "price": item['price'],
            # Fix: Pass these new fields to the schema
            "imgUrl": item.get('imgUrl', ""),
            "stars": item.get('stars', 0.0),
            "reviews": item.get('reviews', 0),
            "score": final_score,
            "reason": reason
        })
    
    # 5. Sort by final score and return top N
    top_picks = sorted(scored_candidates, key=lambda x: x['score'], reverse=True)[:req.n_recommendations]
    
    return {"user_id": user_id, "recommendations": top_picks}

@app.get("/search")
def search_products(query: str):
    if not query:
        return {"results": []}
    
    print(f"Searching for: {query}")
    results = engines['content'].search_products(query, k=20)
    return {"query": query, "results": results}

@app.get("/")
def health_check():
    return {"status": "running", "models_loaded": list(engines.keys())}