# backend/init_db.py
from app import app, db
import logging

# Configure logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def init_database():
    with app.app_context():
        print("--- Connecting to Database ---")
        
        # Option A: SAFE MODE (Only creates missing tables)
        # db.create_all()
        # print("--- Tables Created (Safe Mode) ---")

        # Option B: RESET MODE (Deletes everything and rebuilds)
        # USE THIS if your database is empty or broken from the recent changes
        print("!!! DROPPING ALL TABLES !!!")
        db.drop_all()
        
        print("--- Creating New Tables ---")
        db.create_all()
        
        print("--- Database Initialized Successfully ---")

if __name__ == "__main__":
    init_database()