"""
FastAPI application factory.

- On first run: auto-detects missing data/models and runs the setup pipeline.
- On subsequent runs: loads all engines from disk instantly (no training).
- Registers API router and CORS middleware.
- Run with: uvicorn server.main:app --reload
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from server.config import (
    CORS_ORIGINS,
    CLEANED_CSV_PATH,
    RAW_CSV_PATH,
    SVD_MODEL_PATH,
    TFIDF_BUNDLE_PATH,
    DB_PATH,
)
from server.db.engine import init_db, SessionLocal

# Engine imports
from server.engines.popularity import PopularityEngine
from server.engines.collaborative import CollaborativeEngine
from server.engines.content import ContentEngine
from server.engines.search import SearchEngine

# Service imports
from server.services.recommendation import RecommendationService
from server.services.interaction import InteractionService
from server.services.product import ProductService

# Route imports
from server.api.routes import router, set_services


def _auto_setup():
    """
    Automatically run the data cleaning, interaction seeding, and model
    training pipeline if the required files are missing.

    This makes the project work immediately after cloning — just start
    the server and everything is set up on first run.
    """

    needs_data_setup = not os.path.exists(CLEANED_CSV_PATH)
    needs_model_training = (
        not os.path.exists(SVD_MODEL_PATH)
        or not os.path.exists(TFIDF_BUNDLE_PATH)
    )
    # Check if interaction DB is empty (or doesn't exist)
    needs_seed = False

    if needs_data_setup:
        if not os.path.exists(RAW_CSV_PATH):
            print("[WARNING] Raw dataset not found at:", RAW_CSV_PATH)
            print("          Please place amazon_products.csv in the data/ directory.")
            print("          Skipping auto-setup.")
            return
        print("\n" + "=" * 60)
        print("  ORBIT — First-Run Auto-Setup")
        print("=" * 60)
        print("\n--- Step 1/3: Cleaning & sampling product data ---\n")
        from scripts.setup_data import clean_data
        clean_data()
        # If we just created the data, we definitely need seed + training
        needs_seed = True
        needs_model_training = True

    if needs_seed or not os.path.exists(DB_PATH):
        # If DB doesn't exist, init_db will create it but it'll be empty
        needs_seed = True

    if needs_seed:
        # Check if DB has any interactions — if not, seed it
        init_db()
        from server.db.models import Interaction
        db = SessionLocal()
        try:
            count = db.query(Interaction).count()
            if count == 0:
                db.close()
                print("\n--- Step 2/3: Seeding mock interaction data ---\n")
                from scripts.seed_interactions import generate_mock_data
                generate_mock_data()
            else:
                db.close()
                print(f"[OK] Database already has {count:,} interactions — skipping seed.")
        except Exception:
            db.close()
            print("\n--- Step 2/3: Seeding mock interaction data ---\n")
            from scripts.seed_interactions import generate_mock_data
            generate_mock_data()

    if needs_model_training:
        print("\n--- Step 3/3: Training ML models ---\n")
        from scripts.train_model import main as train_models
        train_models()
        print()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: Auto-setup if needed, then load all pre-trained models from disk.
    """
    # Run auto-setup if any required files are missing
    _auto_setup()

    print("=" * 60)
    print("  ORBIT Recommender — Starting Up")
    print("=" * 60)

    # Ensure database tables exist
    init_db()

    # Load engines (all from disk — no training)
    print("\n--- Loading Engines ---")
    popularity = PopularityEngine()
    collaborative = CollaborativeEngine()
    content = ContentEngine()
    search = SearchEngine(content)  # Shares ContentEngine's TF-IDF data

    # Wire up services
    print("\n--- Wiring Services ---")
    recommendation_svc = RecommendationService(popularity, collaborative, content)
    interaction_svc = InteractionService()
    product_svc = ProductService(popularity)

    # Inject services into routes
    set_services(recommendation_svc, search, interaction_svc, product_svc)

    print("\n" + "=" * 60)
    print("  ORBIT is ready!")
    print("=" * 60 + "\n")

    yield  # App is running

    print("\n--- ORBIT Shutting Down ---")


# Create the app
app = FastAPI(
    title="ORBIT Recommender API",
    description="AI-powered e-commerce recommendation engine",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(router)


# Root health check
@app.get("/")
def health_check():
    return {"status": "running", "version": "2.0.0"}
