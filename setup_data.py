import pandas as pd
import os

# Configuration
INPUT_FILE = "data/amazon_products.csv"
OUTPUT_FILE = "data/cleaned_products.csv"
TARGET_TOTAL = 50000  # Target dataset size

def clean_data():
    print(f"Loading data from {INPUT_FILE}...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    # Load data
    df = pd.read_csv(INPUT_FILE)
    print(f"Original dataset size: {len(df)} rows")

    # 1. Basic Cleaning
    print("Cleaning missing values...")
    df = df.dropna(subset=['asin', 'title', 'categoryName'])
    
    # Ensure numeric types for sorting
    df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce').fillna(0)
    df['stars'] = pd.to_numeric(df['stars'], errors='coerce').fillna(0.0)

    # 2. Identify Categories
    unique_cats = df['categoryName'].unique()
    num_cats = len(unique_cats)
    print(f"Found {num_cats} unique categories.")

    # 3. Calculate Limit Per Category
    # We divide the target total by the number of categories to get a fair share
    limit_per_cat = int(TARGET_TOTAL / num_cats)
    print(f"Aiming for top {limit_per_cat} products per category...")

    # 4. Stratified Sampling (Top N from EACH category)
    # We group by category, sort each group by reviews, and take the top N
    df_stratified = df.groupby('categoryName', group_keys=False).apply(
        lambda x: x.sort_values(by='reviews', ascending=False).head(limit_per_cat)
    )

    # 5. Save
    df_stratified.to_csv(OUTPUT_FILE, index=False)
    
    print(f"Done! Saved {len(df_stratified)} products to {OUTPUT_FILE}")
    print("Category distribution preserved.")

if __name__ == "__main__":
    clean_data()