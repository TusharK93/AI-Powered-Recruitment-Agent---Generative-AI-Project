import os
try:
     from pymongo import MongoClient
except Exception:
     MongoClient = None
class MongoDBClient:
    def __init__(self,uri=None,database='resume_agent'):
          self.uri = uri or os.getenv('MONGODB_URI')
          self.database_name = database
          self.client = MongoClient(self.uri) if (MongoClient and self.uri) else None

    @property
    def db(self):
        return self.client[self.database_name] if self.client else None

    def save_document(self, collection, data):
        if not self.db:
            return None
        return self.db[collection].insert_one(data).inserted_id      
    
          
     