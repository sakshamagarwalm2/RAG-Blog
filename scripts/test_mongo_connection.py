import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

MONGO_URI = "mongodb+srv://sakshamparadox_db_user:PQtLqvrSvpyBBsEA@cluster0.zioyfty.mongodb.net/?appName=Cluster0"

def test_connection():
    print(f"Testing connection to: {MONGO_URI}")
    try:
        # Set a short timeout for the test
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        print("✅ MongoDB Connection Successful!")
        
        # Check databases
        dbs = client.list_database_names()
        print(f"Available Databases: {dbs}")
        return True
    except ServerSelectionTimeoutError as e:
        print(f"❌ Connection Timeout: {e}")
    except ConnectionFailure as e:
        print(f"❌ Connection Failure: {e}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    return False

if __name__ == "__main__":
    test_connection()
