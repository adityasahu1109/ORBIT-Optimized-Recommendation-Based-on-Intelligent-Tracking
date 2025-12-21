import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import torch
import joblib
import os

# Define where we want to save the optimized model
MODEL_PATH = "models/content_engine.pkl"

class ContentEngine:
    def __init__(self, data_path="data/cleaned_products.csv"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Content Engine initializing on device: {self.device}")

        # --- OPTIMIZATION START ---
        # 1. Check if we have a saved model to load fast
        if os.path.exists(MODEL_PATH):
            print(f"⚡ Loading cached Content Engine from {MODEL_PATH}...")
            saved_data = joblib.load(MODEL_PATH)
            
            self.df = saved_data['df']
            self.vectorizer = saved_data['vectorizer']
            self.tfidf_matrix = saved_data['tfidf_matrix']
            print("✅ Model loaded successfully.")
            
        else:
            # 2. If no saved model, build it from scratch (The slow part)
            print("⚠️ No cache found. Building Content Engine from scratch...")
            self.df = pd.read_csv(data_path)
            
            # Create Tags
            self.df['tags'] = self.df['title'] + " " + self.df['categoryName']
            self.df['tags'] = self.df['tags'].fillna("")

            # Vectorize
            print("Vectorizing product text (this takes time)...")
            self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df['tags'])
            
            # SAVE IT! (So we never have to wait again)
            print(f"💾 Saving model to {MODEL_PATH} for future speed...")
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            joblib.dump({
                'df': self.df,
                'vectorizer': self.vectorizer,
                'tfidf_matrix': self.tfidf_matrix
            }, MODEL_PATH)
            print("✅ Model saved.")

        # --- TENSOR PREP ---
        # We do this part every time because moving data to GPU is fast,
        # but pickling GPU tensors can sometimes cause errors across different machines.
        print("Moving data to GPU...")
        tfidf_dense = self.tfidf_matrix.toarray()
        self.tfidf_tensor = torch.tensor(tfidf_dense, dtype=torch.float32).to(self.device)
        self.tfidf_tensor = torch.nn.functional.normalize(self.tfidf_tensor, p=2, dim=1)

    def search_products(self, query, k=10):
        """
        Simple keyword search.
        """
        query = query.lower()
        results = self.df[self.df['title'].str.lower().str.contains(query, na=False)]
        results = results.sort_values(by='reviews', ascending=False).head(k)
        return results[['asin', 'title', 'categoryName', 'price', 'stars', 'reviews']].to_dict(orient='records')

    def find_similar_products(self, product_id, k=5):
        """
        Given a product ID (ASIN), find the top K most similar items.
        """
        idx = self.df.index[self.df['asin'] == product_id].tolist()
        if not idx:
            return []
        idx = idx[0]
        
        # Get vector for this product
        query_vec = self.tfidf_tensor[idx].unsqueeze(0)
        
        # Calculate Cosine Similarity
        cosine_scores = torch.mm(query_vec, self.tfidf_tensor.transpose(0, 1))
        
        # Get Top K
        scores, indices = torch.topk(cosine_scores, k=k+1)
        
        indices = indices.cpu().numpy().flatten()
        scores = scores.cpu().numpy().flatten()
        
        results = []
        for i in range(1, len(indices)):
            item_idx = indices[i]
            results.append({
                "asin": self.df.iloc[item_idx]['asin'],
                "title": self.df.iloc[item_idx]['title'],
                "score": float(scores[i])
            })
            
        return results

# Quick Test
if __name__ == "__main__":
    # First run will be slow (Training), Second run will be fast (Loading)
    engine = ContentEngine()