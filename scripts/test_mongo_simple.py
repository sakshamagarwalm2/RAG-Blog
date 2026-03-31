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
        print("SUCCESS: MongoDB Connection Successful!")
        
        # Check databases
        dbs = client.list_database_names()
        print(f"Available Databases: {dbs}")
        
        # Check specific database
        db_name = "ragblog"
        if db_name in dbs:
            print(f"SUCCESS: Database '{db_name}' exists!")
            db = client[db_name]
            collections = db.list_collection_names()
            print(f"Collections in '{db_name}': {collections}")
        else:
            print(f"WARNING: Database '{db_name}' does not exist yet.")
            
        return True
    except ServerSelectionTimeoutError as e:
        print(f"ERROR: Connection Timeout: {e}")
    except ConnectionFailure as e:
        print(f"ERROR: Connection Failure: {e}")
    except Exception as e:
        print(f"ERROR: An error occurred: {e}")
    return False

if __name__ == "__main__":
    test_connection()