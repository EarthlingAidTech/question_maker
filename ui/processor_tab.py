"""
Processor tab for importing questions from JSON
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from .base_tab import BaseTab
from utils.helpers import parse_json_questions, export_questions_to_csv


class ProcessorTab(BaseTab):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.processed_questions = []
        self.setup()
    
    def setup(self):
        """Setup JSON processor tab"""
        # Create scrollable frame
        scrollable_frame = self.create_scrollable_frame(self.frame)
        
        # Content
        container = tk.Frame(scrollable_frame, bg=self.app.colors['bg'])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            container,
            text="Import Questions from JSON",
            font=('Arial', 18, 'bold'),
            bg=self.app.colors['bg'],
            fg=self.app.colors['primary']
        ).pack(pady=(0, 20))
        
        # JSON input
        json_frame = self.create_label_frame(container, "JSON Input")
        json_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.json_input = scrolledtext.ScrolledText(
            json_frame,
            font=('Consolas', 10),
            wrap=tk.WORD,
            height=15
        )
        self.json_input.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = tk.Frame(container, bg=self.app.colors['bg'])
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.create_button(
            button_frame,
            "Process JSON",
            self.process_json,
            'secondary'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_json_btn = self.create_button(
            button_frame,
            "Save to Database",
            self.save_json_to_db,
            'success'
        )
        self.save_json_btn.config(state=tk.DISABLED)
        self.save_json_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_csv_btn = self.create_button(
            button_frame,
            "Export to CSV",
            self.export_to_csv,
            'warning'
        )
        self.export_csv_btn.config(state=tk.DISABLED)
        self.export_csv_btn.pack(side=tk.LEFT)
        
        # Options
        options_frame = tk.Frame(container, bg=self.app.colors['bg'])
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.auto_add_topics_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Automatically add new topics/classifications to system",
            variable=self.auto_add_topics_var,
            font=('Arial', 11),
            bg=self.app.colors['bg']
        ).pack()
        
        # Results
        results_frame = self.create_label_frame(container, "Processing Results")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(
            results_frame,
            font=('Arial', 11),
            height=8,
            wrap=tk.WORD
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
    
    def process_json(self):
        """Process JSON input"""
        json_text = self.json_input.get(1.0, tk.END).strip()
        if not json_text:
            messagebox.showwarning("No Input", "Please paste JSON data first")
            return
        
        # Parse JSON
        success, result, suggested_topics, suggested_classifications = parse_json_questions(json_text)
        
        if not success:
            messagebox.showerror("Error", result)
            return
        
        questions = result
        
        # Clear results
        self.results_text.delete(1.0, tk.END)
        
        # Process AI suggestions if enabled
        if self.auto_add_topics_var.get() and (suggested_topics or suggested_classifications):
            self.results_text.insert(tk.END, "AI Suggestions found:\n")
            
            # Process suggested topics
            if suggested_topics:
                for topic in suggested_topics:
                    # Find which subject this topic belongs to
                    for q in questions:
                        if q.get('topic') == topic:
                            subject = q.get('subject', '')
                            if subject and self.app.config_manager.add_topic_to_subject(subject, topic):
                                self.results_text.insert(tk.END, f"✓ Added new topic '{topic}' to subject '{subject}'\n")
                            break
            
            # Process suggested classifications
            if suggested_classifications:
                for classification in suggested_classifications:
                    for q in questions:
                        if q.get('classification') == classification:
                            subject = q.get('subject', '')
                            if subject and self.app.config_manager.add_classification_to_subject(subject, classification):
                                self.results_text.insert(tk.END, f"✓ Added new classification '{classification}' to subject '{subject}'\n")
                            break
            
            self.results_text.insert(tk.END, "\n")
        
        # Check for duplicates
        duplicates = []
        new_questions = []
        
        if self.app.db_manager.collection:
            for q in questions:
                # Check for duplicates based on question and subject
                if self.app.db_manager.check_duplicate(q.get('subject', ''), q.get('question', '')):
                    duplicates.append(q['question'])
                else:
                    new_questions.append(q)
        else:
            new_questions = questions
            self.results_text.insert(tk.END, "⚠️ Database not connected. Cannot check for duplicates.\n\n")
        
        # Display results
        self.results_text.insert(tk.END, f"Total questions in JSON: {len(questions)}\n")
        self.results_text.insert(tk.END, f"New questions: {len(new_questions)}\n")
        self.results_text.insert(tk.END, f"Duplicate questions: {len(duplicates)}\n\n")
        
        if duplicates:
            self.results_text.insert(tk.END, "Duplicate questions found:\n")
            for i, dup in enumerate(duplicates, 1):
                self.results_text.insert(tk.END, f"{i}. {dup[:80]}...\n")
        
        # Store processed questions
        self.processed_questions = new_questions
        
        # Enable buttons if there are new questions
        if new_questions:
            self.save_json_btn.config(state=tk.NORMAL)
            self.export_csv_btn.config(state=tk.NORMAL)
            self.update_status(f"Processed {len(questions)} questions. {len(new_questions)} are new.")
        else:
            self.update_status("All questions are duplicates!")
    
    def save_json_to_db(self):
        """Save processed questions to database"""
        if not self.processed_questions:
            messagebox.showwarning("No Data", "No new questions to save")
            return
        
        if not self.app.db_manager.collection:
            messagebox.showerror("Database Error", "Database not connected")
            return
        
        try:
            # Insert questions
# Insert questions
            count = self.app.db_manager.insert_questions(self.processed_questions, self.app.username)
            
            # Update user's question count
            if hasattr(self.app, 'user_manager') and self.app.user_manager.collection:
                self.app.user_manager.update_questions_created(self.app.username, count)
            
            messagebox.showinfo(
                "Success", 
                f"Successfully saved {count} questions to database!"
            )

            
            # Clear inputs
            self.json_input.delete(1.0, tk.END)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"✓ Saved {count} questions to database")
            
            # Disable buttons
            self.save_json_btn.config(state=tk.DISABLED)
            self.export_csv_btn.config(state=tk.DISABLED)
            
            # Update combos
            self.app.update_all_combos()
            
            # Refresh dashboard
            self.app.refresh_dashboard()
            
            self.update_status(f"✓ {count} questions saved to database", self.app.colors['success'])
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save to database:\n{str(e)}")
    
    def export_to_csv(self):
        """Export questions to CSV"""
        if not self.processed_questions:
            messagebox.showwarning("No Data", "No questions to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"mcq_questions_{self.app.username}.csv"
        )
        
        if filename:
            success, message = export_questions_to_csv(self.processed_questions, filename)
            
            if success:
                messagebox.showinfo("Success", message)
                self.update_status(f"✓ Exported {len(self.processed_questions)} questions to CSV", self.app.colors['success'])
            else:
                messagebox.showerror("Export Error", message)