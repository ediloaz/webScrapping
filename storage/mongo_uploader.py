from pymongo import MongoClient
from config.settings import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME

class MongoUploader:
    @staticmethod
    def upload(data):
        print()
        print("Subiendo perfumes a MongoDB...")
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        collection = db[MONGO_COLLECTION_NAME]
        result = collection.insert_many(data)
        print(f"Subidos {len(result.inserted_ids)} perfumes a MongoDB")
