import bpy
import re
import os

CODE_FILE_NAME = "rag_generated_code.py"

def get_code_filepath():
    if bpy.data.filepath:
        directory = os.path.dirname(bpy.data.filepath)
    else:
        directory = bpy.app.tempdir
    
    return os.path.join(directory, CODE_FILE_NAME)

def parse_code(response):   
    if not response:
        return None, "Empty response"
    
    # Pattern to match ```python ... ``` code blocks
    pattern = r"```python\s*(.*?)\s*```"
    matches = re.findall(pattern, response, re.DOTALL)
    
    if matches:
        return matches[0].strip(), None
    
    pattern = r"```\s*(.*?)\s*```"
    matches = re.findall(pattern, response, re.DOTALL)
    
    if matches:
        return matches[0].strip(), None
    
    if response.strip().startswith("import bpy"):
        return response.strip(), None
    
    return None, "No code block found in response"

def save_code(code, filepath=None):   
    if not code:
        return None, "No code to save"
    
    if filepath is None:
        filepath = get_code_filepath()
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Auto-generated Blender code by RAG Assistant\n")
            f.write("# Modify this file as needed and run in Blender\n\n")
            f.write(code)
        
        return filepath, None
    
    except Exception as e:
        return None, f"Failed to save code: {e}"

def execute_code(code):
    # execute Python code in Blender   
    if not code:
        return False, "No code to execute"
    
    try:
        # Execute in Blender's context
        exec(code, {"__builtins__": __builtins__})
        return True, None
    
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    
    except Exception as e:
        return False, f"Execution error: {e}"

def process_response(response):
    # full pipeline: parse, save, and execute code
    
    result = {
        'success': False,
        'code': None,
        'filepath': None,
        'error': None
    }
    
    # parse code
    code, error = parse_code(response)
    if error:
        result['error'] = f"Parse error: {error}"
        return result
    
    result['code'] = code
    
    # save code
    filepath, error = save_code(code)
    if error:
        result['error'] = f"Save error: {error}"
        return result
    
    result['filepath'] = filepath
    
    # execute code
    success, error = execute_code(code)
    if error:
        result['error'] = f"Execution error: {error}"
        return result
    
    result['success'] = True
    return result