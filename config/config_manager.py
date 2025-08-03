"""
Configuration management for MCQ Database Manager
"""

import json
import os
import base64
from utils.constants import DEFAULT_SUBJECT_DATA, CONFIG_FILE


class ConfigManager:
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.subject_data = {}
        self.saved_password = None
        self.saved_username = None
        self.levels = ["easy", "medium", "hard"]
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.subject_data = config.get('subject_data', DEFAULT_SUBJECT_DATA)
                    self.saved_password = config.get('password', None)
                    self.saved_username = config.get('username', None)
            else:
                self.subject_data = DEFAULT_SUBJECT_DATA
                self.saved_password = None
                self.saved_username = None
                # Create initial config file
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.subject_data = DEFAULT_SUBJECT_DATA
            self.saved_password = None
            self.saved_username = None
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'subject_data': self.subject_data,
                'password': self.saved_password,
                'username': self.saved_username
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def encrypt_password(self, password):
        """Simple encryption for password storage"""
        return base64.b64encode(password.encode()).decode()
    
    def decrypt_password(self, encrypted):
        """Decrypt password"""
        try:
            return base64.b64decode(encrypted.encode()).decode()
        except:
            return None
    
    def get_all_subjects(self):
        """Get list of all subjects"""
        subjects = list(self.subject_data.keys())
        return sorted(subjects)
    
    def get_topics_for_subject(self, subject):
        """Get topics for a specific subject"""
        if subject in self.subject_data:
            return self.subject_data[subject].get("topics", [])
        return []
    
    def get_classifications_for_subject(self, subject):
        """Get classifications for a specific subject"""
        if subject in self.subject_data:
            return self.subject_data[subject].get("classifications", [])
        return []
    
    def add_topic_to_subject(self, subject, topic):
        """Add a topic to a subject"""
        if subject not in self.subject_data:
            self.subject_data[subject] = {"topics": [], "classifications": []}
        
        if topic not in self.subject_data[subject]["topics"]:
            self.subject_data[subject]["topics"].append(topic)
            self.save_config()
            return True
        return False
    
    def add_classification_to_subject(self, subject, classification):
        """Add a classification to a subject"""
        if subject not in self.subject_data:
            self.subject_data[subject] = {"topics": [], "classifications": []}
        
        if classification not in self.subject_data[subject]["classifications"]:
            self.subject_data[subject]["classifications"].append(classification)
            self.save_config()
            return True
        return False
    
    def add_new_subject(self, subject):
        """Add a new subject"""
        subject = subject.strip().lower()
        if subject and subject not in self.subject_data:
            self.subject_data[subject] = {"topics": [], "classifications": []}
            self.save_config()
            return True
        return False