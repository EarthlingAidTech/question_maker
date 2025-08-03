"""
Base class for all UI tabs
"""

import tkinter as tk
from tkinter import ttk


class BaseTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(parent, bg=app.colors['bg'])
        
        # Configure grid for responsiveness
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
    
    def setup(self):
        """Setup the tab - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement setup()")
    
    def refresh(self):
        """Refresh the tab content - optional for subclasses"""
        pass
    
    def create_scrollable_frame(self, parent):
        """Create a scrollable frame"""
        # Create main container
        main_container = tk.Frame(parent, bg=self.app.colors['bg'])
        main_container.grid(row=0, column=0, sticky='nsew')
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Scrollable frame
        canvas = tk.Canvas(main_container, bg=self.app.colors['bg'])
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.app.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        return scrollable_frame
    
    def create_label_frame(self, parent, title, **kwargs):
        """Create a styled label frame"""
        default_kwargs = {
            'font': ('Arial', 12, 'bold'),
            'bg': self.app.colors['white'],
            'fg': self.app.colors['primary'],
            'padx': 20,
            'pady': 20
        }
        default_kwargs.update(kwargs)
        
        return tk.LabelFrame(parent, text=title, **default_kwargs)
    
    def create_button(self, parent, text, command, color='secondary', **kwargs):
        """Create a styled button"""
        default_kwargs = {
            'font': ('Arial', 11, 'bold'),
            'bg': self.app.colors[color],
            'fg': 'white',
            'padx': 20,
            'pady': 8,
            'cursor': 'hand2',
            'relief': tk.FLAT
        }
        default_kwargs.update(kwargs)
        
        return tk.Button(parent, text=text, command=command, **default_kwargs)
    
    def update_status(self, message, color=None):
        """Update the app status bar"""
        self.app.update_status(message, color)