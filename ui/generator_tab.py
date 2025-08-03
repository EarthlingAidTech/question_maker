"""
Generator tab for MCQ prompt generation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pyperclip
from .base_tab import BaseTab
from utils.helpers import generate_random_seed


class GeneratorTab(BaseTab):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.setup()
    
    def setup(self):
        """Setup prompt generator tab"""
        # Create scrollable frame
        scrollable_frame = self.create_scrollable_frame(self.frame)
        
        # Content
        container = tk.Frame(scrollable_frame, bg=self.app.colors['bg'])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            container,
            text="Generate MCQ Prompt",
            font=('Arial', 18, 'bold'),
            bg=self.app.colors['bg'],
            fg=self.app.colors['primary']
        ).pack(pady=(0, 20))
        
        # Parameters frame
        params_frame = self.create_label_frame(container, "Parameters")
        params_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Configure grid weights for responsiveness
        for i in range(8):
            params_frame.grid_rowconfigure(i, weight=0)
        params_frame.grid_columnconfigure(0, weight=0, minsize=150)
        params_frame.grid_columnconfigure(1, weight=1)
        
        # Number of questions
        tk.Label(
            params_frame,
            text="Number of Questions:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=0, column=0, sticky='e', padx=10, pady=8)
        
        num_questions_frame = tk.Frame(params_frame, bg=self.app.colors['white'])
        num_questions_frame.grid(row=0, column=1, sticky='ew', padx=10, pady=8)
        
        self.num_questions_entry = tk.Entry(num_questions_frame, font=('Arial', 11), width=10)
        self.num_questions_entry.pack(side=tk.LEFT)
        self.num_questions_entry.insert(0, "10")
        
        # Subject selection
        tk.Label(
            params_frame,
            text="Subject:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=1, column=0, sticky='e', padx=10, pady=8)
        
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(
            params_frame,
            textvariable=self.subject_var,
            values=self.app.config_manager.get_all_subjects(),
            font=('Arial', 11)
        )
        self.subject_combo.grid(row=1, column=1, padx=10, pady=8, sticky='ew')
        self.subject_combo.bind('<<ComboboxSelected>>', self.on_subject_change)
        
        # Instructions for multi-selection
        instruction_frame = tk.Frame(params_frame, bg=self.app.colors['light'], relief=tk.RIDGE, bd=1)
        instruction_frame.grid(row=2, column=0, columnspan=2, pady=(10, 5), padx=10, sticky='ew')
        
        tk.Label(
            instruction_frame,
            text="📌 Multi-Selection Instructions:",
            font=('Arial', 10, 'bold'),
            bg=self.app.colors['light'],
            fg=self.app.colors['secondary']
        ).pack(pady=(5, 0))
        
        tk.Label(
            instruction_frame,
            text="• Click to select one item\n• Ctrl+Click (Cmd+Click on Mac) to select multiple items\n• You can select from Classifications, Topics, or BOTH!",
            font=('Arial', 9),
            bg=self.app.colors['light'],
            fg=self.app.colors['dark'],
            justify=tk.LEFT
        ).pack(pady=(0, 5))
        
        # Classifications selection
        tk.Label(
            params_frame,
            text="Classifications (optional):",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=3, column=0, sticky='ne', padx=10, pady=8)
        
        class_frame = tk.Frame(params_frame, bg=self.app.colors['white'])
        class_frame.grid(row=3, column=1, padx=10, pady=8, sticky='ew')
        class_frame.grid_columnconfigure(0, weight=1)
        class_frame.grid_rowconfigure(0, weight=1)
        
        self.classifications_listbox = tk.Listbox(
            class_frame,
            selectmode=tk.MULTIPLE,
            height=6,
            font=('Arial', 10),
            exportselection=False,
            selectbackground=self.app.colors['secondary'],
            selectforeground='white'
        )
        self.classifications_listbox.grid(row=0, column=0, sticky='nsew')
        
        class_scroll = ttk.Scrollbar(class_frame, command=self.classifications_listbox.yview)
        class_scroll.grid(row=0, column=1, sticky='ns')
        self.classifications_listbox.config(yscrollcommand=class_scroll.set)
        
        # Topics selection
        tk.Label(
            params_frame,
            text="Topics (optional):",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=4, column=0, sticky='ne', padx=10, pady=8)
        
        topics_frame = tk.Frame(params_frame, bg=self.app.colors['white'])
        topics_frame.grid(row=4, column=1, padx=10, pady=8, sticky='ew')
        topics_frame.grid_columnconfigure(0, weight=1)
        topics_frame.grid_rowconfigure(0, weight=1)
        
        self.topics_listbox = tk.Listbox(
            topics_frame,
            selectmode=tk.MULTIPLE,
            height=6,
            font=('Arial', 10),
            exportselection=False,
            selectbackground=self.app.colors['success'],
            selectforeground='white'
        )
        self.topics_listbox.grid(row=0, column=0, sticky='nsew')
        
        topics_scroll = ttk.Scrollbar(topics_frame, command=self.topics_listbox.yview)
        topics_scroll.grid(row=0, column=1, sticky='ns')
        self.topics_listbox.config(yscrollcommand=topics_scroll.set)
        
        # Difficulty Level
        tk.Label(
            params_frame,
            text="Difficulty Level:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=5, column=0, sticky='e', padx=10, pady=8)
        
        self.level_var = tk.StringVar()
        self.level_combo = ttk.Combobox(
            params_frame,
            textvariable=self.level_var,
            values=self.app.config_manager.levels,
            font=('Arial', 11),
            state='readonly'
        )
        self.level_combo.grid(row=5, column=1, padx=10, pady=8, sticky='ew')
        self.level_combo.current(0)
        
        # Marks per question
        tk.Label(
            params_frame,
            text="Marks per Question:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=6, column=0, sticky='e', padx=10, pady=8)
        
        marks_frame = tk.Frame(params_frame, bg=self.app.colors['white'])
        marks_frame.grid(row=6, column=1, sticky='ew', padx=10, pady=8)
        
        self.marks_entry = tk.Entry(marks_frame, font=('Arial', 11), width=10)
        self.marks_entry.pack(side=tk.LEFT)
        self.marks_entry.insert(0, "1")
        
        # Options frame
        options_frame = tk.Frame(params_frame, bg=self.app.colors['white'])
        options_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        self.unique_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Generate unique questions (different from database)",
            variable=self.unique_var,
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).pack()
        
        self.ai_suggest_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Allow AI to suggest new topics/classifications",
            variable=self.ai_suggest_var,
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).pack()
        
        # Seed options
        seed_frame = tk.Frame(params_frame, bg=self.app.colors['white'])
        seed_frame.grid(row=8, column=0, columnspan=2, pady=5)
        
        tk.Label(
            seed_frame,
            text="Variation Seed:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.seed_entry = tk.Entry(seed_frame, font=('Arial', 11), width=25)
        self.seed_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            seed_frame,
            text="Random",
            command=self.generate_random_seed,
            font=('Arial', 10),
            bg=self.app.colors['secondary'],
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2',
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = tk.Frame(container, bg=self.app.colors['bg'])
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.create_button(
            button_frame,
            "Generate Prompt",
            self.generate_prompt,
            'secondary'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.copy_prompt_btn = self.create_button(
            button_frame,
            "Copy to Clipboard",
            self.copy_prompt,
            'success'
        )
        self.copy_prompt_btn.config(state=tk.DISABLED)
        self.copy_prompt_btn.pack(side=tk.LEFT)
        
        # Output area
        output_frame = self.create_label_frame(container, "Generated Prompt")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.prompt_output = scrolledtext.ScrolledText(
            output_frame,
            font=('Consolas', 10),
            wrap=tk.WORD,
            height=15
        )
        self.prompt_output.pack(fill=tk.BOTH, expand=True)
    
    def on_subject_change(self, event=None):
        """Handle subject change to update topics and classifications"""
        subject = self.subject_var.get()
        if not subject:
            return
        
        # Update classifications
        self.classifications_listbox.delete(0, tk.END)
        classifications = self.app.config_manager.get_classifications_for_subject(subject)
        for classification in classifications:
            self.classifications_listbox.insert(tk.END, classification)
        
        # Update topics
        self.topics_listbox.delete(0, tk.END)
        topics = self.app.config_manager.get_topics_for_subject(subject)
        for topic in topics:
            self.topics_listbox.insert(tk.END, topic)
    
    def generate_random_seed(self):
        """Generate random seed"""
        seed = generate_random_seed()
        self.seed_entry.delete(0, tk.END)
        self.seed_entry.insert(0, seed)
    
    def generate_prompt(self):
        """Generate MCQ prompt based on scenario"""
        try:
            # Get values
            num_questions = self.num_questions_entry.get()
            subject = self.subject_var.get()
            selected_classifications = [self.classifications_listbox.get(i) for i in self.classifications_listbox.curselection()]
            selected_topics = [self.topics_listbox.get(i) for i in self.topics_listbox.curselection()]
            level = self.level_var.get()
            marks = self.marks_entry.get()
            generate_unique = self.unique_var.get()
            ai_suggest = self.ai_suggest_var.get()
            seed = self.seed_entry.get().strip()
            
            # Validate
            if not all([num_questions, subject, level, marks]):
                messagebox.showwarning("Incomplete Form", "Please fill required fields (questions, subject, level, marks)")
                return
            
            try:
                int(num_questions)
                int(marks)
            except ValueError:
                messagebox.showerror("Invalid Input", "Number of questions and marks must be integers")
                return
            
            # Build unique instruction
            unique_instruction = ""
            if generate_unique:
                unique_instruction = f"""
**IMPORTANT - Generate Unique Questions:**
- Generate completely NEW and DIFFERENT questions from any previous runs
- Do NOT repeat common questions that are typically asked for this subject
- Use creative and less common scenarios, examples, and concepts
- Avoid standard textbook questions
- Think of edge cases, real-world applications, and interdisciplinary connections
- Include questions about recent developments or trends in the field
- Use varied question formats (scenario-based, comparison, application-based)
"""
                if seed:
                    unique_instruction += f"- Use this variation seed for uniqueness: '{seed}'\n"
                    unique_instruction += f"- Base your question themes and topics on this seed to ensure different outputs\n"
            
            # Determine which prompt template to use
            if not selected_classifications and not selected_topics:
                prompt = self.generate_prompt_template_1(num_questions, subject, level, marks, unique_instruction, ai_suggest)
            elif selected_classifications and not selected_topics:
                prompt = self.generate_prompt_template_2(num_questions, subject, level, marks, selected_classifications, unique_instruction, ai_suggest)
            elif not selected_classifications and selected_topics:
                prompt = self.generate_prompt_template_3(num_questions, subject, level, marks, selected_topics, unique_instruction, ai_suggest)
            else:
                prompt = self.generate_prompt_template_4(num_questions, subject, level, marks, selected_classifications, selected_topics, unique_instruction)
            
            # Display prompt
            self.prompt_output.delete(1.0, tk.END)
            self.prompt_output.insert(1.0, prompt)
            
            # Enable copy button
            self.copy_prompt_btn.config(state=tk.NORMAL)
            
            self.update_status(f"Generated prompt for {num_questions} {subject} questions")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate prompt: {str(e)}")
    
    def copy_prompt(self):
        """Copy prompt to clipboard"""
        prompt = self.prompt_output.get(1.0, tk.END).strip()
        if prompt:
            try:
                pyperclip.copy(prompt)
                self.update_status("Prompt copied to clipboard!", self.app.colors['success'])
            except:
                self.app.root.clipboard_clear()
                self.app.root.clipboard_append(prompt)
                self.update_status("Prompt copied to clipboard!")
    
    def generate_prompt_template_1(self, num_questions, subject, level, marks, unique_instruction, ai_suggest):
        """Template 1: No Classifications & No Topics Selected"""
        available_classifications = ', '.join(self.app.config_manager.get_classifications_for_subject(subject))
        available_topics = ', '.join(self.app.config_manager.get_topics_for_subject(subject))
        
        prompt = f"""Generate {num_questions} multiple choice questions in JSON format based on the following specifications:

**Subject:** {subject}
**Level:** {level}
**Marks per question:** {marks}

**Available Classifications for {subject}:**
{available_classifications}

**Available Topics for {subject}:**
{available_topics}

**Instructions:**
- Choose any combination of classifications and topics from the lists above
- Each question should have ONE topic and ONE classification
- Feel free to suggest new topics or classifications if you find something relevant that's not listed
- Mix different combinations to create variety
- Distribute questions across various topics and classifications

{unique_instruction}

Create questions that test understanding of the subject matter. Each question should have 4 options with only one correct answer.

Return the questions in the following JSON format:

```json
{{
  "questions": [
    {{
      "subject": "{subject}",
      "topic": "selected_topic",  // MUST be a single topic string
      "classification": "selected_classification",  // MUST be a single classification string
      "question": "Your question here",
      "option1": "First option",
      "option2": "Second option",
      "option3": "Third option",
      "option4": "Fourth option",
      "correctAnswer": "The correct option (must match one of the above exactly)",
      "level": "{level}",
      "marks": {marks},
      "created_by": "{self.app.username}"
    }}
  ]{f',\n  "suggested_topics": ["new_topic1", "new_topic2"],  // Only if new topics found\n  "suggested_classifications": ["new_class1"]  // Only if new classifications found' if ai_suggest else ""}
}}
```"""
        return prompt
    
    def generate_prompt_template_2(self, num_questions, subject, level, marks, selected_classifications, unique_instruction, ai_suggest):
        """Template 2: Only Classifications Selected"""
        selected_classifications_list = ', '.join(selected_classifications)
        available_topics_list = ', '.join(self.app.config_manager.get_topics_for_subject(subject))
        
        prompt = f"""Generate {num_questions} multiple choice questions in JSON format based on the following specifications:

**Subject:** {subject}
**Level:** {level}
**Marks per question:** {marks}

**MUST USE THESE CLASSIFICATIONS:**
{selected_classifications_list}

**Available Topics for {subject}:**
{available_topics_list}

**Instructions:**
- Each question MUST use one of the selected classifications above
- For topics, choose from the available topics list or suggest new relevant topics
- Create combinations like: "{selected_classifications[0]} of {{topic1}}", "{selected_classifications[0] if len(selected_classifications) == 1 else selected_classifications[1]} of {{topic3}}", etc.
- Distribute questions evenly across the selected classifications
- Each question should explore how the classification applies to different topics

{unique_instruction}

Create questions that test understanding of the subject matter. Each question should have 4 options with only one correct answer.

Return the questions in the following JSON format:

```json
{{
  "questions": [
    {{
      "subject": "{subject}",
      "topic": "selected_topic",  // MUST be a single topic string
      "classification": "selected_classification",  // MUST be from selected classifications only
      "question": "Your question here",
      "option1": "First option",
      "option2": "Second option",
      "option3": "Third option",
      "option4": "Fourth option",
      "correctAnswer": "The correct option (must match one of the above exactly)",
      "level": "{level}",
      "marks": {marks},
      "created_by": "{self.app.username}"
    }}
  ]{f',\n  "suggested_topics": ["new_topic1", "new_topic2"]  // Only if new topics found' if ai_suggest else ""}
}}
```"""
        return prompt
    
    def generate_prompt_template_3(self, num_questions, subject, level, marks, selected_topics, unique_instruction, ai_suggest):
        """Template 3: Only Topics Selected"""
        selected_topics_list = ', '.join(selected_topics)
        available_classifications_list = ', '.join(self.app.config_manager.get_classifications_for_subject(subject))
        
        prompt = f"""Generate {num_questions} multiple choice questions in JSON format based on the following specifications:

**Subject:** {subject}
**Level:** {level}
**Marks per question:** {marks}

**MUST USE THESE TOPICS:**
{selected_topics_list}

**Available Classifications for {subject}:**
{available_classifications_list}

**Instructions:**
- Each question MUST use one of the selected topics above
- For classifications, choose from the available list or suggest new relevant classifications
- Create combinations like: "{{classification1}} of {selected_topics[0]}", "{{classification3}} of {selected_topics[0] if len(selected_topics) == 1 else selected_topics[1]}", etc.
- Distribute questions evenly across the selected topics
- Each topic should be explored from different classification perspectives

{unique_instruction}

Create questions that test understanding of the subject matter. Each question should have 4 options with only one correct answer.

Return the questions in the following JSON format:

```json
{{
  "questions": [
    {{
      "subject": "{subject}",
      "topic": "selected_topic",  // MUST be from selected topics only
      "classification": "selected_classification",  // MUST be a single classification string
      "question": "Your question here",
      "option1": "First option",
      "option2": "Second option",
      "option3": "Third option",
      "option4": "Fourth option",
      "correctAnswer": "The correct option (must match one of the above exactly)",
      "level": "{level}",
      "marks": {marks},
      "created_by": "{self.app.username}"
    }}
  ]{f',\n  "suggested_classifications": ["new_class1"]  // Only if new classifications found' if ai_suggest else ""}
}}
```"""
        return prompt
    
    def generate_prompt_template_4(self, num_questions, subject, level, marks, selected_classifications, selected_topics, unique_instruction):
        """Template 4: Both Classifications and Topics Selected"""
        selected_classifications_list = ', '.join(selected_classifications)
        selected_topics_list = ', '.join(selected_topics)
        
        prompt = f"""Generate {num_questions} multiple choice questions in JSON format based on the following specifications:

**Subject:** {subject}
**Level:** {level}
**Marks per question:** {marks}

**MUST USE THESE CLASSIFICATIONS:**
{selected_classifications_list}

**MUST USE THESE TOPICS:**
{selected_topics_list}

**Instructions:**
- Each question MUST use one classification from the selected list AND one topic from the selected list
- Create various combinations like: "{selected_classifications[0]} of {selected_topics[0]}", "{selected_classifications[0] if len(selected_classifications) == 1 else selected_classifications[1]} of {selected_topics[0] if len(selected_topics) == 1 else selected_topics[1]}", etc.
- NO new topics or classifications should be suggested
- Distribute questions to cover different classification-topic combinations
- For example, if you have {len(selected_classifications)} classifications and {len(selected_topics)} topics, you can create up to {len(selected_classifications) * len(selected_topics)} different combinations

{unique_instruction}

Create questions that test understanding of the subject matter. Each question should have 4 options with only one correct answer.

Return the questions in the following JSON format:

```json
{{
  "questions": [
    {{
      "subject": "{subject}",
      "topic": "selected_topic",  // MUST be from selected topics only
      "classification": "selected_classification",  // MUST be from selected classifications only
      "question": "Your question here",
      "option1": "First option",
      "option2": "Second option",
      "option3": "Third option",
      "option4": "Fourth option",
      "correctAnswer": "The correct option (must match one of the above exactly)",
      "level": "{level}",
      "marks": {marks},
      "created_by": "{self.app.username}"
    }}
  ]
}}
```"""
        return prompt