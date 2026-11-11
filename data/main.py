import speech_recognition as sr
import requests
import os
import subprocess
import sys
import time
import uuid
from typing import Union
from threading import Lock
import pygame

# Initialize pygame mixer for audio playback
pygame.mixer.init()
audio_lock = Lock()

# Configuration
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"
SUPPORTED_LANGUAGES = ["python", "c"]
CODE_SESSIONS_DIR = "code_sessions"
LESSONS_DIR = "lessons"

# Ensure necessary directories exist
os.makedirs(CODE_SESSIONS_DIR, exist_ok=True)
os.makedirs(LESSONS_DIR, exist_ok=True)

def generate_audio(message: str, voice: str = "Brian"):
    """Generate audio content from text using StreamElements API"""
    url = f"https://api.streamelements.com/kappa/v2/speech?voice={voice}&text={{{message}}}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        result = requests.get(url=url, headers=headers, timeout=10)
        if result.status_code == 200:
            return result.content
    except Exception as e:
        print(f"Error generating audio: {e}")
    return None

def speak(message: str, voice: str = 'Brian') -> None:
    """Speak a message using text-to-speech with thread-safe audio playback"""
    print(f"[SPEAKING]: {message}")
    
    with audio_lock:
        try:
            # Generate unique filename to avoid conflicts
            file_path = f"temp_audio_{uuid.uuid4().hex}.mp3"
            
            result_content = generate_audio(message, voice)
            if result_content is None:
                print("Failed to generate audio")
                return
            
            # Write audio file
            with open(file_path, "wb") as file:
                file.write(result_content)
            
            # Play using pygame
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Clean up
            pygame.mixer.music.unload()
            time.sleep(0.2)  # Small delay to ensure file is released
            
            if os.path.exists(file_path):
                os.remove(file_path)
                
        except Exception as e:
            print(f"Error in speak function: {e}")
            # Try to clean up file even on error
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass

def takeCommand():
    """Listen to user's voice command and convert to text"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening.....")
        r.pause_threshold = 1
        r.energy_threshold = 300
        r.non_speaking_duration = 0.7
        r.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("Listening timed out")
            return "None"
    
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
        return query.lower()
    except Exception as e:
        print("Say that again Please...")
        return "None"

def admin_panel():
    """Admin panel for managing lessons"""
    speak("Admin panel. Please enter username.")
    username = input("Username: ")
    
    speak("Please enter password.")
    password = input("Password: ")
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        speak("Login successful. Welcome to admin panel.")
        print("\n=== ADMIN PANEL ===")
        print("Here you can manage lessons and categories.")
        print(f"Lessons directory: {LESSONS_DIR}")
        print(f"Current structure: lessons/[language]/[module]/[audio_files]")
        speak("Admin functions available. You can now manage lessons in the lessons directory.")
    else:
        speak("Invalid credentials. Access denied.")

def get_available_modules(language):
    """Get available modules for a language"""
    lang_path = os.path.join(LESSONS_DIR, language)
    if not os.path.exists(lang_path):
        return []
    
    modules = [d for d in os.listdir(lang_path) 
               if os.path.isdir(os.path.join(lang_path, d))]
    return sorted(modules)

def get_available_lesson_languages(language, module):
    """Get available lesson audio languages"""
    module_path = os.path.join(LESSONS_DIR, language, module)
    if not os.path.exists(module_path):
        return []
    
    languages = [f.replace('.m4a', '') for f in os.listdir(module_path) 
                 if f.endswith('.m4a')]
    return languages

def play_lesson(language, module, lesson_lang):
    """Play the lesson audio file"""
    lesson_path = os.path.join(LESSONS_DIR, language, module, f"{lesson_lang}.m4a")
    
    if not os.path.exists(lesson_path):
        speak(f"Lesson file not found at {lesson_path}")
        return
    
    speak(f"Playing {module} lesson in {lesson_lang}. Say stop to end the lesson.")
    
    try:
        # Play using pygame for m4a files (if supported) or use system player
        if sys.platform == "win32":
            os.startfile(lesson_path)
        elif sys.platform == "darwin":
            subprocess.run(["afplay", lesson_path])
        else:
            subprocess.run(["xdg-open", lesson_path])
    except Exception as e:
        speak(f"Error playing lesson: {str(e)}")

def learn_mode(username):
    """Handle learning mode"""
    speak(f"Welcome to learn mode, {username}. Which language do you want to learn? Say Python or C.")
    
    while True:
        lang_choice = takeCommand()
        
        if lang_choice == "none":
            speak("I didn't catch that. Please say Python or C.")
            continue
        
        if "python" in lang_choice:
            language = "python"
            break
        elif "c" in lang_choice or lang_choice == "c":
            language = "c"
            break
        else:
            speak("This language is not uploaded yet. Please choose Python or C.")
    
    # Get available modules
    modules = get_available_modules(language)
    
    if not modules:
        speak(f"No modules available for {language} yet.")
        return
    
    speak(f"Available modules are: {', '.join(modules)}. Which module do you want to learn?")
    
    while True:
        module_choice = takeCommand()
        
        if module_choice == "none":
            speak("Please say the module number or name.")
            continue
        
        # Try to match module
        selected_module = None
        for module in modules:
            if module.lower() in module_choice or module_choice in module.lower():
                selected_module = module
                break
        
        if selected_module:
            break
        else:
            speak(f"Module not found. Available modules are: {', '.join(modules)}")
    
    # Get available lesson languages
    lesson_langs = get_available_lesson_languages(language, selected_module)
    
    if not lesson_langs:
        speak("No lessons available for this module yet.")
        return
    
    speak(f"Available languages are: {', '.join(lesson_langs)}. Which language do you prefer?")
    
    while True:
        lang_pref = takeCommand()
        
        if lang_pref == "none":
            speak("Please say your preferred language.")
            continue
        
        # Match lesson language
        selected_lang = None
        for ll in lesson_langs:
            if ll.lower() in lang_pref or lang_pref in ll.lower():
                selected_lang = ll
                break
        
        if selected_lang:
            play_lesson(language, selected_module, selected_lang)
            break
        else:
            speak(f"Language not available. Choose from: {', '.join(lesson_langs)}")

def parse_voice_to_code(voice_input, language):
    """Convert voice command to actual code"""
    voice_input = voice_input.lower().strip()
    
    if language == "python":
        # Print statements
        if "print" in voice_input:
            content = voice_input.replace("print", "").strip()
            return f'print("{content}")'
        
        # Variable assignment
        if "equals" in voice_input or "=" in voice_input:
            parts = voice_input.replace("equals", "=").split("=")
            if len(parts) == 2:
                var_name = parts[0].strip().replace(" ", "_")
                value = parts[1].strip()
                return f'{var_name} = {value}'
        
        # If statement
        if voice_input.startswith("if "):
            condition = voice_input.replace("if ", "").strip()
            return f'if {condition}:'
        
        # For loop
        if "for loop" in voice_input or voice_input.startswith("for "):
            return "for i in range():"
        
        # While loop
        if voice_input.startswith("while "):
            condition = voice_input.replace("while ", "").strip()
            return f'while {condition}:'
        
        # Function definition
        if "define function" in voice_input or "def " in voice_input:
            func_name = voice_input.replace("define function", "").replace("def", "").strip().replace(" ", "_")
            return f'def {func_name}():'
        
        # Import statement
        if "import" in voice_input:
            return voice_input
        
        # Return statement
        if voice_input.startswith("return "):
            value = voice_input.replace("return ", "").strip()
            return f'return {value}'
    
    elif language == "c":
        # Printf statements
        if "print" in voice_input or "printf" in voice_input:
            content = voice_input.replace("print", "").replace("printf", "").strip()
            return f'printf("{content}\\n");'
        
        # Variable declaration
        if "integer" in voice_input or "int " in voice_input:
            var_name = voice_input.replace("integer", "").replace("int", "").strip().replace(" ", "_")
            return f'int {var_name};'
        
        # If statement
        if voice_input.startswith("if "):
            condition = voice_input.replace("if ", "").strip()
            return f'if ({condition}) {{'
        
        # For loop
        if "for loop" in voice_input:
            return 'for (int i = 0; i < n; i++) {'
        
        # While loop
        if voice_input.startswith("while "):
            condition = voice_input.replace("while ", "").strip()
            return f'while ({condition}) {{'
        
        # Include statement
        if "include" in voice_input:
            if "stdio" in voice_input:
                return '#include <stdio.h>'
            elif "stdlib" in voice_input:
                return '#include <stdlib.h>'
    
    # Return original if no pattern matched
    return f"// {voice_input}"

def execute_code(file_path, language):
    """Execute the code file and return output"""
    try:
        if language == "python":
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
        elif language == "c":
            # Compile first
            exe_path = file_path.replace('.c', '.exe')
            compile_result = subprocess.run(
                ['gcc', file_path, '-o', exe_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if compile_result.returncode != 0:
                return f"Compilation error: {compile_result.stderr}"
            
            # Execute
            result = subprocess.run(
                [exe_path],
                capture_output=True,
                text=True,
                timeout=10
            )
        else:
            return "Unsupported language"
        
        if result.returncode == 0:
            return f"Output: {result.stdout}" if result.stdout else "Program executed successfully with no output"
        else:
            return f"Error: {result.stderr}"
    
    except subprocess.TimeoutExpired:
        return "Execution timed out"
    except Exception as e:
        return f"Execution error: {str(e)}"

def code_mode(username):
    """Handle coding mode"""
    speak(f"Welcome to code mode, {username}. Which language do you want to code in? Say Python or C.")
    
    while True:
        lang_choice = takeCommand()
        
        if lang_choice == "none":
            speak("Please say the language name.")
            continue
        
        if "python" in lang_choice:
            language = "python"
            file_ext = ".py"
            break
        elif "c" in lang_choice or lang_choice == "c":
            language = "c"
            file_ext = ".c"
            break
        else:
            speak("Language not supported. Please choose Python or C.")
    
    speak("You can work on a current project by saying 'open' followed by project name, or say 'create new project'.")
    
    while True:
        project_choice = takeCommand()
        
        if project_choice == "none":
            continue
        
        if "create new" in project_choice or "new project" in project_choice:
            # Create new project
            project_name = f"project_{int(time.time())}"
            project_path = os.path.join(CODE_SESSIONS_DIR, project_name)
            os.makedirs(project_path, exist_ok=True)
            speak(f"New project created: {project_name}")
            break
        elif "open" in project_choice:
            # Extract project name
            proj_name = project_choice.replace("open", "").strip().replace(" ", "_")
            project_path = os.path.join(CODE_SESSIONS_DIR, proj_name)
            
            if os.path.exists(project_path):
                speak(f"Opening project: {proj_name}")
                break
            else:
                speak("Project not found. Say 'create new project' to create one.")
        else:
            speak("Say 'open project name' or 'create new project'.")
    
    # Open VS Code in project directory
    try:
        subprocess.Popen(['code', project_path])
        speak("VS Code opened in your project directory.")
    except:
        speak("Could not open VS Code. Please open it manually.")
    
    # Ask for file name
    speak("What file name do you wish? Say the name without extension.")
    
    while True:
        file_name = takeCommand()
        if file_name != "none":
            file_name = file_name.replace(" ", "_")
            break
    
    file_path = os.path.join(project_path, f"{file_name}{file_ext}")
    
    # Create file
    with open(file_path, "w") as f:
        if language == "c":
            f.write("#include <stdio.h>\n\nint main() {\n    \n    return 0;\n}\n")
        else:
            f.write("")
    
    speak(f"File {file_name}{file_ext} created. Say 'edit' to start working on the file.")
    
    # Wait for edit command
    while True:
        cmd = takeCommand()
        if "edit" in cmd:
            break
    
    speak("You can now dictate your code. Say 'execute' to run the code, or 'exit' to stop editing.")
    
    # Coding loop
    while True:
        voice_input = takeCommand()
        
        if voice_input == "none":
            continue
        
        if "exit" in voice_input or "stop" in voice_input:
            speak("Exiting code mode.")
            break
        
        if "execute" in voice_input or "run" in voice_input:
            speak("Executing your code.")
            output = execute_code(file_path, language)
            speak(output)
            continue
        
        # Convert voice to code
        code_line = parse_voice_to_code(voice_input, language)
        
        # Append to file
        with open(file_path, "a") as f:
            f.write(code_line + "\n")
        
        speak(f"Added: {code_line}")

def user_mode():
    """Handle user mode"""
    speak("Welcome to user mode. What is your name?")
    
    username = takeCommand()
    if username == "none":
        username = "User"
    
    speak(f"Hello {username}, what do you wish to do? Say 'learn' or 'code'.")
    
    while True:
        choice = takeCommand()
        
        if choice == "none":
            speak("Please say 'learn' or 'code'.")
            continue
        
        if "learn" in choice:
            learn_mode(username)
            speak("Do you want to continue? Say 'yes' or 'no'.")
            cont = takeCommand()
            if "no" in cont or "exit" in cont:
                break
        elif "code" in choice:
            code_mode(username)
            speak("Do you want to continue? Say 'yes' or 'no'.")
            cont = takeCommand()
            if "no" in cont or "exit" in cont:
                break
        else:
            speak("Invalid choice. Please say 'learn' or 'code'.")

def main():
    """Main application entry point"""
    speak("Welcome to the Voice-Controlled Coding Platform. Say 'admin' for admin panel or 'user' for user mode.")
    
    while True:
        choice = takeCommand()
        
        if choice == "none":
            speak("Please say 'admin' or 'user'.")
            continue
        
        if "admin" in choice:
            admin_panel()
            break
        elif "user" in choice:
            user_mode()
            break
        else:
            speak("Invalid choice. Please say 'admin' or 'user'.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        speak("Shutting down. Goodbye!")
    except Exception as e:
        print(f"Fatal error: {e}")
        speak("An error occurred. Please restart the application.")