from pymongo import MongoClient

MONGO_URI = "mongodb+srv://sakshamparadox_db_user:PQtLqvrSvpyBBsEA@cluster0.zioyfty.mongodb.net/?appName=Cluster0"

def show_collection_contents():
    print("Connecting to MongoDB...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ismaster')
        print("Connected successfully!")
        
        # Check Ragblog database
        db_name = "Ragblog"
        db = client[db_name]
        
        # Check blogs collection
        if "blogs" in db.list_collection_names():
            print(f"\n=== BLOGS COLLECTION (Total: {db.blogs.count_documents({})}) ===")
            blogs = db.blogs.find().limit(3)
            for i, blog in enumerate(blogs, 1):
                print(f"Blog {i}:")
                print(f"  Title: {blog.get('title', 'N/A')}")
                print(f"  URL: {blog.get('url', 'N/A')}")
                print(f"  Has content: {'Yes' if blog.get('content') else 'No'}")
                print(f"  Has embeddings: {'Yes' if blog.get('embedding') else 'No'}")
                print()
        
        # Check videos collection
        if "videos" in db.list_collection_names():
            print(f"\n=== VIDEOS COLLECTION (Total: {db.videos.count_documents({})}) ===")
            videos = db.videos.find().limit(3)
            for i, video in enumerate(videos, 1):
                print(f"Video {i}:")
                print(f"  Title: {video.get('title', 'N/A')}")
                print(f"  URL: {video.get('url', 'N/A')}")
                print(f"  Has summary: {'Yes' if video.get('summary') else 'No'}")
                print(f"  Has transcript: {'Yes' if video.get('transcript') else 'No'}")
                print()
        
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    show_collection_contents()