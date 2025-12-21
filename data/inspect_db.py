import pandas as pd
from sqlalchemy import create_engine
import os

# --- 1. Connect to Database ---
# Use absolute path logic to be safe
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "orbit.db")
DB_URL = f"sqlite:///{DB_PATH}"

print(f"Connecting to database at: {DB_PATH}")

try:
    engine = create_engine(DB_URL)
    
    # --- 2. Read Data ---
    # We read the 'interactions' table into a Pandas DataFrame
    query = "SELECT * FROM interactions ORDER BY timestamp DESC LIMIT 20"
    df = pd.read_sql(query, engine)
    
    # --- 3. Display Data ---
    if df.empty:
        print("\n[WARN] The database is empty! No interactions found.")
    else:
        print(f"\n[SUCCESS] Found {len(df)} recent interactions:\n")
        print(df.to_string(index=False))
        
        # Optional: Show total count
        count_query = "SELECT COUNT(*) FROM interactions"
        total_count = pd.read_sql(count_query, engine).iloc[0, 0]
        print(f"\nTotal rows in database: {total_count}")

except Exception as e:
    print(f"\n[ERROR] Could not read database: {e}")
# ```

# 3.  **Run the script:**
#     Open your terminal (backend environment) and run:
#     ```bash
#     python inspect_db.py