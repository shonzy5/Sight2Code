import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import shutil
from pathlib import Path
import threading
import queue

# Import your existing backend functions
# from your_script import (speak, takeCommand, admin_panel, user_mode, 
#                          code_mode, learn_mode, execute_code, etc.)

class ModernVoiceCodingPlatform:
    """Professional GUI for AI-Powered Voice Coding Platform"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AI-Powered Voice Coding Platform")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Configuration
        self.ADMIN_USERNAME = "admin"
        self.ADMIN_PASSWORD = "1234"
        self.BASE_USERS_DIR = "users"
        self.LESSONS_DIR = "lessons"
        self.SUPPORTED_LANGUAGES = ["python", "c"]
        
        # Ensure directories exist
        os.makedirs(self.BASE_USERS_DIR, exist_ok=True)
        os.makedirs(self.LESSONS_DIR, exist_ok=True)
        
        # Modern color scheme
        self.colors = {
            'primary': '#0f3460',
            'secondary': '#16213e',
            'accent': '#e94560',
            'success': '#2ecc71',
            'warning': '#f39c12',
            'text': '#ffffff',
            'text_secondary': '#a8b2d1',
            'bg': '#1a1a2e',
            'bg_light': '#2d2d44',
            'border': '#3a3a5c'
        }
        
        # Message queue for thread-safe GUI updates
        self.message_queue = queue.Queue()
        
        # Current user and session data
        self.current_user = None
        self.current_mode = None
        
        # Setup styles
        self.setup_styles()
        
        # Show main menu
        self.show_main_menu()
        
        # Start message queue processor
        self.process_queue()
    
    def setup_styles(self):
        """Configure ttk styles for modern appearance"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Primary.TButton',
                       background=self.colors['accent'],
                       foreground=self.colors['text'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=15,
                       font=('Segoe UI', 11, 'bold'))
        
        style.map('Primary.TButton',
                 background=[('active', '#ff5577')])
        
        style.configure('Secondary.TButton',
                       background=self.colors['primary'],
                       foreground=self.colors['text'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=12,
                       font=('Segoe UI', 10))
        
        style.map('Secondary.TButton',
                 background=[('active', '#1a4d7a')])
        
        # Configure label styles
        style.configure('Title.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 28, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 12))
        
        style.configure('Header.TLabel',
                       background=self.colors['bg_light'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 16, 'bold'))
        
        # Configure entry styles
        style.configure('Modern.TEntry',
                       fieldbackground=self.colors['bg_light'],
                       foreground=self.colors['text'],
                       borderwidth=2,
                       relief='flat',
                       padding=10,
                       font=('Segoe UI', 11))
        
        # Configure combobox styles
        style.configure('Modern.TCombobox',
                       fieldbackground=self.colors['bg_light'],
                       background=self.colors['bg_light'],
                       foreground=self.colors['text'],
                       arrowcolor=self.colors['text'],
                       borderwidth=0,
                       padding=10,
                       font=('Segoe UI', 11))
        
        # Configure frame styles
        style.configure('Card.TFrame',
                       background=self.colors['bg_light'],
                       borderwidth=2,
                       relief='flat')
        
        style.configure('Main.TFrame',
                       background=self.colors['bg'])
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_header(self, parent, title, subtitle=""):
        """Create consistent header for all screens"""
        header_frame = ttk.Frame(parent, style='Main.TFrame')
        header_frame.pack(fill='x', padx=40, pady=(30, 20))
        
        title_label = ttk.Label(header_frame, text=title, style='Title.TLabel')
        title_label.pack(anchor='w')
        
        if subtitle:
            subtitle_label = ttk.Label(header_frame, text=subtitle, style='Subtitle.TLabel')
            subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # Separator line
        separator = tk.Canvas(parent, height=2, bg=self.colors['border'], highlightthickness=0)
        separator.pack(fill='x', padx=40, pady=(0, 20))
        
        return header_frame
    
    def show_main_menu(self):
        """Display main menu screen"""
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        # Center container
        center_frame = ttk.Frame(main_frame, style='Main.TFrame')
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo/Title
        title = ttk.Label(center_frame, 
                         text="AI-Powered Voice Coding Platform",
                         style='Title.TLabel')
        title.pack(pady=(0, 10))
        
        subtitle = ttk.Label(center_frame,
                            text="Learn and Code with Voice Commands",
                            style='Subtitle.TLabel')
        subtitle.pack(pady=(0, 50))
        
        # Button container
        button_frame = ttk.Frame(center_frame, style='Main.TFrame')
        button_frame.pack()
        
        # Admin button
        admin_btn = ttk.Button(button_frame,
                              text="Administrator Panel",
                              style='Primary.TButton',
                              command=self.show_admin_login,
                              width=25)
        admin_btn.pack(pady=15)
        
        # User button
        user_btn = ttk.Button(button_frame,
                             text="User Mode",
                             style='Secondary.TButton',
                             command=self.show_user_login,
                             width=25)
        user_btn.pack(pady=15)
        
        # Exit button
        exit_btn = ttk.Button(button_frame,
                             text="Exit Application",
                             style='Secondary.TButton',
                             command=self.root.quit,
                             width=25)
        exit_btn.pack(pady=15)
    
    def show_admin_login(self):
        """Display admin login screen"""
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        self.create_header(main_frame, "Administrator Login", 
                          "Enter credentials to access admin panel")
        
        # Center container
        center_frame = ttk.Frame(main_frame, style='Card.TFrame')
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        center_frame.configure(padding=50)
        
        # Username
        username_label = tk.Label(center_frame, 
                                 text="Username:",
                                 bg=self.colors['bg_light'],
                                 fg=self.colors['text'],
                                 font=('Segoe UI', 11))
        username_label.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        username_entry = ttk.Entry(center_frame, style='Modern.TEntry', width=30)
        username_entry.grid(row=1, column=0, pady=(0, 20))
        username_entry.focus()
        
        # Password
        password_label = tk.Label(center_frame,
                                 text="Password:",
                                 bg=self.colors['bg_light'],
                                 fg=self.colors['text'],
                                 font=('Segoe UI', 11))
        password_label.grid(row=2, column=0, sticky='w', pady=(0, 10))
        
        password_entry = ttk.Entry(center_frame, style='Modern.TEntry', 
                                  width=30, show='●')
        password_entry.grid(row=3, column=0, pady=(0, 30))
        
        # Error message label
        error_label = tk.Label(center_frame,
                              text="",
                              bg=self.colors['bg_light'],
                              fg=self.colors['accent'],
                              font=('Segoe UI', 10))
        error_label.grid(row=4, column=0, pady=(0, 10))
        
        def attempt_login():
            username = username_entry.get()
            password = password_entry.get()
            
            if username == self.ADMIN_USERNAME and password == self.ADMIN_PASSWORD:
                self.show_admin_panel()
            else:
                error_label.config(text="Invalid credentials. Please try again.")
        
        # Login button
        login_btn = ttk.Button(center_frame,
                              text="Login",
                              style='Primary.TButton',
                              command=attempt_login,
                              width=25)
        login_btn.grid(row=5, column=0, pady=5)
        
        # Back button
        back_btn = ttk.Button(center_frame,
                             text="Back to Main Menu",
                             style='Secondary.TButton',
                             command=self.show_main_menu,
                             width=25)
        back_btn.grid(row=6, column=0, pady=5)
        
        # Bind enter key
        password_entry.bind('<Return>', lambda e: attempt_login())
    
    def show_admin_panel(self):
        """Display admin panel with lesson management"""
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        self.create_header(main_frame, "Administrator Panel",
                          "Manage lessons and course content")
        
        # Content area with scrollbar
        content_frame = ttk.Frame(main_frame, style='Main.TFrame')
        content_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Left panel - Upload section
        left_panel = ttk.Frame(content_frame, style='Card.TFrame')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        upload_header = tk.Label(left_panel,
                                text="Upload Lesson Audio",
                                bg=self.colors['bg_light'],
                                fg=self.colors['text'],
                                font=('Segoe UI', 14, 'bold'))
        upload_header.pack(pady=20, padx=20, anchor='w')
        
        # Form frame
        form_frame = ttk.Frame(left_panel, style='Card.TFrame')
        form_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Language selection
        lang_label = tk.Label(form_frame,
                             text="Programming Language:",
                             bg=self.colors['bg_light'],
                             fg=self.colors['text'],
                             font=('Segoe UI', 11))
        lang_label.grid(row=0, column=0, sticky='w', pady=(10, 5), padx=10)
        
        lang_var = tk.StringVar()
        lang_combo = ttk.Combobox(form_frame,
                                 textvariable=lang_var,
                                 values=self.SUPPORTED_LANGUAGES,
                                 state='readonly',
                                 style='Modern.TCombobox',
                                 width=28)
        lang_combo.grid(row=1, column=0, pady=(0, 15), padx=10, sticky='ew')
        lang_combo.set("Select language")
        
        # Module name
        module_label = tk.Label(form_frame,
                               text="Module Name:",
                               bg=self.colors['bg_light'],
                               fg=self.colors['text'],
                               font=('Segoe UI', 11))
        module_label.grid(row=2, column=0, sticky='w', pady=(10, 5), padx=10)
        
        module_entry = ttk.Entry(form_frame, style='Modern.TEntry', width=30)
        module_entry.grid(row=3, column=0, pady=(0, 15), padx=10, sticky='ew')
        
        # Lesson language
        lesson_lang_label = tk.Label(form_frame,
                                    text="Lesson Language (e.g., English, Hindi):",
                                    bg=self.colors['bg_light'],
                                    fg=self.colors['text'],
                                    font=('Segoe UI', 11))
        lesson_lang_label.grid(row=4, column=0, sticky='w', pady=(10, 5), padx=10)
        
        lesson_lang_entry = ttk.Entry(form_frame, style='Modern.TEntry', width=30)
        lesson_lang_entry.grid(row=5, column=0, pady=(0, 15), padx=10, sticky='ew')
        
        # File selection
        file_label = tk.Label(form_frame,
                             text="Audio File (.mp3):",
                             bg=self.colors['bg_light'],
                             fg=self.colors['text'],
                             font=('Segoe UI', 11))
        file_label.grid(row=6, column=0, sticky='w', pady=(10, 5), padx=10)
        
        file_path_var = tk.StringVar()
        file_path_var.set("No file selected")
        
        file_display = tk.Label(form_frame,
                               textvariable=file_path_var,
                               bg=self.colors['bg_light'],
                               fg=self.colors['text_secondary'],
                               font=('Segoe UI', 9),
                               wraplength=300,
                               anchor='w',
                               justify='left')
        file_display.grid(row=7, column=0, pady=(0, 10), padx=10, sticky='w')
        
        def browse_file():
            filename = filedialog.askopenfilename(
                title="Select Audio File",
                filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*"))
            )
            if filename:
                file_path_var.set(filename)
        
        browse_btn = ttk.Button(form_frame,
                               text="Browse Files",
                               style='Secondary.TButton',
                               command=browse_file,
                               width=20)
        browse_btn.grid(row=8, column=0, pady=10, padx=10)
        
        # Status label
        status_label = tk.Label(form_frame,
                               text="",
                               bg=self.colors['bg_light'],
                               fg=self.colors['success'],
                               font=('Segoe UI', 10),
                               wraplength=300)
        status_label.grid(row=9, column=0, pady=10, padx=10)
        
        def upload_lesson():
            lang = lang_var.get()
            module = module_entry.get().strip()
            lesson_lang = lesson_lang_entry.get().strip()
            file_path = file_path_var.get()
            
            # Validation
            if lang == "Select language" or not lang:
                messagebox.showerror("Error", "Please select a programming language")
                return
            
            if not module:
                messagebox.showerror("Error", "Please enter a module name")
                return
            
            if not lesson_lang:
                messagebox.showerror("Error", "Please enter a lesson language")
                return
            
            if file_path == "No file selected" or not os.path.exists(file_path):
                messagebox.showerror("Error", "Please select a valid audio file")
                return
            
            # Create directory structure
            module_path = os.path.join(self.LESSONS_DIR, lang, module)
            os.makedirs(module_path, exist_ok=True)
            
            # Copy file
            dest_path = os.path.join(module_path, f"{lesson_lang}.mp3")
            try:
                shutil.copy2(file_path, dest_path)
                status_label.config(
                    text=f"✓ Lesson uploaded successfully!\nPath: {dest_path}",
                    fg=self.colors['success']
                )
                
                # Clear form
                module_entry.delete(0, 'end')
                lesson_lang_entry.delete(0, 'end')
                file_path_var.set("No file selected")
                
                # Refresh lesson list
                refresh_lesson_list()
                
                messagebox.showinfo("Success", "Lesson uploaded successfully!")
            except Exception as e:
                status_label.config(text=f"Error: {str(e)}", fg=self.colors['accent'])
                messagebox.showerror("Error", f"Failed to upload lesson: {str(e)}")
        
        upload_btn = ttk.Button(form_frame,
                               text="Upload Lesson",
                               style='Primary.TButton',
                               command=upload_lesson,
                               width=20)
        upload_btn.grid(row=10, column=0, pady=20, padx=10)
        
        # Right panel - Existing lessons
        right_panel = ttk.Frame(content_frame, style='Card.TFrame')
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        lessons_header = tk.Label(right_panel,
                                 text="Existing Lessons",
                                 bg=self.colors['bg_light'],
                                 fg=self.colors['text'],
                                 font=('Segoe UI', 14, 'bold'))
        lessons_header.pack(pady=20, padx=20, anchor='w')
        
        # Lessons list with scrollbar
        list_frame = ttk.Frame(right_panel, style='Card.TFrame')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        lessons_text = tk.Text(list_frame,
                              bg=self.colors['bg'],
                              fg=self.colors['text'],
                              font=('Consolas', 10),
                              wrap='word',
                              yscrollcommand=scrollbar.set,
                              relief='flat',
                              padx=10,
                              pady=10)
        lessons_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=lessons_text.yview)
        
        def refresh_lesson_list():
            lessons_text.delete(1.0, 'end')
            lessons_text.insert('end', "📚 LESSON LIBRARY\n" + "="*50 + "\n\n")
            
            for lang in self.SUPPORTED_LANGUAGES:
                lang_path = os.path.join(self.LESSONS_DIR, lang)
                if os.path.exists(lang_path):
                    modules = [d for d in os.listdir(lang_path) 
                              if os.path.isdir(os.path.join(lang_path, d))]
                    
                    if modules:
                        lessons_text.insert('end', f"▶ {lang.upper()}\n", 'lang')
                        for module in sorted(modules):
                            lessons_text.insert('end', f"  └─ {module}\n", 'module')
                            module_path = os.path.join(lang_path, module)
                            files = [f for f in os.listdir(module_path) if f.endswith('.mp3')]
                            for file in sorted(files):
                                lesson_name = file.replace('.mp3', '')
                                lessons_text.insert('end', f"     • {lesson_name}\n", 'file')
                        lessons_text.insert('end', "\n")
            
            # Configure tags for formatting
            lessons_text.tag_config('lang', foreground=self.colors['accent'], 
                                   font=('Consolas', 11, 'bold'))
            lessons_text.tag_config('module', foreground=self.colors['success'])
            lessons_text.tag_config('file', foreground=self.colors['text_secondary'])
        
        refresh_lesson_list()
        
        # Refresh button
        refresh_btn = ttk.Button(right_panel,
                                text="Refresh List",
                                style='Secondary.TButton',
                                command=refresh_lesson_list,
                                width=20)
        refresh_btn.pack(pady=(0, 20))
        
        # Bottom navigation
        nav_frame = ttk.Frame(main_frame, style='Main.TFrame')
        nav_frame.pack(side='bottom', fill='x', padx=40, pady=20)
        
        back_btn = ttk.Button(nav_frame,
                             text="← Back to Main Menu",
                             style='Secondary.TButton',
                             command=self.show_main_menu)
        back_btn.pack(side='left')
    
    def show_user_login(self):
        """Display user login/registration screen"""
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        self.create_header(main_frame, "User Access",
                          "Enter your name to continue")
        
        # Center container
        center_frame = ttk.Frame(main_frame, style='Card.TFrame')
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        center_frame.configure(padding=50)
        
        # Username
        username_label = tk.Label(center_frame,
                                 text="Your Name:",
                                 bg=self.colors['bg_light'],
                                 fg=self.colors['text'],
                                 font=('Segoe UI', 11))
        username_label.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        username_entry = ttk.Entry(center_frame, style='Modern.TEntry', width=30)
        username_entry.grid(row=1, column=0, pady=(0, 30))
        username_entry.focus()
        
        def proceed():
            username = username_entry.get().strip()
            if username:
                self.current_user = username.replace(" ", "_")
                # Create user directory
                user_dir = os.path.join(self.BASE_USERS_DIR, self.current_user)
                os.makedirs(user_dir, exist_ok=True)
                self.show_user_dashboard()
            else:
                messagebox.showerror("Error", "Please enter your name")
        
        # Continue button
        continue_btn = ttk.Button(center_frame,
                                 text="Continue",
                                 style='Primary.TButton',
                                 command=proceed,
                                 width=25)
        continue_btn.grid(row=2, column=0, pady=5)
        
        # Back button
        back_btn = ttk.Button(center_frame,
                             text="Back to Main Menu",
                             style='Secondary.TButton',
                             command=self.show_main_menu,
                             width=25)
        back_btn.grid(row=3, column=0, pady=5)
        
        username_entry.bind('<Return>', lambda e: proceed())
    
    def show_user_dashboard(self):
        """Display user dashboard with Learn and Code options"""
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        self.create_header(main_frame, f"Welcome, {self.current_user}",
                          "Choose your activity")
        
        # Center container with cards
        center_frame = ttk.Frame(main_frame, style='Main.TFrame')
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Learn Mode Card
        learn_card = ttk.Frame(center_frame, style='Card.TFrame')
        learn_card.grid(row=0, column=0, padx=30, pady=20)
        learn_card.configure(padding=40)
        
        learn_icon = tk.Label(learn_card,
                             text="📚",
                             bg=self.colors['bg_light'],
                             font=('Segoe UI', 48))
        learn_icon.pack()
        
        learn_title = tk.Label(learn_card,
                              text="Learn Mode",
                              bg=self.colors['bg_light'],
                              fg=self.colors['text'],
                              font=('Segoe UI', 18, 'bold'))
        learn_title.pack(pady=(10, 5))
        
        learn_desc = tk.Label(learn_card,
                             text="Access programming lessons\nwith audio tutorials",
                             bg=self.colors['bg_light'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 10),
                             justify='center')
        learn_desc.pack(pady=(0, 20))
        
        learn_btn = ttk.Button(learn_card,
                              text="Start Learning",
                              style='Primary.TButton',
                              command=self.show_learn_mode,
                              width=20)
        learn_btn.pack()
        
        # Code Mode Card
        code_card = ttk.Frame(center_frame, style='Card.TFrame')
        code_card.grid(row=0, column=1, padx=30, pady=20)
        code_card.configure(padding=40)
        
        code_icon = tk.Label(code_card,
                            text="💻",
                            bg=self.colors['bg_light'],
                            font=('Segoe UI', 48))
        code_icon.pack()
        
        code_title = tk.Label(code_card,
                             text="Code Mode",
                             bg=self.colors['bg_light'],
                             fg=self.colors['text'],
                             font=('Segoe UI', 18, 'bold'))
        code_title.pack(pady=(10, 5))
        
        code_desc = tk.Label(code_card,
                            text="Write code using\nAI-powered voice commands",
                            bg=self.colors['bg_light'],
                            fg=self.colors['text_secondary'],
                            font=('Segoe UI', 10),
                            justify='center')
        code_desc.pack(pady=(0, 20))
        
        code_btn = ttk.Button(code_card,
                             text="Start Coding",
                             style='Primary.TButton',
                             command=self.show_code_mode,
                             width=20)
        code_btn.pack()
        
        # Bottom navigation
        nav_frame = ttk.Frame(main_frame, style='Main.TFrame')
        nav_frame.pack(side='bottom', fill='x', padx=40, pady=20)
        
        logout_btn = ttk.Button(nav_frame,
                               text="← Logout",
                               style='Secondary.TButton',
                               command=self.show_main_menu)
        logout_btn.pack(side='left')
    
    def show_learn_mode(self):
        """Display learn mode interface"""
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        self.create_header(main_frame, "Learn Mode",
                          "Select a course and start learning")
        
        content_frame = ttk.Frame(main_frame, style='Main.TFrame')
        content_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Left panel - Selection
        left_panel = ttk.Frame(content_frame, style='Card.TFrame')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        left_panel.configure(padding=30)
        
        # Language selection
        lang_label = tk.Label(left_panel,
                             text="Programming Language:",
                             bg=self.colors['bg_light'],
                             fg=self.colors['text'],
                             font=('Segoe UI', 12, 'bold'))
        lang_label.pack(anchor='w', pady=(0, 10))
        
        lang_var = tk.StringVar()
        lang_frame = ttk.Frame(left_panel, style='Card.TFrame')
        lang_frame.pack(fill='x', pady=(0, 20))
        
        for lang in self.SUPPORTED_LANGUAGES:
            rb = tk.Radiobutton(lang_frame,
                               text=lang.capitalize(),
                               variable=lang_var,
                               value=lang,
                               bg=self.colors['bg_light'],
                               fg=self.colors['text'],
                               selectcolor=self.colors['bg'],
                               activebackground=self.colors['bg_light'],
                               activeforeground=self.colors['accent'],
                               font=('Segoe UI', 11),
                               command=lambda: update_modules())
            rb.pack(anchor='w', pady=5)
        
        # Module selection
        module_label = tk.Label(left_panel,
                               text="Select Module:",
                               bg=self.colors['bg_light'],
                               fg=self.colors['text'],
                               font=('Segoe UI', 12, 'bold'))
        module_label.pack(anchor='w', pady=(10, 10))
        
        module_var = tk.StringVar()
        module_listbox = tk.Listbox(left_panel,
                                    bg=self.colors['bg'],
                                    fg=self.colors['text'],
                                    font=('Segoe UI', 11),
                                    selectbackground=self.colors['accent'],
                                    selectforeground=self.colors['text'],
                                    relief='flat',
                                    highlightthickness=0,
                                    height=6)
        module_listbox.pack(fill='x', pady=(0, 20))
        
        # Lesson language selection
        lesson_lang_label = tk.Label(left_panel,
                                     text="Lesson Language:",
                                     bg=self.colors['bg_light'],
                                     fg=self.colors['text'],
                                     font=('Segoe UI', 12, 'bold'))
        lesson_lang_label.pack(anchor='w', pady=(10, 10))
        
        lesson_lang_listbox = tk.Listbox(left_panel,
                                         bg=self.colors['bg'],
                                         fg=self.colors['text'],
                                         font=('Segoe UI', 11),
                                         selectbackground=self.colors['accent'],
                                         selectforeground=self.colors['text'],
                                         relief='flat',
                                         highlightthickness=0,
                                         height=4)
        lesson_lang_listbox.pack(fill='x', pady=(0, 20))
        
        def update_modules():
            module_listbox.delete(0, 'end')
            lesson_lang_listbox.delete(0, 'end')
            lang = lang_var.get()
            if lang:
                lang_path = os.path.join(self.LESSONS_DIR, lang)
                if os.path.exists(lang_path):
                    modules = [d for d in os.listdir(lang_path)
                              if os.path.isdir(os.path.join(lang_path, d))]
                    for module in sorted(modules):
                        module_listbox.insert('end', module)
        
        def update_lesson_languages(event):
            lesson_lang_listbox.delete(0, 'end')
            selection = module_listbox.curselection()
            if selection:
                module = module_listbox.get(selection[0])
                lang = lang_var.get()
                module_path = os.path.join(self.LESSONS_DIR, lang, module)
                if os.path.exists(module_path):
                    files = [f.replace('.mp3', '') for f in os.listdir(module_path)
                            if f.endswith('.mp3')]
                    for file in sorted(files):
                        lesson_lang_listbox.insert('end', file)
        
        module_listbox.bind('<<ListboxSelect>>', update_lesson_languages)
        
        def start_lesson():
            lang = lang_var.get()
            module_sel = module_listbox.curselection()
            lesson_sel = lesson_lang_listbox.curselection()
            
            if not lang:
                messagebox.showerror("Error", "Please select a programming language")
                return
            if not module_sel:
                messagebox.showerror("Error", "Please select a module")
                return
            if not lesson_sel:
                messagebox.showerror("Error", "Please select a lesson language")
                return
            
            module = module_listbox.get(module_sel[0])
            lesson_lang = lesson_lang_listbox.get(lesson_sel[0])
            
            # Here you would integrate with your play_lesson function
            messagebox.showinfo("Playing Lesson",
                              f"Now playing:\nLanguage: {lang}\nModule: {module}\nLesson: {lesson_lang}")
            
            # TODO: Integrate with actual play_lesson function
            # play_lesson(lang, module, lesson_lang)
        
        play_btn = ttk.Button(left_panel,
                             text="▶ Play Lesson",
                             style='Primary.TButton',
                             command=start_lesson,
                             width=25)
        play_btn.pack(pady=10)
        
        # Right panel - Instructions
        right_panel = ttk.Frame(content_frame, style='Card.TFrame')
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        right_panel.configure(padding=30)
        
        info_title = tk.Label(right_panel,
                             text="📖 Instructions",
                             bg=self.colors['bg_light'],
                             fg=self.colors['text'],
                             font=('Segoe UI', 14, 'bold'))
        info_title.pack(anchor='w', pady=(0, 20))
        
        instructions = """
1. Select a programming language (Python or C)

2. Choose a module from the available lessons

3. Select your preferred lesson language

4. Click "Play Lesson" to start

5. Use voice commands during playback:
   • Say "stop" to end the lesson
   • Say "pause" to temporarily pause
   • Say "resume" to continue

6. You can return to this screen anytime
        """
        
        info_text = tk.Text(right_panel,
                           bg=self.colors['bg'],
                           fg=self.colors['text_secondary'],
                           font=('Segoe UI', 11),
                           wrap='word',
                           relief='flat',
                           padx=15,
                           pady=15,
                           height=15)
        info_text.pack(fill='both', expand=True)
        info_text.insert('1.0', instructions)
        info_text.config(state='disabled')
        
        # Bottom navigation
        nav_frame = ttk.Frame(main_frame, style='Main.TFrame')
        nav_frame.pack(side='bottom', fill='x', padx=40, pady=20)
        
        back_btn = ttk.Button(nav_frame,
                             text="← Back to Dashboard",
                             style='Secondary.TButton',
                             command=self.show_user_dashboard)
        back_btn.pack(side='left')
    
    def show_code_mode(self):
        """Display code mode interface"""
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        self.create_header(main_frame, "AI Code Mode",
                          "Write code with voice commands")
        
        content_frame = ttk.Frame(main_frame, style='Main.TFrame')
        content_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Top controls
        controls_frame = ttk.Frame(content_frame, style='Card.TFrame')
        controls_frame.pack(fill='x', pady=(0, 10))
        controls_frame.configure(padding=20)
        
        # Language selection
        lang_label = tk.Label(controls_frame,
                             text="Language:",
                             bg=self.colors['bg_light'],
                             fg=self.colors['text'],
                             font=('Segoe UI', 11))
        lang_label.pack(side='left', padx=(0, 10))
        
        lang_var = tk.StringVar()
        lang_combo = ttk.Combobox(controls_frame,
                                 textvariable=lang_var,
                                 values=self.SUPPORTED_LANGUAGES,
                                 state='readonly',
                                 width=15)
        lang_combo.pack(side='left', padx=(0, 20))
        lang_combo.set("python")
        
        # Project name
        project_label = tk.Label(controls_frame,
                                text="Project:",
                                bg=self.colors['bg_light'],
                                fg=self.colors['text'],
                                font=('Segoe UI', 11))
        project_label.pack(side='left', padx=(0, 10))
        
        project_entry = ttk.Entry(controls_frame, width=20)
        project_entry.pack(side='left', padx=(0, 20))
        project_entry.insert(0, "my_project")
        
        # File name
        file_label = tk.Label(controls_frame,
                             text="File:",
                             bg=self.colors['bg_light'],
                             fg=self.colors['text'],
                             font=('Segoe UI', 11))
        file_label.pack(side='left', padx=(0, 10))
        
        file_entry = ttk.Entry(controls_frame, width=20)
        file_entry.pack(side='left')
        file_entry.insert(0, "main")
        
        # Editor area
        editor_frame = ttk.Frame(content_frame, style='Card.TFrame')
        editor_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Line numbers frame
        line_numbers_frame = tk.Frame(editor_frame, bg=self.colors['bg'], width=40)
        line_numbers_frame.pack(side='left', fill='y')
        
        line_numbers = tk.Text(line_numbers_frame,
                              width=4,
                              bg=self.colors['bg'],
                              fg=self.colors['text_secondary'],
                              font=('Consolas', 11),
                              state='disabled',
                              relief='flat',
                              padx=5)
        line_numbers.pack(fill='y')
        
        # Code editor
        code_text = scrolledtext.ScrolledText(editor_frame,
                                             bg=self.colors['bg'],
                                             fg=self.colors['text'],
                                             font=('Consolas', 11),
                                             insertbackground=self.colors['accent'],
                                             selectbackground=self.colors['primary'],
                                             relief='flat',
                                             padx=10,
                                             pady=10,
                                             wrap='none')
        code_text.pack(side='left', fill='both', expand=True)
        
        def update_line_numbers(event=None):
            line_numbers.config(state='normal')
            line_numbers.delete(1.0, 'end')
            
            line_count = code_text.get(1.0, 'end-1c').count('\n') + 1
            line_nums = '\n'.join(str(i) for i in range(1, line_count + 1))
            line_numbers.insert(1.0, line_nums)
            line_numbers.config(state='disabled')
        
        code_text.bind('<KeyRelease>', update_line_numbers)
        update_line_numbers()
        
        # Control buttons
        button_frame = ttk.Frame(content_frame, style='Card.TFrame')
        button_frame.pack(fill='x', pady=(0, 10))
        button_frame.configure(padding=15)
        
        def start_listening():
            # TODO: Integrate with takeCommand() function
            messagebox.showinfo("Listening", "Microphone activated. Speak your command...")
        
        voice_btn = ttk.Button(button_frame,
                              text="🎤 Voice Command",
                              style='Primary.TButton',
                              command=start_listening)
        voice_btn.pack(side='left', padx=5)
        
        def execute_code():
            # TODO: Integrate with execute_code() function
            code = code_text.get(1.0, 'end-1c')
            output_text.delete(1.0, 'end')
            output_text.insert('end', "Executing code...\n\n")
            messagebox.showinfo("Execute", "Code execution started")
        
        run_btn = ttk.Button(button_frame,
                            text="▶ Run Code",
                            style='Secondary.TButton',
                            command=execute_code)
        run_btn.pack(side='left', padx=5)
        
        def clear_code():
            if messagebox.askyesno("Confirm", "Clear all code?"):
                code_text.delete(1.0, 'end')
                update_line_numbers()
        
        clear_btn = ttk.Button(button_frame,
                              text="🗑 Clear",
                              style='Secondary.TButton',
                              command=clear_code)
        clear_btn.pack(side='left', padx=5)
        
        def show_guide():
            guide_window = tk.Toplevel(self.root)
            guide_window.title("Voice Commands Guide")
            guide_window.geometry("600x500")
            guide_window.configure(bg=self.colors['bg'])
            
            guide_text_widget = scrolledtext.ScrolledText(guide_window,
                                                          bg=self.colors['bg_light'],
                                                          fg=self.colors['text'],
                                                          font=('Segoe UI', 10),
                                                          padx=20,
                                                          pady=20,
                                                          wrap='word')
            guide_text_widget.pack(fill='both', expand=True, padx=20, pady=20)
            
            guide_content = """
VOICE COMMANDS GUIDE

AI-POWERED CODING:
• Describe what you want in natural language
• "make a variable called x and set it to 5"
• "create a for loop"
• "print hello world"
• "define a function called calculate"
• "create an if statement to check if x is greater than 10"

EDITING COMMANDS:
• "delete line [number]" - Delete specific line
• "delete last line" - Remove the last line
• "clear all" - Clear entire file content
• "show code" - Display current code with line numbers

INDENTATION:
• "indent" - Increase indentation level
• "dedent" or "remove indent" - Decrease indentation level

EXECUTION:
• "execute" or "run" - Run your code
• "guide" - Show this help guide
• "exit" or "stop" - Exit code mode

EXAMPLES:

Python:
• "create a list called numbers"
• "add a while loop"
• "import numpy"

C:
• "include stdio header"
• "declare an integer variable named count"
• "create a printf statement"
            """
            
            guide_text_widget.insert('1.0', guide_content)
            guide_text_widget.config(state='disabled')
        
        guide_btn = ttk.Button(button_frame,
                              text="📖 Guide",
                              style='Secondary.TButton',
                              command=show_guide)
        guide_btn.pack(side='left', padx=5)
        
        # Output console
        output_label = tk.Label(content_frame,
                               text="Output Console:",
                               bg=self.colors['bg'],
                               fg=self.colors['text'],
                               font=('Segoe UI', 11, 'bold'),
                               anchor='w')
        output_label.pack(fill='x', pady=(10, 5))
        
        output_text = scrolledtext.ScrolledText(content_frame,
                                               bg=self.colors['bg'],
                                               fg='#00ff00',
                                               font=('Consolas', 10),
                                               height=8,
                                               relief='flat',
                                               padx=10,
                                               pady=10)
        output_text.pack(fill='x')
        output_text.insert('end', "Ready for code execution...\n")
        
        # Bottom navigation
        nav_frame = ttk.Frame(main_frame, style='Main.TFrame')
        nav_frame.pack(side='bottom', fill='x', padx=40, pady=20)
        
        back_btn = ttk.Button(nav_frame,
                             text="← Back to Dashboard",
                             style='Secondary.TButton',
                             command=self.show_user_dashboard)
        back_btn.pack(side='left')
    
    def process_queue(self):
        """Process message queue for thread-safe GUI updates"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                # Handle messages here
                print(message)
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)


def main():
    """Launch the application"""
    root = tk.Tk()
    app = ModernVoiceCodingPlatform(root)
    root.mainloop()


if __name__ == "__main__":
    main()
