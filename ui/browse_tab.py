"""
Browse tab for viewing and editing questions
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
from .base_tab import BaseTab
from utils.helpers import export_questions_to_csv, safe_grab_set, validate_question


class BrowseTab(BaseTab):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.current_questions = []
        self.current_page = 0
        self.setup()
    
    def setup(self):
        """Setup browse and edit tab"""
        # Main container
        container = tk.Frame(self.frame, bg=self.app.colors['bg'])
        container.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Title and search bar
        top_frame = tk.Frame(container, bg=self.app.colors['bg'])
        top_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        top_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(
            top_frame,
            text="Browse Questions",
            font=('Arial', 18, 'bold'),
            bg=self.app.colors['bg'],
            fg=self.app.colors['primary']
        ).grid(row=0, column=0, sticky='w')
        
        # Search frame
        search_frame = tk.Frame(top_frame, bg=self.app.colors['bg'])
        search_frame.grid(row=0, column=1, sticky='e')
        
        tk.Label(
            search_frame,
            text="Search:",
            font=('Arial', 11),
            bg=self.app.colors['bg']
        ).pack(side=tk.LEFT, padx=5)
        
        self.search_entry = tk.Entry(search_frame, font=('Arial', 11))
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_entry.bind('<Return>', lambda e: self.search_questions())
        
        self.create_button(
            search_frame,
            "🔍 Search",
            self.search_questions,
            'secondary',
            padx=15,
            pady=5,
            font=('Arial', 10)
        ).pack(side=tk.LEFT)
        
        # Filters frame
        filters_frame = self.create_label_frame(container, "Filters", padx=20, pady=15)
        filters_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        
        # Setup filters
        self.setup_filters(filters_frame)
        
        # Questions list
        list_frame = tk.Frame(container, bg=self.app.colors['bg'])
        list_frame.grid(row=2, column=0, sticky='nsew')
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Create treeview
        columns = ('ID', 'Question', 'Subject', 'Topic', 'Classification', 'Level', 'Marks', 'Created By')
        self.questions_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        self.questions_tree.grid(row=0, column=0, sticky='nsew')
        
        # Define column headings
        for col in columns:
            self.questions_tree.heading(col, text=col)
        
        # Set column widths
        self.set_treeview_column_widths()
        
        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.questions_tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.questions_tree.xview)
        self.questions_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Bind double-click to edit
        self.questions_tree.bind('<Double-Button-1>', self.edit_question)
        
        # Bind resize event
        self.questions_tree.bind('<Configure>', self.on_treeview_resize)
        
        # Auto-load data after a short delay
        self.frame.after(500, self.initial_load)
        
        # Action buttons
        action_frame = tk.Frame(container, bg=self.app.colors['bg'])
        action_frame.grid(row=3, column=0, sticky='ew', pady=(20, 0))
        
        self.create_button(
            action_frame,
            "Refresh",
            self.refresh_questions,
            'secondary'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.create_button(
            action_frame,
            "Edit Selected",
            lambda: self.edit_question(None),
            'warning'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.create_button(
            action_frame,
            "Delete Selected",
            self.delete_question,
            'danger'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.create_button(
            action_frame,
            "Export Selected",
            self.export_selected,
            'success'
        ).pack(side=tk.LEFT)
        
        # Pagination frame
        self.setup_pagination(container)
    
    def setup_filters(self, parent):
        """Setup filter controls"""
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(3, weight=1)
        parent.grid_columnconfigure(5, weight=1)
        
        # Row 1
        tk.Label(
            parent,
            text="Subject:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        
        self.filter_subject = ttk.Combobox(
            parent,
            values=['All'] + self.app.config_manager.get_all_subjects(),
            font=('Arial', 10),
            state='readonly'
        )
        self.filter_subject.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self.filter_subject.current(0)
        self.filter_subject.bind('<<ComboboxSelected>>', self.on_filter_subject_change)
        
        tk.Label(
            parent,
            text="Level:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=0, column=2, sticky='e', padx=5, pady=5)
        
        self.filter_level = ttk.Combobox(
            parent,
            values=['All'] + self.app.config_manager.levels,
            font=('Arial', 10),
            state='readonly'
        )
        self.filter_level.grid(row=0, column=3, sticky='ew', padx=5, pady=5)
        self.filter_level.current(0)
        
        tk.Label(
            parent,
            text="Created by:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=0, column=4, sticky='e', padx=5, pady=5)
        
        self.filter_created_by = ttk.Combobox(
            parent,
            values=['All', 'My Questions'],
            font=('Arial', 10),
            state='readonly'
        )
        self.filter_created_by.grid(row=0, column=5, sticky='ew', padx=5, pady=5)
        self.filter_created_by.current(0)
        
        # Row 2
        tk.Label(
            parent,
            text="Topic:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        
        self.filter_topic = ttk.Combobox(
            parent,
            values=['All'],
            font=('Arial', 10),
            state='readonly'
        )
        self.filter_topic.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        self.filter_topic.current(0)
        
        tk.Label(
            parent,
            text="Classification:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=1, column=2, sticky='e', padx=5, pady=5)
        
        self.filter_classification = ttk.Combobox(
            parent,
            values=['All'],
            font=('Arial', 10),
            state='readonly'
        )
        self.filter_classification.grid(row=1, column=3, sticky='ew', padx=5, pady=5)
        self.filter_classification.current(0)
        
        # Apply filters button
        self.create_button(
            parent,
            "Apply Filters",
            self.apply_filters,
            'info',
            padx=20,
            pady=5,
            font=('Arial', 10)
        ).grid(row=1, column=5, padx=5, pady=5)
    
    def setup_pagination(self, parent):
        """Setup pagination controls"""
        pagination_frame = tk.Frame(parent, bg=self.app.colors['bg'])
        pagination_frame.grid(row=4, column=0, sticky='ew', pady=(10, 0))
        
        self.prev_btn = self.create_button(
            pagination_frame,
            "← Previous",
            self.prev_page,
            'light',
            padx=15,
            pady=5,
            font=('Arial', 10),
            fg=self.app.colors['dark']
        )
        self.prev_btn.config(state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.page_label = tk.Label(
            pagination_frame,
            text="Page 1 of 1",
            font=('Arial', 11),
            bg=self.app.colors['bg']
        )
        self.page_label.pack(side=tk.LEFT, padx=20)
        
        self.next_btn = self.create_button(
            pagination_frame,
            "Next →",
            self.next_page,
            'light',
            padx=15,
            pady=5,
            font=('Arial', 10),
            fg=self.app.colors['dark']
        )
        self.next_btn.config(state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=5)
    
    def set_treeview_column_widths(self):
        """Set responsive column widths based on window size"""
        try:
            tree_width = self.questions_tree.winfo_width()
            if tree_width <= 1:  # Widget not yet rendered
                tree_width = 800  # Default width
            
            # Calculate proportional widths
            total_weight = 50 + 300 + 100 + 120 + 120 + 60 + 50 + 100
            
            self.questions_tree.column('ID', width=int(tree_width * 50/total_weight), minwidth=40)
            self.questions_tree.column('Question', width=int(tree_width * 300/total_weight), minwidth=150)
            self.questions_tree.column('Subject', width=int(tree_width * 100/total_weight), minwidth=80)
            self.questions_tree.column('Topic', width=int(tree_width * 120/total_weight), minwidth=80)
            self.questions_tree.column('Classification', width=int(tree_width * 120/total_weight), minwidth=80)
            self.questions_tree.column('Level', width=int(tree_width * 60/total_weight), minwidth=50)
            self.questions_tree.column('Marks', width=int(tree_width * 50/total_weight), minwidth=40)
            self.questions_tree.column('Created By', width=int(tree_width * 100/total_weight), minwidth=80)
        except:
            pass
    
    def on_treeview_resize(self, event=None):
        """Handle treeview resize event"""
        self.set_treeview_column_widths()
    
    def on_filter_subject_change(self, event=None):
        """Update topic and classification filters when subject filter changes"""
        subject = self.filter_subject.get()
        if subject == 'All':
            # Get all unique topics from database
            if self.app.db_manager.collection:
                topics = self.app.db_manager.get_distinct_values("topic")
                self.filter_topic['values'] = ['All'] + sorted(topics)
                
                classifications = self.app.db_manager.get_distinct_values("classification")
                self.filter_classification['values'] = ['All'] + sorted(classifications)
            else:
                self.filter_topic['values'] = ['All']
                self.filter_classification['values'] = ['All']
        else:
            # Get topics for specific subject
            topics = self.app.config_manager.get_topics_for_subject(subject)
            self.filter_topic['values'] = ['All'] + topics
            
            # Get classifications for specific subject
            classifications = self.app.config_manager.get_classifications_for_subject(subject)
            self.filter_classification['values'] = ['All'] + classifications
        
        self.filter_topic.current(0)
        self.filter_classification.current(0)
    
    def apply_filters(self):
        """Apply filters and refresh questions list"""
        if not self.app.db_manager.collection:
            messagebox.showwarning("Database Error", "Database not connected")
            return
        
        try:
            # Build filter query
            query = {}
            
            # Subject filter
            subject = self.filter_subject.get()
            if subject != 'All':
                query['subject'] = subject
            
            # Topic filter
            topic = self.filter_topic.get()
            if topic != 'All':
                query['topic'] = topic
            
            # Classification filter
            classification = self.filter_classification.get()
            if classification != 'All':
                query['classification'] = classification
            
            # Level filter
            level = self.filter_level.get()
            if level != 'All':
                query['level'] = level
            
            # Created by filter
            created_by = self.filter_created_by.get()
            if created_by == 'My Questions':
                query['created_by'] = self.app.username
            
            # Get questions
            self.current_questions = self.app.db_manager.find_questions(query)
            self.app.current_page = 0
            
            # Update display
            self.display_questions()
            
            self.update_status(f"Found {len(self.current_questions)} questions matching filters")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filters: {str(e)}")
    
    def search_questions(self):
        """Search questions"""
        if not self.app.db_manager.collection:
            messagebox.showwarning("Database Error", "Database not connected")
            return
        
        search_text = self.search_entry.get().strip()
        if not search_text:
            self.apply_filters()
            return
        
        try:
            # Build search query
            query = {
                "$or": [
                    {"question": {"$regex": search_text, "$options": "i"}},
                    {"subject": {"$regex": search_text, "$options": "i"}},
                    {"topic": {"$regex": search_text, "$options": "i"}},
                    {"classification": {"$regex": search_text, "$options": "i"}},
                    {"created_by": {"$regex": search_text, "$options": "i"}}
                ]
            }
            
            # Apply existing filters
            subject = self.filter_subject.get()
            if subject != 'All':
                query['subject'] = subject
            
            topic = self.filter_topic.get()
            if topic != 'All':
                query['topic'] = topic
            
            classification = self.filter_classification.get()
            if classification != 'All':
                query['classification'] = classification
            
            level = self.filter_level.get()
            if level != 'All':
                query['level'] = level
            
            created_by = self.filter_created_by.get()
            if created_by == 'My Questions':
                query['created_by'] = self.app.username
            
            # Get questions
            self.current_questions = self.app.db_manager.find_questions(query)
            self.app.current_page = 0
            
            # Update display
            self.display_questions()
            
            self.update_status(f"Found {len(self.current_questions)} questions matching '{search_text}'")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search: {str(e)}")
    
    def display_questions(self):
        """Display questions in treeview"""
        # Clear existing items
        for item in self.questions_tree.get_children():
            self.questions_tree.delete(item)
        
        # Calculate pagination
        total_pages = max(1, (len(self.current_questions) + self.app.questions_per_page - 1) // self.app.questions_per_page)
        self.app.current_page = min(self.app.current_page, total_pages - 1)
        
        start_idx = self.app.current_page * self.app.questions_per_page
        end_idx = min(start_idx + self.app.questions_per_page, len(self.current_questions))
        
        # Display questions for current page
        for i in range(start_idx, end_idx):
            q = self.current_questions[i]
            question_text = q.get('question', '')[:60] + '...' if len(q.get('question', '')) > 60 else q.get('question', '')
            
            self.questions_tree.insert('', 'end', values=(
                str(q.get('_id', ''))[-8:],  # Show last 8 chars of ID
                question_text,
                q.get('subject', ''),
                q.get('topic', ''),
                q.get('classification', ''),
                q.get('level', ''),
                q.get('marks', ''),
                q.get('created_by', '')
            ), tags=(str(q.get('_id', '')),))  # Store full ID in tags
        
        # Update pagination controls
        self.page_label.config(text=f"Page {self.app.current_page + 1} of {total_pages}")
        self.prev_btn.config(state=tk.NORMAL if self.app.current_page > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.app.current_page < total_pages - 1 else tk.DISABLED)
    
    def prev_page(self):
        """Go to previous page"""
        if self.app.current_page > 0:
            self.app.current_page -= 1
            self.display_questions()
    
    def next_page(self):
        """Go to next page"""
        total_pages = (len(self.current_questions) + self.app.questions_per_page - 1) // self.app.questions_per_page
        if self.app.current_page < total_pages - 1:
            self.app.current_page += 1
            self.display_questions()
    
    def refresh_questions(self):
        """Refresh questions list"""
        self.apply_filters()
    
    def initial_load(self):
        """Initial data load when tab is first shown"""
        if self.app.db_manager.collection and not hasattr(self, 'data_loaded'):
            self.apply_filters()
            self.data_loaded = True
    
    def edit_question(self, event):
        """Edit selected question"""
        selection = self.questions_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a question to edit")
            return
        
        # Get question ID from tags
        item = self.questions_tree.item(selection[0])
        question_id = item['tags'][0]
        
        # Find question in current list
        question = None
        for q in self.current_questions:
            if str(q.get('_id', '')) == question_id:
                question = q
                break
        
        if not question:
            messagebox.showerror("Error", "Question not found")
            return
        
        # Create edit dialog
        EditQuestionDialog(self.app, question, self.on_question_updated)
    
    def on_question_updated(self):
        """Callback when question is updated"""
        self.apply_filters()
    
    def delete_question(self):
        """Delete selected question"""
        selection = self.questions_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a question to delete")
            return
        
        # Get question details
        item = self.questions_tree.item(selection[0])
        question_id = item['tags'][0]
        
        # Find question to check ownership
        question = None
        for q in self.current_questions:
            if str(q.get('_id', '')) == question_id:
                question = q
                break
        
        if not question:
            messagebox.showerror("Error", "Question not found")
            return
        
        # Check if user owns the question
        if question.get('created_by') != self.app.username:
            response = messagebox.askyesno(
                "Confirm Delete", 
                f"This question was created by '{question.get('created_by', 'Unknown')}'.\n"
                "Are you sure you want to delete it?"
            )
            if not response:
                return
        else:
            # Confirm deletion for own questions
            if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete your question?"):
                return
        
        try:
            # Delete from database
            if self.app.db_manager.delete_question(question_id):
                messagebox.showinfo("Success", "Question deleted successfully!")
                self.apply_filters()
                self.app.refresh_dashboard()
            else:
                messagebox.showerror("Error", "Failed to delete question")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete question: {str(e)}")
    
    def export_selected(self):
        """Export selected questions"""
        selection = self.questions_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select questions to export")
            return
        
        # Get selected questions
        selected_questions = []
        for item in selection:
            question_id = self.questions_tree.item(item)['tags'][0]
            for q in self.current_questions:
                if str(q.get('_id', '')) == question_id:
                    selected_questions.append(q)
                    break
        
        if not selected_questions:
            return
        
        # Ask for filename
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"selected_questions_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            success, message = export_questions_to_csv(selected_questions, filename)
            
            if success:
                messagebox.showinfo("Success", message)
                self.update_status(f"✓ Exported {len(selected_questions)} questions", self.app.colors['success'])
            else:
                messagebox.showerror("Export Error", message)


class EditQuestionDialog:
    """Dialog for editing a question"""
    
    def __init__(self, app, question, callback):
        self.app = app
        self.question = question
        self.callback = callback
        self.widgets = {}
        
        # Create dialog
        self.dialog = tk.Toplevel(app.root)
        self.dialog.title("Edit Question")
        self.dialog.geometry("800x750")
        self.dialog.transient(app.root)
        self.dialog.configure(bg=app.colors['white'])
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 800) // 2
        y = (self.dialog.winfo_screenheight() - 750) // 2
        self.dialog.geometry(f"800x750+{x}+{y}")
        
        # Make dialog modal
        self.dialog.update()
        self.dialog.after(100, lambda: safe_grab_set(self.dialog))
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup edit dialog UI"""
        # Create scrollable frame
        canvas = tk.Canvas(self.dialog, bg=self.app.colors['white'])
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.app.colors['white'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create form
        form_frame = tk.Frame(scrollable_frame, bg=self.app.colors['white'], padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Subject
        self.add_form_field(form_frame, 0, "Subject:", 'subject', 'combobox',
                           values=self.app.config_manager.get_all_subjects())
        
        # Topic
        self.add_form_field(form_frame, 1, "Topic:", 'topic', 'combobox')
        
        # Classification
        self.add_form_field(form_frame, 2, "Classification:", 'classification', 'combobox')
        
        # Update topics and classifications based on subject
        def update_combos():
            subject = self.widgets['subject'].get()
            if subject:
                topics = self.app.config_manager.get_topics_for_subject(subject)
                self.widgets['topic']['values'] = topics
                
                classifications = self.app.config_manager.get_classifications_for_subject(subject)
                self.widgets['classification']['values'] = classifications
        
        update_combos()
        self.widgets['subject'].bind('<<ComboboxSelected>>', lambda e: update_combos())
        
        # Level
        self.add_form_field(form_frame, 3, "Level:", 'level', 'combobox',
                           values=self.app.config_manager.levels, readonly=True)
        
        # Marks
        self.add_form_field(form_frame, 4, "Marks:", 'marks', 'entry')
        
        # Question
        self.add_form_field(form_frame, 5, "Question:", 'question', 'text', height=4)
        
        # Options
        for i in range(1, 5):
            self.add_form_field(form_frame, 5+i, f"Option {i}:", f'option{i}', 'entry')
        
        # Correct Answer
        self.add_form_field(form_frame, 10, "Correct Answer:", 'correctAnswer', 'combobox')
        self.update_correct_answer_options()
        
        # Dynamic update for correct answer dropdown
        def update_correct_answer_options(*args):
            current_correct = self.widgets['correctAnswer'].get()
            options = [
                self.widgets['option1'].get(),
                self.widgets['option2'].get(),
                self.widgets['option3'].get(),
                self.widgets['option4'].get()
            ]
            self.widgets['correctAnswer']['values'] = options
            if current_correct in options:
                self.widgets['correctAnswer'].set(current_correct)
        
        # Bind option changes
        for i in range(1, 5):
            self.widgets[f'option{i}'].bind('<KeyRelease>', update_correct_answer_options)
        
        # Created by (readonly)
        tk.Label(
            form_frame,
            text="Created by:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=11, column=0, sticky='e', padx=10, pady=5)
        
        tk.Label(
            form_frame,
            text=self.question.get('created_by', 'Unknown'),
            font=('Arial', 11),
            bg=self.app.colors['white'],
            fg=self.app.colors['dark']
        ).grid(row=11, column=1, padx=10, pady=5, sticky='w')
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=self.app.colors['white'])
        button_frame.grid(row=12, column=0, columnspan=2, pady=20)
        
        tk.Button(
            button_frame,
            text="Save Changes",
            command=self.save_changes,
            font=('Arial', 11, 'bold'),
            bg=self.app.colors['success'],
            fg='white',
            padx=30,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy,
            font=('Arial', 11),
            bg=self.app.colors['light'],
            fg=self.app.colors['dark'],
            padx=30,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT
        ).pack(side=tk.LEFT)
    
    def add_form_field(self, parent, row, label, field_name, widget_type, **kwargs):
        """Add a form field to the dialog"""
        tk.Label(
            parent,
            text=label,
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=row, column=0, sticky='ne' if widget_type == 'text' else 'e', padx=10, pady=5)
        
        if widget_type == 'entry':
            widget = tk.Entry(parent, font=('Arial', 11), width=50)
            widget.insert(0, self.question.get(field_name, ''))
        elif widget_type == 'combobox':
            widget = ttk.Combobox(parent, font=('Arial', 11), width=47, **kwargs)
            widget.set(self.question.get(field_name, ''))
        elif widget_type == 'text':
            widget = tk.Text(parent, font=('Arial', 11), width=50, height=kwargs.get('height', 4), wrap=tk.WORD)
            widget.insert(1.0, self.question.get(field_name, ''))
        
        widget.grid(row=row, column=1, padx=10, pady=5, sticky='w')
        self.widgets[field_name] = widget
    
    def update_correct_answer_options(self):
        """Update correct answer dropdown options"""
        self.widgets['correctAnswer']['values'] = [
            self.question.get('option1', ''),
            self.question.get('option2', ''),
            self.question.get('option3', ''),
            self.question.get('option4', '')
        ]
    
    def save_changes(self):
        """Save changes to the question"""
        try:
            # Get updated values
            updated = {
                'subject': self.widgets['subject'].get(),
                'topic': self.widgets['topic'].get(),
                'classification': self.widgets['classification'].get(),
                'level': self.widgets['level'].get(),
                'marks': int(self.widgets['marks'].get()),
                'question': self.widgets['question'].get(1.0, tk.END).strip(),
                'option1': self.widgets['option1'].get(),
                'option2': self.widgets['option2'].get(),
                'option3': self.widgets['option3'].get(),
                'option4': self.widgets['option4'].get(),
                'correctAnswer': self.widgets['correctAnswer'].get()
            }
            
            # Validate
            is_valid, message = validate_question(updated)
            if not is_valid:
                messagebox.showwarning("Validation Error", message)
                return
            
            # Update in database
            self.app.db_manager.update_question(str(self.question['_id']), updated)
            
            messagebox.showinfo("Success", "Question updated successfully!")
            self.dialog.destroy()
            
            # Refresh list
            if self.callback:
                self.callback()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Marks must be a number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update question: {str(e)}")