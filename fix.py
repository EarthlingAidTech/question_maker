#!/usr/bin/env python3
"""
Emergency fix for empty tabs in MCQ Database Manager
"""

import os
import shutil
from datetime import datetime

def backup_file(filename):
    """Create a backup of the file"""
    if os.path.exists(filename):
        backup_name = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filename, backup_name)
        print(f"✓ Backed up {filename} to {backup_name}")

def emergency_fix():
    print("🚨 Emergency Fix for Empty Tabs\n")
    
    # Fix 1: Update app.py
    print("Fixing app.py...")
    backup_file("app.py")
    
    try:
        with open("app.py", "r") as f:
            content = f.read()
        
        # Fix 1: Add refresh_all_tabs method
        if "def refresh_all_tabs(self):" not in content:
            # Find insertion point
            insert_after = "def refresh_dashboard(self):\n        \"\"\"Refresh dashboard statistics\"\"\"\n        self.dashboard_tab.refresh()"
            
            new_method = """
    
    def refresh_all_tabs(self):
        \"\"\"Refresh all tabs after database connection\"\"\"
        print("Refreshing all tabs...")
        try:
            # Refresh dashboard
            if hasattr(self, 'dashboard_tab'):
                self.dashboard_tab.refresh()
                print("✓ Dashboard refreshed")
            
            # Force load data in browse tab
            if hasattr(self, 'browse_tab'):
                # Set the filter to 'All' and apply
                self.browse_tab.filter_subject.set('All')
                self.browse_tab.filter_level.set('All')
                self.browse_tab.filter_created_by.set('All')
                self.browse_tab.apply_filters()
                print("✓ Browse tab refreshed")
            
            # Update all combos
            self.update_all_combos()
            print("✓ All combos updated")
        except Exception as e:
            print(f"Error refreshing tabs: {e}")"""
            
            content = content.replace(insert_after, insert_after + new_method)
        
        # Fix 2: Replace refresh_dashboard with refresh_all_tabs
        content = content.replace(
            "# Load initial data\n                    self.refresh_dashboard()",
            "# Load initial data\n                    self.refresh_all_tabs()"
        )
        
        # Fix 3: Add debug to init_tabs
        if "def init_tabs(self):" in content:
            content = content.replace(
                "def init_tabs(self):\n        \"\"\"Initialize all tabs\"\"\"",
                "def init_tabs(self):\n        \"\"\"Initialize all tabs\"\"\"\n        print(\"Initializing tabs...\")"
            )
        
        # Write back
        with open("app.py", "w") as f:
            f.write(content)
        
        print("✅ app.py fixed!\n")
        
    except Exception as e:
        print(f"❌ Error fixing app.py: {e}\n")
        return False
    
    # Fix 2: Update browse_tab.py
    print("Fixing ui/browse_tab.py...")
    backup_file("ui/browse_tab.py")
    
    try:
        with open("ui/browse_tab.py", "r") as f:
            content = f.read()
        
        # Add force refresh in setup
        if "# Pagination frame" in content:
            content = content.replace(
                "# Pagination frame\n        self.setup_pagination(container)",
                "# Pagination frame\n        self.setup_pagination(container)\n        \n        # Force initial data load\n        self.frame.after(1000, lambda: self.apply_filters() if self.app.db_manager.collection else None)"
            )
        
        # Add debug to apply_filters
        content = content.replace(
            "def apply_filters(self):\n        \"\"\"Apply filters and refresh questions list\"\"\"",
            "def apply_filters(self):\n        \"\"\"Apply filters and refresh questions list\"\"\"\n        print(\"Applying filters...\")"
        )
        
        # Fix display_questions to show debug info
        content = content.replace(
            "def display_questions(self):\n        \"\"\"Display questions in treeview\"\"\"",
            "def display_questions(self):\n        \"\"\"Display questions in treeview\"\"\"\n        print(f\"Displaying {len(self.current_questions)} questions...\")"
        )
        
        # Write back
        with open("ui/browse_tab.py", "w") as f:
            f.write(content)
        
        print("✅ ui/browse_tab.py fixed!\n")
        
    except Exception as e:
        print(f"❌ Error fixing ui/browse_tab.py: {e}\n")
        return False
    
    # Fix 3: Update dashboard_tab.py
    print("Fixing ui/dashboard_tab.py...")
    backup_file("ui/dashboard_tab.py")
    
    try:
        with open("ui/dashboard_tab.py", "r") as f:
            content = f.read()
        
        # Add debug to refresh
        content = content.replace(
            "def refresh(self):\n        \"\"\"Refresh dashboard statistics\"\"\"",
            "def refresh(self):\n        \"\"\"Refresh dashboard statistics\"\"\"\n        print(\"Refreshing dashboard...\")"
        )
        
        # Add force refresh on init
        if "self.level_chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)" in content:
            content = content.replace(
                "self.level_chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)",
                "self.level_chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)\n        \n        # Auto-refresh after a delay\n        self.frame.after(1000, lambda: self.refresh() if self.app.db_manager.collection else None)"
            )
        
        # Write back
        with open("ui/dashboard_tab.py", "w") as f:
            f.write(content)
        
        print("✅ ui/dashboard_tab.py fixed!\n")
        
    except Exception as e:
        print(f"❌ Error fixing ui/dashboard_tab.py: {e}\n")
        return False
    
    print("\n✅ Emergency fixes applied!")
    print("\n📋 Next Steps:")
    print("1. Close the application if it's running")
    print("2. Start the application again: python main.py")
    print("3. After connecting to MongoDB, you should see:")
    print("   - Console messages showing 'Refreshing all tabs...'")
    print("   - Data should appear in Dashboard and Browse tabs")
    print("\n4. If data still doesn't show:")
    print("   - Go to Browse & Edit tab")
    print("   - Click the 'Refresh' or 'Apply Filters' button")
    print("\n💡 The console will show debug messages to help identify any issues.")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("MCQ DATABASE MANAGER - EMERGENCY FIX")
    print("=" * 60)
    
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found!")
        print("Make sure you run this script from the project root directory.")
    elif not os.path.exists("ui/browse_tab.py"):
        print("❌ Error: ui/browse_tab.py not found!")
        print("Make sure all files are created first.")
    else:
        emergency_fix()
        print("\n🎉 Done! Restart the application now.")