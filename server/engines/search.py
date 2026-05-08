"""
Smart search engine using TF-IDF relevance scoring.

Replaces the old substring-matching search with proper information retrieval:
    - Query is vectorized through the same TF-IDF vectorizer as products
    - Cosine similarity gives a relevance score for every product
    - Results are ranked by: relevance * 0.7 + quality * 0.3
    - Minimum similarity threshold filters garbage results
    - Regex-safe: no str.contains(), immune to special characters

This engine reuses the TF-IDF bundle built by the ContentEngine,
so it shares the same vectorizer and matrix. No separate training needed.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from server.engines.base import BaseEngine
from server.engines.content import ContentEngine
from server.config import SEARCH_RELEVANCE_WEIGHT, SEARCH_QUALITY_WEIGHT, SEARCH_MIN_SIMILARITY


class SearchEngine(BaseEngine):
    def __init__(self, content_engine: ContentEngine):
        """
        Takes a reference to the ContentEngine so they share the same
        TF-IDF vectorizer and matrix (no duplicate data).
        """
        self.content = content_engine
        self.quality_scores: np.ndarray | None = None
        self.initialize()

    def get_name(self) -> str:
        return "SearchEngine"

    def initialize(self) -> None:
        """Precompute normalized quality scores for all products."""
        if self.content.df.empty:
            print(f"[{self.get_name()}] ⚠️  ContentEngine has no data — search won't work.")
            return

        df = self.content.df

        # Quality = bayesian_stars * log_reviews (combined quality signal)
        reviews = np.log1p(df["reviews"].values.astype(float))
        stars = df["stars"].values.astype(float)

        raw_quality = stars * reviews

        # Normalize to [0, 1]
        qmin, qmax = raw_quality.min(), raw_quality.max()
        if qmax > qmin:
            self.quality_scores = (raw_quality - qmin) / (qmax - qmin)
        else:
            self.quality_scores = np.zeros(len(df))

        print(f"[{self.get_name()}] ✅ Ready — quality scores precomputed.")

    # ──────────────────────────────────────────────
    # SEARCH
    # ──────────────────────────────────────────────

    def search(self, query: str, k: int = 20) -> list[dict]:
        """
        Search products by query string.

        Args:
            query: User's search text (e.g., "wireless headphones")
            k: Maximum number of results to return

        Returns:
            List of product dicts sorted by hybrid score (relevance + quality)
        """
        if self.content.vectorizer is None or self.content.tfidf_matrix is None:
            return []

        if not query or not query.strip():
            return []

        # Vectorize the query through the same TF-IDF pipeline
        query_vec = self.content.vectorizer.transform([query.lower()])

        # Cosine similarity: query vs all products
        relevance_scores = cosine_similarity(query_vec, self.content.tfidf_matrix).flatten()

        # Filter out results below the minimum similarity threshold
        valid_mask = relevance_scores >= SEARCH_MIN_SIMILARITY
        valid_indices = np.where(valid_mask)[0]

        if len(valid_indices) == 0:
            return []

        # Hybrid scoring: relevance + quality
        hybrid_scores = (
            SEARCH_RELEVANCE_WEIGHT * relevance_scores[valid_indices]
            + SEARCH_QUALITY_WEIGHT * self.quality_scores[valid_indices]
        )

        # Get top K from valid results
        top_local_indices = np.argsort(hybrid_scores)[::-1][:k]
        top_global_indices = valid_indices[top_local_indices]

        # Build results
        df = self.content.df
        results = []
        for i, global_idx in enumerate(top_global_indices):
            row = df.iloc[global_idx]
            results.append({
                "asin": row["asin"],
                "title": row["title"],
                "categoryName": row["categoryName"],
                "price": float(row["price"]),
                "stars": float(row["stars"]),
                "reviews": int(row["reviews"]),
                "imgUrl": row.get("imgUrl", ""),
                "relevance_score": float(relevance_scores[global_idx]),
                "quality_score": float(self.quality_scores[global_idx]),
                "score": float(hybrid_scores[top_local_indices[i]]),
            })

        return results
