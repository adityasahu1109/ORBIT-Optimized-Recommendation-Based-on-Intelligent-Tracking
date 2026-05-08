"""
One-time model training script.

Trains and saves:
    1. SVD collaborative filtering model (from interaction data)
    2. TF-IDF content engine bundle (from product catalog)

These models are loaded from disk on every server startup.
Only re-run this script when you want to refresh the models
(e.g., after adding new interactions or updating the product catalog).

Usage:
    python -m scripts.train_model
"""

import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    print("=" * 60)
    print("  ORBIT — Model Training Pipeline")
    print("=" * 60)

    # ── Step 1: Build TF-IDF Content Engine ──
    print("\n--- Step 1: Building TF-IDF Content Engine ---\n")
    from server.engines.content import ContentEngine
    ContentEngine.build_and_save()

    # ── Step 2: Train SVD Collaborative Model ──
    print("\n--- Step 2: Training SVD Collaborative Model ---\n")
    from server.engines.collaborative import CollaborativeEngine
    CollaborativeEngine.train_and_save()

    print("\n" + "=" * 60)
    print("  ✅ All models trained and saved!")
    print("  You can now start the server with:")
    print("    uvicorn server.main:app --reload")
    print("=" * 60)


if __name__ == "__main__":
    main()
