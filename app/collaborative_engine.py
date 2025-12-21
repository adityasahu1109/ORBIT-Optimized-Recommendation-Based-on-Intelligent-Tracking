import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, Interaction
from surprise import Dataset, Reader, SVD
from surprise import dump
import os

# Path to save the model
MODEL_PATH = "models/svd_model.pkl"

class CollaborativeEngine:
    def __init__(self):
        print("Initializing Collaborative Engine...")
        self.model = None
        
        # Try to load existing model first
        if os.path.exists(MODEL_PATH):
            print(f"Loading SVD model from {MODEL_PATH}...")
            # surprise.dump.load returns a tuple (predictions, algorithm)
            _, self.model = dump.load(MODEL_PATH)
            print("✅ Model loaded successfully.")
        else:
            print("No saved model found. Training new one...")
            self.train_model()

    def _load_data_from_db(self):
        """
        Fetches interaction data and converts it to a User-Item Matrix.
        """
        db: Session = SessionLocal()
        query = db.query(Interaction).statement
        df = pd.read_sql(query, db.bind)
        db.close()
        
        if df.empty:
            print("Warning: No interactions found in DB.")
            return pd.DataFrame(columns=['user_id', 'product_id', 'score'])

        # Define weights
        weights = {
            'view': 1.0,
            'click': 2.0,
            'add_to_cart': 3.0,
            'purchase': 5.0
        }
        
        # Apply weights
        df['score'] = df['interaction_type'].map(weights)
        
        # Aggregate: If user views AND buys, take the max score
        df_final = df.groupby(['user_id', 'product_id'])['score'].max().reset_index()
        
        return df_final

    def train_model(self):
        """
        Trains the SVD algorithm and saves it to disk.
        """
        print("Loading data from database...")
        df = self._load_data_from_db()
        
        if df.empty:
            return

        print(f"Training SVD model on {len(df)} unique user-item interactions...")
        
        reader = Reader(rating_scale=(1, 5)) 
        data = Dataset.load_from_df(df[['user_id', 'product_id', 'score']], reader)
        
        trainset = data.build_full_trainset()
        self.model = SVD(n_factors=50, n_epochs=20, lr_all=0.005, reg_all=0.02)
        self.model.fit(trainset)
        
        print("SVD Model trained successfully.")
        
        # SAVE THE MODEL
        print(f"Saving model to {MODEL_PATH}...")
        # We ensure the folder exists first
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        dump.dump(MODEL_PATH, algo=self.model)
        print("✅ Model saved.")

    def predict_score(self, user_id, product_id):
        """
        Predicts how much a user will like a specific product (1-5 scale).
        """
        if self.model is None:
            return 0.0
        prediction = self.model.predict(str(user_id), str(product_id))
        return prediction.est

# Quick Test
if __name__ == "__main__":
    cf_engine = CollaborativeEngine()
    # Force retrain to test saving
    cf_engine.train_model()