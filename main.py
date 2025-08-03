"""
MCQ Database Management System - Main Entry Point
"""

import tkinter as tk
from app import MCQDatabaseManager


def main():
    root = tk.Tk()
    app = MCQDatabaseManager(root)
    
    # Make window responsive
    root.update_idletasks()
    
    # Center the window
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Configure window resizing
    root.minsize(800, 600)
    
    root.mainloop()


if __name__ == "__main__":
    main()