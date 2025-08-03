"""
Question model and related data structures
"""

from datetime import datetime
from typing import Dict, List, Optional


class Question:
    """Question data model"""
    
    def __init__(self, data: Dict = None):
        if data is None:
            data = {}
        
        self._id = data.get('_id')
        self.subject = data.get('subject', '')
        self.topic = data.get('topic', '')
        self.classification = data.get('classification', '')
        self.question = data.get('question', '')
        self.option1 = data.get('option1', '')
        self.option2 = data.get('option2', '')
        self.option3 = data.get('option3', '')
        self.option4 = data.get('option4', '')
        self.correct_answer = data.get('correctAnswer', '')
        self.level = data.get('level', 'easy')
        self.marks = data.get('marks', 1)
        self.created_by = data.get('created_by', '')
        self.created_at = data.get('created_at', datetime.now())
        self.updated_at = data.get('updated_at', datetime.now())
    
    def to_dict(self) -> Dict:
        """Convert question to dictionary"""
        return {
            'subject': self.subject,
            'topic': self.topic,
            'classification': self.classification,
            'question': self.question,
            'option1': self.option1,
            'option2': self.option2,
            'option3': self.option3,
            'option4': self.option4,
            'correctAnswer': self.correct_answer,
            'level': self.level,
            'marks': self.marks,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def validate(self) -> tuple[bool, str]:
        """Validate question data"""
        # Check required fields
        required_fields = [
            ('subject', self.subject),
            ('topic', self.topic),
            ('classification', self.classification),
            ('question', self.question),
            ('option1', self.option1),
            ('option2', self.option2),
            ('option3', self.option3),
            ('option4', self.option4),
            ('correctAnswer', self.correct_answer),
            ('level', self.level)
        ]
        
        for field_name, field_value in required_fields:
            if not field_value:
                return False, f"Missing required field: {field_name}"
        
        # Check if correct answer matches one of the options
        options = [self.option1, self.option2, self.option3, self.option4]
        if self.correct_answer not in options:
            return False, "Correct answer must match one of the options"
        
        # Validate marks
        try:
            int(self.marks)
        except:
            return False, "Marks must be a number"
        
        # Validate level
        valid_levels = ['easy', 'medium', 'hard']
        if self.level not in valid_levels:
            return False, f"Level must be one of: {', '.join(valid_levels)}"
        
        return True, "Valid"
    
    def get_display_text(self, max_length: int = 60) -> str:
        """Get truncated question text for display"""
        if len(self.question) > max_length:
            return self.question[:max_length] + '...'
        return self.question
    
    @staticmethod
    def from_json_format(json_data: Dict) -> 'Question':
        """Create Question from JSON format"""
        return Question(json_data)
    
    def __repr__(self):
        return f"<Question: {self.get_display_text(30)} ({self.subject}/{self.level})>"


class QuestionFilter:
    """Filter criteria for questions"""
    
    def __init__(self):
        self.subject: Optional[str] = None
        self.topic: Optional[str] = None
        self.classification: Optional[str] = None
        self.level: Optional[str] = None
        self.created_by: Optional[str] = None
        self.search_text: Optional[str] = None
    
    def to_query(self) -> Dict:
        """Convert filter to MongoDB query"""
        query = {}
        
        if self.subject and self.subject != 'All':
            query['subject'] = self.subject
        
        if self.topic and self.topic != 'All':
            query['topic'] = self.topic
        
        if self.classification and self.classification != 'All':
            query['classification'] = self.classification
        
        if self.level and self.level != 'All':
            query['level'] = self.level
        
        if self.created_by:
            query['created_by'] = self.created_by
        
        if self.search_text:
            query['$or'] = [
                {"question": {"$regex": self.search_text, "$options": "i"}},
                {"subject": {"$regex": self.search_text, "$options": "i"}},
                {"topic": {"$regex": self.search_text, "$options": "i"}},
                {"classification": {"$regex": self.search_text, "$options": "i"}},
                {"created_by": {"$regex": self.search_text, "$options": "i"}}
            ]
        
        return query