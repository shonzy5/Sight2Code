"""
Admin Panel for Managing Programming Lessons
Allows uploading and organizing audio lessons by language and module
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
import os
import shutil
from threading import Thread
from voice_utils import speak


class AdminPanel(BoxLayout):
    """Admin interface for lesson management"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        
        # Title
        title = Label(
            text='Admin Panel - Lesson Management',
            font_size='24sp',
            size_hint=(1, 0.1),
            bold=True
        )
        self.add_widget(title)
        
        # Language selection
        lang_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        lang_layout.add_widget(Label(text='Programming Language:', size_hint=(0.3, 1)))
        
        self.lang_input = TextInput(
            text='Python',
            multiline=False,
            size_hint=(0.5, 1)
        )
        lang_layout.add_widget(self.lang_input)
        
        self.add_widget(lang_layout)
        
        # Module selection
        module_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        module_layout.add_widget(Label(text='Module Number (1-5):', size_hint=(0.3, 1)))
        
        self.module_input = TextInput(
            text='1',
            multiline=False,
            size_hint=(0.5, 1)
        )
        module_layout.add_widget(self.module_input)
        
        self.add_widget(module_layout)
        
        # Audio language selection
        audio_lang_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        audio_lang_layout.add_widget(Label(text='Audio Language:', size_hint=(0.3, 1)))
        
        self.audio_lang_input = TextInput(
            text='English',
            multiline=False,
            size_hint=(0.5, 1)
        )
        audio_lang_layout.add_widget(self.audio_lang_input)
        
        self.add_widget(audio_lang_layout)
        
        # Upload button
        upload_btn = Button(
            text='Upload Audio Lesson',
            size_hint=(1, 0.1),
            background_color=(0.2, 0.7, 0.9, 1)
        )
        upload_btn.bind(on_press=self.open_file_chooser)
        self.add_widget(upload_btn)
        
        # Status message
        self.status_label = Label(
            text='',
            size_hint=(1, 0.1),
            color=(0, 1, 0, 1)
        )
        self.add_widget(self.status_label)
        
        # Lesson overview
        overview_title = Label(
            text='Current Lessons:',
            font_size='20sp',
            size_hint=(1, 0.08),
            bold=True
        )
        self.add_widget(overview_title)
        
        # Scrollable lesson list
        scroll = ScrollView(size_hint=(1, 0.42))
        self.lesson_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.lesson_grid.bind(minimum_height=self.lesson_grid.setter('height'))
        scroll.add_widget(self.lesson_grid)
        self.add_widget(scroll)
        
        # Refresh lessons
        self.refresh_lessons()
    
    def open_file_chooser(self, instance):
        """Open file chooser dialog"""
        content = BoxLayout(orientation='vertical')
        
        file_chooser = FileChooserListView(
            filters=['*.m4a', '*.mp3', '*.wav'],
            path=os.path.expanduser('~')
        )
        
        btn_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        select_btn = Button(text='Select')
        cancel_btn = Button(text='Cancel')
        
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(file_chooser)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Select Audio File',
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        def select_file(instance):
            if file_chooser.selection:
                self.upload_lesson(file_chooser.selection[0])
            popup.dismiss()
        
        select_btn.bind(on_press=select_file)
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def upload_lesson(self, file_path):
        """Upload lesson file to appropriate directory"""
        try:
            lang = self.lang_input.text.strip()
            module_num = self.module_input.text.strip()
            audio_lang = self.audio_lang_input.text.strip()
            
            if not lang or not module_num or not audio_lang:
                self.status_label.text = 'Please fill all fields'
                self.status_label.color = (1, 0, 0, 1)
                return
            
            # Create destination path
            dest_dir = f'data/lessons/{lang}/Module{module_num}'
            os.makedirs(dest_dir, exist_ok=True)
            
            # Get file extension
            _, ext = os.path.splitext(file_path)
            dest_file = os.path.join(dest_dir, f'{audio_lang}{ext}')
            
            # Copy file
            shutil.copy2(file_path, dest_file)
            
            self.status_label.text = f'Uploaded: {lang}/Module{module_num}/{audio_lang}{ext}'
            self.status_label.color = (0, 1, 0, 1)
            
            Thread(target=lambda: speak(f"Lesson uploaded successfully for {lang}, Module {module_num}, {audio_lang}")).start()
            
            # Refresh lesson list
            self.refresh_lessons()
            
        except Exception as e:
            self.status_label.text = f'Error: {str(e)}'
            self.status_label.color = (1, 0, 0, 1)
            Thread(target=lambda: speak("Upload failed. Please check the details and try again.")).start()
    
    def refresh_lessons(self):
        """Refresh the lesson overview"""
        self.lesson_grid.clear_widgets()
        
        lessons_dir = 'data/lessons'
        
        if not os.path.exists(lessons_dir):
            return
        
        # List all languages
        for lang in os.listdir(lessons_dir):
            lang_path = os.path.join(lessons_dir, lang)
            
            if not os.path.isdir(lang_path):
                continue
            
            # Language header
            lang_label = Label(
                text=f'\n{lang}:',
                size_hint_y=None,
                height=40,
                bold=True,
                color=(0.3, 0.7, 1, 1)
            )
            self.lesson_grid.add_widget(lang_label)
            
            # List modules
            modules = sorted([m for m in os.listdir(lang_path) if os.path.isdir(os.path.join(lang_path, m))])
            
            for module in modules:
                module_path = os.path.join(lang_path, module)
                files = os.listdir(module_path)
                
                if files:
                    file_list = ', '.join([f.replace('.m4a', '').replace('.mp3', '').replace('.wav', '') for f in files])
                    module_label = Label(
                        text=f'  {module}: {file_list}',
                        size_hint_y=None,
                        height=30
                    )
                    self.lesson_grid.add_widget(module_label)