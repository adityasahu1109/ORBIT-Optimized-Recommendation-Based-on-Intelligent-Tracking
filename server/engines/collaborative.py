"""
SVD-based Collaborative Filtering engine.

Train-once architecture:
    1. Run `scripts/train_model.py` to train and save the SVD model.
    2. On server startup, the model is loaded from disk — no retraining.
    3. New interactions are used for the user profile (via the recommendation
       orchestrator), but the SVD model itself is static until manually retrained.

Key improvements over the old system:
    - Temporal decay: recent interactions matter more
    - Additive aggregation: repeated views accumulate signal
    - Proper [1.0, 5.0] rating scale normalization
"""

import os
import pandas as pd
import numpy as np
from math import exp
from datetime import datetime, timezone

from server.engines.base import BaseEngine
from server.config import (
    SVD_MODEL_PATH,
    INTERACTION_WEIGHTS,
    DECAY_HALFLIFE_DAYS,
    SVD_N_FACTORS,
    SVD_N_EPOCHS,
    SVD_LR,
    SVD_REG,
)


class CollaborativeEngine(BaseEngine):
    def __init__(self):
        self.model = None
        self.initialize()

    def get_name(self) -> str:
        return "CollaborativeEngine"

    def initialize(self) -> None:
        """Load the pre-trained SVD model from disk."""
        if os.path.exists(SVD_MODEL_PATH):
            from surprise import dump as surprise_dump
            print(f"[{self.get_name()}] Loading SVD model from {SVD_MODEL_PATH}...")
            _, self.model = surprise_dump.load(SVD_MODEL_PATH)
            print(f"[{self.get_name()}] ✅ Model loaded.")
        else:
            print(
                f"[{self.get_name()}] ⚠️  No saved model found at {SVD_MODEL_PATH}. "
                f"Run `python -m scripts.train_model` to train first."
            )

    # ──────────────────────────────────────────────
    # PREDICTION
    # ──────────────────────────────────────────────

    def predict_score(self, user_id: str, product_id: str) -> float:
        """
        Predict how much a user would like a product (1.0–5.0 scale).
        Returns the global mean (~3.0) if the model isn't loaded.
        """
        if self.model is None:
            return 3.0  # Neutral fallback
        prediction = self.model.predict(str(user_id), str(product_id))
        return prediction.est

    # ──────────────────────────────────────────────
    # TRAINING (called from scripts/train_model.py)
    # ──────────────────────────────────────────────

    @staticmethod
    def build_training_data_from_db() -> pd.DataFrame:
        """
        Fetch interactions from DB, apply temporal decay and additive
        aggregation, return a DataFrame ready for Surprise.

        Returns:
            DataFrame with columns [user_id, product_id, score]
            where score is in [1.0, 5.0]
        """
        from server.db.engine import SessionLocal
        from server.db.models import Interaction

        db = SessionLocal()
        try:
            interactions = db.query(Interaction).all()
        finally:
            db.close()

        if not interactions:
            print("⚠️  No interactions in database.")
            return pd.DataFrame(columns=["user_id", "product_id", "score"])

        now = datetime.now(timezone.utc)
        records = []
        for ix in interactions:
            # Base weight from interaction type
            base_weight = INTERACTION_WEIGHTS.get(ix.interaction_type, 1.0)

            # Temporal decay: half-life decay so older actions matter less
            ts = ix.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            days_ago = max((now - ts).total_seconds() / 86400, 0)
            decay = exp(-0.693 * days_ago / DECAY_HALFLIFE_DAYS)

            records.append({
                "user_id": ix.user_id,
                "product_id": ix.product_id,
                "decayed_score": base_weight * decay,
            })

        df = pd.DataFrame(records)

        # Additive aggregation: if a user viewed 5 times then bought,
        # all signals accumulate instead of just keeping max
        df = df.groupby(["user_id", "product_id"], as_index=False)["decayed_score"].sum()

        # Normalize to [1.0, 5.0] scale for SVD
        min_score = df["decayed_score"].min()
        max_score = df["decayed_score"].max()

        if max_score > min_score:
            df["score"] = 1.0 + 4.0 * (df["decayed_score"] - min_score) / (max_score - min_score)
        else:
            df["score"] = 3.0  # All scores equal — neutral

        return df[["user_id", "product_id", "score"]]

    @staticmethod
    def train_and_save():
        """Train SVD model and save to disk. Called from scripts/train_model.py."""
        from surprise import Dataset, Reader, SVD as SurpriseSVD
        from surprise import dump as surprise_dump

        print("Building training data with temporal decay...")
        df = CollaborativeEngine.build_training_data_from_db()

        if df.empty:
            print("Cannot train — no data.")
            return

        print(f"Training SVD on {len(df)} user-item pairs...")

        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(df[["user_id", "product_id", "score"]], reader)
        trainset = data.build_full_trainset()

        model = SurpriseSVD(
            n_factors=SVD_N_FACTORS,
            n_epochs=SVD_N_EPOCHS,
            lr_all=SVD_LR,
            reg_all=SVD_REG,
        )
        model.fit(trainset)

        os.makedirs(os.path.dirname(SVD_MODEL_PATH), exist_ok=True)
        surprise_dump.dump(SVD_MODEL_PATH, algo=model)
        print(f"✅ SVD model saved to {SVD_MODEL_PATH}")
