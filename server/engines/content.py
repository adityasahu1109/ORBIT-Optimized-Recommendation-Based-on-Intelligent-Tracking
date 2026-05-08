"""
Content-based similarity engine using TF-IDF.

Train-once architecture:
    1. The TF-IDF vectorizer + matrix are built once by `scripts/train_model.py`
       and saved as a pickle bundle.
    2. On server startup, the bundle is loaded from disk — no re-vectorizing.
    3. Similarity is computed on sparse matrices using sklearn (no PyTorch needed).

Key improvements over old system:
    - No PyTorch / dense matrix conversion (saves ~900MB RAM)
    - Enriched tags: title + category + price_bucket + quality_bucket
    - Sparse cosine similarity via sklearn
"""

import os
import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from server.engines.base import BaseEngine
from server.config import CLEANED_CSV_PATH, TFIDF_BUNDLE_PATH, TFIDF_MAX_FEATURES


class ContentEngine(BaseEngine):
    def __init__(self):
        self.df: pd.DataFrame = pd.DataFrame()
        self.vectorizer: TfidfVectorizer | None = None
        self.tfidf_matrix = None
        self.initialize()

    def get_name(self) -> str:
        return "ContentEngine"

    def initialize(self) -> None:
        """Load pre-built TF-IDF bundle from disk."""
        if os.path.exists(TFIDF_BUNDLE_PATH):
            print(f"[{self.get_name()}] Loading TF-IDF bundle from cache...")
            bundle = joblib.load(TFIDF_BUNDLE_PATH)
            self.df = bundle["df"]
            self.vectorizer = bundle["vectorizer"]
            self.tfidf_matrix = bundle["tfidf_matrix"]
            print(f"[{self.get_name()}] ✅ Loaded ({self.tfidf_matrix.shape[0]} products, "
                  f"{self.tfidf_matrix.shape[1]} features).")
        else:
            print(
                f"[{self.get_name()}] ⚠️  No TF-IDF bundle at {TFIDF_BUNDLE_PATH}. "
                f"Run `python -m scripts.train_model` to build it."
            )

    # ──────────────────────────────────────────────
    # SIMILARITY
    # ──────────────────────────────────────────────

    def find_similar_products(self, product_asin: str, k: int = 5) -> list[dict]:
        """
        Given a product ASIN, find the top K most similar products
        based on TF-IDF cosine similarity.
        """
        if self.tfidf_matrix is None:
            return []

        idx_list = self.df.index[self.df["asin"] == product_asin].tolist()
        if not idx_list:
            return []

        idx = idx_list[0]

        # Compute cosine similarity of this product against all others
        query_vec = self.tfidf_matrix[idx]
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Get top K+1 (includes self), then skip self
        top_indices = np.argsort(scores)[::-1][1: k + 1]

        results = []
        for i in top_indices:
            row = self.df.iloc[i]
            results.append({
                "asin": row["asin"],
                "title": row["title"],
                "categoryName": row["categoryName"],
                "price": float(row["price"]),
                "imgUrl": row.get("imgUrl", ""),
                "stars": float(row["stars"]),
                "reviews": int(row["reviews"]),
                "score": float(scores[i]),
            })
        return results

    # ──────────────────────────────────────────────
    # BUILD (called from scripts/train_model.py)
    # ──────────────────────────────────────────────

    @staticmethod
    def build_and_save():
        """Build the TF-IDF matrix and save to disk."""
        print("Building TF-IDF content engine...")

        df = pd.read_csv(CLEANED_CSV_PATH)

        # --- Enriched tags ---
        # Price buckets
        price_bins = [0, 15, 50, 150, float("inf")]
        price_labels = ["budget", "mid_range", "premium", "luxury"]
        df["price_bucket"] = pd.cut(df["price"], bins=price_bins, labels=price_labels)

        # Quality buckets
        star_bins = [0, 2.5, 3.5, 4.2, 5.01]
        star_labels = ["low_rated", "average", "well_rated", "top_rated"]
        df["quality_bucket"] = pd.cut(df["stars"], bins=star_bins, labels=star_labels)

        # Bestseller flag as text token
        df["bestseller_token"] = df["isBestSeller"].apply(
            lambda x: "bestseller" if x else ""
        )

        # Combine: title + category + price bucket + quality bucket + bestseller
        df["tags"] = (
            df["title"].fillna("")
            + " " + df["categoryName"].fillna("")
            + " " + df["price_bucket"].astype(str)
            + " " + df["quality_bucket"].astype(str)
            + " " + df["bestseller_token"]
        )

        # Vectorize
        print(f"Vectorizing with max_features={TFIDF_MAX_FEATURES}...")
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=TFIDF_MAX_FEATURES,
        )
        tfidf_matrix = vectorizer.fit_transform(df["tags"])

        # Save bundle (sparse matrix stays sparse — no dense conversion!)
        os.makedirs(os.path.dirname(TFIDF_BUNDLE_PATH), exist_ok=True)
        bundle = {
            "df": df,
            "vectorizer": vectorizer,
            "tfidf_matrix": tfidf_matrix,  # scipy sparse
        }
        joblib.dump(bundle, TFIDF_BUNDLE_PATH)
        print(f"✅ TF-IDF bundle saved to {TFIDF_BUNDLE_PATH} "
              f"(shape: {tfidf_matrix.shape})")
