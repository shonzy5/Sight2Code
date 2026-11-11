"""
Voice-Controlled Coding Platform for Visually Impaired Users
Main Application Entry Point
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock
import json
import os
from threading import Thread

# Import custom modules
from voice_utils import speak, takeCommand
from admin_panel import AdminPanel
from user_panel import UserPanel
from code_interpreter import CodeInterpreter
# Set window size
Window.size = (800, 600)

class WelcomeScreen(Screen):
    """Initial dashboard with Admin/User options"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # Welcome message
        title = Label(
            text='Voice Coding Platform',
            font_size='32sp',
            size_hint=(1, 0.2),
            bold=True
        )
        
        subtitle = Label(
            text='Accessible Coding for Everyone',
            font_size='20sp',
            size_hint=(1, 0.1)
        )
        
        # Buttons
        btn_layout = BoxLayout(orientation='vertical', spacing=15, size_hint=(1, 0.7))
        
        self.admin_btn = Button(
            text='ADMIN',
            font_size='24sp',
            size_hint=(1, 0.5),
            background_color=(0.2, 0.6, 0.8, 1)
        )
        self.admin_btn.bind(on_press=self.go_to_admin)
        
        self.user_btn = Button(
            text='USER',
            font_size='24sp',
            size_hint=(1, 0.5),
            background_color=(0.2, 0.8, 0.6, 1)
        )
        self.user_btn.bind(on_press=self.go_to_user)
        
        btn_layout.add_widget(self.admin_btn)
        btn_layout.add_widget(self.user_btn)
        
        self.layout.add_widget(title)
        self.layout.add_widget(subtitle)
        self.layout.add_widget(btn_layout)
        
        self.add_widget(self.layout)
        
        # Speak welcome message on startup
        Clock.schedule_once(self.welcome_message, 0.5)
    
    def welcome_message(self, dt):
        Thread(target=lambda: speak("Welcome to Voice Coding Platform. Say Admin or User to continue.")).start()
    
    def go_to_admin(self, instance):
        Thread(target=lambda: speak("Opening Admin Panel")).start()
        self.manager.current = 'admin_login'
    
    def go_to_user(self, instance):
        Thread(target=lambda: speak("Opening User Panel")).start()
        self.manager.current = 'user_login'


class AdminLoginScreen(Screen):
    """Admin authentication screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        title = Label(text='Admin Login', font_size='28sp', size_hint=(1, 0.15))
        
        # Username
        username_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        username_layout.add_widget(Label(text='Username:', size_hint=(0.3, 1)))
        self.username_input = TextInput(multiline=False, size_hint=(0.7, 1))
        username_layout.add_widget(self.username_input)
        
        # Password
        password_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        password_layout.add_widget(Label(text='Password:', size_hint=(0.3, 1)))
        self.password_input = TextInput(multiline=False, password=True, size_hint=(0.7, 1))
        password_layout.add_widget(self.password_input)
        
        # Buttons
        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        
        login_btn = Button(text='Login', background_color=(0.2, 0.8, 0.6, 1))
        login_btn.bind(on_press=self.login)
        
        back_btn = Button(text='Back', background_color=(0.8, 0.2, 0.2, 1))
        back_btn.bind(on_press=self.go_back)
        
        btn_layout.add_widget(login_btn)
        btn_layout.add_widget(back_btn)
        
        self.message_label = Label(text='', size_hint=(1, 0.1), color=(1, 0, 0, 1))
        
        self.layout.add_widget(title)
        self.layout.add_widget(username_layout)
        self.layout.add_widget(password_layout)
        self.layout.add_widget(btn_layout)
        self.layout.add_widget(self.message_label)
        
        self.add_widget(self.layout)
    
    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        # Simple authentication (in production, use proper security)
        if username == 'admin' and password == '1234':
            Thread(target=lambda: speak("Login successful. Welcome Admin.")).start()
            self.manager.current = 'admin_panel'
        else:
            self.message_label.text = 'Invalid credentials'
            Thread(target=lambda: speak("Invalid credentials. Please try again.")).start()
    
    def go_back(self, instance):
        self.manager.current = 'welcome'


class UserLoginScreen(Screen):
    """User voice-based login screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        title = Label(text='User Voice Login', font_size='28sp', size_hint=(1, 0.2))
        
        self.status_label = Label(
            text='Press "Start Voice Login" or say your name',
            font_size='18sp',
            size_hint=(1, 0.3)
        )
        
        # Buttons
        btn_layout = BoxLayout(size_hint=(1, 0.3), spacing=10)
        
        voice_btn = Button(text='Start Voice Login', background_color=(0.2, 0.8, 0.6, 1))
        voice_btn.bind(on_press=self.voice_login)
        
        back_btn = Button(text='Back', background_color=(0.8, 0.2, 0.2, 1))
        back_btn.bind(on_press=self.go_back)
        
        btn_layout.add_widget(voice_btn)
        btn_layout.add_widget(back_btn)
        
        self.layout.add_widget(title)
        self.layout.add_widget(self.status_label)
        self.layout.add_widget(btn_layout)
        
        self.add_widget(self.layout)
    
    def voice_login(self, instance):
        Thread(target=self.process_voice_login).start()
    
    def process_voice_login(self):
        speak("Please say your name")
        name = takeCommand()
        
        if name and name.lower() != "none":
            speak(f"Welcome {name}. Logging you in.")
            Clock.schedule_once(lambda dt: self.login_success(name), 0)
        else:
            speak("Could not recognize your voice. Please try again.")
    
    def login_success(self, name):
        # Store user info in app
        app = App.get_running_app()
        app.current_user = name
        self.manager.current = 'user_panel'
    
    def go_back(self, instance):
        self.manager.current = 'welcome'


class AdminPanelScreen(Screen):
    """Admin dashboard for managing lessons"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.admin_panel = AdminPanel()
        self.add_widget(self.admin_panel)
        
        # Add back button
        back_btn = Button(
            text='Logout',
            size_hint=(0.2, 0.08),
            pos_hint={'x': 0.75, 'y': 0.9},
            background_color=(0.8, 0.2, 0.2, 1)
        )
        back_btn.bind(on_press=self.logout)
        self.add_widget(back_btn)
    
    def logout(self, instance):
        Thread(target=lambda: speak("Logging out")).start()
        self.manager.current = 'welcome'


class UserPanelScreen(Screen):
    """User dashboard with Learn/Code options"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_panel = UserPanel()
        self.add_widget(self.user_panel)
        
        # Add back button
        back_btn = Button(
            text='Logout',
            size_hint=(0.2, 0.08),
            pos_hint={'x': 0.75, 'y': 0.9},
            background_color=(0.8, 0.2, 0.2, 1)
        )
        back_btn.bind(on_press=self.logout)
        self.add_widget(back_btn)
    
    def logout(self, instance):
        Thread(target=lambda: speak("Logging out. Goodbye!")).start()
        self.manager.current = 'welcome'


class VoiceCodeApp(App):
    """Main application class"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = [
            'data',
            'data/lessons',
            'data/lessons/Python',
            'data/lessons/C',
            'data/code_sessions'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        # Create sample module structure
        for lang in ['Python', 'C']:
            for i in range(1, 6):
                module_path = f'data/lessons/{lang}/Module{i}'
                os.makedirs(module_path, exist_ok=True)
    
    def build(self):
        # Create screen manager
        sm = ScreenManager()
        
        # Add screens
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(AdminLoginScreen(name='admin_login'))
        sm.add_widget(UserLoginScreen(name='user_login'))
        sm.add_widget(AdminPanelScreen(name='admin_panel'))
        sm.add_widget(UserPanelScreen(name='user_panel'))
        
        return sm


if __name__ == '__main__':
    VoiceCodeApp().run()