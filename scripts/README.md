# ORBIT Scripts — Setup, Seed, and Training

The `scripts/` directory contains three standalone utilities that prepare the system for use. These are **run-once** scripts — you don't need to re-run them unless you're changing the dataset or retraining models.

---

## Execution Order

Run these **once** in order before starting the server:

```bash
# From the project root directory:

# 1. Clean and sample from the raw 2.2M product CSV → ~156K products
python -m scripts.setup_data

# 2. Generate mock user interactions for testing
python -m scripts.seed_interactions

# 3. Train SVD model + build TF-IDF bundle
python -m scripts.train_model
```

---

## Script Details

### `setup_data.py` — Data Cleaning Pipeline

**Input**: `data/amazon_products.csv` (2.2M raw products)  
**Output**: `data/cleaned_products.csv` (~156K stratified sample)

What it does:
1. Drops rows missing `asin`, `title`, or `categoryName`
2. Coerces numeric columns (`reviews`, `stars`, `price`, `boughtInLastMonth`)
3. Performs **stratified sampling**: takes top N products per category (sorted by review count)
4. Target size is configurable via `TARGET_DATASET_SIZE` in `server/config.py` (default: 200,000)

### `seed_interactions.py` — Mock Data Generator

**Input**: `data/cleaned_products.csv`  
**Output**: Rows in `data/orbit.db` → `interactions` table

Generates realistic interaction patterns:
- 100 simulated users (IDs 1001–1100)
- Each user has 2–3 preferred categories
- 75% of interactions are with preferred categories
- Interaction funnel: 50% views, 28% clicks, 15% add-to-cart, 7% purchases
- Temporal spread over 30 days with recency bias (beta distribution)
- ~5% are "cold" users (0–2 interactions) for cold-start testing

### `train_model.py` — Model Training Pipeline

**Input**: `data/cleaned_products.csv` + `data/orbit.db`  
**Output**: `models/svd_model.pkl` + `models/tfidf_bundle.pkl`

Trains and saves:
1. **TF-IDF Content Engine** — Vectorizes enriched product tags (title + category + price/quality buckets), saves sparse matrix + vectorizer as a joblib bundle
2. **SVD Collaborative Model** — Fetches interactions from DB, applies temporal decay, normalizes to [1,5] scale, trains a Surprise SVD model

---

## When to Re-Run

| Script | Re-run when... |
|--------|---------------|
| `setup_data.py` | You change `TARGET_DATASET_SIZE` or get a new raw CSV |
| `seed_interactions.py` | You want fresh mock data or change the user count |
| `train_model.py` | After re-running either of the above scripts |
