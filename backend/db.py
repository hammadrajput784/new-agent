import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Use an environment variable for the URI, with a local default
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "campus_db"

def get_db_connection():
    """
    Establishes and returns a connection to the MongoDB database.
    Includes error handling for connection failures.
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # The ismaster command is a lightweight way to force a connection check.
        client.admin.command('ismaster')
        print("✅ MongoDB connection successful.")
        return client[DB_NAME]
    except ConnectionFailure as e:
        print(f"❌ Could not connect to MongoDB: {e}")
        return None

# Establish the database connection once when the module is loaded
db_connection = get_db_connection()

def get_students_collection():
    """
    A helper function to get the 'students' collection directly.
    Returns None if the database connection failed.
    """
    if db_connection is not None:
        return db_connection.students
    return None

# --- Connection Test ---
# This block will only run when you execute `python backend/db.py` directly.
# It's a simple way to check if your connection is configured correctly.
if __name__ == "__main__":
    print("--- Running Database Connection Test ---")
    students_collection = get_students_collection()
    if students_collection is not None:
        print(f"Successfully retrieved '{students_collection.name}' collection from the '{DB_NAME}' database.")
        print("Your db.py file is set up correctly!")
    else:
        print("Failed to set up the database connection. Please check your MONGO_URI and ensure MongoDB is running.")