"""
Constants and configuration values for MCQ Database Manager
"""

# Color scheme
COLORS = {
    'primary': '#2c3e50',
    'secondary': '#3498db',
    'success': '#27ae60',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#9b59b6',
    'light': '#ecf0f1',
    'dark': '#34495e',
    'bg': '#f8f9fa',
    'white': '#ffffff'
}

# Database connection
MONGODB_CONNECTION_STRING = "mongodb+srv://earthlingaidtech:{password}@cluster0.zsi3qjh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = 'mcq_database'
COLLECTION_NAME = 'questions'

# UI Configuration
QUESTIONS_PER_PAGE_DEFAULT = 10
QUESTIONS_PER_PAGE_SMALL = 8
WINDOW_BREAK_POINT = 1000  # Width in pixels

# File paths
CONFIG_FILE = "mcq_config_enhanced.json"

# Difficulty levels
DIFFICULTY_LEVELS = ["easy", "medium", "hard"]

# Default subject data
DEFAULT_SUBJECT_DATA = {
    "c": {
        "topics": ["arrays", "pointers", "structures", "functions", "file handling", 
                  "dynamic memory", "strings", "recursion", "linked lists", "sorting algorithms"],
        "classifications": ["Fundamentals", "Advanced Concepts", "Applications", "Problem Solving"]
    },
    "python": {
        "topics": ["lists", "dictionaries", "functions", "classes", "modules", 
                  "file handling", "exceptions", "decorators", "generators", "lambda functions"],
        "classifications": ["Basics", "Data Structures", "OOP", "Advanced Features"]
    },
    "java": {
        "topics": ["classes", "inheritance", "interfaces", "collections", "streams",
                  "multithreading", "exceptions", "generics", "annotations", "JDBC"],
        "classifications": ["Core Java", "Advanced Java", "Enterprise", "Design Patterns"]
    },
    "cloud computing": {
        "topics": ["AWS", "Azure", "GCP", "virtualization", "containers", "kubernetes",
                  "serverless", "microservices", "DevOps", "security"],
        "classifications": ["Infrastructure", "Services", "Architecture", "Best Practices"]
    },
    "english": {
        "topics": ["grammar", "vocabulary", "comprehension", "writing skills", "literature",
                  "poetry", "essays", "communication", "idioms", "punctuation"],
        "classifications": ["Language Skills", "Literature", "Writing", "Communication"]
    },
    "database": {
        "topics": ["SQL", "normalization", "transactions", "indexing", "NoSQL",
                  "MongoDB", "joins", "triggers", "stored procedures", "optimization"],
        "classifications": ["Relational DB", "NoSQL", "Design", "Performance"]
    },
    "aptitude": {
        "topics": ["quantitative", "logical reasoning", "verbal ability", "data interpretation",
                  "puzzles", "coding-decoding", "series", "percentages", "probability", "time-work"],
        "classifications": ["Numerical", "Logical", "Verbal", "Analytical"]
    },
    "cybersec": {
        "topics": ["cryptography", "network security", "web security", "malware", "ethical hacking",
                  "forensics", "compliance", "risk management", "authentication", "firewalls"],
        "classifications": ["Network Security", "Application Security", "Cryptography", "Governance"]
    },
    "machine learning": {
        "topics": ["supervised learning", "unsupervised learning", "neural networks", "deep learning",
                  "feature engineering", "model evaluation", "NLP", "computer vision", "reinforcement learning"],
        "classifications": ["Algorithms", "Applications", "Theory", "Implementation"]
    }
}