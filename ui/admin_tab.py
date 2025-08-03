"""
Admin tab for user management and monitoring
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from .base_tab import BaseTab
from utils.helpers import safe_grab_set


class AdminTab(BaseTab):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.is_authenticated = False
        self.refresh_task_id = None
        self.setup()
    
    def setup(self):
        """Setup admin tab"""
        # Initially show password prompt
        self.password_frame = tk.Frame(self.frame, bg=self.app.colors['bg'])
        self.password_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_password_screen()
        
        # Create admin panel (hidden initially)
        self.admin_panel = tk.Frame(self.frame, bg=self.app.colors['bg'])
        # Don't pack it yet
    
    def setup_password_screen(self):
        """Setup password entry screen"""
        # Center container
        center_frame = tk.Frame(self.password_frame, bg=self.app.colors['white'], relief=tk.RAISED, bd=2)
        center_frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=250)
        
        # Title
        tk.Label(
            center_frame,
            text="🔒 Admin Authentication",
            font=('Arial', 18, 'bold'),
            bg=self.app.colors['white'],
            fg=self.app.colors['danger']
        ).pack(pady=(30, 20))
        
        # Password label
        tk.Label(
            center_frame,
            text="Enter Admin Password:",
            font=('Arial', 12),
            bg=self.app.colors['white']
        ).pack(pady=(0, 10))
        
        # Password entry
        self.admin_password_entry = tk.Entry(center_frame, show="*", font=('Arial', 12), width=25)
        self.admin_password_entry.pack(pady=(0, 20))
        self.admin_password_entry.bind('<Return>', lambda e: self.verify_password())
        
        # Login button
        self.create_button(
            center_frame,
            "Login",
            self.verify_password,
            'danger',
            padx=40,
            pady=8
        ).pack()
        
        # Focus on password entry
        self.admin_password_entry.focus()
    
    def verify_password(self):
        """Verify admin password"""
        password = self.admin_password_entry.get()
        
        if password == "admin":
            self.is_authenticated = True
            self.app.is_admin = True
            self.password_frame.pack_forget()
            self.setup_admin_panel()
            self.admin_panel.pack(fill=tk.BOTH, expand=True)
            self.refresh_data()
            self.update_status("Admin access granted", self.app.colors['success'])
        else:
            messagebox.showerror("Access Denied", "Invalid admin password")
            self.admin_password_entry.delete(0, tk.END)
    
    def setup_admin_panel(self):
        """Setup the actual admin panel"""
        # Create scrollable frame
        canvas = tk.Canvas(self.admin_panel, bg=self.app.colors['bg'])
        scrollbar = ttk.Scrollbar(self.admin_panel, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.app.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Content
        container = tk.Frame(scrollable_frame, bg=self.app.colors['bg'])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title and refresh button
        title_frame = tk.Frame(container, bg=self.app.colors['bg'])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            title_frame,
            text="Admin Dashboard",
            font=('Arial', 18, 'bold'),
            bg=self.app.colors['bg'],
            fg=self.app.colors['danger']
        ).pack(side=tk.LEFT)
        
        self.create_button(
            title_frame,
            "🔄 Refresh",
            self.refresh_data,
            'secondary',
            padx=15,
            pady=5,
            font=('Arial', 10)
        ).pack(side=tk.RIGHT)
        
        # Online Users Frame
        online_frame = self.create_label_frame(container, "Currently Online Users")
        online_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Online users list
        self.online_listbox = tk.Listbox(online_frame, height=5, font=('Arial', 10))
        self.online_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Summary Statistics
        stats_frame = self.create_label_frame(container, "System Statistics")
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.stats_text = tk.Text(stats_frame, height=6, font=('Arial', 10), wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # All Users Table
        users_frame = self.create_label_frame(container, "All Registered Users")
        users_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for users
        columns = ('Username', 'Full Name', 'Department', 'Status', 'Last Active', 
                  'Sessions', 'Total Time', 'Questions', 'Member Since')
        
        self.users_tree = ttk.Treeview(users_frame, columns=columns, show='headings', height=15)
        
        # Define columns
        column_widths = {
            'Username': 100,
            'Full Name': 150,
            'Department': 120,
            'Status': 80,
            'Last Active': 150,
            'Sessions': 80,
            'Total Time': 100,
            'Questions': 80,
            'Member Since': 120
        }
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        vsb = ttk.Scrollbar(users_frame, orient="vertical", command=self.users_tree.yview)
        hsb = ttk.Scrollbar(users_frame, orient="horizontal", command=self.users_tree.xview)
        self.users_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.users_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        users_frame.grid_rowconfigure(0, weight=1)
        users_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click to view user details
        self.users_tree.bind('<Double-Button-1>', self.view_user_details)
        
        # Auto-refresh timer
        self.auto_refresh_var = tk.BooleanVar(value=True)
        auto_refresh_frame = tk.Frame(container, bg=self.app.colors['bg'])
        auto_refresh_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Checkbutton(
            auto_refresh_frame,
            text="Auto-refresh every 30 seconds",
            variable=self.auto_refresh_var,
            font=('Arial', 10),
            bg=self.app.colors['bg']
        ).pack(side=tk.LEFT)
        
        # Start auto-refresh
        self.schedule_refresh()
    
    def refresh_data(self):
        """Refresh all admin data"""
        if not self.is_authenticated:
            return
        
        if not hasattr(self.app, 'user_manager') or not self.app.user_manager.collection:
            self.update_status("User database not connected", self.app.colors['warning'])
            return
        
        try:
            # Get online users
            online_users = self.app.user_manager.get_online_users()
            
            # Update online users list
            self.online_listbox.delete(0, tk.END)
            for user in online_users:
                display_name = user.get('profile', {}).get('full_name') or user['username']
                last_active = user['last_active'].strftime('%H:%M:%S')
                self.online_listbox.insert(tk.END, f"{display_name} ({user['username']}) - Active: {last_active}")
            
            if not online_users:
                self.online_listbox.insert(tk.END, "No users currently online")
            
            # Get all users
            all_users = self.app.user_manager.get_all_users()
            
            # Update statistics
            self.update_statistics(all_users, online_users)
            
            # Update users table
            self.update_users_table(all_users, online_users)
            
            self.update_status(f"Admin data refreshed at {datetime.datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.update_status(f"Error refreshing data: {str(e)}", self.app.colors['danger'])
    
    def update_statistics(self, all_users, online_users):
        """Update summary statistics"""
        self.stats_text.delete(1.0, tk.END)
        
        total_users = len(all_users)
        online_count = len(online_users)
        
        # Calculate totals
        total_questions = sum(user.get('questions_created', 0) for user in all_users)
        total_sessions = sum(user.get('total_sessions', 0) for user in all_users)
        total_time = sum(user.get('total_time_seconds', 0) for user in all_users)
        
        # Get database stats
        db_stats = self.app.db_manager.get_statistics() if self.app.db_manager.collection else {}
        
        stats_text = f"""Total Registered Users: {total_users}
Currently Online: {online_count}
Total User Sessions: {total_sessions}
Total Time Spent: {self.app.user_manager.format_duration(total_time)}
Total Questions in Database: {db_stats.get('total', 0)}
Total Questions Created by Users: {total_questions}"""
        
        self.stats_text.insert(1.0, stats_text)
    
    def update_users_table(self, all_users, online_users):
        """Update the users table"""
        # Clear existing items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Get online usernames for quick lookup
        online_usernames = {user['username'] for user in online_users}
        
        # Add users to table
        for user in all_users:
            username = user.get('username', '')
            full_name = user.get('profile', {}).get('full_name', '')
            department = user.get('profile', {}).get('department', '')
            status = "🟢 Online" if username in online_usernames else "⚫ Offline"
            
            last_active = user.get('last_active')
            if last_active:
                last_active_str = last_active.strftime('%Y-%m-%d %H:%M')
            else:
                last_active_str = "Never"
            
            sessions = str(user.get('total_sessions', 0))
            total_time = self.app.user_manager.format_duration(user.get('total_time_seconds', 0))
            questions = str(user.get('questions_created', 0))
            
            created_at = user.get('created_at')
            if created_at:
                member_since = created_at.strftime('%Y-%m-%d')
            else:
                member_since = "Unknown"
            
            # Insert with color based on status
            tag = 'online' if username in online_usernames else 'offline'
            self.users_tree.insert('', 'end', values=(
                username, full_name, department, status, last_active_str,
                sessions, total_time, questions, member_since
            ), tags=(tag,))
        
        # Configure tags
        self.users_tree.tag_configure('online', background='#d4f1d4')
        self.users_tree.tag_configure('offline', background='#f8f8f8')
    
    def view_user_details(self, event):
        """View detailed information for a user"""
        selection = self.users_tree.selection()
        if not selection:
            return
        
        item = self.users_tree.item(selection[0])
        username = item['values'][0]
        
        # Create details dialog
        UserDetailsDialog(self.app, username)
    
    def schedule_refresh(self):
        """Schedule automatic refresh"""
        if self.is_authenticated and self.auto_refresh_var.get():
            self.refresh_data()
        
        # Schedule next refresh (30 seconds)
        self.refresh_task_id = self.admin_panel.after(30000, self.schedule_refresh)
    
    def request_password(self):
        """Request password when admin tab is clicked"""
        if not self.is_authenticated:
            self.admin_password_entry.delete(0, tk.END)
            self.admin_password_entry.focus()
    
    def cleanup(self):
        """Cleanup method for proper shutdown"""
        # Cancel any scheduled refreshes
        if hasattr(self, 'refresh_task_id'):
            try:
                self.admin_panel.after_cancel(self.refresh_task_id)
            except:
                pass


class UserDetailsDialog:
    """Dialog to show detailed user information"""
    
    def __init__(self, app, username):
        self.app = app
        self.username = username
        
        # Create dialog
        self.dialog = tk.Toplevel(app.root)
        self.dialog.title(f"User Details - {username}")
        self.dialog.geometry("600x700")
        self.dialog.transient(app.root)
        self.dialog.configure(bg=app.colors['white'])
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 600) // 2
        y = (self.dialog.winfo_screenheight() - 700) // 2
        self.dialog.geometry(f"600x700+{x}+{y}")
        
        # Make dialog modal
        self.dialog.update()
        self.dialog.after(100, lambda: safe_grab_set(self.dialog))
        
        self.setup_ui()
        self.load_user_data()
    
    def setup_ui(self):
        """Setup user details UI"""
        # Title
        title_frame = tk.Frame(self.dialog, bg=self.app.colors['primary'], height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text=f"User: {self.username}",
            font=('Arial', 16, 'bold'),
            bg=self.app.colors['primary'],
            fg='white'
        ).pack(expand=True)
        
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
        
        # Content
        self.content_frame = tk.Frame(scrollable_frame, bg=self.app.colors['white'], padx=20, pady=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Close button
        close_frame = tk.Frame(self.dialog, bg=self.app.colors['white'])
        close_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            close_frame,
            text="Close",
            command=self.dialog.destroy,
            font=('Arial', 11),
            bg=self.app.colors['light'],
            fg=self.app.colors['dark'],
            padx=30,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT
        ).pack()
    
    def load_user_data(self):
        """Load and display user data"""
        if not hasattr(self.app, 'user_manager') or not self.app.user_manager.collection:
            tk.Label(
                self.content_frame,
                text="User database not connected",
                font=('Arial', 12),
                bg=self.app.colors['white'],
                fg=self.app.colors['danger']
            ).pack()
            return
        
        try:
            # Get full user data
            user = self.app.user_manager.collection.find_one({"username": self.username})
            
            if not user:
                tk.Label(
                    self.content_frame,
                    text="User not found",
                    font=('Arial', 12),
                    bg=self.app.colors['white'],
                    fg=self.app.colors['danger']
                ).pack()
                return
            
            # Profile Information
            self.add_section("Profile Information")
            profile = user.get('profile', {})
            self.add_field("Full Name", profile.get('full_name', 'Not provided'))
            self.add_field("Email", profile.get('email', 'Not provided'))
            self.add_field("Department", profile.get('department', 'Not provided'))
            self.add_field("Role", profile.get('role', 'Not provided'))
            self.add_field("Bio", profile.get('bio', 'Not provided'))
            
            # Account Information
            self.add_section("Account Information")
            self.add_field("Username", user.get('username', ''))
            self.add_field("Status", "Online" if user.get('status') == 'online' else "Offline")
            
            created_at = user.get('created_at')
            if created_at:
                self.add_field("Member Since", created_at.strftime('%Y-%m-%d %H:%M'))
            
            last_active = user.get('last_active')
            if last_active:
                self.add_field("Last Active", last_active.strftime('%Y-%m-%d %H:%M:%S'))
            
            # Activity Statistics
            self.add_section("Activity Statistics")
            self.add_field("Total Sessions", str(user.get('total_sessions', 0)))
            self.add_field("Total Time", self.app.user_manager.format_duration(user.get('total_time_seconds', 0)))
            
            questions_count = self.app.db_manager.get_user_questions_count(self.username)
            self.add_field("Questions Created", str(questions_count))
            
            # Recent Sessions
            self.add_section("Recent Sessions (Last 5)")
            sessions = user.get('sessions', [])[-5:]
            
            if sessions:
                for i, session in enumerate(reversed(sessions), 1):
                    if 'start' in session:
                        session_text = f"{i}. {session['start'].strftime('%Y-%m-%d %H:%M')} - Duration: {self.app.user_manager.format_duration(session.get('duration_seconds', 0))}"
                        tk.Label(
                            self.content_frame,
                            text=session_text,
                            font=('Arial', 10),
                            bg=self.app.colors['white'],
                            wraplength=500,
                            justify=tk.LEFT
                        ).pack(anchor='w', pady=2)
            else:
                tk.Label(
                    self.content_frame,
                    text="No session history",
                    font=('Arial', 10, 'italic'),
                    bg=self.app.colors['white'],
                    fg=self.app.colors['secondary']
                ).pack(anchor='w')
                
        except Exception as e:
            tk.Label(
                self.content_frame,
                text=f"Error loading user data: {str(e)}",
                font=('Arial', 12),
                bg=self.app.colors['white'],
                fg=self.app.colors['danger']
            ).pack()
    
    def add_section(self, title):
        """Add a section header"""
        tk.Label(
            self.content_frame,
            text=title,
            font=('Arial', 14, 'bold'),
            bg=self.app.colors['white'],
            fg=self.app.colors['primary']
        ).pack(anchor='w', pady=(15, 5))
    
    def add_field(self, label, value):
        """Add a field with label and value"""
        field_frame = tk.Frame(self.content_frame, bg=self.app.colors['white'])
        field_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            field_frame,
            text=f"{label}:",
            font=('Arial', 10, 'bold'),
            bg=self.app.colors['white'],
            width=20,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Label(
            field_frame,
            text=str(value),
            font=('Arial', 10),
            bg=self.app.colors['white'],
            wraplength=350,
            justify=tk.LEFT
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)