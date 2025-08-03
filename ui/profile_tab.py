"""
Profile tab for user information management
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from .base_tab import BaseTab


class ProfileTab(BaseTab):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.setup()
    
    def setup(self):
        """Setup profile tab"""
        # Create scrollable frame
        scrollable_frame = self.create_scrollable_frame(self.frame)
        
        # Content
        container = tk.Frame(scrollable_frame, bg=self.app.colors['bg'])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            container,
            text="User Profile",
            font=('Arial', 18, 'bold'),
            bg=self.app.colors['bg'],
            fg=self.app.colors['primary']
        ).pack(pady=(0, 20))
        
        # Profile Information Frame
        profile_frame = self.create_label_frame(container, "Profile Information")
        profile_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Configure grid
        profile_frame.grid_columnconfigure(1, weight=1)
        
        # Username (readonly)
        tk.Label(
            profile_frame,
            text="Username:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=0, column=0, sticky='e', padx=10, pady=8)
        
        tk.Label(
            profile_frame,
            text=self.app.username,
            font=('Arial', 11, 'bold'),
            bg=self.app.colors['white'],
            fg=self.app.colors['primary']
        ).grid(row=0, column=1, sticky='w', padx=10, pady=8)
        
        # Full Name
        tk.Label(
            profile_frame,
            text="Full Name:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=1, column=0, sticky='e', padx=10, pady=8)
        
        self.full_name_entry = tk.Entry(profile_frame, font=('Arial', 11), width=40)
        self.full_name_entry.grid(row=1, column=1, sticky='ew', padx=10, pady=8)
        
        # Email
        tk.Label(
            profile_frame,
            text="Email:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=2, column=0, sticky='e', padx=10, pady=8)
        
        self.email_entry = tk.Entry(profile_frame, font=('Arial', 11), width=40)
        self.email_entry.grid(row=2, column=1, sticky='ew', padx=10, pady=8)
        
        # Department
        tk.Label(
            profile_frame,
            text="Department:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=3, column=0, sticky='e', padx=10, pady=8)
        
        self.department_entry = tk.Entry(profile_frame, font=('Arial', 11), width=40)
        self.department_entry.grid(row=3, column=1, sticky='ew', padx=10, pady=8)
        
        # Role
        tk.Label(
            profile_frame,
            text="Role:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=4, column=0, sticky='e', padx=10, pady=8)
        
        self.role_entry = tk.Entry(profile_frame, font=('Arial', 11), width=40)
        self.role_entry.grid(row=4, column=1, sticky='ew', padx=10, pady=8)
        
        # Bio
        tk.Label(
            profile_frame,
            text="Bio:",
            font=('Arial', 11),
            bg=self.app.colors['white']
        ).grid(row=5, column=0, sticky='ne', padx=10, pady=8)
        
        bio_frame = tk.Frame(profile_frame, bg=self.app.colors['white'])
        bio_frame.grid(row=5, column=1, sticky='ew', padx=10, pady=8)
        
        self.bio_text = tk.Text(bio_frame, font=('Arial', 11), width=40, height=4, wrap=tk.WORD)
        self.bio_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        bio_scroll = ttk.Scrollbar(bio_frame, command=self.bio_text.yview)
        bio_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.bio_text.config(yscrollcommand=bio_scroll.set)
        
        # Save button
        save_btn_frame = tk.Frame(profile_frame, bg=self.app.colors['white'])
        save_btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        self.create_button(
            save_btn_frame,
            "Save Profile",
            self.save_profile,
            'success'
        ).pack()
        
        # Statistics Frame
        stats_frame = self.create_label_frame(container, "Activity Statistics")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create stats labels
        self.stats_labels = {}
        stats_info = [
            ("Questions Created:", "0"),
            ("Total Sessions:", "0"),
            ("Total Time:", "0h 0m"),
            ("Member Since:", "N/A"),
            ("Last Active:", "N/A")
        ]
        
        for i, (label, default) in enumerate(stats_info):
            tk.Label(
                stats_frame,
                text=label,
                font=('Arial', 11),
                bg=self.app.colors['white']
            ).grid(row=i, column=0, sticky='e', padx=10, pady=5)
            
            value_label = tk.Label(
                stats_frame,
                text=default,
                font=('Arial', 11, 'bold'),
                bg=self.app.colors['white'],
                fg=self.app.colors['secondary']
            )
            value_label.grid(row=i, column=1, sticky='w', padx=10, pady=5)
            
            self.stats_labels[label] = value_label
        
        # Recent Sessions Frame
        sessions_frame = self.create_label_frame(container, "Recent Sessions")
        sessions_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Create treeview for sessions
        columns = ('Date', 'Start Time', 'Duration')
        self.sessions_tree = ttk.Treeview(sessions_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.sessions_tree.heading(col, text=col)
            self.sessions_tree.column(col, width=150)
        
        self.sessions_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load profile data after connection
        self.frame.after(1000, self.load_profile)
    
    def load_profile(self):
        """Load user profile data"""
        if not hasattr(self.app, 'user_manager') or not self.app.user_manager.collection:
            return
        
        try:
            # Get profile data
            profile = self.app.user_manager.get_user_profile(self.app.username)
            
            if profile:
                self.full_name_entry.delete(0, tk.END)
                self.full_name_entry.insert(0, profile.get('full_name', ''))
                
                self.email_entry.delete(0, tk.END)
                self.email_entry.insert(0, profile.get('email', ''))
                
                self.department_entry.delete(0, tk.END)
                self.department_entry.insert(0, profile.get('department', ''))
                
                self.role_entry.delete(0, tk.END)
                self.role_entry.insert(0, profile.get('role', ''))
                
                self.bio_text.delete(1.0, tk.END)
                self.bio_text.insert(1.0, profile.get('bio', ''))
            
            # Load statistics
            self.load_statistics()
            
            # Load recent sessions
            self.load_recent_sessions()
            
        except Exception as e:
            print(f"Error loading profile: {e}")
    
    def load_statistics(self):
        """Load user statistics"""
        if not hasattr(self.app, 'user_manager') or not self.app.user_manager.collection:
            return
        
        try:
            # Get user data
            user = self.app.user_manager.collection.find_one({"username": self.app.username})
            
            if user:
                # Questions created
                questions_count = self.app.db_manager.get_user_questions_count(self.app.username)
                self.stats_labels["Questions Created:"].config(text=str(questions_count))
                
                # Total sessions
                self.stats_labels["Total Sessions:"].config(
                    text=str(user.get('total_sessions', 0))
                )
                
                # Total time
                total_seconds = user.get('total_time_seconds', 0)
                self.stats_labels["Total Time:"].config(
                    text=self.app.user_manager.format_duration(total_seconds)
                )
                
                # Member since
                created_at = user.get('created_at')
                if created_at:
                    self.stats_labels["Member Since:"].config(
                        text=created_at.strftime('%Y-%m-%d')
                    )
                
                # Last active
                last_active = user.get('last_active')
                if last_active:
                    self.stats_labels["Last Active:"].config(
                        text=last_active.strftime('%Y-%m-%d %H:%M')
                    )
                    
        except Exception as e:
            print(f"Error loading statistics: {e}")
    
    def load_recent_sessions(self):
        """Load recent sessions"""
        if not hasattr(self.app, 'user_manager') or not self.app.user_manager.collection:
            return
        
        try:
            # Clear existing items
            for item in self.sessions_tree.get_children():
                self.sessions_tree.delete(item)
            
            # Get recent sessions
            sessions = self.app.user_manager.get_user_sessions(self.app.username, limit=10)
            
            for session in reversed(sessions):  # Show newest first
                if 'start' in session and 'duration_seconds' in session:
                    date = session['start'].strftime('%Y-%m-%d')
                    start_time = session['start'].strftime('%H:%M:%S')
                    duration = self.app.user_manager.format_duration(session['duration_seconds'])
                    
                    self.sessions_tree.insert('', 'end', values=(date, start_time, duration))
                    
        except Exception as e:
            print(f"Error loading sessions: {e}")
    
    def save_profile(self):
        """Save profile information"""
        if not hasattr(self.app, 'user_manager') or not self.app.user_manager.collection:
            messagebox.showerror("Error", "Database not connected")
            return
        
        try:
            profile_data = {
                'full_name': self.full_name_entry.get().strip(),
                'email': self.email_entry.get().strip(),
                'department': self.department_entry.get().strip(),
                'role': self.role_entry.get().strip(),
                'bio': self.bio_text.get(1.0, tk.END).strip()
            }
            
            # Validate email if provided
            if profile_data['email'] and '@' not in profile_data['email']:
                messagebox.showwarning("Invalid Email", "Please enter a valid email address")
                return
            
            # Update profile
            if self.app.user_manager.update_user_profile(self.app.username, profile_data):
                messagebox.showinfo("Success", "Profile updated successfully!")
                self.update_status("Profile saved", self.app.colors['success'])
            else:
                messagebox.showerror("Error", "Failed to update profile")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {str(e)}")
    
    def refresh(self):
        """Refresh profile data"""
        self.load_profile()