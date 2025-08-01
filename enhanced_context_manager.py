"""
Enhanced Context Manager for Development Assistant
Handles large codebases, JIRA data, and git history efficiently
"""
import json
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Any
import os

class DevelopmentContextManager:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "dev_context.db"
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for structured storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Code patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_patterns (
                id INTEGER PRIMARY KEY,
                file_path TEXT,
                language TEXT,
                pattern_type TEXT,  -- class, function, variable, etc.
                code_snippet TEXT,
                metadata TEXT,  -- JSON string
                hash TEXT UNIQUE
            )
        """)
        
        # JIRA tickets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jira_tickets (
                id INTEGER PRIMARY KEY,
                ticket_id TEXT UNIQUE,
                title TEXT,
                description TEXT,
                status TEXT,
                assignee TEXT,
                created_date TEXT,
                resolved_date TEXT,
                metadata TEXT
            )
        """)
        
        # Git commits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS git_commits (
                id INTEGER PRIMARY KEY,
                commit_hash TEXT UNIQUE,
                author TEXT,
                date TEXT,
                message TEXT,
                files_changed TEXT,  -- JSON array
                diff_summary TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_code_pattern(self, file_path: str, language: str, 
                          pattern_type: str, code_snippet: str, 
                          metadata: Dict[str, Any]):
        """Store code patterns with deduplication"""
        code_hash = hashlib.md5(code_snippet.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO code_patterns 
                (file_path, language, pattern_type, code_snippet, metadata, hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (file_path, language, pattern_type, code_snippet, 
                  json.dumps(metadata), code_hash))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error storing code pattern: {e}")
        finally:
            conn.close()
    
    def query_similar_patterns(self, query_type: str, language: str = None, 
                              limit: int = 10) -> List[Dict]:
        """Query similar code patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = """
            SELECT file_path, code_snippet, metadata 
            FROM code_patterns 
            WHERE pattern_type = ?
        """
        params = [query_type]
        
        if language:
            sql += " AND language = ?"
            params.append(language)
            
        sql += f" LIMIT {limit}"
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        
        return [{"file_path": r[0], "code": r[1], "metadata": json.loads(r[2])} 
                for r in results]
    
    def get_folder_structure_examples(self, language: str) -> Dict[str, List[str]]:
        """Get common folder structures for a language"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT file_path FROM code_patterns 
            WHERE language = ?
        """, (language,))
        
        file_paths = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Analyze folder patterns
        folders = {}
        for path in file_paths:
            parts = Path(path).parts
            if len(parts) > 1:
                folder = parts[-2]  # Parent folder
                if folder not in folders:
                    folders[folder] = []
                folders[folder].append(Path(path).name)
        
        return folders
    
    def get_naming_conventions(self, language: str, pattern_type: str) -> List[str]:
        """Extract naming conventions from existing code"""
        patterns = self.query_similar_patterns(pattern_type, language)
        names = []
        
        for pattern in patterns:
            metadata = pattern["metadata"]
            if "name" in metadata:
                names.append(metadata["name"])
        
        return names

# Enhanced tools for the multi-agent
import os
import ast
import re
from pathlib import Path

# Global context manager instance
context_manager = None

def get_context_manager():
    """Get or create global context manager instance"""
    global context_manager
    if context_manager is None:
        workspace_path = os.getcwd()  # Current working directory
        context_manager = DevelopmentContextManager(workspace_path)
    return context_manager

def scan_codebase(query):
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

def analyze_jira_history(query):
    """Tool to analyze JIRA ticket patterns"""
    cm = get_context_manager()
    
    # For MVP, return guidance on JIRA integration
    return """JIRA analysis tool ready. To use:
1. Connect JIRA API (add credentials to settings)
2. Import ticket history using: jira.import_tickets()
3. Query patterns like: 'common bug types', 'sprint patterns'

Current status: No JIRA data imported yet. Run initial import first."""

def check_git_conventions(query):
    """Tool to check git commit conventions"""
    cm = get_context_manager()
    
    # Simple git log analysis
    try:
        import subprocess
        result = subprocess.run(['git', 'log', '--oneline', '-10'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            commits = result.stdout.strip().split('\n')
            
            # Analyze commit message patterns
            patterns = []
            for commit in commits:
                if ':' in commit:
                    prefix = commit.split(':')[0].split()[-1]  # Get last word before :
                    patterns.append(prefix)
            
            common_patterns = list(set(patterns))
            
            return f"Git analysis complete. Found {len(commits)} recent commits. Common prefixes: {common_patterns[:5]}. Suggests using conventional commit format."
        else:
            return "No git repository found in current directory."
            
    except Exception as e:
        return f"Git analysis failed: {str(e)}. Ensure git is installed and this is a git repository."
