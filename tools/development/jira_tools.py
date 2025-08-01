"""
JIRA integration tools
"""
from enhanced_context_manager import get_context_manager

def analyze_jira_history(query):
    """Tool to analyze JIRA ticket patterns"""
    cm = get_context_manager()
    
    # For MVP, return guidance on JIRA integration
    return """JIRA analysis tool ready. To use:
1. Connect JIRA API (add credentials to settings)
2. Import ticket history using: jira.import_tickets()
3. Query patterns like: 'common bug types', 'sprint patterns'

Current status: No JIRA data imported yet. Run initial import first."""

def import_jira_tickets(query):
    """Import JIRA tickets from API"""
    # Placeholder for JIRA API integration
    return "JIRA import tool ready. Configure JIRA credentials in settings.json first."
