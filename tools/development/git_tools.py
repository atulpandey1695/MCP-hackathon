import json
import os
from datetime import datetime
import git
import shutil
import tempfile
from langchain.tools import tool


@tool
def fetch_remote_git_history(repo_url, branch='main', max_commits=50, output_file='tools/output/git_history_index.json', auth_token=None):
    """Fetch git history from a remote repository URL and write to file
    
    Args:
        repo_url (str): Repository URL to clone
        branch (str): Branch to fetch from (default: 'main')
        max_commits (int): Maximum number of commits to fetch (default: 50)
        output_file (str): Output file path (default: 'tools/output/git_history_index.json.json')
        auth_token (str): Optional GitHub token for private repos
        
    Returns:
        dict: Result dictionary with status, message, and metadata
    """
    try:
        if not repo_url:
            return {'error': 'repo_url is required', 'status': 'error'}
        
        # Create temporary directory for cloning
        temp_dir = tempfile.mkdtemp(prefix='git_clone_')
        
        try:
            # Prepare authenticated URL if token provided
            if auth_token and 'github.com' in repo_url:
                if repo_url.startswith('https://'):
                    authenticated_url = repo_url.replace('https://github.com/', f'https://{auth_token}@github.com/')
                else:
                    authenticated_url = repo_url
            else:
                authenticated_url = repo_url
            
            # Clone the repository
            print(f"Cloning repository: {repo_url}")
            repo = git.Repo.clone_from(authenticated_url, temp_dir, depth=max_commits + 10)
            
            # Get the current branch name safely
            try:
                current_branch = repo.active_branch.name
            except:
                current_branch = "HEAD"
            
            # Switch to specified branch if not default
            try:
                if branch != 'main' and branch != current_branch:
                    repo.git.checkout(branch)
                    current_branch = branch
            except:
                # If branch switch fails, continue with current branch
                pass
            
            # Get commits from the repository
            try:
                commits = list(repo.iter_commits(max_count=max_commits))
            except Exception as e:
                return {'error': f'Failed to get commits: {str(e)}', 'status': 'error'}
            
            # Extract commit information
            git_history = []
            for commit in commits:
                # Get changed files
                changed_files = []
                if commit.parents:  # Not the initial commit
                    try:
                        diff = commit.parents[0].diff(commit)
                        changed_files = [item.a_path or item.b_path for item in diff]
                    except:
                        changed_files = []
                commit_info = {
                    "sha": commit.hexsha,
                    "short_sha": commit.hexsha[:7],
                    "message": commit.message.strip(),
                    "author": {
                        "name": commit.author.name,
                        "email": commit.author.email
                    },
                    "authored_date": commit.authored_datetime.isoformat(),
                    "committed_date": commit.committed_datetime.isoformat(),
                    "changed_files": changed_files
                }
                git_history.append(commit_info)

            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Prepare output data
            output_data = {
                "repository": {
                    "url": repo_url,
                    "cloned_branch": current_branch,
                    "requested_branch": branch,
                    "remote_url": repo_url
                },
                "metadata": {
                    "total_commits_fetched": len(git_history),
                    "max_commits_requested": max_commits,
                    "fetch_timestamp": datetime.now().isoformat(),
                    "clone_method": "temporary"
                },
                "commits": git_history
            }
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            convert_remote_git_history_index_to_faiss()    
            
            # Cleanup temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return {
                'status': 'success',
                'message': 'Remote git history fetched and written to file',
                'repository_url': repo_url,
                'branch': current_branch,
                'commits_fetched': len(git_history),
                'output_file': output_file,
                'file_size_bytes': os.path.getsize(output_file)
            }
        
        except git.exc.GitCommandError as e:
            # Cleanup on error
            shutil.rmtree(temp_dir, ignore_errors=True)
            return {'error': f'Git error: {str(e)}', 'status': 'error'}
        
        except Exception as e:
            # Cleanup on error
            shutil.rmtree(temp_dir, ignore_errors=True)
            return {'error': f'Clone error: {str(e)}', 'status': 'error'}
    
    except Exception as e:
        return {'error': str(e), 'status': 'error'}

def convert_remote_git_history_index_to_faiss():
    """
    Convert remote_git_history_index.json to FAISS index for semantic search.
    """
    from tools.utils.faiss_converter import remote_git_history_to_faiss
    json_file_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'git_history_index.json')
    faiss_index_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'git_history_faiss_index')

    faiss_index = remote_git_history_to_faiss(json_file_path, faiss_index_path)
    print(f"FAISS index created at {faiss_index_path}")