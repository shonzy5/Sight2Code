"""
User Panel for Learning and Coding
Voice-controlled interface for playing lessons and writing code
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from threading import Thread
import os
from voice_utils import speak, takeCommand
from code_interpreter import CodeInterpreter
from playsound import playsound
import subprocess


class UserPanel(BoxLayout):
    """User interface for learning and coding"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        self.code_interpreter = CodeInterpreter()
        self.is_listening = False
        self.current_mode = None
        
        # Welcome and name input
        self.welcome_user()
    
    def welcome_user(self):
        speak("Welcome! What is your name?")
        name = takeCommand()
        speak(f"Hello {name}, what do you wish to do? Say 'learn' or 'code'.")
        command = takeCommand()
        if "learn" in command.lower():
            self.start_learn_mode()
        elif "code" in command.lower():
            self.start_code_mode()
        else:
            speak("Invalid choice. Please say 'learn' or 'code'.")
            self.welcome_user()

    def start_learn_mode(self):
        """Enter learning mode"""
        self.current_mode = 'learn'
        Thread(target=self.learn_flow).start()
    
    def learn_flow(self):
        """Voice-guided learning flow"""
        speak("Learning mode activated. Which programming language would you like to learn? Python or C?")
        
        lang_choice = takeCommand()
        
        if lang_choice and lang_choice.lower() != "none":
            if "python" in lang_choice.lower():
                self.selected_language = "Python"
            elif "c" in lang_choice.lower() or "see" in lang_choice.lower():
                self.selected_language = "C"
            else:
                speak("Language not recognized. Please say Python or C.")
                return
            
            speak(f"{self.selected_language} selected. Which module would you like? Say module 1 to 5.")
            
            module_choice = takeCommand()
            
            if module_choice and module_choice.lower() != "none":
                # Extract number from speech
                for i in range(1, 6):
                    if str(i) in module_choice or self.number_to_word(i) in module_choice.lower():
                        self.selected_module = f"Module{i}"
                        break
                
                if not self.selected_module:
                    speak("Module not recognized. Please try again.")
                    return
                
                speak(f"Module {self.selected_module.replace('Module', '')} selected. Which language? Hindi, Marathi, or English?")
                
                audio_lang_choice = takeCommand()
                
                if audio_lang_choice and audio_lang_choice.lower() != "none":
                    if "hindi" in audio_lang_choice.lower():
                        self.selected_audio_lang = "Hindi"
                    elif "marathi" in audio_lang_choice.lower():
                        self.selected_audio_lang = "Marathi"
                    elif "english" in audio_lang_choice.lower():
                        self.selected_audio_lang = "English"
                    else:
                        speak("Audio language not recognized.")
                        return
                    
                    # Play the lesson
                    self.play_lesson()
    
    def play_lesson(self):
        """Play the selected lesson audio"""
        lesson_path = f"data/lessons/{self.selected_language}/{self.selected_module}"
        
        if not os.path.exists(lesson_path):
            speak("Lesson not found. Please contact admin to upload this lesson.")
            return
        
        # Find audio file
        audio_files = [f for f in os.listdir(lesson_path) if f.startswith(self.selected_audio_lang)]
        
        if not audio_files:
            speak("Audio file not found for this lesson.")
            return
        
        audio_path = os.path.join(lesson_path, audio_files[0])
        
        speak(f"Playing lesson: {self.selected_language}, {self.selected_module}, in {self.selected_audio_lang}")
        
        try:
            playsound(audio_path)
            speak("Lesson completed. Would you like to hear another lesson?")
        except Exception as e:
            speak("Error playing audio file.")
            print(f"Error: {e}")
    
    def start_code_mode(self):
        """Enter coding mode"""
        self.current_mode = 'code'
        Thread(target=self.code_flow).start()
    
    def code_flow(self):
        """Voice-guided coding flow"""
        speak("Coding mode activated. You can dictate your code now. Say your code line by line. Say 'stop coding' when done.")
        
        Clock.schedule_once(lambda dt: self.update_status("Listening for code..."), 0)
        
        while self.current_mode == 'code':
            command = takeCommand()
            
            if command and command.lower() != "none":
                if "stop coding" in command.lower() or "exit" in command.lower():
                    speak("Exiting coding mode.")
                    self.current_mode = None
                    break
                
                # Interpret the command as code
                code_line = self.code_interpreter.interpret(command)
                
                if code_line:
                    Clock.schedule_once(lambda dt: self.append_code(code_line), 0)
                    speak(f"Added: {command}")
    
    def listen_command(self, instance):
        """Listen for a single voice command"""
        Thread(target=self.process_voice_command).start()
    
    def process_voice_command(self):
        """Process voice command"""
        speak("Listening for command")
        command = takeCommand()
        
        if command and command.lower() != "none":
            Clock.schedule_once(lambda dt: self.update_status(f"You said: {command}"), 0)
            
            if "learn" in command.lower():
                self.start_learn_mode(None)
            elif "code" in command.lower():
                self.start_code_mode(None)
            elif "run" in command.lower():
                self.run_code(None)
            elif "clear" in command.lower():
                self.clear_editor(None)
            else:
                speak("Command not recognized. Say Learn, Code, Run, or Clear.")
    
    def append_code(self, code_line):
        """Append code to editor"""
        current_code = self.code_editor.text
        self.code_editor.text = current_code + code_line + "\n"
    
    def run_code(self, instance):
        """Execute the code"""
        code = self.code_editor.text
        
        if not code.strip():
            self.output_display.text = "No code to run"
            Thread(target=lambda: speak("No code to run")).start()
            return
        
        Thread(target=lambda: speak("Running your code")).start()
        
        # Execute code
        output = self.code_interpreter.execute(code)
        self.output_display.text = output
        
        # Speak output
        Thread(target=lambda: speak(f"Output: {output}")).start()
    
    def clear_editor(self, instance):
        """Clear the code editor"""
        self.code_editor.text = ""
        self.output_display.text = ""
        Thread(target=lambda: speak("Editor cleared")).start()
    
    def save_code(self, instance):
        """Save code to file"""
        code = self.code_editor.text
        
        if not code.strip():
            Thread(target=lambda: speak("No code to save")).start()
            return
        
        # Create filename
        import time
        filename = f"data/code_sessions/code_{int(time.time())}.py"
        
        with open(filename, 'w') as f:
            f.write(code)
        
        self.output_display.text = f"Saved as: {filename}"
        Thread(target=lambda: speak("Code saved successfully")).start()
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.text = message
    
    @staticmethod
    def number_to_word(num):
        """Convert number to word"""
        numbers = {
            1: "one", 2: "two", 3: "three",
            4: "four", 5: "five"
        }
        return numbers.get(num, "")
    
    def select_module(self, language):
        speak(f"You selected {language}. Which module would you like to learn? Say module 1 to 5.")
        module_choice = takeCommand()
        # Logic to play lesson based on module choice
        self.play_lesson(language, module_choice)

    def create_project(self, lang_choice):
        speak("Would you like to create a new project or open an existing one?")
        command = takeCommand()
        if "create" in command.lower():
            self.create_new_project()
        elif "open" in command.lower():
            self.open_existing_project()
        else:
            speak("Invalid choice. Please say 'create' or 'open'.")

    def create_new_project(self):
        speak("What is the name of your project?")
        project_name = takeCommand()
        project_path = f"data/code_sessions/{project_name}"
        os.makedirs(project_path, exist_ok=True)
        speak(f"Project {project_name} created. What file name do you wish to create?")
        file_name = takeCommand()
        speak("What language is it?")
        lang_choice = takeCommand()
        if "python" in lang_choice.lower():
            file_path = os.path.join(project_path, f"{file_name}.py")
        elif "c" in lang_choice.lower():
            file_path = os.path.join(project_path, f"{file_name}.c")
        else:
            speak("Invalid language. Please say Python or C.")
            return
        
        # Open VS Code in the project directory
        subprocess.Popen(["code", project_path])
        speak("You can start editing your file. Say 'edit' to begin.")