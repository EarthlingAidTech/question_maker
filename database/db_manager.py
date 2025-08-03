"""
Database operations manager for MCQ Database
"""

from pymongo import MongoClient
from urllib.parse import quote_plus
from bson import ObjectId
import datetime
from utils.constants import MONGODB_CONNECTION_STRING, DATABASE_NAME, COLLECTION_NAME


class DatabaseManager:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.collection = None
    
    def connect(self, password):
        """Connect to MongoDB database"""
        try:
            encoded_password = quote_plus(password)
            connection_string = MONGODB_CONNECTION_STRING.format(password=encoded_password)
            
            self.mongo_client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            self.mongo_client.server_info()  # Test connection
            
            # Setup database and collection
            self.db = self.mongo_client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]
            
            # Create indexes for better performance
            self.create_indexes()
            
            return True, "Connected successfully"
            
        except Exception as e:
            return False, str(e)
    
    def create_indexes(self):
        """Create database indexes for better performance"""
        if self.collection:
            self.collection.create_index([("question", 1), ("subject", 1)])
            self.collection.create_index("subject")
            self.collection.create_index("topic")
            self.collection.create_index("classification")
            self.collection.create_index("level")
            self.collection.create_index("created_by")
    
    def get_statistics(self):
        """Get database statistics"""
        if not self.collection:
            return {}
        
        stats = {
            'total': self.collection.count_documents({}),
            'easy': self.collection.count_documents({"level": "easy"}),
            'medium': self.collection.count_documents({"level": "medium"}),
            'hard': self.collection.count_documents({"level": "hard"}),
            'subjects': len(self.collection.distinct("subject"))
        }
        return stats
    
    def get_user_questions_count(self, username):
        """Get count of questions created by user"""
        if not self.collection:
            return 0
        return self.collection.count_documents({"created_by": username})
    
    def get_subject_distribution(self, limit=10):
        """Get subject distribution data"""
        if not self.collection:
            return []
        
        pipeline = [
            {"$group": {"_id": "$subject", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        return list(self.collection.aggregate(pipeline))
    
    def check_duplicate(self, subject, question):
        """Check if question already exists"""
        if not self.collection:
            return False
        
        existing = self.collection.find_one({
            "subject": subject,
            "question": question
        })
        return existing is not None
    
    def insert_questions(self, questions, username):
        """Insert multiple questions"""
        if not self.collection:
            raise Exception("Database not connected")
        
        # Add metadata to each question
        for q in questions:
            q['created_at'] = datetime.datetime.now()
            q['updated_at'] = datetime.datetime.now()
            
            # Ensure created_by field exists
            if 'created_by' not in q:
                q['created_by'] = username
            
            # Ensure topic and classification are strings, not arrays
            if isinstance(q.get('topic'), list):
                q['topic'] = q['topic'][0] if q['topic'] else ''
            if isinstance(q.get('classification'), list):
                q['classification'] = q['classification'][0] if q['classification'] else ''
        
        # Insert questions
        result = self.collection.insert_many(questions)
        return len(result.inserted_ids)
    
    def find_questions(self, query, sort_by='created_at', sort_order=-1):
        """Find questions with query"""
        if not self.collection:
            return []
        
        return list(self.collection.find(query).sort(sort_by, sort_order))
    
    def update_question(self, question_id, updates):
        """Update a question"""
        if not self.collection:
            raise Exception("Database not connected")
        
        updates['updated_at'] = datetime.datetime.now()
        
        return self.collection.update_one(
            {'_id': ObjectId(question_id)},
            {'$set': updates}
        )
    
    def delete_question(self, question_id):
        """Delete a question"""
        if not self.collection:
            raise Exception("Database not connected")
        
        result = self.collection.delete_one({'_id': ObjectId(question_id)})
        return result.deleted_count > 0
    
    def get_distinct_values(self, field):
        """Get distinct values for a field"""
        if not self.collection:
            return []
        
        return self.collection.distinct(field)