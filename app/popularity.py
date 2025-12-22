import pandas as pd
import numpy as np

class PopularityRecommender:
    def __init__(self, data_path="data/cleaned_products.csv"):
        """
        Initialize the Popularity Engine.
        It loads the cleaned product catalog and calculates a popularity score
        for every product immediately on startup.
        """
        self.df = pd.read_csv(data_path)
        self._compute_popularity_score()
    
    def _compute_popularity_score(self):
        """
        Calculates a 'score' for each product based on:
        1. Star Rating (0-5)
        2. Number of Reviews (Trust signal)
        3. Bought In Last Month (Trending signal)
        4. Best Seller Status (Quality signal)
        """
        # normalize review count (log scale to prevent huge numbers from dominating)
        # We add 1 to avoid log(0)
        self.df['log_reviews'] = np.log1p(self.df['reviews'])
        
        # Weighted Scoring Formula:
        # Score = (Stars * 2) + (Log_Reviews * 0.5) + (Bought_Last_Month * 0.01)
        # We give high weight to Stars and Reviews.
        
        self.df['popularity_score'] = (
            (self.df['stars'] * 2.0) + 
            (self.df['log_reviews'] * 0.5) + 
            (self.df['boughtInLastMonth'] * 0.01)
        )
        
        # Add a bonus for Best Sellers
        # If isBestSeller is True, add a fixed bonus (e.g., 2.0 points)
        self.df['popularity_score'] += self.df['isBestSeller'].apply(lambda x: 2.0 if x == True else 0.0)
        
        # Sort the dataframe once so we can quickly slice it later
        self.df = self.df.sort_values(by='popularity_score', ascending=False)

    def get_recommendations(self, k=10):
        """
        Returns the top K popular products.
        Used for Cold Start (New Users).
        """
        top_items = self.df.head(k)
        return top_items[['asin', 'title', 'categoryName', 'price', 'stars', 'reviews', 'imgUrl']].to_dict(orient='records')

# Quick test if running this file directly
if __name__ == "__main__":
    pop_engine = PopularityRecommender()
    print(f"Loaded {len(pop_engine.df)} products.")
    
    print("\n--- Top 5 Popular Recommendations ---")
    recs = pop_engine.get_recommendations(5)
    for i, item in enumerate(recs, 1):
        print(f"{i}. {item['title'][:60]}... | Stars: {item['stars']} | Reviews: {item['reviews']}")