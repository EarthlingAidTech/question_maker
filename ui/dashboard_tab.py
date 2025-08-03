"""
Dashboard tab for MCQ Database Manager
"""

import tkinter as tk
from .base_tab import BaseTab
from utils.helpers import is_matplotlib_available

if is_matplotlib_available():
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class DashboardTab(BaseTab):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.stat_cards = {}
        self.setup()
    
    def setup(self):
        """Setup dashboard tab"""
        # Create scrollable frame
        scrollable_frame = self.create_scrollable_frame(self.frame)
        
        # Content
        container = tk.Frame(scrollable_frame, bg=self.app.colors['bg'])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            container,
            text="Dashboard Overview",
            font=('Arial', 18, 'bold'),
            bg=self.app.colors['bg'],
            fg=self.app.colors['primary']
        ).pack(pady=(0, 20))
        
        # Stats cards row
        stats_row = tk.Frame(container, bg=self.app.colors['bg'])
        stats_row.pack(fill=tk.X, pady=(0, 20))
        
        # Create stat cards
        stats = [
            ("Total Questions", "0", self.app.colors['secondary']),
            ("Easy Questions", "0", self.app.colors['success']),
            ("Medium Questions", "0", self.app.colors['warning']),
            ("Hard Questions", "0", self.app.colors['danger']),
            ("Total Subjects", "0", self.app.colors['info']),
            ("My Questions", "0", self.app.colors['dark'])
        ]
        
        for i, (title, value, color) in enumerate(stats):
            card = self.create_stat_card(stats_row, title, value, color)
            card.grid(row=0, column=i, padx=10, pady=5, sticky='nsew')
            stats_row.grid_columnconfigure(i, weight=1)
            self.stat_cards[title] = card
        
        # Charts frame
        charts_frame = tk.Frame(container, bg=self.app.colors['bg'])
        charts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Subject distribution chart
        self.subject_chart_frame = self.create_label_frame(
            charts_frame,
            "Questions by Subject"
        )
        self.subject_chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Level distribution chart
        self.level_chart_frame = self.create_label_frame(
            charts_frame,
            "Questions by Difficulty"
        )
        self.level_chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    def create_stat_card(self, parent, title, value, color):
        """Create a statistics card"""
        card = tk.Frame(parent, bg=color, relief=tk.RAISED, bd=1)
        card.pack_propagate(False)
        card.configure(height=100)
        
        tk.Label(
            card,
            text=title,
            font=('Arial', 11),
            bg=color,
            fg='white'
        ).pack(pady=(10, 5))
        
        value_label = tk.Label(
            card,
            text=value,
            font=('Arial', 24, 'bold'),
            bg=color,
            fg='white'
        )
        value_label.pack()
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def refresh(self):
        """Refresh dashboard statistics"""
        if not self.app.db_manager.collection:
            return
        
        try:
            # Get statistics from database
            stats = self.app.db_manager.get_statistics()
            my_questions = self.app.db_manager.get_user_questions_count(self.app.username)
            
            # Update stat cards
            self.stat_cards["Total Questions"].value_label.config(text=str(stats.get('total', 0)))
            self.stat_cards["Easy Questions"].value_label.config(text=str(stats.get('easy', 0)))
            self.stat_cards["Medium Questions"].value_label.config(text=str(stats.get('medium', 0)))
            self.stat_cards["Hard Questions"].value_label.config(text=str(stats.get('hard', 0)))
            self.stat_cards["Total Subjects"].value_label.config(text=str(stats.get('subjects', 0)))
            self.stat_cards["My Questions"].value_label.config(text=str(my_questions))
            
            # Update total questions label in toolbar
            self.app.total_questions_label.config(text=f"Total Questions: {stats.get('total', 0)}")
            
            # Update charts
            self.update_charts()
            
        except Exception as e:
            self.update_status(f"Error refreshing dashboard: {str(e)}", self.app.colors['danger'])
    
    def update_charts(self):
        """Update dashboard charts"""
        if not self.app.db_manager.collection or not is_matplotlib_available():
            return
        
        try:
            # Clear existing charts
            for widget in self.subject_chart_frame.winfo_children():
                if isinstance(widget, tk.Widget) and widget.winfo_class() != 'Label':
                    widget.destroy()
            
            for widget in self.level_chart_frame.winfo_children():
                if isinstance(widget, tk.Widget) and widget.winfo_class() != 'Label':
                    widget.destroy()
            
            # Subject distribution
            subject_data = self.app.db_manager.get_subject_distribution()
            
            if subject_data:
                # Create bar chart for subjects
                fig1, ax1 = plt.subplots(figsize=(6, 4))
                subjects = [item['_id'] for item in subject_data]
                counts = [item['count'] for item in subject_data]
                
                bars = ax1.bar(range(len(subjects)), counts, color=self.app.colors['secondary'])
                ax1.set_xticks(range(len(subjects)))
                ax1.set_xticklabels(subjects, rotation=45, ha='right')
                ax1.set_ylabel('Number of Questions')
                ax1.set_title('Top 10 Subjects by Question Count')
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom')
                
                plt.tight_layout()
                
                canvas1 = FigureCanvasTkAgg(fig1, self.subject_chart_frame)
                canvas1.draw()
                canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Level distribution (pie chart)
            stats = self.app.db_manager.get_statistics()
            level_data = [
                {"_id": "easy", "count": stats.get('easy', 0)},
                {"_id": "medium", "count": stats.get('medium', 0)},
                {"_id": "hard", "count": stats.get('hard', 0)}
            ]
            
            if any(item['count'] > 0 for item in level_data):
                fig2, ax2 = plt.subplots(figsize=(5, 4))
                levels = [item['_id'].capitalize() for item in level_data]
                counts = [item['count'] for item in level_data]
                colors = [self.app.colors['success'], self.app.colors['warning'], self.app.colors['danger']]
                
                # Filter out zero counts
                non_zero = [(l, c, col) for l, c, col in zip(levels, counts, colors) if c > 0]
                if non_zero:
                    levels, counts, colors = zip(*non_zero)
                    
                    wedges, texts, autotexts = ax2.pie(counts, labels=levels, colors=colors,
                                                    autopct='%1.1f%%', startangle=90)
                    ax2.set_title('Question Distribution by Difficulty')
                    
                    plt.tight_layout()
                    
                    canvas2 = FigureCanvasTkAgg(fig2, self.level_chart_frame)
                    canvas2.draw()
                    canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            self.update_status(f"Error updating charts: {str(e)}", self.app.colors['danger'])