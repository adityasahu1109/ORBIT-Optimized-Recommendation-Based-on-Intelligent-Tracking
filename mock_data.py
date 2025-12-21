import pandas as pd
import random
from database import SessionLocal, Interaction, init_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

# Configuration
NUM_USERS = 100            # Create 100 fake users
MIN_INTERACTIONS = 10      # Min actions per user
MAX_INTERACTIONS = 30      # Max actions per user

# Interaction Types & Weights (for reference, though we just log the type string here)
ACTION_TYPES = ['view', 'click', 'add_to_cart', 'purchase']
# Probabilities: Users view more often than they buy
ACTION_PROBS = [0.5, 0.3, 0.15, 0.05] 

def generate_mock_data():
    print("Loading products...")
    df = pd.read_csv("data/cleaned_products.csv")
    
    # Get list of all categories to assign "favorites"
    categories = df['categoryName'].unique()
    
    db: Session = SessionLocal()
    
    print(f"Generating data for {NUM_USERS} users...")
    
    interaction_buffer = []
    
    for user_id in range(1001, 1001 + NUM_USERS):
        # 1. Assign a persona (Favorite Category)
        # This ensures the data has patterns for the AI to learn
        fav_category = random.choice(categories)
        
        # Filter products for this category
        cat_products = df[df['categoryName'] == fav_category]['asin'].tolist()
        all_products = df['asin'].tolist()
        
        # Determine how many actions this user performs
        num_actions = random.randint(MIN_INTERACTIONS, MAX_INTERACTIONS)
        
        for _ in range(num_actions):
            # 80% chance to interact with favorite category, 20% random exploration
            if random.random() < 0.8 and cat_products:
                product_id = random.choice(cat_products)
            else:
                product_id = random.choice(all_products)
            
            # Pick an action (view, click, etc.)
            action = random.choices(ACTION_TYPES, weights=ACTION_PROBS)[0]
            
            # Create the record
            interaction = Interaction(
                user_id=str(user_id),
                product_id=product_id,
                interaction_type=action,
                timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            interaction_buffer.append(interaction)
    
    # Bulk save to database
    print(f"Saving {len(interaction_buffer)} interactions to database...")
    db.add_all(interaction_buffer)
    db.commit()
    db.close()
    print("Done! Database populated.")

if __name__ == "__main__":
    # Ensure tables exist
    init_db()
    generate_mock_data()