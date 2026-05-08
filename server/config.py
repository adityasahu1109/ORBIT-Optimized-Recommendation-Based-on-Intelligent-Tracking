"""
Centralized configuration for the ORBIT Recommender System.
All paths, hyperparameters, and settings in one place.
"""

import os

# ──────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

RAW_CSV_PATH = os.path.join(DATA_DIR, "amazon_products.csv")
CLEANED_CSV_PATH = os.path.join(DATA_DIR, "cleaned_products.csv")
DB_PATH = os.path.join(DATA_DIR, "orbit.db")
DB_URL = f"sqlite:///{DB_PATH}"

SVD_MODEL_PATH = os.path.join(MODELS_DIR, "svd_model.pkl")
TFIDF_BUNDLE_PATH = os.path.join(MODELS_DIR, "tfidf_bundle.pkl")

# ──────────────────────────────────────────────
# INTERACTION WEIGHTS
# ──────────────────────────────────────────────
INTERACTION_WEIGHTS = {
    "view": 1.0,
    "click": 2.0,
    "add_to_cart": 3.5,
    "purchase": 5.0,
}

# ──────────────────────────────────────────────
# RECOMMENDATION HYPERPARAMETERS
# ──────────────────────────────────────────────

# Temporal decay: interactions lose half their weight after this many days
DECAY_HALFLIFE_DAYS = 14

# How many recent interactions to consider for building user profile
USER_HISTORY_LIMIT = 20

# Maximum category boost a single category can add to the final score
MAX_CATEGORY_BOOST = 0.8

# Weights for combining SVD score + category boost
SVD_WEIGHT = 0.7
CATEGORY_BOOST_WEIGHT = 0.3

# Minimum distinct categories in the top-N results
MIN_DIVERSITY_CATEGORIES = 3

# ──────────────────────────────────────────────
# POPULARITY ENGINE
# ──────────────────────────────────────────────
# Bayesian prior: minimum votes before a product's rating is trusted
BAYESIAN_MIN_VOTES = 25

# ──────────────────────────────────────────────
# SVD MODEL
# ──────────────────────────────────────────────
SVD_N_FACTORS = 50
SVD_N_EPOCHS = 20
SVD_LR = 0.005
SVD_REG = 0.02

# ──────────────────────────────────────────────
# TF-IDF / CONTENT ENGINE
# ──────────────────────────────────────────────
TFIDF_MAX_FEATURES = 5000

# ──────────────────────────────────────────────
# SEARCH
# ──────────────────────────────────────────────
SEARCH_RELEVANCE_WEIGHT = 0.7
SEARCH_QUALITY_WEIGHT = 0.3
SEARCH_MIN_SIMILARITY = 0.02   # Filter out garbage results below this threshold

# ──────────────────────────────────────────────
# API / SERVER
# ──────────────────────────────────────────────
CORS_ORIGINS = ["*"]  # Allow all origins in development

# ──────────────────────────────────────────────
# DATA SETUP
# ──────────────────────────────────────────────
TARGET_DATASET_SIZE = 200000

# ──────────────────────────────────────────────
# MOCK DATA
# ──────────────────────────────────────────────
MOCK_NUM_USERS = 100
MOCK_MIN_INTERACTIONS = 10
MOCK_MAX_INTERACTIONS = 30
