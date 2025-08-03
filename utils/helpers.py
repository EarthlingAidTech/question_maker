"""
Helper functions for MCQ Database Manager
"""

import datetime
import random
import csv
import json
from tkinter import messagebox


def generate_random_seed():
    """Generate random seed for prompt variation"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = random.randint(1000, 9999)
    return f"seed_{timestamp}_{random_num}"


def safe_grab_set(window):
    """Safely set grab on a window"""
    try:
        window.grab_set()
    except:
        pass  # Some window managers don't support grab


def export_questions_to_csv(questions, filename):
    """Export questions to CSV file"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['subject', 'topic', 'classification', 'question', 
                        'option1', 'option2', 'option3', 'option4', 
                        'correctAnswer', 'level', 'marks', 'created_by']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for q in questions:
                row = {field: q.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        return True, f"Exported {len(questions)} questions successfully"
    except Exception as e:
        return False, f"Failed to export: {str(e)}"


def import_questions_from_csv(filename):
    """Import questions from CSV file"""
    try:
        questions = []
        
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Convert marks to int
                try:
                    row['marks'] = int(row.get('marks', 1))
                except:
                    row['marks'] = 1
                
                # Ensure topic and classification are strings
                if not row.get('topic'):
                    row['topic'] = ''
                if not row.get('classification'):
                    row['classification'] = ''
                
                questions.append(row)
        
        return True, questions
    except Exception as e:
        return False, str(e)


def parse_json_questions(json_text):
    """Parse JSON text containing questions"""
    try:
        data = json.loads(json_text)
        questions = data.get('questions', [])
        
        if not questions:
            return False, "No questions found in JSON", None, None
        
        suggested_topics = data.get('suggested_topics', [])
        suggested_classifications = data.get('suggested_classifications', [])
        
        return True, questions, suggested_topics, suggested_classifications
        
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format: {str(e)}", None, None
    except Exception as e:
        return False, f"An error occurred: {str(e)}", None, None


def validate_question(question):
    """Validate a question object"""
    required_fields = ['subject', 'topic', 'classification', 'level', 'question',
                      'option1', 'option2', 'option3', 'option4', 'correctAnswer']
    
    for field in required_fields:
        if not question.get(field):
            return False, f"Missing required field: {field}"
    
    # Check if correct answer matches one of the options
    correct = question['correctAnswer']
    options = [question['option1'], question['option2'], 
              question['option3'], question['option4']]
    
    if correct not in options:
        return False, "Correct answer must match one of the options"
    
    # Validate marks
    try:
        int(question.get('marks', 1))
    except:
        return False, "Marks must be a number"
    
    return True, "Valid"


def create_backup_data(questions, subject_data):
    """Create backup data structure"""
    # Convert ObjectId to string for JSON serialization
    for q in questions:
        if '_id' in q:
            q['_id'] = str(q['_id'])
        if 'created_at' in q and hasattr(q['created_at'], 'isoformat'):
            q['created_at'] = q['created_at'].isoformat()
        if 'updated_at' in q and hasattr(q['updated_at'], 'isoformat'):
            q['updated_at'] = q['updated_at'].isoformat()
    
    return {
        'backup_date': datetime.datetime.now().isoformat(),
        'total_questions': len(questions),
        'questions': questions,
        'subject_data': subject_data
    }


# Check matplotlib availability
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib
    matplotlib.use('TkAgg')
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not installed. Charts will not be available.")


def is_matplotlib_available():
    """Check if matplotlib is available"""
    return MATPLOTLIB_AVAILABLE