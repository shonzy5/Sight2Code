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
import re
from playsound import playsound, PlaysoundException
import threading
import customtkinter as ctk
from tkinter import messagebox
from interfaceAd import Sight2CodeDashboard

# -------------------------------------------------
# GLOBAL PLAYBACK STATE
# -------------------------------------------------
_current_lesson_thread: Union[threading.Thread, None] = None

# Initialize pygame mixer for audio playback
pygame.mixer.init()
audio_lock = Lock()

# Configuration
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"
SUPPORTED_LANGUAGES = ["python", "c"]
BASE_USERS_DIR = "users"
LESSONS_DIR = "lessons"
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise RuntimeError("Set the MISTRAL_API_KEY environment variable")
MODEL_URL = 'https://api.mistral.ai/v1/chat/completions'

# Ensure necessary directories exist
os.makedirs(BASE_USERS_DIR, exist_ok=True)
os.makedirs(LESSONS_DIR, exist_ok=True)

# Set appearance for CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Color scheme - Light subtle theme
COLORS = {
    "primary": "#6366f1",        # Soft indigo
    "secondary": "#3b82f6",      # Soft blue
    "success": "#10b981",        # Soft green
    "warning": "#f59e0b",        # Soft orange
    "danger": "#ef4444",         # Soft red
    "dark_bg": "#ffffff",        # White background
    "card_bg": "#f8fafc",        # Very light gray/off-white
    "text_primary": "#1e293b",   # Dark text for light background
    "text_secondary": "#64748b", # Medium gray text
    "border": "#e2e8f0",         # Light border
    "hover": "#f1f5f9",          # Light hover background
}

# -------------------------------------------------
# INDENTATION HELPER FOR PYTHON
# -------------------------------------------------
_INDENT_KEYWORDS = {
    "if", "elif", "else", "for", "while", "def", "class",
    "try", "except", "finally", "with", "async"
}

def _needs_indent(line: str) -> bool:
    """True if the line opens a block that requires indentation."""
    stripped = line.strip()
    if not stripped or not stripped.endswith(":"):
        return False
    word = stripped[:-1].strip().split()[-1]
    return word in _INDENT_KEYWORDS

def _current_indent_level(lines: list[str]) -> int:
    """Return the indentation level of the last non-blank line."""
    for line in reversed(lines):
        stripped = line.rstrip()
        if stripped:
            return len(line) - len(stripped)
    return 0

def _indent_line(line: str, level: int) -> str:
    return " " * (4 * level) + line.strip() + "\n"

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
        file_path = None
        try:
            file_path = f"temp_audio_{uuid.uuid4().hex}.mp3"
            result_content = generate_audio(message, voice)
            if result_content is None:
                print("Failed to generate audio")
                return
            with open(file_path, "wb") as file:
                file.write(result_content)
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.music.unload()
            time.sleep(0.2)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error in speak function: {e}")
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass

def remove_emojis(text):
    """Remove emojis from text"""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

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

def get_user_directory(username):
    """Get or create user-specific directory"""
    user_dir = os.path.join(BASE_USERS_DIR, username.lower().replace(" ", "_"))
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def get_llm_code_response(user_instruction, current_code, language):
    """Get AI-generated code line from Mistral API with full code context"""
    HEADERS = {
        'Authorization': f'Bearer {MISTRAL_API_KEY}',
        'Content-Type': 'application/json',
    }
    system_content = f"""You are an expert code generation assistant specialized in {language} programming.
    CRITICAL RULES:
    1. Generate ONLY ONE LINE of code per request
    2. The line must be valid {language} syntax
    3. Return ONLY the code line - no explanations, no comments, no markdown
    4. Consider the full code context provided
    5. Generate code that logically follows from the existing code
    6. Handle any type of instruction: variable creation, loops, functions, conditionals, etc.

    Examples of valid responses:
    - x = 5
    - for i in range(10):
    - if condition == True:
    - def calculate_sum(a, b):
    - print("Hello World")

    Current code context:
    {current_code if current_code.strip() else "Empty file - starting fresh"}

    User wants you to: {user_instruction}
    Generate the appropriate single line of {language} code."""

    conversation_history = f"user\n{user_instruction}\nmodel\n"
    data = {
        "model": "mistral-large-2411",
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": conversation_history}
        ],
        "temperature": 0.3,
        "max_tokens": 150
    }
    print(f"[INFO] Sending instruction to AI: {user_instruction}")
    try:
        response = requests.post(MODEL_URL, json=data, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            res = response.json()
            model_response = res['choices'][0]['message']["content"].strip()
            # Remove markdown code blocks
            model_response = model_response.replace("```python", "").replace("``````", "")
            model_response = model_response.strip()
            model_response = remove_emojis(model_response)
            # Get first non-empty line
            lines = [l for l in model_response.split('\n') if l.strip()]
            if lines:
                model_response = lines[0]  # ← Extract the FIRST element from the list
            print(f"[INFO] AI Generated Code: {model_response}")
            return model_response

        else:
            print(f"[ERROR] Request failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] AI API Exception: {e}")
        return None



def get_llm_instruction_interpretation(user_voice_input, current_code, language):
    """Get natural language interpretation of what code to generate"""
    HEADERS = {
        'Authorization': f'Bearer {MISTRAL_API_KEY}',
        'Content-Type': 'application/json',
    }
    system_content = f"""You are a helpful coding assistant that interprets user voice commands into clear coding instructions.
Your job is to understand what the user wants to code and describe it clearly in one sentence.

Examples:
User says: "make a variable called x and set it to 5"
You respond: "Create a variable named x and assign it the value 5"

User says: "create a for loop"
You respond: "Create a for loop that iterates"

User says: "print hello world"
You respond: "Print the text 'hello world'"

Current code context:
{current_code if current_code.strip() else "Empty file"}

Language: {language}
Convert the user's voice command into a clear instruction for code generation."""

    conversation_history = f"user\n{user_voice_input}\nmodel\n"
    data = {
        "model": "mistral-large-2411",
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": conversation_history}
        ],
        "temperature": 0.5,
        "max_tokens": 100
    }
    try:
        response = requests.post(MODEL_URL, json=data, headers=HEADERS, timeout=20)
        if response.status_code == 200:
            res = response.json()
            interpretation = res['choices']['message']["content"].strip()
            interpretation = remove_emojis(interpretation)
            return interpretation
        else:
            return user_voice_input
    except Exception as e:
        print(f"[ERROR] Exception interpreting instruction: {e}")
        return user_voice_input

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
    languages = [f.replace('.mp3', '') for f in os.listdir(module_path)
                 if f.endswith('.mp3')]
    return languages

def _stop_current_lesson():
    """Force-stop the currently playing lesson."""
    global _current_lesson_thread
    with audio_lock:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
    _current_lesson_thread = None

def play_lesson(language, module, lesson_lang):
    """Play the lesson audio file with pygame mixer (blocking playback)"""
    global _current_lesson_thread
    lesson_path = os.path.join(LESSONS_DIR, language, module, f"{lesson_lang}.mp3")
    if not os.path.exists(lesson_path):
        speak(f"Lesson file not found at {lesson_path}")
        return
    
    speak(f"Playing {module} lesson in {lesson_lang}. Say stop to end the lesson.")
    try:
        with audio_lock:
            pygame.mixer.music.load(lesson_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
    except Exception as e:
        speak(f"Playback error: {e}")

def learn_mode(username, ui_callback=None):
    """Handle learning mode"""
    if ui_callback:
        ui_callback("learn_mode_start")
    
    speak(f"Welcome to learn mode, {username}. Which language do you want to learn? Say Python or C.")
    
    while True:
        lang_choice = takeCommand()
        if lang_choice == "none":
            speak("I didn't catch that. Please say Python or C.")
            continue
        
        if "python" in lang_choice:
            language = "python"
            break
        elif "c" in lang_choice:
            language = "c"
            break
        else:
            speak("This language is not uploaded yet. Please choose Python or C.")
    
    if ui_callback:
        ui_callback("language_selected", language)
    
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
        
        selected_module = None
        for module in modules:
            if module.lower() in module_choice or module_choice in module.lower():
                selected_module = module
                break
        
        if selected_module:
            break
        else:
            speak(f"Module not found. Available modules are: {', '.join(modules)}")
    
    if ui_callback:
        ui_callback("module_selected", selected_module)
    
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
        
        selected_lang = None
        for ll in lesson_langs:
            if ll.lower() in lang_pref or lang_pref in ll.lower():
                selected_lang = ll
                break
        
        if selected_lang:
            if ui_callback:
                ui_callback("lesson_playing", selected_module, selected_lang)
            
            lesson_thread = threading.Thread(
                target=play_lesson,
                args=(language, selected_module, selected_lang),
                daemon=True
            )
            lesson_thread.start()
            
            while lesson_thread.is_alive():
                command = takeCommand()
                if command != "none" and "stop" in command:
                    _stop_current_lesson()
                    speak("Lesson stopped.")
                    break
                time.sleep(0.5)
            break
        else:
            speak(f"Language not available. Choose from: {', '.join(lesson_langs)}")

def show_guide():
    """Display voice command guide for code editing"""
    guide_text = """
========== VOICE CODING GUIDE ==========
AI-POWERED CODING:
- Just describe what you want in natural language
- "make a variable called x and set it to 5"
- "create a for loop"
- "print hello world"
- "define a function called calculate"
- "create an if statement to check if x is greater than 10"
- The AI understands context and generates appropriate code

EDITING COMMANDS:
- "delete line [number]" - Delete specific line (e.g., "delete line 3")
- "delete last line" - Remove the last line added
- "clear all" - Clear entire file content
- "show code" - Display current code with line numbers

EXECUTION:
- "execute" or "run" - Run your code
- "guide" - Show this help guide
- "exit" or "stop" - Exit code mode

EXAMPLES:
Python:
- "create a list called numbers"
- "add a while loop"
- "import numpy"

C:
- "include stdio header"
- "declare an integer variable named count"
- "create a printf statement"
=========================================
"""
    print(guide_text)
    speak("Guide displayed on screen. Just describe what code you want in natural language, and the AI will generate it for you. The AI understands your full code context and generates one line at a time.")

def read_code_file(file_path):
    """Read code file and return lines"""
    try:
        with open(file_path, "r") as f:
            return f.readlines()
    except:
        return []

def write_code_file(file_path, lines):
    """Write lines to code file"""
    with open(file_path, "w") as f:
        f.writelines(lines)

def get_current_code_context(file_path):
    """Get current code as string for context"""
    lines = read_code_file(file_path)
    return "".join(lines)

def show_code(file_path):
    """Display code with line numbers"""
    lines = read_code_file(file_path)
    if not lines:
        print("File is empty.")
        speak("File is empty.")
        return
    
    print("\n========== CURRENT CODE ==========")
    for idx, line in enumerate(lines, 1):
        print(f"{idx}: {line.rstrip()}")
    print("==================================\n")
    speak(f"Showing {len(lines)} lines of code on screen.")

def delete_line(file_path, line_number):
    """Delete a specific line from the file"""
    lines = read_code_file(file_path)
    if 1 <= line_number <= len(lines):
        del lines[line_number - 1]
        write_code_file(file_path, lines)
        speak(f"Deleted line {line_number}")
        return True
    else:
        speak(f"Invalid line number. File has {len(lines)} lines.")
        return False

def delete_last_line(file_path):
    """Delete the last line from the file"""
    lines = read_code_file(file_path)
    if lines:
        lines = lines[:-1]
        write_code_file(file_path, lines)
        speak("Deleted last line")
        return True
    else:
        speak("File is already empty.")
        return False

def clear_all_code(file_path, language):
    """Clear all code and reset to template"""
    with open(file_path, "w") as f:
        if language == "c":
            f.write("#include <stdio.h>\n\nint main() {\n    \n    return 0;\n}\n")
        else:
            f.write("")
    speak("All code cleared.")

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
            exe_path = file_path.replace('.c', '.exe' if sys.platform == "win32" else '.out')
            compile_result = subprocess.run(
                ['gcc', file_path, '-o', exe_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            if compile_result.returncode != 0:
                return f"Compilation error: {compile_result.stderr}"
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

def get_user_projects(user_dir):
    """Get list of user's projects"""
    if not os.path.exists(user_dir):
        return []
    return [d for d in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, d))]

def code_mode(username, ui_callback=None, code_changes_callback=None):
    """Handle coding mode with AI-powered code generation"""
    user_dir = get_user_directory(username)
    
    if ui_callback:
        ui_callback("code_mode_start")
    
    speak(f"Welcome to AI-powered code mode, {username}. Which language do you want to code in? Say Python or C.")
    
    while True:
        lang_choice = takeCommand()
        if lang_choice == "none":
            speak("Please say the language name.")
            continue
        
        if "python" in lang_choice:
            language = "python"
            file_ext = ".py"
            break
        elif "c" in lang_choice:
            language = "c"
            file_ext = ".c"
            break
        else:
            speak("Language not supported. Please choose Python or C.")
    
    if ui_callback:
        ui_callback("language_selected", language)
    
    existing_projects = get_user_projects(user_dir)
    
    if existing_projects:
        speak(f"You have {len(existing_projects)} existing projects. Say 'open' followed by project name, or say 'create new project'.")
        print(f"Existing projects: {', '.join(existing_projects)}")
    else:
        speak("Say 'create new project' to start.")
    
    while True:
        project_choice = takeCommand()
        if project_choice == "none":
            continue
        
        if "create new" in project_choice or "new project" in project_choice:
            speak("What do you want to name your project?")
            while True:
                project_name = takeCommand()
                if project_name != "none":
                    project_name = project_name.replace(" ", "_")
                    break
                speak("Please say the project name.")
            
            project_path = os.path.join(user_dir, project_name)
            if os.path.exists(project_path):
                speak("Project with this name already exists. Say a different name.")
                continue
            
            os.makedirs(project_path, exist_ok=True)
            speak(f"New project '{project_name}' created successfully.")
            break
        
        elif "open" in project_choice:
            proj_name = project_choice.replace("open", "").replace("project", "").strip().replace(" ", "_")
            if not proj_name:
                speak("Please say the project name you want to open.")
                continue
            
            matched_project = None
            for proj in existing_projects:
                if proj_name in proj.lower() or proj.lower() in proj_name:
                    matched_project = proj
                    break
            
            if matched_project:
                project_path = os.path.join(user_dir, matched_project)
                speak(f"Opening project: {matched_project}")
                break
            else:
                speak("Project not found. Say 'create new project' or correct name.")
        else:
            speak("Say 'open project name' or 'create new project'.")
    
    if ui_callback:
        ui_callback("project_selected", project_path)
    
    try:
        subprocess.Popen(['code', project_path])
        speak("VS Code opened in your project directory.")
    except:
        speak("Could not open VS Code. Please open it manually.")
    
    speak("What file name do you wish? Say the name without extension.")
    while True:
        file_name = takeCommand()
        if file_name != "none":
            file_name = file_name.replace(" ", "_")
            break
        speak("Please say the file name.")
    
    file_path = os.path.join(project_path, f"{file_name}{file_ext}")
    
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            if language == "c":
                f.write("#include <stdio.h>\n\nint main() {\n    \n    return 0;\n}\n")
            else:
                f.write("")
        speak(f"File {file_name}{file_ext} created.")
    else:
        speak(f"Opening existing file {file_name}{file_ext}.")
    
    if ui_callback:
        ui_callback("file_created", file_path)
    
    speak("AI coding mode active. Just describe what code you want in natural language. Say 'guide' for help, 'show code' to see current code, or 'execute' to run.")
    
    current_indent_level = 0
    
    while True:
        voice_input = takeCommand()
        if voice_input == "none":
            continue
        
        if "exit" in voice_input or "stop coding" in voice_input:
            speak("Exiting code mode.")
            break
        
        if "guide" in voice_input or "help" in voice_input:
            show_guide()
            continue
        
        if "show code" in voice_input or "display code" in voice_input:
            show_code(file_path)
            continue
        
        if "execute" in voice_input or "run" in voice_input:
            speak("Executing your code.")
            output = execute_code(file_path, language)
            print(output)
            speak(output)
            continue
        
        if "delete line" in voice_input:
            try:
                parts = voice_input.split("line")
                if len(parts) > 1:
                    num_str = parts.strip().split()[1]
                    word_to_num = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10}
                    line_num = word_to_num.get(num_str.lower(), int(num_str))
                    delete_line(file_path, line_num)
                else:
                    speak("Please specify line number.")
            except:
                speak("Could not understand line number.")
            continue
        
        if "delete last line" in voice_input:
            delete_last_line(file_path)
            continue
        
        if "clear all" in voice_input or "clear code" in voice_input:
            speak("Are you sure you want to clear all code? Say 'yes' to confirm.")
            confirm = takeCommand()
            if "yes" in confirm:
                clear_all_code(file_path, language)
                current_indent_level = 0
            else:
                speak("Clear cancelled.")
            continue
        
        speak("Generating code with AI...")
        current_code = get_current_code_context(file_path)
        
        indent_level = current_indent_level
        voice_input_clean = voice_input
        
        dedent_keywords = ["remove indent", "dedent", "unindent", "outdent"]
        dedent_count = 0
        for keyword in dedent_keywords:
            if keyword in voice_input.lower():
                dedent_count += voice_input.lower().count(keyword)
                voice_input_clean = re.sub(keyword, "", voice_input_clean, flags=re.IGNORECASE).strip()
        
        if dedent_count > 0:
            indent_level = max(0, current_indent_level - dedent_count)
            current_indent_level = indent_level
            speak(f"Removing indent to level {indent_level}")
        
        indent_count = 0
        if dedent_count == 0:
            indent_count = voice_input.count(" indent ") + voice_input.count("indent ") + voice_input.count(" tab ") + voice_input.count("tab ")
            if voice_input.lower().startswith("indent ") or voice_input.lower().startswith("tab "):
                indent_count += 1
            
            if indent_count > 0:
                indent_level += indent_count
                current_indent_level = indent_level
                voice_input_clean = voice_input_clean.replace("indent", "").replace("tab", "").strip()
                speak(f"Indenting to level {indent_level}")
        
        if indent_count == 0 and dedent_count == 0:
            indent_level = current_indent_level
            voice_input_clean = voice_input
        
        code_line = get_llm_code_response(voice_input_clean, current_code, language)
        
        if code_line:
            indented_line = (" " * (4 * indent_level)) + code_line + "\n"
            with open(file_path, "a") as f:
                f.write(indented_line)
            
            spoken = code_line.strip()
            print(f"AI Generated (Indent Level {indent_level}): {indented_line.rstrip()}")
            speak(f"Added: {spoken}")
            
            if code_changes_callback:
                code_changes_callback(f"Added: {spoken}")
        else:
            speak("Sorry, I couldn't generate code for that instruction. Please try again.")


# =============================================================================
# USER INTERFACE CLASSES
# =============================================================================

class LoginSelectionWindow(ctk.CTk):
    """Initial window for selecting user or admin login"""
    def __init__(self):
        super().__init__()
        
        self.title("Sight2Code - Welcome")
        self.geometry("800x600")
        self.resizable(False, False)
        
        self.selected_mode = None
        self.voice_thread = None
        self.listening = True
        
        self.setup_ui()
        self.start_voice_listening()
    
    def setup_ui(self):
        """Setup the login selection UI"""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=COLORS["dark_bg"])
        main_frame.pack(fill="both", expand=True)
        
        # Logo/Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="👁️ Sight2Code",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=COLORS["primary"]
        )
        title_label.pack(pady=(80, 20))
        
        subtitle = ctk.CTkLabel(
            main_frame,
            text="AI-Powered Voice Coding Platform",
            font=ctk.CTkFont(size=18),
            text_color=COLORS["text_secondary"]
        )
        subtitle.pack(pady=(0, 60))
        
        # Instruction
        instruction = ctk.CTkLabel(
            main_frame,
            text="Select login mode by clicking or using voice command",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        )
        instruction.pack(pady=(0, 40))
        
        # Button container
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        # User button
        self.user_btn = ctk.CTkButton(
            button_frame,
            text="👤 User Login",
            command=lambda: self.select_mode("user"),
            width=250,
            height=80,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color="#818cf8",
            corner_radius=15
        )
        self.user_btn.pack(side="left", padx=20)
        
        # Admin button
        self.admin_btn = ctk.CTkButton(
            button_frame,
            text="🔧 Admin Login",
            command=lambda: self.select_mode("admin"),
            width=250,
            height=80,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color=COLORS["secondary"],
            hover_color="#60a5fa",
            corner_radius=15
        )
        self.admin_btn.pack(side="left", padx=20)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="🎤 Voice control active - Say 'User' or 'Admin'",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["success"]
        )
        self.status_label.pack(pady=(40, 20))
    
    def start_voice_listening(self):
        """Start listening for voice commands in background"""
        def listen_loop():
            speak("Welcome to Sight to Code. Say user for user mode, or admin for admin panel.")
            while self.listening:
                command = takeCommand()
                if command != "none":
                    if "user" in command:
                        self.after(0, lambda: self.select_mode("user"))
                        break
                    elif "admin" in command:
                        self.after(0, lambda: self.select_mode("admin"))
                        break
        
        self.voice_thread = threading.Thread(target=listen_loop, daemon=True)
        self.voice_thread.start()
    
    def select_mode(self, mode):
        """Handle mode selection"""
        self.listening = False
        self.selected_mode = mode
        
        # Highlight selected button
        if mode == "user":
            self.user_btn.configure(fg_color=COLORS["success"])
            speak("User mode selected")
        else:
            self.admin_btn.configure(fg_color=COLORS["success"])
            speak("Admin mode selected")
        
        self.after(1000, self.proceed_to_mode)
    
    def proceed_to_mode(self):
        """Proceed to selected mode"""
        self.destroy()
        
        if self.selected_mode == "admin":
            # Open admin dashboard
            admin_app = Sight2CodeDashboard()
            admin_app.mainloop()
        else:
            # Open user interface
            user_app = UserInterface()
            user_app.mainloop()


class UserInterface(ctk.CTk):
    """Voice-controlled user interface with visual feedback"""
    def __init__(self):
        super().__init__()
        
        self.title("Sight2Code - User Mode")
        self.geometry("1200x800")
        
        self.username = None
        self.current_mode = None
        self.code_changes = []
        
        self.setup_ui()
        self.start_user_flow()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color=COLORS["dark_bg"])
        self.main_container.pack(fill="both", expand=True)
        
        # Header
        header = ctk.CTkFrame(self.main_container, fg_color=COLORS["card_bg"], height=80)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="👁️ Sight2Code - User Mode",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["primary"]
        )
        title.pack(side="left", padx=30, pady=20)
        
        self.status_indicator = ctk.CTkLabel(
            header,
            text="🎤 Listening",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["success"]
        )
        self.status_indicator.pack(side="right", padx=30, pady=20)
        
        # Content area
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Options panel (left side)
        self.options_panel = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card_bg"], width=300)
        self.options_panel.pack(side="left", fill="y", padx=(0, 20))
        self.options_panel.pack_propagate(False)
        
        options_title = ctk.CTkLabel(
            self.options_panel,
            text="Available Options",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        options_title.pack(pady=20)
        
        # Options buttons
        self.option_buttons = {}
        
        self.learn_btn = self.create_option_button("📚 Learn Mode", "learn")
        self.code_btn = self.create_option_button("💻 Code Mode", "code")
        self.exit_btn = self.create_option_button("🚪 Exit", "exit")
        
        # Main display area (right side)
        self.display_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card_bg"])
        self.display_frame.pack(side="right", fill="both", expand=True)
        
        # Welcome message
        welcome_label = ctk.CTkLabel(
            self.display_frame,
            text="Welcome to Sight2Code!\n\nUse voice commands or click buttons to navigate",
            font=ctk.CTkFont(size=20),
            text_color=COLORS["text_primary"]
        )
        welcome_label.pack(expand=True)
        
        # Code changes display (for code mode)
        self.code_changes_frame = None
    
    def create_option_button(self, text, option_id):
        """Create an option button"""
        btn = ctk.CTkButton(
            self.options_panel,
            text=text,
            command=lambda: self.option_clicked(option_id),
            height=60,
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["secondary"],
            hover_color="#60a5fa",
            corner_radius=10
        )
        btn.pack(fill="x", padx=20, pady=10)
        self.option_buttons[option_id] = btn
        return btn
    
    def highlight_option(self, option_id):
        """Highlight selected option"""
        for opt_id, btn in self.option_buttons.items():
            if opt_id == option_id:
                btn.configure(fg_color=COLORS["success"])
            else:
                btn.configure(fg_color=COLORS["secondary"])
    
    def option_clicked(self, option_id):
        """Handle option button click"""
        self.highlight_option(option_id)
        
        if option_id == "learn":
            self.current_mode = "learn"
            threading.Thread(target=lambda: learn_mode(self.username, self.ui_callback), daemon=True).start()
        elif option_id == "code":
            self.current_mode = "code"
            self.setup_code_display()
            threading.Thread(target=lambda: code_mode(self.username, self.ui_callback, self.code_changes_callback), daemon=True).start()
        elif option_id == "exit":
            speak("Thank you for using Sight2Code. Goodbye!")
            self.quit()
    
    def setup_code_display(self):
        """Setup code changes display"""
        # Clear display frame
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = ctk.CTkLabel(
            self.display_frame,
            text="Code Changes",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["primary"]
        )
        title.pack(pady=20)
        
        # Scrollable code changes area
        self.code_changes_frame = ctk.CTkScrollableFrame(
            self.display_frame,
            fg_color=COLORS["card_bg"]
        )
        self.code_changes_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def code_changes_callback(self, change_text):
        """Callback for code changes"""
        if self.code_changes_frame:
            change_label = ctk.CTkLabel(
                self.code_changes_frame,
                text=f"-  {change_text}",
                font=ctk.CTkFont(size=13, family="Courier New"),
                text_color=COLORS["success"],
                anchor="w"
            )
            change_label.pack(anchor="w", pady=5, padx=10)
            
            # Auto-scroll to bottom
            self.code_changes_frame._parent_canvas.yview_moveto(1.0)
    
    def ui_callback(self, event_type, *args):
        """Callback for UI updates from voice modes"""
        if event_type == "learn_mode_start":
            self.highlight_option("learn")
        elif event_type == "code_mode_start":
            self.highlight_option("code")
        elif event_type == "language_selected":
            if args:  # Check if args is not empty
                language = args[0]  # Get first argument
                self.update_status(f"Language: {language.upper()}")
        elif event_type == "module_selected":
            if args:
                module = args[0]
                self.update_status(f"Module: {module}")
        elif event_type == "project_selected":
            if args:
                project = args[0]
                self.update_status(f"Project: {os.path.basename(project)}")

    
    def update_status(self, status_text):
        """Update status indicator"""
        self.status_indicator.configure(text=f"🎤 {status_text}")
    
    def start_user_flow(self):
        """Start the user flow"""
        def get_username():
            speak("Welcome to user mode. What is your name?")
            username = takeCommand()
            if username == "none":
                username = "User"
            self.username = username.replace(" ", "_")
            speak(f"Hello {self.username}, what do you wish to do? Say learn or code.")
            
            # Listen for mode selection
            while True:
                choice = takeCommand()
                if choice == "none":
                    continue
                
                if "learn" in choice:
                    self.after(0, lambda: self.option_clicked("learn"))
                    break
                elif "code" in choice:
                    self.after(0, lambda: self.option_clicked("code"))
                    break
        
        threading.Thread(target=get_username, daemon=True).start()


def main():
    """Main application entry point"""
    # Show login selection window
    app = LoginSelectionWindow()
    app.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        speak("Shutting down. Goodbye!")
    except Exception as e:
        print(f"Fatal error: {e}")
        speak("An error occurred. Please restart the application.")
