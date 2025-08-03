"""
User management for MCQ Database Manager
"""

from pymongo import MongoClient
from urllib.parse import quote_plus
import datetime
from utils.constants import MONGODB_CONNECTION_STRING, DATABASE_NAME


class UserManager:
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
            self.collection = self.db['users']
            
            # Create indexes
            self.collection.create_index("username", unique=True)
            self.collection.create_index("last_active")
            
            return True, "Connected successfully"
            
        except Exception as e:
            return False, str(e)
    
    def create_or_update_user(self, username):
        """Create or update user record"""
        if not self.collection:
            return None
        
        try:
            # Current timestamp
            now = datetime.datetime.now()
            
            # First, try to find existing user
            existing_user = self.collection.find_one({"username": username})
            
            if existing_user:
                # Update existing user
                result = self.collection.update_one(
                    {"username": username},
                    {
                        "$set": {
                            "last_active": now,
                            "status": "online"
                        }
                    }
                )
            else:
                # Create new user with all fields
                new_user = {
                    "username": username,
                    "last_active": now,
                    "status": "online",
                    "created_at": now,
                    "profile": {
                        "full_name": "",
                        "email": "",
                        "department": "",
                        "role": "",
                        "bio": ""
                    },
                    "total_sessions": 0,
                    "total_time_seconds": 0,
                    "questions_created": 0,
                    "sessions": []
                }
                
                result = self.collection.insert_one(new_user)
            
            return result
            
        except Exception as e:
            print(f"Error creating/updating user: {e}")
            return None
    
    def update_user_profile(self, username, profile_data):
        """Update user profile information"""
        if not self.collection:
            return False
        
        try:
            self.collection.update_one(
                {"username": username},
                {
                    "$set": {
                        "profile": profile_data,
                        "last_active": datetime.datetime.now()
                    }
                }
            )
            return True
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False
    
    def get_user_profile(self, username):
        """Get user profile information"""
        if not self.collection:
            return None
        
        try:
            user = self.collection.find_one({"username": username})
            if user:
                return user.get("profile", {})
            return None
        except:
            return None
    
    def get_all_users(self):
        """Get all users for admin view"""
        if not self.collection:
            return []
        
        try:
            users = list(self.collection.find({}, {
                "_id": 0,
                "username": 1,
                "status": 1,
                "last_active": 1,
                "created_at": 1,
                "total_sessions": 1,
                "total_time_seconds": 1,
                "questions_created": 1,
                "profile.full_name": 1,
                "profile.department": 1
            }).sort("last_active", -1))
            
            return users
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def log_session(self, username, session_start, duration):
        """Log a user session"""
        if not self.collection:
            return
        
        try:
            # Calculate duration in seconds
            duration_seconds = int(duration.total_seconds())
            
            # Create session record
            session_record = {
                "start": session_start,
                "end": datetime.datetime.now(),
                "duration_seconds": duration_seconds
            }
            
            # Update user stats
            self.collection.update_one(
                {"username": username},
                {
                    "$inc": {
                        "total_sessions": 1,
                        "total_time_seconds": duration_seconds
                    },
                    "$set": {
                        "status": "offline",
                        "last_active": datetime.datetime.now()
                    },
                    "$push": {
                        "sessions": {
                            "$each": [session_record],
                            "$slice": -100  # Keep last 100 sessions
                        }
                    }
                }
            )
        except Exception as e:
            print(f"Error logging session: {e}")
    
    def get_user_sessions(self, username, limit=10):
        """Get recent sessions for a user"""
        if not self.collection:
            return []
        
        try:
            user = self.collection.find_one(
                {"username": username},
                {"sessions": {"$slice": -limit}}
            )
            
            if user and "sessions" in user:
                return user["sessions"]
            return []
        except:
            return []
    
    def update_questions_created(self, username, count=1):
        """Update questions created count"""
        if not self.collection:
            return
        
        try:
            self.collection.update_one(
                {"username": username},
                {"$inc": {"questions_created": count}}
            )
        except:
            pass
    
    def get_online_users(self):
        """Get currently online users (active in last 5 minutes)"""
        if not self.collection:
            return []
        
        try:
            five_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=5)
            
            online_users = list(self.collection.find({
                "status": "online",
                "last_active": {"$gte": five_minutes_ago}
            }, {
                "_id": 0,
                "username": 1,
                "last_active": 1,
                "profile.full_name": 1
            }))
            
            return online_users
        except:
            return []
    
    def format_duration(self, seconds):
        """Format duration in seconds to human readable format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"