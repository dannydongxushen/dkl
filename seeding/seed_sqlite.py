# seeding/seed_sqlite.py
import os
import yaml
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE_DIR, "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

DATA_DIR = os.path.join(BASE_DIR, config["paths"]["data_dir"])
DB_FILE = os.path.join(BASE_DIR, config["paths"]["sqlite_db"])
CSV_FILES = config["paths"]["csv_files"]

def init_sqlite():
    print(f"--- Initializing SQLite database: {DB_FILE} ---")
    
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        
    conn = sqlite3.connect(DB_FILE)
    
    for file in CSV_FILES:
        file_path = os.path.join(DATA_DIR, file)
        table_name = file.replace(".csv", "")
        
        try:
            df = pd.read_csv(file_path)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"✅ Successfully imported table: {table_name} ({len(df)} records)")
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
        except Exception as e:
            print(f"❌ Failed to import {file}: {str(e)}")
            
    conn.close()
    print("--- SQLite initialization completed ---\n")

if __name__ == "__main__":
    init_sqlite()