from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
import git
import shutil
import tempfile

app = Flask(__name__)

@app.route('/api/githistory', methods=['POST'])
def write_json_to_file():
    """Write JSON POST body to a file"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if data is None:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds
        filename = f'data/githistory.json'
        
        # Read existing data if file exists
        existing_data = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_content = f.read().strip()
                    if existing_content:
                        existing_data = json.loads(existing_content)
                        # If existing data is not a list, convert it to a list
                        if not isinstance(existing_data, list):
                            existing_data = [existing_data]
            except (json.JSONDecodeError, FileNotFoundError):
                existing_data = []
        
        # Add timestamp to new data
        data_with_timestamp = {
            "timestamp": timestamp,
            "data": data
        }
        
        # Append new data to existing data
        existing_data.append(data_with_timestamp)
        
        # Write updated data to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'status': 'success',
            'message': 'JSON data appended to file',
            'filename': filename,
            'timestamp': timestamp,
            'data_size': len(json.dumps(data)),
            'total_entries': len(existing_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fetch-git-history', methods=['POST'])
def fetch_git_history():
    """Fetch git history from a repository and write to file"""
    try:
        # Get request data
        data = request.get_json()
        repo_path = data.get('repo_path', '.') if data else '.'
        max_commits = data.get('max_commits', 50) if data else 50
        output_file = data.get('output_file', 'data/repo_git_history.json') if data else 'data/repo_git_history.json'
        
        # Validate repository path
        if not os.path.exists(repo_path):
            return jsonify({'error': f'Repository path does not exist: {repo_path}'}), 400
        
        # Open the repository
        try:
            repo = git.Repo(repo_path)
        except git.exc.InvalidGitRepositoryError:
            return jsonify({'error': f'Invalid git repository: {repo_path}'}), 400
        
        # Get commits
        commits = list(repo.iter_commits(max_count=max_commits))
        
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
                "path": repo_path,
                "current_branch": repo.active_branch.name if repo.active_branch else "detached",
                "remote_url": next(iter(repo.remotes.origin.urls), None) if repo.remotes else None
            },
            "metadata": {
                "total_commits_fetched": len(git_history),
                "max_commits_requested": max_commits,
                "fetch_timestamp": datetime.now().isoformat()
            },
            "commits": git_history
        }
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'status': 'success',
            'message': 'Git history fetched and written to file',
            'repository_path': repo_path,
            'commits_fetched': len(git_history),
            'output_file': output_file,
            'file_size_bytes': os.path.getsize(output_file)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fetch-remote-git-history', methods=['POST'])
def fetch_remote_git_history():
    """Fetch git history from a remote repository URL and write to file"""
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        repo_url = data.get('repo_url')
        branch = data.get('branch', 'main')  # Default to main branch
        max_commits = data.get('max_commits', 50)
        output_file = data.get('output_file', 'data/remote_git_history.json')
        auth_token = data.get('auth_token')  # Optional GitHub token for private repos
        
        if not repo_url:
            return jsonify({'error': 'repo_url is required'}), 400
        
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
                return jsonify({'error': f'Failed to get commits: {str(e)}'}), 500
            
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
            
            # Cleanup temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return jsonify({
                'status': 'success',
                'message': 'Remote git history fetched and written to file',
                'repository_url': repo_url,
                'branch': current_branch,
                'commits_fetched': len(git_history),
                'output_file': output_file,
                'file_size_bytes': os.path.getsize(output_file)
            })
        
        except git.exc.GitCommandError as e:
            # Cleanup on error
            shutil.rmtree(temp_dir, ignore_errors=True)
            return jsonify({'error': f'Git error: {str(e)}'}), 400
        
        except Exception as e:
            # Cleanup on error
            shutil.rmtree(temp_dir, ignore_errors=True)
            return jsonify({'error': f'Clone error: {str(e)}'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting JSON Writer API on http://localhost:5000")
    print("POST endpoint: http://localhost:5000/api/githistory")
    print("POST endpoint: http://localhost:5000/api/fetch-git-history")
    print("POST endpoint: http://localhost:5000/api/fetch-remote-git-history")
    app.run(host='localhost', port=5000, debug=True)
