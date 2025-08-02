"""
Codebase analysis tools
"""
from enhanced_context_manager import DevelopmentContextManager, get_context_manager
import os
import ast
from pathlib import Path
from langchain.tools import tool

@tool
def scan_codebase(query: str) -> str:
    """Tool to scan and analyze codebase patterns"""
    cm = get_context_manager()
    
    # Extract language or pattern type from query
    query_lower = query.lower()
    
    if "python" in query_lower:
        language = "python"
    elif "javascript" in query_lower or "js" in query_lower:
        language = "javascript"
    elif "java" in query_lower:
        language = "java"
    else:
        language = None
    
    # Scan current directory for code files
    code_files = []
    extensions = {'.py': 'python', '.js': 'javascript', '.java': 'java', 
                  '.ts': 'typescript', '.cpp': 'cpp', '.c': 'c'}
    
    for ext, lang in extensions.items():
        if language is None or lang == language:
            code_files.extend(Path('.').rglob(f'*{ext}'))
    
    patterns_found = 0
    for file_path in code_files[:10]:  # Limit for MVP
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Simple pattern extraction
            if file_path.suffix == '.py':
                # Extract class and function names
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            cm.store_code_pattern(
                                str(file_path), 'python', 'class',
                                f"class {node.name}:", 
                                {"name": node.name, "file": str(file_path)}
                            )
                            patterns_found += 1
                        elif isinstance(node, ast.FunctionDef):
                            cm.store_code_pattern(
                                str(file_path), 'python', 'function',
                                f"def {node.name}():", 
                                {"name": node.name, "file": str(file_path)}
                            )
                            patterns_found += 1
                except:
                    pass
        except:
            continue
    
    # Get folder structure analysis
    if language:
        folders = cm.get_folder_structure_examples(language)
        folder_info = f"Common folders: {list(folders.keys())[:5]}"
    else:
        folder_info = "Multiple languages detected"
    
    return f"Codebase scan completed. Found {patterns_found} patterns. {folder_info}. Use specific queries like 'python naming conventions' for detailed analysis."

def analyze_folder_structure(query):
    """Analyze and suggest folder structures"""
    cm = get_context_manager()
    
    # Get current folder structure
    current_dirs = [d for d in Path('.').iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    return f"Current structure: {[d.name for d in current_dirs]}. Analyzing patterns from database..."
