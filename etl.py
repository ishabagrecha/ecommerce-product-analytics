# etl.py
import pandas as pd
import sqlite3
import os

# --- CONFIGURATION ---
# Ensure this matches exactly where you put your downloaded file
CSV_FILE_PATH = 'data/2019-Nov.csv' 
DB_NAME = 'ecommerce.db'

def load_data():
    # 1. Check if CSV exists
    if not os.path.exists(CSV_FILE_PATH):
        print(f"❌ Error: File not found at {CSV_FILE_PATH}")
        print("Please move your downloaded CSV file into a 'data' folder.")
        return

    print(f"🚀 Starting ETL Process...")
    print(f"Reading from: {CSV_FILE_PATH}")
    print(f"Writing to:   {DB_NAME}")

    # 2. Connect to Database (Creates it if it doesn't exist)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 3. Create the Table
    print("   ↳ Creating table structure...")
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())

    # 4. Load Data in Chunks
    # We read 100,000 rows at a time to save memory
    chunk_size = 100000
    
    print("   ↳ Loading data (this might take a minute)...")
    
    try:
        # We are using Pandas to read the CSV, then dumping it to SQL
        for i, chunk in enumerate(pd.read_csv(CSV_FILE_PATH, chunksize=chunk_size)):
            
            # Clean up column names (remove spaces)
            chunk.columns = [c.strip() for c in chunk.columns]
            
            # Write to SQL
            chunk.to_sql('events', conn, if_exists='append', index=False)
            
            # Print progress every 5 chunks so you know it's working
            if (i + 1) % 5 == 0:
                print(f"     Processed {(i + 1) * chunk_size} rows...")

        print(f"✅ Success! Data loaded into {DB_NAME}")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    load_data()