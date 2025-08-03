import tempfile
import shutil
import subprocess
import openai
import os
import json
import ast
def train_agent_on_github_repo(repo_url, output_path=None):
    """
    Clones a GitHub repo, indexes its codebase, and updates the agent's knowledge base.
    """
    target_dir = os.getcwd() + '/target'  # Use current working directory
    repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    clone_path = os.path.join(target_dir, repo_name)
    # Ensure target_dir is empty before cloning
    if os.path.exists(target_dir):
        # Remove target_dir even if it contains read-only files
        def onerror(func, path, exc_info):
            import stat
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(target_dir, onerror=onerror)
    try:
        print(f"Cloning repo {repo_url} to {target_dir}...")
        subprocess.run(["git", "clone", repo_url, target_dir], check=True)
        print("Generating codebase index...")
        result = generate_codebase_index(codebase_path=target_dir, output_path=output_path)
        print(result)
        return result
    except Exception as e:
        return f"[ERROR] Failed to train agent on repo: {e}"
   
def convert_codebase_index_to_faiss():
    """
    Convert codebase_index.json to FAISS index for semantic search.
    """
    from tools.utils.faiss_converter import codebase_json_to_faiss
    json_file_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'codebase_index.json')
    faiss_index_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'codebase_faiss_index')
    
    faiss_index = codebase_json_to_faiss(json_file_path, faiss_index_path)
    print(f"FAISS index created at {faiss_index_path}")

def generate_codebase_index(codebase_path=None, output_path=None):
    """
    Scans the codebase directory for Python and TypeScript/JavaScript files, extracts function/class names and docstrings/comments, and saves the index as JSON.
    """
    if codebase_path is None:
        codebase_path = os.path.join(os.path.dirname(__file__), '..', '..', 'codebase')
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'codebase_index.json')
    index = []
    import re
    function_regex = re.compile(r'(?:function\s+|const\s+|let\s+|var\s+)?([a-zA-Z0-9_]+)\s*\([^)]*\)\s*{')
    class_regex = re.compile(r'class\s+([a-zA-Z0-9_]+)')
    for root, dirs, files in os.walk(codebase_path):
        # Skip any directory containing '.git' in its path
        if '.git' in root:
            continue
        dirs[:] = [d for d in dirs if '.git' not in d and d not in ['__pycache__', '.svn', '.hg']]
        for file in files:
            file_path = os.path.join(root, file)
            # Skip any file containing '.git' in its path
            if '.git' in file_path:
                continue
            # Read file content (truncate to first 1000 chars for large files)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except Exception:
                file_content = ''
            half_length = len(file_content) // 2
            half_content = file_content[:half_length] + ('...' if len(file_content) > half_length else '')
            # Add file-level entry with half content
            index.append({
                'type': 'file',
                'name': file,
                'file': file_path,
                'content': half_content
            })
            if file.endswith('.py'):
                try:
                    tree = ast.parse(file_content, filename=file_path)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            index.append({
                                'type': 'function',
                                'name': node.name,
                                'doc': ast.get_docstring(node),
                                'file': file_path
                            })
                        elif isinstance(node, ast.ClassDef):
                            index.append({
                                'type': 'class',
                                'name': node.name,
                                'doc': ast.get_docstring(node),
                                'file': file_path
                            })
                except Exception:
                    pass
            elif file.endswith('.ts') or file.endswith('.js'):
                # Extract comments
                lines = file_content.splitlines()
                comments = [line.strip() for line in lines if line.strip().startswith('//') or line.strip().startswith('/*')]
                # Extract functions
                for match in function_regex.finditer(file_content):
                    index.append({
                        'type': 'function',
                        'name': match.group(1),
                        'doc': '',
                        'file': file_path
                    })
                # Extract classes
                for match in class_regex.finditer(file_content):
                    index.append({
                        'type': 'class',
                        'name': match.group(1),
                        'doc': '',
                        'file': file_path
                    })
                # Add file-level comments
                if comments:
                    index.append({
                        'type': 'comments',
                        'name': file,
                        'comments': comments,
                        'file': file_path
                    })
    with open(output_path, 'w', encoding='utf-8') as out:
        json.dump(index, out, indent=2)
    print(f"Codebase index generated at {output_path} with {len(index)} entries.")
    convert_codebase_index_to_faiss()
    return f"Codebase index generated at {output_path} with {len(index)} entries. FAISS index created."
    
def search_codebase_index(query, index_path=None, max_results=5):
    if index_path is None:
        index_path = os.path.join(os.path.dirname(__file__), '..', 'codebase_index.json')
    if not os.path.exists(index_path):
        return []
    with open(index_path, 'r', encoding='utf-8') as f:
        index = json.load(f)
    query_lower = query.lower()
    results = []
    for item in index:
        text = f"{item.get('file','')} {item.get('name','')} {item.get('doc','')} "
        text += ' '.join(item.get('comments', [])) if 'comments' in item else ''
        text += f" {item.get('content','')}" if 'content' in item else ''
        #if query_lower in text.lower():
        results.append(item)
        # if len(results) >= max_results:
        #     break
    return results

# def question_answering(query: str) -> str:
#     """
#     Answer questions using codebase_index.json and OpenAI.
#     """
#     # Search codebase index for relevant context
#     context_items = search_codebase_index(query)
#     if not context_items:
#         return "No relevant codebase context found for your query. Please try a different question."
#     # Limit codebase context to first 1000 characters
#     context_snippets = "\n\n".join([
#         f"File: {item.get('file')}, Name: {item.get('name')}, Content/Doc: {(item.get('doc','') or item.get('content',''))[:300]}"
#         for item in context_items
#     ])
#     # Load recent chat history from chatbot_context.json
#     chat_history_path = os.path.join(os.path.dirname(__file__), '..', 'chatbot_context.json')
#     chat_history = []
#     if os.path.exists(chat_history_path):
#         try:
#             with open(chat_history_path, 'r', encoding='utf-8') as f:
#                 history = json.load(f)
#                 chat_history = history[-3:] if len(history) > 3 else history
#         except Exception:
#             pass
#     chat_history_str = "\n".join([
#         f"{msg['role']}: {msg['content']}" for msg in chat_history
#     ])
#     prompt = (
#         f"User question: {query}\n\n"
#         f"Recent chat history:\n{chat_history_str}\n\n"
#         f"Relevant codebase context:\n{context_snippets}\n\n"
#         f"Answer the question using the codebase context and chat history above."
#     )
#     api_key = os.getenv('OPENAI_API_KEY')
#     if not api_key:
#         settings_path = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
#         if os.path.exists(settings_path):
#             try:
#                 with open(settings_path, 'r', encoding='utf-8') as f:
#                     settings = json.load(f)
#                     api_key = settings.get('OPENAI_API_KEY')
#             except Exception:
#                 pass
#     openai.api_key = api_key
#     try:
#         response = openai.chat.completions.create(
#             model="gpt-4",
#             messages=[{"role": "user", "content": prompt}]
#         )
#         if not hasattr(response, 'choices') or not response.choices or not hasattr(response.choices[0], 'message'):
#             return "OpenAI API did not return a valid response."
#         answer = response.choices[0].message.content
#     except Exception as e:
#         return f"[ERROR] OpenAI API call failed: {e}\nCheck your API key and network connection."
#     return answer

