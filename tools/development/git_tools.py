"""
Git analysis tools
"""
import subprocess
from enhanced_context_manager import get_context_manager

def check_git_conventions(query):
    """Tool to check git commit conventions"""
    cm = get_context_manager()
    
    # Simple git log analysis
    try:
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

def analyze_git_history(query):
    """Detailed git history analysis"""
    try:
        # Get more detailed git stats
        result = subprocess.run(['git', 'log', '--pretty=format:%an|%s', '-20'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            commits = result.stdout.strip().split('\n')
            authors = {}
            
            for commit in commits:
                if '|' in commit:
                    author, message = commit.split('|', 1)
                    authors[author] = authors.get(author, 0) + 1
            
            top_contributors = sorted(authors.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return f"Git history analysis: Top contributors: {top_contributors}. Total commits analyzed: {len(commits)}"
        else:
            return "No git repository found."
    except Exception as e:
        return f"Git history analysis failed: {str(e)}"
