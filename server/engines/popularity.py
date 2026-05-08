"""
Popularity-based recommendation engine.

Uses Bayesian-averaged star ratings combined with review volume and
trending signals to rank products. Used for cold-start users (no history)
and as a candidate generator for the hybrid pipeline.
"""

import pandas as pd
import numpy as np

from server.engines.base import BaseEngine
from server.config import CLEANED_CSV_PATH, BAYESIAN_MIN_VOTES


class PopularityEngine(BaseEngine):
    def __init__(self):
        self.df: pd.DataFrame = pd.DataFrame()
        self.initialize()

    def get_name(self) -> str:
        return "PopularityEngine"

    def initialize(self) -> None:
        print(f"[{self.get_name()}] Loading product catalog...")
        self.df = pd.read_csv(CLEANED_CSV_PATH)
        self._compute_scores()
        print(f"[{self.get_name()}] ✅ Ready — {len(self.df)} products scored.")

    # ──────────────────────────────────────────────
    # SCORING
    # ──────────────────────────────────────────────

    def _compute_scores(self):
        """
        Bayesian popularity score that prevents low-vote outliers
        from dominating the rankings.

        Formula:
            bayesian_stars = (R * v + C * m) / (v + m)
            where:
                R = product's average star rating
                v = product's number of reviews
                C = global mean star rating across all products
                m = minimum votes threshold (from config)

            popularity = bayesian_stars * 2.0
                       + log1p(reviews) * 0.5
                       + log1p(boughtInLastMonth) * 0.3
                       + (2.0 if isBestSeller)
        """
        C = self.df["stars"].mean()  # Global average ~4.1
        m = BAYESIAN_MIN_VOTES

        v = self.df["reviews"]
        R = self.df["stars"]

        # Bayesian average — pulls low-review products toward the global mean
        self.df["bayesian_stars"] = (R * v + C * m) / (v + m)

        # Log-scaled review volume (prevents 100K-review products from dominating)
        self.df["log_reviews"] = np.log1p(v)

        # Trending signal
        self.df["log_trending"] = np.log1p(self.df["boughtInLastMonth"])

        # Combined score
        self.df["popularity_score"] = (
            self.df["bayesian_stars"] * 2.0
            + self.df["log_reviews"] * 0.5
            + self.df["log_trending"] * 0.3
            + self.df["isBestSeller"].apply(lambda x: 2.0 if x else 0.0)
        )

        # Pre-sort for fast top-K retrieval
        self.df = self.df.sort_values(by="popularity_score", ascending=False).reset_index(drop=True)

    # ──────────────────────────────────────────────
    # PUBLIC API
    # ──────────────────────────────────────────────

    def get_top_products(self, k: int = 10) -> list[dict]:
        """Return the top K globally popular products."""
        return self._to_product_dicts(self.df.head(k))

    def get_top_in_category(self, category: str, k: int = 10) -> list[dict]:
        """Return the top K popular products within a specific category."""
        cat_df = self.df[self.df["categoryName"] == category].head(k)
        return self._to_product_dicts(cat_df)

    def get_product_info(self, asin: str) -> dict | None:
        """Look up a single product by ASIN."""
        row = self.df[self.df["asin"] == asin]
        if row.empty:
            return None
        return self._row_to_dict(row.iloc[0])

    def get_product_category(self, asin: str) -> str | None:
        """Get the category of a product by ASIN."""
        row = self.df[self.df["asin"] == asin]
        if row.empty:
            return None
        return row.iloc[0]["categoryName"]

    # ──────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────

    def _to_product_dicts(self, subset: pd.DataFrame) -> list[dict]:
        """Convert a DataFrame subset to a list of product dictionaries."""
        return [self._row_to_dict(row) for _, row in subset.iterrows()]

    @staticmethod
    def _row_to_dict(row: pd.Series) -> dict:
        return {
            "asin": row["asin"],
            "title": row["title"],
            "categoryName": row["categoryName"],
            "price": float(row["price"]),
            "stars": float(row["stars"]),
            "reviews": int(row["reviews"]),
            "imgUrl": row.get("imgUrl", ""),
            "isBestSeller": bool(row.get("isBestSeller", False)),
            "boughtInLastMonth": int(row.get("boughtInLastMonth", 0)),
            "popularity_score": float(row.get("popularity_score", 0.0)),
        }
