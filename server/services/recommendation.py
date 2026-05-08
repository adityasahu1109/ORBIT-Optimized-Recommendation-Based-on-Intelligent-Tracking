"""
Recommendation Orchestrator.

This is the brain of ORBIT. It combines signals from multiple engines
to produce the final recommendation list.

Three strategies:
    1. COLD START — user has no history → popularity-ranked, diverse results
    2. PERSONALIZED — user has history → weighted user profile + SVD + diversity
    3. CONTEXT-AWARE — user is viewing a product → content-based similarity

Key design decisions (fixing the old system):
    - Category profile built from last 20 interactions with temporal decay
      (not just the last one)
    - Category boost is proportional to profile weight, not a flat +1.5
    - A single view contributes ~5% to the profile (1/20), making a max
      boost contribution of only ~0.012 to the final score
    - Diversity enforcement ensures at least 3 categories in top results
"""

from math import exp
from datetime import datetime, timezone
from collections import defaultdict

from sqlalchemy.orm import Session

from server.engines.popularity import PopularityEngine
from server.engines.collaborative import CollaborativeEngine
from server.engines.content import ContentEngine
from server.services.interaction import InteractionService
from server.config import (
    INTERACTION_WEIGHTS,
    DECAY_HALFLIFE_DAYS,
    MAX_CATEGORY_BOOST,
    SVD_WEIGHT,
    CATEGORY_BOOST_WEIGHT,
    MIN_DIVERSITY_CATEGORIES,
    USER_HISTORY_LIMIT,
)


class RecommendationService:
    def __init__(
        self,
        popularity: PopularityEngine,
        collaborative: CollaborativeEngine,
        content: ContentEngine,
    ):
        self.popularity = popularity
        self.collaborative = collaborative
        self.content = content

    # ──────────────────────────────────────────────
    # MAIN ENTRY POINT
    # ──────────────────────────────────────────────

    def get_recommendations(
        self,
        db: Session,
        user_id: str,
        product_id_viewed: str | None = None,
        n: int = 10,
    ) -> dict:
        """
        Generate recommendations for a user.

        Returns:
            {
                "user_id": str,
                "strategy": "cold_start" | "personalized" | "content_based",
                "recommendations": [...]
            }
        """

        # ── SCENARIO 1: Context-Aware (viewing a specific product) ──
        if product_id_viewed:
            return self._context_aware(user_id, product_id_viewed, n)

        # ── SCENARIO 2: Check if user has history ──
        has_history = InteractionService.has_history(db, user_id)

        if not has_history:
            return self._cold_start(user_id, n)
        else:
            return self._personalized(db, user_id, n)

    # ──────────────────────────────────────────────
    # STRATEGY 1: COLD START
    # ──────────────────────────────────────────────

    def _cold_start(self, user_id: str, n: int) -> dict:
        """
        No history → return popular products with category diversity.
        """
        candidates = self.popularity.get_top_products(k=n * 3)
        diversified = self._enforce_diversity(candidates, n)

        results = []
        for item in diversified:
            results.append({
                **self._base_product_dict(item),
                "score": item.get("popularity_score", 0.0),
                "reason": "Trending now",
            })

        return {
            "user_id": user_id,
            "strategy": "cold_start",
            "recommendations": results[:n],
        }

    # ──────────────────────────────────────────────
    # STRATEGY 2: PERSONALIZED
    # ──────────────────────────────────────────────

    def _personalized(self, db: Session, user_id: str, n: int) -> dict:
        """
        Has history → build user profile, generate candidates,
        score with SVD + bounded category boost, enforce diversity.
        """
        # 1. Build category profile from recent interactions
        interactions = InteractionService.get_recent_interactions(
            db, user_id, limit=USER_HISTORY_LIMIT
        )
        category_profile = self._build_category_profile(interactions)

        # 2. Generate candidates
        candidates = self._generate_candidates(category_profile)

        # 3. Score each candidate
        scored = []
        for item in candidates:
            svd_score = self.collaborative.predict_score(user_id, item["asin"])

            # Category boost proportional to profile weight
            cat = item.get("categoryName", "")
            profile_weight = category_profile.get(cat, 0.0)
            category_boost = profile_weight * MAX_CATEGORY_BOOST

            # Weighted combination
            final_score = (SVD_WEIGHT * svd_score) + (CATEGORY_BOOST_WEIGHT * category_boost)

            # Determine reason
            if profile_weight > 0.15:
                reason = f"Based on your interest in {cat}"
            elif profile_weight > 0:
                reason = "Recommended for you"
            else:
                reason = "Popular pick"

            scored.append({
                **self._base_product_dict(item),
                "score": final_score,
                "reason": reason,
            })

        # 4. Sort and enforce diversity
        scored.sort(key=lambda x: x["score"], reverse=True)
        diversified = self._enforce_diversity(scored, n)

        return {
            "user_id": user_id,
            "strategy": "personalized",
            "recommendations": diversified[:n],
        }

    # ──────────────────────────────────────────────
    # STRATEGY 3: CONTEXT-AWARE
    # ──────────────────────────────────────────────

    def _context_aware(self, user_id: str, product_asin: str, n: int) -> dict:
        """
        User is viewing a product → return similar products.
        """
        similar = self.content.find_similar_products(product_asin, k=n)

        results = []
        for item in similar:
            results.append({
                **self._base_product_dict(item),
                "score": item.get("score", 0.0),
                "reason": "Similar to viewed product",
            })

        return {
            "user_id": user_id,
            "strategy": "content_based",
            "recommendations": results,
        }

    # ──────────────────────────────────────────────
    # USER PROFILE BUILDER
    # ──────────────────────────────────────────────

    def _build_category_profile(self, interactions) -> dict[str, float]:
        """
        Build a category weight distribution from recent interactions.

        Each interaction contributes:
            weight = interaction_type_weight * temporal_decay

        Returns:
            Dict mapping category_name → normalized weight (sums to 1.0)
        """
        now = datetime.now(timezone.utc)
        category_weights: dict[str, float] = defaultdict(float)

        for ix in interactions:
            # Look up category
            cat = self.popularity.get_product_category(ix.product_id)
            if not cat:
                continue

            # Interaction weight
            base_weight = INTERACTION_WEIGHTS.get(ix.interaction_type, 1.0)

            # Temporal decay
            ts = ix.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            days_ago = max((now - ts).total_seconds() / 86400, 0)
            decay = exp(-0.693 * days_ago / DECAY_HALFLIFE_DAYS)

            category_weights[cat] += base_weight * decay

        # Normalize to probability distribution
        total = sum(category_weights.values())
        if total > 0:
            return {cat: w / total for cat, w in category_weights.items()}
        return {}

    # ──────────────────────────────────────────────
    # CANDIDATE GENERATION
    # ──────────────────────────────────────────────

    def _generate_candidates(self, category_profile: dict[str, float]) -> list[dict]:
        """
        Generate a broad pool of candidate products:
            - Top 30 globally popular products
            - Top 10 from each of the user's top-3 preferred categories
        Deduplicated by ASIN.
        """
        seen = set()
        candidates = []

        # Global popular items
        for item in self.popularity.get_top_products(k=30):
            if item["asin"] not in seen:
                seen.add(item["asin"])
                candidates.append(item)

        # Category-specific items from user's top categories
        sorted_cats = sorted(category_profile.items(), key=lambda x: x[1], reverse=True)
        for cat, _ in sorted_cats[:3]:
            for item in self.popularity.get_top_in_category(cat, k=10):
                if item["asin"] not in seen:
                    seen.add(item["asin"])
                    candidates.append(item)

        return candidates

    # ──────────────────────────────────────────────
    # DIVERSITY ENFORCEMENT
    # ──────────────────────────────────────────────

    @staticmethod
    def _enforce_diversity(items: list[dict], n: int) -> list[dict]:
        """
        Ensure at least MIN_DIVERSITY_CATEGORIES distinct categories
        appear in the top N results. If the top N is too homogeneous,
        swap in next-best items from underrepresented categories.
        """
        if len(items) <= n:
            return items

        selected = []
        remaining = list(items)
        category_counts: dict[str, int] = defaultdict(int)

        # First pass: greedily pick top-scored items
        for item in remaining[:]:
            cat = item.get("categoryName", item.get("category", "Unknown"))
            selected.append(item)
            category_counts[cat] += 1
            remaining.remove(item)

            if len(selected) >= n:
                break

        # Check diversity
        if len(category_counts) >= MIN_DIVERSITY_CATEGORIES:
            return selected

        # Second pass: swap in items from new categories
        needed = MIN_DIVERSITY_CATEGORIES - len(category_counts)
        for item in remaining:
            cat = item.get("categoryName", item.get("category", "Unknown"))
            if cat not in category_counts:
                # Replace the last item from the most over-represented category
                most_common = max(category_counts, key=category_counts.get)
                for i in range(len(selected) - 1, -1, -1):
                    sc = selected[i].get("categoryName", selected[i].get("category", ""))
                    if sc == most_common and category_counts[most_common] > 1:
                        category_counts[most_common] -= 1
                        selected[i] = item
                        category_counts[cat] = 1
                        needed -= 1
                        break

                if needed <= 0:
                    break

        return selected

    # ──────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────

    @staticmethod
    def _base_product_dict(item: dict) -> dict:
        """Extract the standard product fields from a dict."""
        return {
            "asin": item.get("asin", ""),
            "title": item.get("title", ""),
            "category": item.get("categoryName", item.get("category", "Unknown")),
            "price": float(item.get("price", 0.0)),
            "imgUrl": item.get("imgUrl", ""),
            "stars": float(item.get("stars", 0.0)),
            "reviews": int(item.get("reviews", 0)),
        }
