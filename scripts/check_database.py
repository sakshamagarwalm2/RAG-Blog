from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

MONGO_URI = "mongodb+srv://sakshamparadox_db_user:PQtLqvrSvpyBBsEA@cluster0.zioyfty.mongodb.net/?appName=Cluster0"

def check_database():
    print(f"Connecting to MongoDB...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ismaster')
        print("Connected successfully!")
        
        # Check Ragblog database (capital R)
        db_name = "Ragblog"
        if db_name in client.list_database_names():
            print(f"\nDatabase '{db_name}' exists!")
            db = client[db_name]
            collections = db.list_collection_names()
            print(f"Collections in '{db_name}': {collections}")
            
            # Check each collection
            for collection_name in collections:
                collection = db[collection_name]
                count = collection.count_documents({})
                print(f"  - {collection_name}: {count} documents")
        else:
            print(f"Database '{db_name}' does not exist.")
            
        # Also check ragblog (lowercase) in case it's created later
        db_name_lower = "ragblog"
        if db_name_lower in client.list_database_names():
            print(f"\nDatabase '{db_name_lower}' exists!")
            db = client[db_name_lower]
            collections = db.list_collection_names()
            print(f"Collections in '{db_name_lower}': {collections}")
            
            # Check each collection
            for collection_name in collections:
                collection = db[collection_name]
                count = collection.count_documents({})
                print(f"  - {collection_name}: {count} documents")
        else:
            print(f"\nDatabase '{db_name_lower}' does not exist yet.")
            
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    check_database()