"""
Mock interaction data generator.

Creates realistic interaction patterns for testing:
    - Each user has 2-3 preferred categories (not just 1)
    - Interaction funnel: many views → fewer clicks → fewer carts → few purchases
    - Temporal spread over 30 days with recency bias
    - Includes "cold" users with 0-2 interactions for cold-start testing

Usage:
    python -m scripts.seed_interactions
"""

import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import random
from datetime import datetime, timedelta, timezone

from server.db.engine import SessionLocal, init_db
from server.db.models import Interaction
from server.config import (
    CLEANED_CSV_PATH,
    MOCK_NUM_USERS,
    MOCK_MIN_INTERACTIONS,
    MOCK_MAX_INTERACTIONS,
)


# Interaction types and their relative probabilities
ACTION_TYPES = ["view", "click", "add_to_cart", "purchase"]
ACTION_PROBS = [0.50, 0.28, 0.15, 0.07]


def generate_mock_data():
    print("Loading product catalog...")
    df = pd.read_csv(CLEANED_CSV_PATH)
    categories = df["categoryName"].unique().tolist()
    all_asins = df["asin"].tolist()

    # Build category → ASIN lookup
    cat_products = {
        cat: df[df["categoryName"] == cat]["asin"].tolist()
        for cat in categories
    }

    print(f"Generating interactions for {MOCK_NUM_USERS} users...")

    init_db()
    db = SessionLocal()

    # Clear existing mock data (user IDs 1001-1100)
    db.query(Interaction).filter(
        Interaction.user_id.between("1001", str(1000 + MOCK_NUM_USERS))
    ).delete(synchronize_session=False)
    db.commit()

    buffer = []
    user_counts = {}  # Track interaction counts per user
    now = datetime.now(timezone.utc)

    for user_idx in range(MOCK_NUM_USERS):
        user_id = str(1001 + user_idx)

        # -- Cold users: ~5% of users have minimal interactions --
        if random.random() < 0.05:
            num_actions = random.randint(0, 2)
        else:
            num_actions = random.randint(MOCK_MIN_INTERACTIONS, MOCK_MAX_INTERACTIONS)

        user_counts[user_id] = num_actions

        # -- Assign 2-3 favorite categories --
        num_fav_cats = random.randint(2, 3)
        fav_cats = random.sample(categories, min(num_fav_cats, len(categories)))
        fav_asins = []
        for c in fav_cats:
            fav_asins.extend(cat_products.get(c, []))

        for _ in range(num_actions):
            # 75% chance to interact with favorite categories, 25% random
            if random.random() < 0.75 and fav_asins:
                product_id = random.choice(fav_asins)
            else:
                product_id = random.choice(all_asins)

            action = random.choices(ACTION_TYPES, weights=ACTION_PROBS, k=1)[0]

            # Temporal spread: more recent interactions are more likely
            # Using beta distribution for recency bias
            days_ago = int(random.betavariate(2, 5) * 30)
            timestamp = now - timedelta(
                days=days_ago,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            buffer.append(Interaction(
                user_id=user_id,
                product_id=product_id,
                interaction_type=action,
                timestamp=timestamp,
            ))

    # Bulk save
    print(f"Saving {len(buffer):,} interactions to database...")
    db.add_all(buffer)
    db.commit()
    db.close()

    # Stats (use tracked counts, not ORM objects)
    cold_users = sum(1 for count in user_counts.values() if count <= 2)
    print(f"[OK] Done!")
    print(f"     Total interactions: {len(buffer):,}")
    print(f"     Cold users (0-2 interactions): {cold_users}")
    print(f"     Active users: {MOCK_NUM_USERS - cold_users}")


if __name__ == "__main__":
    generate_mock_data()
