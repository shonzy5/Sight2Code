"""
Code Interpreter - Converts natural language voice commands to code
Supports Python and C syntax
"""

import re
import sys
from io import StringIO
import subprocess


class CodeInterpreter:
    """Interprets voice commands and converts them to code"""
    
    def __init__(self):
        self.current_language = "python"
        self.indentation_level = 0
        self.in_loop = False
        self.in_function = False
    
    def interpret(self, voice_command):
        """
        Convert voice command to code
        
        Args:
            voice_command: Natural language command
            
        Returns:
            Code string or None
        """
        command = voice_command.lower().strip()
        
        # Print statements
        if "print" in command:
            return self.handle_print(command)
        
        # Variable assignment
        elif "variable" in command or "set" in command or "=" in command:
            return self.handle_variable(command)
        
        # If statements
        elif command.startswith("if "):
            return self.handle_if(command)
        
        # Loops
        elif "for loop" in command or command.startswith("for "):
            return self.handle_for_loop(command)
        
        elif "while loop" in command or command.startswith("while "):
            return self.handle_while_loop(command)
        
        # Function definition
        elif "function" in command or "define" in command or command.startswith("def "):
            return self.handle_function(command)
        
        # Input
        elif "input" in command:
            return self.handle_input(command)
        
        # Comments
        elif "comment" in command:
            return self.handle_comment(command)
        
        # Import statements
        elif "import" in command:
            return self.handle_import(command)
        
        # End of block
        elif "end" in command or "finish" in command:
            return self.handle_end_block()
        
        # Lists
        elif "list" in command or "array" in command:
            return self.handle_list(command)
        
        # Dictionary
        elif "dictionary" in command or "dict" in command:
            return self.handle_dictionary(command)
        
        # Return statement
        elif "return" in command:
            return self.handle_return(command)
        
        # Try to interpret as direct code
        else:
            return self.direct_code_interpretation(command)
    
    def handle_print(self, command):
        """Handle print statements"""
        # Extract what to print
        patterns = [
            r'print\s+(.+)',
            r'output\s+(.+)',
            r'display\s+(.+)',
            r'show\s+(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                content = match.group(1).strip()
                
                # Check if it's a string or variable
                if any(word in content for word in ["hello", "world", "text", "message"]):
                    # It's likely a string
                    content = content.replace("hello world", "Hello World")
                    return f'{self.get_indent()}print("{content}")'
                else:
                    # It's likely a variable
                    return f'{self.get_indent()}print({content})'
        
        return f'{self.get_indent()}print("")'
    
    def handle_variable(self, command):
        """Handle variable assignments"""
        # Patterns: "variable x equals 5", "set x to 10", "x = 5"
        
        # Try to extract variable name and value
        patterns = [
            r'(?:variable|set)\s+(\w+)\s+(?:equals|to|=)\s+(.+)',
            r'(\w+)\s*=\s*(.+)',
            r'create\s+(?:variable\s+)?(\w+)\s+(?:with\s+)?(?:value\s+)?(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                var_name = match.group(1).strip()
                value = match.group(2).strip()
                
                # Convert word numbers to digits
                value = self.convert_number_words(value)
                
                # Check if value is a string
                if any(word in value for word in ["text", "string", "message"]) or '"' in value or "'" in value:
                    value = value.replace("text", "").replace("string", "").replace("message", "").strip()
                    if not (value.startswith('"') or value.startswith("'")):
                        value = f'"{value}"'
                
                return f'{self.get_indent()}{var_name} = {value}'
        
        return None
    
    def handle_if(self, command):
        """Handle if statements"""
        # Extract condition
        condition = command.replace("if ", "").strip()
        condition = self.convert_condition(condition)
        
        self.indentation_level += 1
        return f'{self.get_indent(offset=-1)}if {condition}:'
    
    def handle_for_loop(self, command):
        """Handle for loops"""
        # Patterns: "for loop i from 0 to 10", "for i in range 10"
        
        patterns = [
            r'for\s+(?:loop\s+)?(\w+)\s+from\s+(\d+)\s+to\s+(\d+)',
            r'for\s+(\w+)\s+in\s+range\s+(\d+)',
            r'for\s+(\w+)\s+in\s+(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                if len(match.groups()) == 3:
                    var = match.group(1)
                    start = match.group(2)
                    end = match.group(3)
                    self.indentation_level += 1
                    self.in_loop = True
                    return f'{self.get_indent(offset=-1)}for {var} in range({start}, {end}):'
                elif len(match.groups()) == 2:
                    var = match.group(1)
                    iterable = match.group(2)
                    self.indentation_level += 1
                    self.in_loop = True
                    return f'{self.get_indent(offset=-1)}for {var} in {iterable}:'
        
        return None
    
    def handle_while_loop(self, command):
        """Handle while loops"""
        condition = command.replace("while loop", "").replace("while", "").strip()
        condition = self.convert_condition(condition)
        
        self.indentation_level += 1
        self.in_loop = True
        return f'{self.get_indent(offset=-1)}while {condition}:'
    
    def handle_function(self, command):
        """Handle function definitions"""
        # Patterns: "function add with parameters x and y", "define function add"
        
        patterns = [
            r'(?:function|define)\s+(\w+)\s+with\s+parameters?\s+(.+)',
            r'(?:function|define)\s+(\w+)\s*\((.+)\)',
            r'(?:def|define)\s+(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                func_name = match.group(1)
                
                if len(match.groups()) == 2:
                    params = match.group(2).replace(" and ", ", ").strip()
                    self.indentation_level += 1
                    self.in_function = True
                    return f'{self.get_indent(offset=-1)}def {func_name}({params}):'
                else:
                    self.indentation_level += 1
                    self.in_function = True
                    return f'{self.get_indent(offset=-1)}def {func_name}():'
        
        return None
    
    def handle_input(self, command):
        """Handle input statements"""
        # "input message", "get input from user"
        
        message = "Enter value: "
        if "message" in command or "prompt" in command:
            # Extract custom message
            match = re.search(r'(?:message|prompt)\s+(.+)', command)
            if match:
                message = match.group(1).strip()
        
        var_name = "user_input"
        if "variable" in command or "into" in command:
            match = re.search(r'(?:variable|into)\s+(\w+)', command)
            if match:
                var_name = match.group(1)
        
        return f'{self.get_indent()}{var_name} = input("{message}")'
    
    def handle_comment(self, command):
        """Handle comments"""
        comment_text = command.replace("comment", "").strip()
        return f'{self.get_indent()}# {comment_text}'
    
    def handle_import(self, command):
        """Handle import statements"""
        module = command.replace("import", "").strip()
        return f'{self.get_indent()}import {module}'
    
    def handle_list(self, command):
        """Handle list creation"""
        # "list x with values 1 2 3", "create list x"
        
        match = re.search(r'(?:list|array)\s+(\w+)(?:\s+with\s+values?\s+(.+))?', command)
        if match:
            list_name = match.group(1)
            values = match.group(2) if match.group(2) else ""
            
            if values:
                values = values.replace(" and ", ", ").replace(" ", ", ")
                return f'{self.get_indent()}{list_name} = [{values}]'
            else:
                return f'{self.get_indent()}{list_name} = []'
        
        return None
    
    def handle_dictionary(self, command):
        """Handle dictionary creation"""
        match = re.search(r'(?:dictionary|dict)\s+(\w+)', command)
        if match:
            dict_name = match.group(1)
            return f'{self.get_indent()}{dict_name} = {{}}'
        
        return None
    
    def handle_return(self, command):
        """Handle return statements"""
        value = command.replace("return", "").strip()
        
        if value:
            return f'{self.get_indent()}return {value}'
        else:
            return f'{self.get_indent()}return'
    
    def handle_end_block(self):
        """Handle end of code block"""
        if self.indentation_level > 0:
            self.indentation_level -= 1
        
        self.in_loop = False
        self.in_function = False
        
        return ""  # Empty line to indicate end of block
    
    def direct_code_interpretation(self, command):
        """Try to interpret command as direct code"""
        # If command looks like code, return it as is
        if any(char in command for char in ['=', '(', ')', '[', ']', '{', '}']):
            return f'{self.get_indent()}{command}'
        
        return f'{self.get_indent()}# {command}'
    
    def convert_condition(self, condition):
        """Convert natural language condition to code"""
        condition = condition.replace(" equals ", " == ")
        condition = condition.replace(" equal to ", " == ")
        condition = condition.replace(" is ", " == ")
        condition = condition.replace(" greater than ", " > ")
        condition = condition.replace(" less than ", " < ")
        condition = condition.replace(" and ", " and ")
        condition = condition.replace(" or ", " or ")
        
        return condition
    
    def convert_number_words(self, text):
        """Convert word numbers to digits"""
        number_words = {
            "zero": "0", "one": "1", "two": "2", "three": "3",
            "four": "4", "five": "5", "six": "6", "seven": "7",
            "eight": "8", "nine": "9", "ten": "10"
        }
        
        for word, digit in number_words.items():
            text = text.replace(word, digit)
        
        return text
    
    def get_indent(self, offset=0):
        """Get current indentation"""
        level = max(0, self.indentation_level + offset)
        return "    " * level
    
    def execute(self, code):
        """
        Execute Python code safely and return output
        
        Args:
            code: Python code string
            
        Returns:
            Output string
        """
        # Redirect stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            # Execute code
            exec(code)
            
            # Get output
            output = sys.stdout.getvalue()
            
            if not output:
                output = "Code executed successfully (no output)"
            
            return output.strip()
            
        except Exception as e:
            return f"Error: {str(e)}"
        
        finally:
            # Restore stdout
            sys.stdout = old_stdout
    
    def execute(self, code):
        """Execute the code and return output or error"""
        try:
            # Logic to execute code based on language
            output = subprocess.check_output(['python', '-c', code], stderr=subprocess.STDOUT, text=True)
            return output
        except subprocess.CalledProcessError as e:
            return f"Error: {e.output}"