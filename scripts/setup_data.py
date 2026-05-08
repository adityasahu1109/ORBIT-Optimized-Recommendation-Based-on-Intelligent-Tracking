"""
Data cleaning pipeline.

Reads the raw Amazon products CSV, performs stratified sampling to create
a balanced dataset, and saves the cleaned output.

Usage:
    python -m scripts.setup_data

Note: Does NOT modify the original amazon_products.csv.
"""

import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from server.config import RAW_CSV_PATH, CLEANED_CSV_PATH, TARGET_DATASET_SIZE


def clean_data():
    print(f"Loading raw data from {RAW_CSV_PATH}...")

    if not os.path.exists(RAW_CSV_PATH):
        print(f"[ERROR] {RAW_CSV_PATH} not found.")
        print("Please place the amazon_products.csv file in the data/ directory.")
        return

    df = pd.read_csv(RAW_CSV_PATH)
    print(f"Original dataset: {len(df):,} rows")

    # -- Basic Cleaning --
    print("Cleaning missing values...")
    df = df.dropna(subset=["asin", "title", "categoryName"])

    # Ensure numeric types
    df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce").fillna(0).astype(int)
    df["stars"] = pd.to_numeric(df["stars"], errors="coerce").fillna(0.0)
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0)
    df["boughtInLastMonth"] = pd.to_numeric(df["boughtInLastMonth"], errors="coerce").fillna(0).astype(int)

    # -- Stratified Sampling --
    unique_cats = df["categoryName"].unique()
    num_cats = len(unique_cats)
    print(f"Found {num_cats} unique categories.")

    limit_per_cat = max(1, int(TARGET_DATASET_SIZE / num_cats))
    print(f"Sampling top {limit_per_cat} products per category...")

    # Use list comprehension to avoid FutureWarning with groupby.apply
    sampled_frames = []
    for cat, group in df.groupby("categoryName"):
        sampled_frames.append(
            group.sort_values(by="reviews", ascending=False).head(limit_per_cat)
        )
    df_stratified = pd.concat(sampled_frames, ignore_index=True)

    # -- Save --
    os.makedirs(os.path.dirname(CLEANED_CSV_PATH), exist_ok=True)
    df_stratified.to_csv(CLEANED_CSV_PATH, index=False)

    print(f"[OK] Saved {len(df_stratified):,} products to {CLEANED_CSV_PATH}")
    print(f"     Category distribution preserved across {num_cats} categories.")


if __name__ == "__main__":
    clean_data()
