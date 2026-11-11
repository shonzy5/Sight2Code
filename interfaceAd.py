"""
Sight2Code - Professional Dashboard
A modern GUI interface for the voice-controlled coding platform for visually impaired users
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import os
import json
from datetime import datetime
from pathlib import Path
import shutil
from typing import Dict, List
import threading

# Set appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Color Scheme - Light Subtle Theme
COLORS = {
    "primary": "#6366f1",        # Soft indigo - Main brand color
    "secondary": "#3b82f6",      # Soft blue - Secondary actions
    "success": "#10b981",        # Soft green - Success states
    "warning": "#f59e0b",        # Soft orange - Warnings
    "danger": "#ef4444",         # Soft red - Errors
    "dark_bg": "#ffffff",        # White background
    "card_bg": "#f8fafc",        # Very light gray - Card background
    "sidebar_bg": "#f1f5f9",     # Light gray - Sidebar background
    "text_primary": "#1e293b",   # Dark text - Primary text
    "text_secondary": "#64748b", # Medium gray - Secondary text
    "accent": "#e2e8f0",         # Light gray - Neutral accent
    "border": "#e2e8f0",         # Very light gray - Border color
    "hover": "#f1f5f9",          # Light hover background
    "card_hover": "#f1f5f9",     # Card hover state
}

class Sight2CodeDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Sight2Code - Professional Dashboard")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        
        # Data paths
        self.BASE_USERS_DIR = "users"
        self.LESSONS_DIR = "lessons"
        self.DATA_DIR = "dashboard_data"
        self.ensure_directories()
        
        # Current state
        self.current_view = None
        self.selected_student = None
        self.is_admin_mode = False
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.load_dashboard_data()
        
    def ensure_directories(self):
        """Ensure all necessary directories exist"""
        for directory in [self.BASE_USERS_DIR, self.LESSONS_DIR, self.DATA_DIR]:
            os.makedirs(directory, exist_ok=True)
            
    def setup_ui(self):
        """Setup the main UI structure"""
        # Create main container with grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Show dashboard by default
        self.show_dashboard()
        
    def create_sidebar(self):
        """Create the navigation sidebar"""
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=COLORS["sidebar_bg"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Logo/Title Section
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=100)
        logo_frame.pack(fill="x", padx=20, pady=20)
        logo_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            logo_frame, 
            text="👁 Sight2Code",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["primary"]
        )
        title_label.pack(pady=10)
        
        subtitle = ctk.CTkLabel(
            logo_frame,
            text="Empowering Vision",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        subtitle.pack()
        
        # Mode Switch
        self.mode_switch_frame = ctk.CTkFrame(self.sidebar, fg_color=COLORS["card_bg"], corner_radius=10)
        self.mode_switch_frame.pack(fill="x", padx=15, pady=10)
        
        mode_label = ctk.CTkLabel(
            self.mode_switch_frame,
            text="Admin Mode",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        mode_label.pack(pady=(10, 5))
        
        self.admin_switch = ctk.CTkSwitch(
            self.mode_switch_frame,
            text="",
            command=self.toggle_admin_mode,
            fg_color=COLORS["accent"],
            progress_color=COLORS["primary"]
        )
        self.admin_switch.pack(pady=(0, 10))
        
        # Separator
        separator = ctk.CTkFrame(self.sidebar, height=2, fg_color=COLORS["border"])
        separator.pack(fill="x", padx=20, pady=15)
        
        # Navigation Buttons
        nav_label = ctk.CTkLabel(
            self.sidebar,
            text="NAVIGATION",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_secondary"]
        )
        nav_label.pack(anchor="w", padx=20, pady=(10, 15))
        
        self.nav_buttons = {}
        
        # Dashboard
        self.create_nav_button("📊 Dashboard", "dashboard", self.show_dashboard)
        
        # Students
        self.create_nav_button("👥 Students", "students", self.show_students)
        
        # Lessons (Admin only)
        self.lessons_btn = self.create_nav_button("📚 Lessons", "lessons", self.show_lessons)
        
        # Upload (Admin only)
        self.upload_btn = self.create_nav_button("⬆ Upload", "upload", self.show_upload)
        
        # Analytics
        self.create_nav_button("📈 Analytics", "analytics", self.show_analytics)
        
        # Settings
        self.create_nav_button("⚙ Settings", "settings", self.show_settings)
        
        # Footer
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=20, pady=20)
        
        version_label = ctk.CTkLabel(
            footer,
            text="Version 1.0.0",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        version_label.pack()
        
        # Update admin visibility
        self.update_admin_visibility()
        
    def create_nav_button(self, text, name, command):
        """Create a navigation button"""
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            command=command,
            anchor="w",
            height=45,
            corner_radius=10,
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["hover"],
            font=ctk.CTkFont(size=14)
        )
        btn.pack(fill="x", padx=15, pady=5)
        self.nav_buttons[name] = btn
        return btn
        
    def highlight_nav_button(self, name):
        """Highlight the active navigation button"""
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.configure(
                    fg_color=COLORS["primary"],
                    text_color="#ffffff",
                    font=ctk.CTkFont(size=14, weight="bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"],
                    font=ctk.CTkFont(size=14)
                )
                
    def create_main_content(self):
        """Create the main content area"""
        self.main_content = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["dark_bg"])
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        
    def clear_main_content(self):
        """Clear the main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
            
    def toggle_admin_mode(self):
        """Toggle between admin and user mode"""
        self.is_admin_mode = self.admin_switch.get()
        self.update_admin_visibility()
        self.show_dashboard()  # Refresh dashboard
        
    def update_admin_visibility(self):
        """Update visibility of admin-only features"""
        if self.is_admin_mode:
            self.lessons_btn.pack(fill="x", padx=15, pady=5, before=self.nav_buttons["analytics"])
            self.upload_btn.pack(fill="x", padx=15, pady=5, before=self.nav_buttons["analytics"])
        else:
            self.lessons_btn.pack_forget()
            self.upload_btn.pack_forget()
            
    # ==================== DASHBOARD VIEW ====================
    def show_dashboard(self):
        """Show the main dashboard"""
        self.clear_main_content()
        self.highlight_nav_button("dashboard")
        self.current_view = "dashboard"
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(
            self.main_content,
            fg_color="transparent"
        )
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        
        header_title = ctk.CTkLabel(
            header_frame,
            text="Dashboard Overview",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        header_title.pack(side="left")
        
        date_label = ctk.CTkLabel(
            header_frame,
            text=datetime.now().strftime("%B %d, %Y"),
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        )
        date_label.pack(side="right", padx=20)
        
        # Statistics Cards
        stats_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 30))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Get statistics
        stats = self.get_dashboard_stats()
        
        # Total Students Card
        self.create_stat_card(
            stats_frame, 
            "👥 Total Students", 
            str(stats["total_students"]),
            COLORS["primary"],
            0
        )
        
        # Total Lessons Card
        self.create_stat_card(
            stats_frame,
            "📚 Total Lessons",
            str(stats["total_lessons"]),
            COLORS["secondary"],
            1
        )
        
        # Active Users Card
        self.create_stat_card(
            stats_frame,
            "✅ Active Users",
            str(stats["active_users"]),
            COLORS["success"],
            2
        )
        
        # Completion Rate Card
        self.create_stat_card(
            stats_frame,
            "📈 Avg Progress",
            f"{stats['avg_progress']}%",
            COLORS["warning"],
            3
        )
        
        # Recent Activity Section
        activity_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["card_bg"], corner_radius=15)
        activity_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        activity_header = ctk.CTkLabel(
            activity_frame,
            text="📋 Recent Activity",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        activity_header.pack(anchor="w", padx=25, pady=(20, 15))
        
        # Activity list
        activity_list = self.get_recent_activity()
        for activity in activity_list[:5]:  # Show latest 5
            self.create_activity_item(activity_frame, activity)
            
        if not activity_list:
            no_activity = ctk.CTkLabel(
                activity_frame,
                text="No recent activity",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            )
            no_activity.pack(pady=20)
            
    def create_stat_card(self, parent, title, value, color, column):
        """Create a statistics card"""
        card = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"], corner_radius=15)
        card.grid(row=0, column=column, sticky="ew", padx=10)
        
        # Color accent bar
        accent = ctk.CTkFrame(card, fg_color=color, height=5, corner_radius=5)
        accent.pack(fill="x", padx=15, pady=(15, 10))
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        value_label.pack(pady=(10, 5))
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        )
        title_label.pack(pady=(0, 20))
        
    def create_activity_item(self, parent, activity):
        """Create an activity list item"""
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(fill="x", padx=25, pady=8)
        
        # Icon/Indicator
        indicator = ctk.CTkLabel(
            item_frame,
            text="●",
            font=ctk.CTkFont(size=20),
            text_color=activity.get("color", COLORS["primary"]),
            width=30
        )
        indicator.pack(side="left")
        
        # Content
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.pack(side="left", fill="x", expand=True)
        
        activity_text = ctk.CTkLabel(
            content_frame,
            text=activity["text"],
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        activity_text.pack(anchor="w")
        
        time_text = ctk.CTkLabel(
            content_frame,
            text=activity["time"],
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        time_text.pack(anchor="w")
        
    # ==================== STUDENTS VIEW ====================
    def show_students(self):
        """Show students list and details"""
        self.clear_main_content()
        self.highlight_nav_button("students")
        self.current_view = "students"
        
        # Main container
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkLabel(
            container,
            text="👥 Student Management",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Students content
        content_frame = ctk.CTkFrame(container, fg_color=COLORS["card_bg"], corner_radius=15)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Create scrollable list
        scroll = ctk.CTkScrollableFrame(content_frame, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        scroll.grid_columnconfigure(0, weight=1)
        
        # Get students
        students = self.get_all_students()
        
        if not students:
            no_students = ctk.CTkLabel(
                scroll,
                text="No students found",
                font=ctk.CTkFont(size=16),
                text_color=COLORS["text_secondary"]
            )
            no_students.pack(pady=50)
        else:
            for idx, student in enumerate(students):
                self.create_student_card(scroll, student, idx)
                
    def create_student_card(self, parent, student, index):
        """Create a student card"""
        card = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"], corner_radius=10)
        card.grid(row=index, column=0, sticky="ew", pady=10)
        card.grid_columnconfigure(1, weight=1)
        
        # Avatar
        avatar_frame = ctk.CTkFrame(card, fg_color=COLORS["primary"], width=60, height=60, corner_radius=30)
        avatar_frame.grid(row=0, column=0, padx=20, pady=20)
        avatar_frame.grid_propagate(False)
        
        avatar_label = ctk.CTkLabel(
            avatar_frame,
            text=student["name"][0].upper(),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        avatar_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=20)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=student["name"],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        stats_text = f"Projects: {student['projects']} | Lessons: {student['lessons_completed']}"
        stats_label = ctk.CTkLabel(
            info_frame,
            text=stats_text,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        stats_label.pack(anchor="w", pady=(5, 0))
        
        # Progress
        progress_frame = ctk.CTkFrame(card, fg_color="transparent")
        progress_frame.grid(row=0, column=2, padx=20, pady=20)
        
        progress_label = ctk.CTkLabel(
            progress_frame,
            text=f"{student['progress']}%",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["success"]
        )
        progress_label.pack()
        
        progressbar = ctk.CTkProgressBar(
            progress_frame,
            width=150,
            height=10,
            progress_color=COLORS["success"]
        )
        progressbar.pack(pady=(5, 0))
        progressbar.set(student['progress'] / 100)
        
        # View button
        view_btn = ctk.CTkButton(
            card,
            text="View Details",
            command=lambda s=student: self.show_student_details(s),
            width=120,
            height=35,
            fg_color=COLORS["secondary"],
            hover_color="#60a5fa",
            corner_radius=8
        )
        view_btn.grid(row=0, column=3, padx=20, pady=20)
        
    def show_student_details(self, student):
        """Show detailed view of a student"""
        # Create new window for student details
        details_window = ctk.CTkToplevel(self)
        details_window.title(f"Student Details - {student['name']}")
        details_window.geometry("1000x700")
        details_window.transient(self)
        details_window.grab_set()
        
        # Main container
        container = ctk.CTkFrame(details_window, fg_color=COLORS["dark_bg"])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(container, fg_color=COLORS["card_bg"], corner_radius=15)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        avatar_label = ctk.CTkLabel(
            header_frame,
            text=student["name"][0].upper(),
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text_primary"],
            width=80,
            height=80,
            fg_color=COLORS["primary"],
            corner_radius=40
        )
        avatar_label.pack(side="left", padx=30, pady=20)
        
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=20)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=student["name"],
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        joined_label = ctk.CTkLabel(
            info_frame,
            text=f"Joined: {student.get('joined_date', 'N/A')}",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        joined_label.pack(anchor="w", pady=(5, 0))
        
        # Tabview for different sections
        tabview = ctk.CTkTabview(container, fg_color=COLORS["card_bg"], corner_radius=15)
        tabview.grid(row=1, column=0, sticky="nsew")
        
        # Projects tab
        projects_tab = tabview.add("Projects")
        self.populate_projects_tab(projects_tab, student)
        
        # Code files tab
        code_tab = tabview.add("Code Files")
        self.populate_code_tab(code_tab, student)
        
        # Lessons tab
        lessons_tab = tabview.add("Lessons")
        self.populate_lessons_tab(lessons_tab, student)
        
        # Activity tab
        activity_tab = tabview.add("Activity")
        self.populate_activity_tab(activity_tab, student)
        
    def populate_projects_tab(self, parent, student):
        """Populate the projects tab"""
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        projects = self.get_student_projects(student["name"])
        
        if not projects:
            no_projects = ctk.CTkLabel(
                scroll,
                text="No projects yet",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            )
            no_projects.pack(pady=50)
        else:
            for project in projects:
                proj_frame = ctk.CTkFrame(scroll, fg_color=COLORS["card_bg"], corner_radius=10)
                proj_frame.pack(fill="x", pady=10)
                
                proj_label = ctk.CTkLabel(
                    proj_frame,
                    text=f"📁 {project['name']}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=COLORS["text_primary"],
                    anchor="w"
                )
                proj_label.pack(anchor="w", padx=20, pady=(15, 5))
                
                details = ctk.CTkLabel(
                    proj_frame,
                    text=f"Language: {project['language']} | Files: {project['files']} | Modified: {project['modified']}",
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["text_secondary"],
                    anchor="w"
                )
                details.pack(anchor="w", padx=20, pady=(0, 15))
                
    def populate_code_tab(self, parent, student):
        """Populate the code files tab with a code viewer"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        
        # File selector
        selector_frame = ctk.CTkFrame(container, fg_color=COLORS["card_bg"], corner_radius=10)
        selector_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        select_label = ctk.CTkLabel(
            selector_frame,
            text="Select File:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        select_label.pack(side="left", padx=15, pady=15)
        
        # Get code files
        code_files = self.get_student_code_files(student["name"])
        
        if code_files:
            file_var = ctk.StringVar(value=code_files[0])
            
            file_menu = ctk.CTkOptionMenu(
                selector_frame,
                variable=file_var,
                values=code_files,
                command=lambda choice: self.display_code_file(code_viewer, student["name"], choice),
                fg_color=COLORS["secondary"],
                button_color=COLORS["primary"],
                button_hover_color="#818cf8",
                width=300
            )
            file_menu.pack(side="left", padx=10, pady=15)
        
        # Code viewer
        code_frame = ctk.CTkFrame(container, fg_color=COLORS["card_bg"], corner_radius=10)
        code_frame.grid(row=1, column=0, sticky="nsew")
        code_frame.grid_columnconfigure(0, weight=1)
        code_frame.grid_rowconfigure(0, weight=1)
        
        code_viewer = ctk.CTkTextbox(
            code_frame,
            font=ctk.CTkFont(family="Courier New", size=13),
            fg_color="#ffffff",
            text_color="#1e293b",
            wrap="none"
        )
        code_viewer.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        if code_files:
            self.display_code_file(code_viewer, student["name"], code_files[0])
        else:
            code_viewer.insert("1.0", "No code files found for this student.")
            code_viewer.configure(state="disabled")
            
    def display_code_file(self, textbox, student_name, file_path):
        """Display code file content in textbox"""
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        
        try:
            full_path = os.path.join(self.BASE_USERS_DIR, student_name.lower().replace(" ", "_"), file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Add line numbers
            lines = content.split('\n')
            numbered_content = '\n'.join([f"{i+1:4d} | {line}" for i, line in enumerate(lines)])
            
            textbox.insert("1.0", numbered_content)
        except Exception as e:
            textbox.insert("1.0", f"Error loading file: {str(e)}")
            
        textbox.configure(state="disabled")
        
    def populate_lessons_tab(self, parent, student):
        """Populate the lessons tab"""
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        lessons = self.get_student_lesson_history(student["name"])
        
        if not lessons:
            no_lessons = ctk.CTkLabel(
                scroll,
                text="No lessons viewed yet",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            )
            no_lessons.pack(pady=50)
        else:
            for lesson in lessons:
                lesson_frame = ctk.CTkFrame(scroll, fg_color=COLORS["card_bg"], corner_radius=10)
                lesson_frame.pack(fill="x", pady=10)
                
                # Status indicator
                status_color = COLORS["success"] if lesson["completed"] else COLORS["warning"]
                status_indicator = ctk.CTkLabel(
                    lesson_frame,
                    text="●",
                    font=ctk.CTkFont(size=20),
                    text_color=status_color,
                    width=30
                )
                status_indicator.pack(side="left", padx=15, pady=15)
                
                # Lesson info
                info_frame = ctk.CTkFrame(lesson_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, pady=15)
                
                lesson_title = ctk.CTkLabel(
                    info_frame,
                    text=f"📚 {lesson['module']} - {lesson['language']}",
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color=COLORS["text_primary"],
                    anchor="w"
                )
                lesson_title.pack(anchor="w")
                
                lesson_date = ctk.CTkLabel(
                    info_frame,
                    text=f"Viewed: {lesson['date']}",
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["text_secondary"],
                    anchor="w"
                )
                lesson_date.pack(anchor="w", pady=(3, 0))
                
    def populate_activity_tab(self, parent, student):
        """Populate the activity tab"""
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        activities = self.get_student_activity(student["name"])
        
        if not activities:
            no_activity = ctk.CTkLabel(
                scroll,
                text="No activity recorded",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            )
            no_activity.pack(pady=50)
        else:
            for activity in activities:
                self.create_activity_item(scroll, activity)
                
    # ==================== LESSONS VIEW ====================
    def show_lessons(self):
        """Show lessons management (Admin only)"""
        self.clear_main_content()
        self.highlight_nav_button("lessons")
        self.current_view = "lessons"
        
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkLabel(
            container,
            text="📚 Lessons Library",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Content
        content = ctk.CTkFrame(container, fg_color=COLORS["card_bg"], corner_radius=15)
        content.grid(row=1, column=0, sticky="nsew")
        
        # Tabview for different languages
        tabview = ctk.CTkTabview(content, fg_color="transparent")
        tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Python lessons
        python_tab = tabview.add("Python")
        self.populate_lessons_list(python_tab, "python")
        
        # C lessons
        c_tab = tabview.add("C")
        self.populate_lessons_list(c_tab, "c")
        
    def populate_lessons_list(self, parent, language):
        """Populate lessons list for a language"""
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        lessons = self.get_available_lessons(language)
        
        if not lessons:
            no_lessons = ctk.CTkLabel(
                scroll,
                text=f"No lessons available for {language.upper()}",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            )
            no_lessons.pack(pady=50)
        else:
            for lesson in lessons:
                lesson_frame = ctk.CTkFrame(scroll, fg_color=COLORS["card_bg"], corner_radius=10)
                lesson_frame.pack(fill="x", pady=10, padx=10)
                
                lesson_label = ctk.CTkLabel(
                    lesson_frame,
                    text=f"📖 {lesson['module']}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=COLORS["text_primary"],
                    anchor="w"
                )
                lesson_label.pack(side="left", padx=20, pady=15)
                
                files_label = ctk.CTkLabel(
                    lesson_frame,
                    text=f"Files: {lesson['files']}",
                    font=ctk.CTkFont(size=13),
                    text_color=COLORS["text_secondary"]
                )
                files_label.pack(side="right", padx=20, pady=15)
                
    # ==================== UPLOAD VIEW ====================
    def show_upload(self):
        """Show upload interface (Admin only)"""
        self.clear_main_content()
        self.highlight_nav_button("upload")
        self.current_view = "upload"
        
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        header = ctk.CTkLabel(
            container,
            text="⬆ Upload Lessons",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        header.pack(anchor="w", pady=(0, 30))
        
        # Upload form
        form_frame = ctk.CTkFrame(container, fg_color=COLORS["card_bg"], corner_radius=15)
        form_frame.pack(fill="both", expand=True)
        
        # Form content
        form_content = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_content.pack(padx=50, pady=50, fill="both", expand=True)
        
        # Language selection
        lang_label = ctk.CTkLabel(
            form_content,
            text="Programming Language:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        lang_label.pack(anchor="w", pady=(10, 5))
        
        self.upload_lang_var = ctk.StringVar(value="python")
        lang_menu = ctk.CTkOptionMenu(
            form_content,
            variable=self.upload_lang_var,
            values=["python", "c"],
            fg_color=COLORS["secondary"],
            button_color=COLORS["primary"],
            width=300,
            height=40
        )
        lang_menu.pack(anchor="w", pady=(0, 20))
        
        # Module name
        module_label = ctk.CTkLabel(
            form_content,
            text="Module Name:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        module_label.pack(anchor="w", pady=(10, 5))
        
        self.upload_module_entry = ctk.CTkEntry(
            form_content,
            placeholder_text="e.g., module1_basics, module2_loops",
            width=300,
            height=40
        )
        self.upload_module_entry.pack(anchor="w", pady=(0, 20))
        
        # Lesson language (audio language)
        lesson_lang_label = ctk.CTkLabel(
            form_content,
            text="Lesson Language (Audio):",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        lesson_lang_label.pack(anchor="w", pady=(10, 5))
        
        self.upload_lesson_lang_entry = ctk.CTkEntry(
            form_content,
            placeholder_text="e.g., english, hindi, tamil",
            width=300,
            height=40
        )
        self.upload_lesson_lang_entry.pack(anchor="w", pady=(0, 20))
        
        # File selection
        file_label = ctk.CTkLabel(
            form_content,
            text="Audio File (.mp3):",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        file_label.pack(anchor="w", pady=(10, 5))
        
        file_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        file_frame.pack(anchor="w", pady=(0, 30))
        
        self.upload_file_label = ctk.CTkLabel(
            file_frame,
            text="No file selected",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        )
        self.upload_file_label.pack(side="left", padx=(0, 15))
        
        browse_btn = ctk.CTkButton(
            file_frame,
            text="Browse",
            command=self.browse_audio_file,
            width=120,
            height=40,
            fg_color=COLORS["accent"],
            hover_color="#cbd5e1"
        )
        browse_btn.pack(side="left")
        
        # Upload button
        upload_btn = ctk.CTkButton(
            form_content,
            text="Upload Lesson",
            command=self.upload_lesson,
            width=200,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["success"],
            hover_color="#34d399"
        )
        upload_btn.pack(anchor="w", pady=(20, 0))
        
        self.selected_audio_file = None
        
    def browse_audio_file(self):
        """Browse for audio file"""
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        
        if file_path:
            self.selected_audio_file = file_path
            filename = os.path.basename(file_path)
            self.upload_file_label.configure(text=filename, text_color=COLORS["success"])
            
    def upload_lesson(self):
        """Upload a lesson file"""
        # Validate inputs
        language = self.upload_lang_var.get()
        module = self.upload_module_entry.get().strip()
        lesson_lang = self.upload_lesson_lang_entry.get().strip().lower()
        
        if not module:
            messagebox.showerror("Error", "Please enter a module name")
            return
            
        if not lesson_lang:
            messagebox.showerror("Error", "Please enter a lesson language")
            return
            
        if not self.selected_audio_file:
            messagebox.showerror("Error", "Please select an audio file")
            return
            
        # Create directory structure
        module_dir = os.path.join(self.LESSONS_DIR, language, module)
        os.makedirs(module_dir, exist_ok=True)
        
        # Copy file
        dest_path = os.path.join(module_dir, f"{lesson_lang}.mp3")
        
        try:
            shutil.copy2(self.selected_audio_file, dest_path)
            messagebox.showinfo("Success", f"Lesson uploaded successfully!\n\nPath: {dest_path}")
            
            # Reset form
            self.upload_module_entry.delete(0, "end")
            self.upload_lesson_lang_entry.delete(0, "end")
            self.upload_file_label.configure(text="No file selected", text_color=COLORS["text_secondary"])
            self.selected_audio_file = None
            
            # Log activity
            self.log_activity({
                "text": f"New lesson uploaded: {language}/{module}/{lesson_lang}",
                "time": datetime.now().strftime("%H:%M %p"),
                "color": COLORS["success"]
            })
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload lesson:\n{str(e)}")
            
    # ==================== ANALYTICS VIEW ====================
    def show_analytics(self):
        """Show analytics and insights"""
        self.clear_main_content()
        self.highlight_nav_button("analytics")
        self.current_view = "analytics"
        
        scroll_frame = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkLabel(
            scroll_frame,
            text="📈 Analytics & Insights",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, 30))
        
        # Analytics cards
        analytics = self.get_analytics_data()
        
        # Most popular language
        pop_lang_card = ctk.CTkFrame(scroll_frame, fg_color=COLORS["card_bg"], corner_radius=15)
        pop_lang_card.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        self.create_analytics_section(
            pop_lang_card,
            "🏆 Most Popular Language",
            analytics["popular_language"],
            f"{analytics['language_usage']}% of students"
        )
        
        # Most viewed lesson
        pop_lesson_card = ctk.CTkFrame(scroll_frame, fg_color=COLORS["card_bg"], corner_radius=15)
        pop_lesson_card.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        self.create_analytics_section(
            pop_lesson_card,
            "📚 Most Viewed Lesson",
            analytics["popular_lesson"],
            f"{analytics['lesson_views']} views"
        )
        
        # Average completion rate
        completion_card = ctk.CTkFrame(scroll_frame, fg_color=COLORS["card_bg"], corner_radius=15)
        completion_card.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        
        self.create_analytics_section(
            completion_card,
            "✅ Average Completion Rate",
            f"{analytics['avg_completion']}%",
            "Across all students"
        )
        
    def create_analytics_section(self, parent, title, value, description):
        """Create an analytics section"""
        title_label = ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(anchor="w", padx=25, pady=(20, 10))
        
        value_label = ctk.CTkLabel(
            parent,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["primary"]
        )
        value_label.pack(anchor="w", padx=25, pady=(0, 5))
        
        desc_label = ctk.CTkLabel(
            parent,
            text=description,
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        )
        desc_label.pack(anchor="w", padx=25, pady=(0, 20))
        
    # ==================== SETTINGS VIEW ====================
    def show_settings(self):
        """Show settings"""
        self.clear_main_content()
        self.highlight_nav_button("settings")
        self.current_view = "settings"
        
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        header = ctk.CTkLabel(
            container,
            text="⚙ Settings",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        header.pack(anchor="w", pady=(0, 30))
        
        # Settings content
        settings_frame = ctk.CTkFrame(container, fg_color=COLORS["card_bg"], corner_radius=15)
        settings_frame.pack(fill="both", expand=True)
        
        settings_content = ctk.CTkScrollableFrame(settings_frame, fg_color="transparent")
        settings_content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Appearance section
        appearance_label = ctk.CTkLabel(
            settings_content,
            text="Appearance",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        appearance_label.pack(anchor="w", pady=(0, 15))
        
        theme_frame = ctk.CTkFrame(settings_content, fg_color=COLORS["card_bg"], corner_radius=10)
        theme_frame.pack(fill="x", pady=(0, 20))
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Theme Mode:",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_primary"]
        )
        theme_label.pack(side="left", padx=20, pady=15)
        
        theme_var = ctk.StringVar(value="light")
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            variable=theme_var,
            values=["dark", "light", "system"],
            command=lambda choice: ctk.set_appearance_mode(choice),
            fg_color=COLORS["secondary"],
            button_color=COLORS["primary"],
            width=150
        )
        theme_menu.pack(side="right", padx=20, pady=15)
        
        # About section
        separator = ctk.CTkFrame(settings_content, height=2, fg_color=COLORS["border"])
        separator.pack(fill="x", pady=30)
        
        about_label = ctk.CTkLabel(
            settings_content,
            text="About Sight2Code",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        about_label.pack(anchor="w", pady=(0, 15))
        
        about_text = """
        Sight2Code is an AI-powered voice-controlled coding platform designed to empower 
        visually impaired individuals to learn programming through voice commands and audio lessons.
        
        Version: 1.0.0
        Developed with ❤ for accessibility in education
        """
        
        about_desc = ctk.CTkLabel(
            settings_content,
            text=about_text,
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
            justify="left"
        )
        about_desc.pack(anchor="w", pady=(0, 20))
        
    # ==================== DATA METHODS ====================
    def load_dashboard_data(self):
        """Load dashboard data from files"""
        self.data_file = os.path.join(self.DATA_DIR, "dashboard_data.json")
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.dashboard_data = json.load(f)
            except:
                self.dashboard_data = self.get_default_data()
        else:
            self.dashboard_data = self.get_default_data()
            self.save_dashboard_data()
            
    def save_dashboard_data(self):
        """Save dashboard data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.dashboard_data, f, indent=4)
            
    def get_default_data(self):
        """Get default dashboard data structure"""
        return {
            "students": [],
            "activities": [],
            "lessons_viewed": {},
            "analytics": {}
        }
        
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        students = self.get_all_students()
        lessons = self.get_all_lessons_count()
        
        active_users = len([s for s in students if s.get("active", True)])
        
        if students:
            avg_progress = sum(s["progress"] for s in students) / len(students)
        else:
            avg_progress = 0
            
        return {
            "total_students": len(students),
            "total_lessons": lessons,
            "active_users": active_users,
            "avg_progress": int(avg_progress)
        }
        
    def get_all_students(self):
        """Get all students from users directory"""
        students = []
        
        if os.path.exists(self.BASE_USERS_DIR):
            for user_dir in os.listdir(self.BASE_USERS_DIR):
                user_path = os.path.join(self.BASE_USERS_DIR, user_dir)
                if os.path.isdir(user_path):
                    # Get student info
                    projects = [d for d in os.listdir(user_path) if os.path.isdir(os.path.join(user_path, d))]
                    
                    students.append({
                        "name": user_dir.replace("_", " ").title(),
                        "projects": len(projects),
                        "lessons_completed": self.get_student_lessons_count(user_dir),
                        "progress": self.calculate_student_progress(user_dir),
                        "joined_date": self.get_user_joined_date(user_path),
                        "active": True
                    })
                    
        return students
        
    def get_student_projects(self, student_name):
        """Get projects for a student"""
        projects = []
        user_dir = os.path.join(self.BASE_USERS_DIR, student_name.lower().replace(" ", "_"))
        
        if os.path.exists(user_dir):
            for proj_dir in os.listdir(user_dir):
                proj_path = os.path.join(user_dir, proj_dir)
                if os.path.isdir(proj_path):
                    files = [f for f in os.listdir(proj_path) if os.path.isfile(os.path.join(proj_path, f))]
                    
                    # Get file extension to determine language
                    language = "Unknown"
                    for f in files:
                        if f.endswith('.py'):
                            language = "Python"
                            break
                        elif f.endswith('.c'):
                            language = "C"
                            break
                    
                    # Get modification time
                    modified = datetime.fromtimestamp(os.path.getmtime(proj_path)).strftime("%Y-%m-%d")
                    
                    projects.append({
                        "name": proj_dir,
                        "language": language,
                        "files": len(files),
                        "modified": modified
                    })
                    
        return projects
        
    def get_student_code_files(self, student_name):
        """Get code files for a student"""
        code_files = []
        user_dir = os.path.join(self.BASE_USERS_DIR, student_name.lower().replace(" ", "_"))
        
        if os.path.exists(user_dir):
            for root, dirs, files in os.walk(user_dir):
                for file in files:
                    if file.endswith(('.py', '.c')):
                        rel_path = os.path.relpath(os.path.join(root, file), user_dir)
                        code_files.append(rel_path)
                        
        return code_files
        
    def get_student_lessons_count(self, user_dir):
        """Get count of lessons completed by student"""
        # This would be tracked in your backend - returning sample data
        return len(self.get_student_lesson_history(user_dir))
        
    def get_student_lesson_history(self, student_name):
        """Get lesson viewing history for a student"""
        # Sample data - integrate with your backend logging
        return [
            {
                "module": "Module 1: Basics",
                "language": "Python",
                "date": "2025-11-04",
                "completed": True
            },
            {
                "module": "Module 2: Loops",
                "language": "Python",
                "date": "2025-11-03",
                "completed": False
            }
        ]
        
    def calculate_student_progress(self, user_dir):
        """Calculate student progress percentage"""
        # Simple calculation based on projects and lessons
        projects = len([d for d in os.listdir(os.path.join(self.BASE_USERS_DIR, user_dir)) 
                       if os.path.isdir(os.path.join(self.BASE_USERS_DIR, user_dir, d))])
        lessons = self.get_student_lessons_count(user_dir)
        
        # Weighted average
        progress = min(100, (projects * 20 + lessons * 10))
        return progress
        
    def get_user_joined_date(self, user_path):
        """Get user joined date"""
        timestamp = os.path.getctime(user_path)
        return datetime.fromtimestamp(timestamp).strftime("%B %d, %Y")
        
    def get_student_activity(self, student_name):
        """Get activity log for a student"""
        # Sample data - integrate with your backend logging
        return [
            {
                "text": "Created new project: calculator",
                "time": "2 hours ago",
                "color": COLORS["success"]
            },
            {
                "text": "Completed lesson: Module 1",
                "time": "1 day ago",
                "color": COLORS["primary"]
            }
        ]
        
    def get_all_lessons_count(self):
        """Get total count of lessons"""
        count = 0
        if os.path.exists(self.LESSONS_DIR):
            for lang_dir in os.listdir(self.LESSONS_DIR):
                lang_path = os.path.join(self.LESSONS_DIR, lang_dir)
                if os.path.isdir(lang_path):
                    for module_dir in os.listdir(lang_path):
                        module_path = os.path.join(lang_path, module_dir)
                        if os.path.isdir(module_path):
                            count += len([f for f in os.listdir(module_path) if f.endswith('.mp3')])
        return count
        
    def get_available_lessons(self, language):
        """Get available lessons for a language"""
        lessons = []
        lang_path = os.path.join(self.LESSONS_DIR, language)
        
        if os.path.exists(lang_path):
            for module_dir in os.listdir(lang_path):
                module_path = os.path.join(lang_path, module_dir)
                if os.path.isdir(module_path):
                    files = [f for f in os.listdir(module_path) if f.endswith('.mp3')]
                    lessons.append({
                        "module": module_dir,
                        "files": len(files)
                    })
                    
        return lessons
        
    def get_recent_activity(self):
        """Get recent activity across all users"""
        # Sample data - integrate with your backend logging
        return [
            {
                "text": "User John created new project: web_scraper",
                "time": "10 minutes ago",
                "color": COLORS["success"]
            },
            {
                "text": "User Sarah completed Python Module 3",
                "time": "1 hour ago",
                "color": COLORS["primary"]
            },
            {
                "text": "Admin uploaded new lesson: C Pointers",
                "time": "2 hours ago",
                "color": COLORS["warning"]
            }
        ]
        
    def log_activity(self, activity):
        """Log an activity"""
        self.dashboard_data["activities"].insert(0, activity)
        # Keep only last 50 activities
        self.dashboard_data["activities"] = self.dashboard_data["activities"][:50]
        self.save_dashboard_data()
        
    def get_analytics_data(self):
        """Get analytics data"""
        # Sample data - calculate from actual data
        return {
            "popular_language": "Python",
            "language_usage": 75,
            "popular_lesson": "Module 1: Python Basics",
            "lesson_views": 42,
            "avg_completion": 68
        }


def main():
    """Main entry point"""
    app = Sight2CodeDashboard()
    app.mainloop()


if __name__ == "__main__":
    main()