from motor.motor_asyncio import AsyncIOMotorClient
from src.settings import MONGODB_URL ,DATABASE_NAME
from bson  import ObjectId 
from pymongo import ReturnDocument
from src.security import security

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        self.user_collection = self.db["user"]
        self.file_collection = self.db["file"]
    def get_user_collection(self):
        return self.user_collection

    async def create_user(self,user):
        user = {
            "name": user["name"],
            "email": user["email"],
            "password": security.hash_password(user["password"])
         }        
        
        result = await self.user_collection.insert_one(user)
        user["_id"] = str(result.inserted_id)
        return user

    def get_user(self , id):
        user =  self.user_collection.find_one({"_id": ObjectId(id)})
        return user

    def login(self , email):
        user  = self.user_collection.find_one({"email": email})
        return user
    
    async def delete_chunks( self,document_id: str):

        await self.file_collection.delete_many({
            "document_id": document_id
        })

    async def save_chunks( self, chunks: list[dict]):
        if chunks:
            await self.file_collection.insert_many(chunks)


    async def get_document_by_filename(self ,filename):
         document = await self.file_collection.find_one({"file_name": filename})
         return document    

    async def vector_search(
    self,
    query_embedding: list[float],
    limit: int = 5,
    source_types: list[str] | None = None
):
        vector_search_stage = {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": limit
            }
        }

        # Add filter only when we actually want to restrict sources
        if source_types:
            vector_search_stage["$vectorSearch"]["filter"] = {
            "source_type": {
                "$in": source_types
            }
        }

        pipeline = [
            vector_search_stage,
            {
                "$project": {
                    "_id": 0,
                    "document_id": 1,
                    "file_name": 1,
                    "chunk_index": 1,
                    "text": 1,
                    "source_type": 1,
                    "metadata": 1,
                    "score": {
                        "$meta": "vectorSearchScore"
                    }
                }
            }
        ]

        cursor = self.file_collection.aggregate(pipeline)

        return await cursor.to_list(length=limit)