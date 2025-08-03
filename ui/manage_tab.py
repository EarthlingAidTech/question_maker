"""
Manage tab for subjects, topics, and classifications management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import json
from .base_tab import BaseTab
from utils.helpers import export_questions_to_csv, import_questions_from_csv, create_backup_data


class ManageTab(BaseTab):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.setup()
    
    def setup(self):
        """Setup management tab"""
        # Create scrollable frame
        scrollable_frame = self.create_scrollable_frame(self.frame)
        
        # Content
        container = tk.Frame(scrollable_frame, bg=self.app.colors['bg'])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            container,
            text="Manage Subjects, Topics & Classifications",
            font=('Arial', 18, 'bold'),
            bg=self.app.colors['bg'],
            fg=self.app.colors['primary']
        ).pack(pady=(0, 20))
        
        # Subject management frame
        subject_frame = self.create_label_frame(container, "Subject Management")
        subject_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Subject selection
        subject_select_frame = tk.Frame(subject_frame, bg=self.app.colors['white'])
        subject_select_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            subject_select_frame,
            text="Select Subject:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.manage_subject_var = tk.StringVar()
        self.manage_subject_combo = ttk.Combobox(
            subject_select_frame,
            textvariable=self.manage_subject_var,
            values=self.app.config_manager.get_all_subjects(),
            font=('Arial', 11),
            width=30
        )
        self.manage_subject_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.manage_subject_combo.bind('<<ComboboxSelected>>', self.on_manage_subject_change)
        
        # Add new subject
        tk.Label(
            subject_select_frame,
            text="New Subject:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).pack(side=tk.LEFT, padx=(20, 10))
        
        self.new_subject_entry = tk.Entry(subject_select_frame, font=('Arial', 11), width=20)
        self.new_subject_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        self.create_button(
            subject_select_frame,
            "Add Subject",
            self.add_new_subject,
            'success',
            padx=15,
            pady=5,
            font=('Arial', 10)
        ).pack(side=tk.LEFT)
        
        # Topics and Classifications management
        manage_content_frame = tk.Frame(subject_frame, bg=self.app.colors['white'])
        manage_content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid for equal distribution
        manage_content_frame.grid_rowconfigure(0, weight=1)
        manage_content_frame.grid_columnconfigure(0, weight=1)
        manage_content_frame.grid_columnconfigure(1, weight=1)
        
        # Topics frame
        self.setup_topics_frame(manage_content_frame)
        
        # Classifications frame
        self.setup_classifications_frame(manage_content_frame)
        
        # Database operations
        self.setup_database_operations(container)
    
    def setup_topics_frame(self, parent):
        """Setup topics management frame"""
        topics_frame = tk.Frame(parent, bg=self.app.colors['white'])
        topics_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        tk.Label(
            topics_frame,
            text="Topics for Selected Subject",
            font=('Arial', 11, 'bold'),
            bg=self.app.colors['white']
        ).pack(pady=(0, 10))
        
        # Topics input
        topics_input_frame = tk.Frame(topics_frame, bg=self.app.colors['white'])
        topics_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.new_topic_entry = tk.Entry(topics_input_frame, font=('Arial', 10))
        self.new_topic_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.create_button(
            topics_input_frame,
            "Add Topic",
            self.add_topic,
            'success',
            padx=10,
            pady=3,
            font=('Arial', 9)
        ).pack(side=tk.LEFT)
        
        # Topics list
        topics_list_frame = tk.Frame(topics_frame, bg=self.app.colors['white'])
        topics_list_frame.pack(fill=tk.BOTH, expand=True)
        
        topics_scroll = ttk.Scrollbar(topics_list_frame)
        topics_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.topics_listbox_manage = tk.Listbox(
            topics_list_frame,
            font=('Arial', 10),
            height=10,
            yscrollcommand=topics_scroll.set
        )
        self.topics_listbox_manage.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        topics_scroll.config(command=self.topics_listbox_manage.yview)
    
    def setup_classifications_frame(self, parent):
        """Setup classifications management frame"""
        class_frame = tk.Frame(parent, bg=self.app.colors['white'])
        class_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        
        tk.Label(
            class_frame,
            text="Classifications for Selected Subject",
            font=('Arial', 11, 'bold'),
            bg=self.app.colors['white']
        ).pack(pady=(0, 10))
        
        # Classifications input
        class_input_frame = tk.Frame(class_frame, bg=self.app.colors['white'])
        class_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.new_classification_entry = tk.Entry(class_input_frame, font=('Arial', 10))
        self.new_classification_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.create_button(
            class_input_frame,
            "Add Classification",
            self.add_classification,
            'success',
            padx=10,
            pady=3,
            font=('Arial', 9)
        ).pack(side=tk.LEFT)
        
        # Classifications list
        class_list_frame = tk.Frame(class_frame, bg=self.app.colors['white'])
        class_list_frame.pack(fill=tk.BOTH, expand=True)
        
        class_scroll = ttk.Scrollbar(class_list_frame)
        class_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.classifications_listbox_manage = tk.Listbox(
            class_list_frame,
            font=('Arial', 10),
            height=10,
            yscrollcommand=class_scroll.set
        )
        self.classifications_listbox_manage.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        class_scroll.config(command=self.classifications_listbox_manage.yview)
    
    def setup_database_operations(self, parent):
        """Setup database operations section"""
        db_frame = self.create_label_frame(parent, "Database Operations")
        db_frame.pack(fill=tk.X)
        
        ops_frame = tk.Frame(db_frame, bg=self.app.colors['white'])
        ops_frame.pack(fill=tk.X)
        
        self.create_button(
            ops_frame,
            "Export All Questions",
            self.export_all_questions,
            'info'
        ).pack(side=tk.LEFT, padx=5)
        
        self.create_button(
            ops_frame,
            "Import from CSV",
            self.import_from_csv,
            'warning'
        ).pack(side=tk.LEFT, padx=5)
        
        self.create_button(
            ops_frame,
            "Backup Database",
            self.backup_database,
            'success'
        ).pack(side=tk.LEFT, padx=5)
    
    def on_manage_subject_change(self, event=None):
        """Handle subject change in manage tab"""
        subject = self.manage_subject_var.get()
        if not subject:
            return
        
        # Update topics list
        self.topics_listbox_manage.delete(0, tk.END)
        topics = self.app.config_manager.get_topics_for_subject(subject)
        for topic in topics:
            self.topics_listbox_manage.insert(tk.END, topic)
        
        # Update classifications list
        self.classifications_listbox_manage.delete(0, tk.END)
        classifications = self.app.config_manager.get_classifications_for_subject(subject)
        for classification in classifications:
            self.classifications_listbox_manage.insert(tk.END, classification)
    
    def add_new_subject(self):
        """Add new subject"""
        subject = self.new_subject_entry.get().strip()
        if not subject:
            return
        
        if self.app.config_manager.add_new_subject(subject):
            # Update all subject combos
            self.app.update_all_combos()
            
            # Update local combo
            self.manage_subject_combo['values'] = self.app.config_manager.get_all_subjects()
            
            self.new_subject_entry.delete(0, tk.END)
            self.update_status(f"Added subject: {subject}", self.app.colors['success'])
            messagebox.showinfo("Success", f"Subject '{subject}' added successfully!")
        else:
            messagebox.showinfo("Info", "Subject already exists or invalid input")
    
    def add_topic(self):
        """Add topic to selected subject"""
        subject = self.manage_subject_var.get()
        topic = self.new_topic_entry.get().strip()
        
        if not subject:
            messagebox.showwarning("No Subject", "Please select a subject first")
            return
        
        if not topic:
            return
        
        if self.app.config_manager.add_topic_to_subject(subject, topic):
            self.new_topic_entry.delete(0, tk.END)
            self.on_manage_subject_change()  # Refresh the listbox
            self.update_status(f"Added topic '{topic}' to subject '{subject}'", self.app.colors['success'])
        else:
            messagebox.showinfo("Info", "Topic already exists for this subject")
    
    def add_classification(self):
        """Add classification to selected subject"""
        subject = self.manage_subject_var.get()
        classification = self.new_classification_entry.get().strip()
        
        if not subject:
            messagebox.showwarning("No Subject", "Please select a subject first")
            return
        
        if not classification:
            return
        
        if self.app.config_manager.add_classification_to_subject(subject, classification):
            self.new_classification_entry.delete(0, tk.END)
            self.on_manage_subject_change()  # Refresh the listbox
            self.update_status(f"Added classification '{classification}' to subject '{subject}'", self.app.colors['success'])
        else:
            messagebox.showinfo("Info", "Classification already exists for this subject")
    
    def export_all_questions(self):
        """Export all questions from database"""
        if not self.app.db_manager.collection:
            messagebox.showerror("Database Error", "Database not connected")
            return
        
        try:
            # Get all questions
            all_questions = self.app.db_manager.find_questions({})
            
            if not all_questions:
                messagebox.showinfo("No Data", "No questions in database")
                return
            
            # Ask for filename
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"all_questions_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if filename:
                success, message = export_questions_to_csv(all_questions, filename)
                
                if success:
                    messagebox.showinfo("Success", message)
                    self.update_status(f"✓ Exported all {len(all_questions)} questions", self.app.colors['success'])
                else:
                    messagebox.showerror("Export Error", message)
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def import_from_csv(self):
        """Import questions from CSV"""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        success, result = import_questions_from_csv(filename)
        
        if not success:
            messagebox.showerror("Import Error", result)
            return
        
        questions = result
        imported = 0
        duplicates = 0
        
        try:
            for row in questions:
                # Check for duplicate
                if not self.app.db_manager.check_duplicate(row.get('subject', ''), row.get('question', '')):
                    # Add created_by if not present
                    if 'created_by' not in row or not row['created_by']:
                        row['created_by'] = self.app.username
                    
                    self.app.db_manager.insert_questions([row], self.app.username)
                    imported += 1
                else:
                    duplicates += 1
            
            messagebox.showinfo(
                "Import Complete",
                f"Imported: {imported} questions\nDuplicates skipped: {duplicates}"
            )
            
            self.app.refresh_dashboard()
            self.update_status(f"✓ Imported {imported} questions from CSV", self.app.colors['success'])
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import: {str(e)}")
    
    def backup_database(self):
        """Backup entire database"""
        if not self.app.db_manager.collection:
            messagebox.showerror("Database Error", "Database not connected")
            return
        
        try:
            # Get all questions
            all_questions = self.app.db_manager.find_questions({})
            
            if not all_questions:
                messagebox.showinfo("No Data", "No questions to backup")
                return
            
            # Create backup filename
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"mcq_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if filename:
                # Create backup data
                backup_data = create_backup_data(all_questions, self.app.config_manager.subject_data)
                
                # Save to JSON
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Backed up {len(all_questions)} questions to:\n{filename}")
                self.update_status(f"✓ Database backed up successfully", self.app.colors['success'])
                
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to backup: {str(e)}")