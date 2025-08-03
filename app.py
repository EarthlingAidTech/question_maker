"""
Main application class for MCQ Database Manager
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip

from config.config_manager import ConfigManager
from database.db_manager import DatabaseManager
from utils.constants import COLORS, WINDOW_BREAK_POINT, QUESTIONS_PER_PAGE_DEFAULT, QUESTIONS_PER_PAGE_SMALL
from utils.helpers import safe_grab_set

# Import UI tabs
from ui.dashboard_tab import DashboardTab
from ui.generator_tab import GeneratorTab
from ui.processor_tab import ProcessorTab
from ui.browse_tab import BrowseTab
from ui.manage_tab import ManageTab


class MCQDatabaseManager:
    def __init__(self, root):
        self.root = root
        self.root.title("MCQ Database Management System - Enhanced")
        
        # Make window responsive
        self.root.minsize(800, 600)
        self.root.geometry("1200x800")
        
        # Configure grid weights for responsiveness
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Set background
        self.root.configure(bg='#f0f0f0')
        
        # Define color scheme
        self.colors = COLORS
        
        # Username variable
        self.username = None
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.db_manager = DatabaseManager()
        
        # Current questions for display
        self.current_questions = []
        self.current_page = 0
        self.questions_per_page = QUESTIONS_PER_PAGE_DEFAULT
        
        # Ask for username first
        self.ask_username()
        
        # Setup UI
        self.setup_styles()
        self.setup_ui()
        self.setup_database_connection()
        
        # Initialize tabs
        self.init_tabs()
        
        # Make window responsive
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def ask_username(self):
        """Ask for username at startup"""
        username_dialog = tk.Toplevel(self.root)
        username_dialog.title("Welcome")
        username_dialog.geometry("400x200")
        username_dialog.transient(self.root)
        username_dialog.configure(bg=self.colors['white'])
        
        # Center the dialog
        username_dialog.update_idletasks()
        x = (username_dialog.winfo_screenwidth() - 400) // 2
        y = (username_dialog.winfo_screenheight() - 200) // 2
        username_dialog.geometry(f"400x200+{x}+{y}")
        
        # Make dialog modal
        username_dialog.update()
        username_dialog.after(100, lambda: safe_grab_set(username_dialog))
        
        # Title
        title_frame = tk.Frame(username_dialog, bg=self.colors['primary'], height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="👤 User Login",
            font=('Arial', 16, 'bold'),
            bg=self.colors['primary'],
            fg='white'
        ).pack(expand=True)
        
        # Input frame
        input_frame = tk.Frame(username_dialog, bg=self.colors['white'], pady=20)
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            input_frame,
            text="Enter your username:",
            font=('Arial', 12),
            bg=self.colors['white']
        ).pack(pady=(0, 10))
        
        username_entry = tk.Entry(input_frame, font=('Arial', 11), width=30)
        username_entry.pack(pady=5)
        
        # Load last username if exists
        if self.config_manager.saved_username:
            username_entry.insert(0, self.config_manager.saved_username)
        
        def proceed():
            username = username_entry.get().strip()
            if username:
                self.username = username
                self.config_manager.saved_username = username
                self.config_manager.save_config()
                username_dialog.destroy()
            else:
                messagebox.showwarning("Input Required", "Please enter a username")
        
        # Buttons
        button_frame = tk.Frame(input_frame, bg=self.colors['white'])
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Continue",
            command=proceed,
            font=('Arial', 11, 'bold'),
            bg=self.colors['success'],
            fg='white',
            padx=30,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT
        ).pack()
        
        username_entry.bind('<Return>', lambda e: proceed())
        username_entry.focus()
        
        # Don't allow closing without username
        username_dialog.protocol("WM_DELETE_WINDOW", lambda: None)
    
    def on_window_resize(self, event=None):
        """Handle window resize for responsiveness"""
        if event and event.widget == self.root:
            width = self.root.winfo_width()
            if width < WINDOW_BREAK_POINT:
                self.questions_per_page = QUESTIONS_PER_PAGE_SMALL
            else:
                self.questions_per_page = QUESTIONS_PER_PAGE_DEFAULT
    
    def setup_styles(self):
        """Configure ttk styles for better appearance"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure notebook style
        style.configure('TNotebook', background=self.colors['bg'])
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Arial', 10))
        
        # Configure treeview style
        style.configure('Treeview', background=self.colors['white'], 
                       fieldbackground=self.colors['white'],
                       font=('Arial', 10))
        style.configure('Treeview.Heading', font=('Arial', 11, 'bold'))
        
        # Configure combobox style
        style.configure('TCombobox', fieldbackground=self.colors['white'])
    
    def setup_database_connection(self):
        """Setup MongoDB connection with password prompt"""
        password_dialog = tk.Toplevel(self.root)
        password_dialog.title("MongoDB Connection")
        password_dialog.geometry("400x250")
        password_dialog.transient(self.root)
        password_dialog.configure(bg=self.colors['white'])
        
        # Center the dialog
        password_dialog.update_idletasks()
        x = (password_dialog.winfo_screenwidth() - 400) // 2
        y = (password_dialog.winfo_screenheight() - 250) // 2
        password_dialog.geometry(f"400x250+{x}+{y}")
        
        # Make dialog modal
        password_dialog.update()
        password_dialog.after(100, lambda: safe_grab_set(password_dialog))
        
        # Logo/Title
        title_frame = tk.Frame(password_dialog, bg=self.colors['primary'], height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="🔐 MongoDB Authentication",
            font=('Arial', 16, 'bold'),
            bg=self.colors['primary'],
            fg='white'
        ).pack(expand=True)
        
        # Password input
        input_frame = tk.Frame(password_dialog, bg=self.colors['white'], pady=20)
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            input_frame,
            text="Enter MongoDB Password:",
            font=('Arial', 12),
            bg=self.colors['white']
        ).pack(pady=(0, 10))
        
        password_entry = tk.Entry(input_frame, show="*", font=('Arial', 11), width=30)
        password_entry.pack(pady=5)
        
        # Load saved password if exists
        if self.config_manager.saved_password:
            decrypted = self.config_manager.decrypt_password(self.config_manager.saved_password)
            if decrypted:
                password_entry.insert(0, decrypted)
        
        # Remember password checkbox
        remember_var = tk.BooleanVar(value=bool(self.config_manager.saved_password))
        tk.Checkbutton(
            input_frame,
            text="Remember password",
            variable=remember_var,
            font=('Arial', 10),
            bg=self.colors['white']
        ).pack(pady=5)
        
        def connect():
            password = password_entry.get()
            if password:
                # Show loading
                loading_label = tk.Label(input_frame, text="Connecting...", 
                                       font=('Arial', 10), 
                                       bg=self.colors['white'],
                                       fg=self.colors['info'])
                loading_label.pack()
                password_dialog.update()
                
                # Connect to MongoDB
                success, message = self.db_manager.connect(password)
                
                if success:
                    # Save password if requested
                    if remember_var.get():
                        self.config_manager.saved_password = self.config_manager.encrypt_password(password)
                    else:
                        self.config_manager.saved_password = None
                    self.config_manager.save_config()
                    
                    self.update_status(f"✓ Connected to MongoDB successfully (User: {self.username})", self.colors['success'])
                    password_dialog.destroy()
                    
                    # Load initial data
                    self.refresh_all_tabs()
                else:
                    loading_label.destroy()
                    messagebox.showerror("Connection Error", f"Failed to connect:\n{message}")
                    self.update_status("✗ MongoDB connection failed", self.colors['danger'])
            else:
                messagebox.showwarning("Input Required", "Please enter the database password")
        
        # Buttons
        button_frame = tk.Frame(input_frame, bg=self.colors['white'])
        button_frame.pack(pady=10)
        
        connect_btn = tk.Button(
            button_frame,
            text="Connect",
            command=connect,
            font=('Arial', 11, 'bold'),
            bg=self.colors['success'],
            fg='white',
            padx=30,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT
        )
        connect_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=password_dialog.destroy,
            font=('Arial', 11),
            bg=self.colors['light'],
            fg=self.colors['dark'],
            padx=30,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        password_entry.bind('<Return>', lambda e: connect())
        password_entry.focus()
    
    def setup_ui(self):
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.grid(row=0, column=0, sticky='nsew')
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Top toolbar
        self.setup_toolbar(main_container)
        
        # Main content area with notebook
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.grid(row=0, column=0, sticky='nsew')
        
        # Create tab frames
        self.dashboard_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.generator_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.processor_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.browse_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.manage_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_frame, text="📊 Dashboard")
        self.notebook.add(self.generator_frame, text="🔧 Generate Prompt")
        self.notebook.add(self.processor_frame, text="📥 Import Questions")
        self.notebook.add(self.browse_frame, text="📚 Browse & Edit")
        self.notebook.add(self.manage_frame, text="⚙️ Manage")
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            font=('Arial', 10),
            bg=self.colors['dark'],
            fg='white',
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=10
        )
        self.status_bar.grid(row=1, column=0, sticky='ew')
    
    def setup_toolbar(self, parent):
        """Create top toolbar"""
        toolbar = tk.Frame(parent, bg=self.colors['primary'], height=60)
        toolbar.grid(row=0, column=0, sticky='ew')
        toolbar.grid_propagate(False)
        
        # Title
        title_label = tk.Label(
            toolbar,
            text="MCQ Database Management System",
            font=('Arial', 20, 'bold'),
            bg=self.colors['primary'],
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Quick stats and user info
        self.stats_frame = tk.Frame(toolbar, bg=self.colors['primary'])
        self.stats_frame.pack(side=tk.RIGHT, padx=20)
        
        # User label
        self.user_label = tk.Label(
            self.stats_frame,
            text=f"👤 User: {self.username if self.username else 'Unknown'}",
            font=('Arial', 11),
            bg=self.colors['primary'],
            fg='white'
        )
        self.user_label.pack()
        
        self.total_questions_label = tk.Label(
            self.stats_frame,
            text="Total Questions: 0",
            font=('Arial', 12),
            bg=self.colors['primary'],
            fg='white'
        )
        self.total_questions_label.pack()
    
    def init_tabs(self):
        """Initialize all tabs"""
        self.dashboard_tab = DashboardTab(self.dashboard_frame, self)
        self.generator_tab = GeneratorTab(self.generator_frame, self)
        self.processor_tab = ProcessorTab(self.processor_frame, self)
        self.browse_tab = BrowseTab(self.browse_frame, self)
        self.manage_tab = ManageTab(self.manage_frame, self)
    
    def update_status(self, message, color=None):
        """Update status bar"""
        self.status_bar.config(text=message)
        if color:
            self.status_bar.config(bg=color)
        else:
            self.status_bar.config(bg=self.colors['dark'])
    
    def refresh_dashboard(self):
        """Refresh dashboard statistics"""
        self.dashboard_tab.refresh()
    
    def refresh_all_tabs(self):
        """Refresh all tabs after database connection"""
        # Refresh dashboard
        self.dashboard_tab.refresh()
        
        # Load initial data in browse tab
        if hasattr(self, 'browse_tab'):
            self.browse_tab.apply_filters()
        
        # Update subject combos in all tabs
        self.update_all_combos()
    
    def update_all_combos(self):
        """Update all comboboxes with new subjects"""
        subjects = self.config_manager.get_all_subjects()
        
        # Update generator subject combo
        if hasattr(self.generator_tab, 'subject_combo') and self.generator_tab.subject_combo.winfo_exists():
            current = self.generator_tab.subject_combo.get()
            self.generator_tab.subject_combo['values'] = subjects
            if current in subjects:
                self.generator_tab.subject_combo.set(current)
        
        # Update manage subject combo
        if hasattr(self.manage_tab, 'manage_subject_combo') and self.manage_tab.manage_subject_combo.winfo_exists():
            current = self.manage_tab.manage_subject_combo.get()
            self.manage_tab.manage_subject_combo['values'] = subjects
            if current in subjects:
                self.manage_tab.manage_subject_combo.set(current)
        
        # Update filter subject combo
        if hasattr(self.browse_tab, 'filter_subject') and self.browse_tab.filter_subject.winfo_exists():
            current = self.browse_tab.filter_subject.get()
            self.browse_tab.filter_subject['values'] = ['All'] + subjects
            self.browse_tab.filter_subject.set(current)
    
    def on_tab_changed(self, event):
        """Handle tab change event"""
        selected_tab = event.widget.tab('current')['text']
        
        # Load data for specific tabs when they're selected
        if selected_tab == "📚 Browse & Edit" and hasattr(self, 'browse_tab'):
            # Check if browse tab has never loaded data
            if not hasattr(self.browse_tab, 'data_loaded'):
                self.browse_tab.apply_filters()
                self.browse_tab.data_loaded = True