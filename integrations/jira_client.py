"""JIRA integration client for creating epics and stories."""
import json
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import os


class JiraClient(ABC):
    """Abstract base class for JIRA integration."""
    
    @abstractmethod
    def create_epic(self, epic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an epic in JIRA."""
        pass
    
    @abstractmethod
    def create_story(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a story in JIRA."""
        pass
    
    @abstractmethod
    def link_story_to_epic(self, story_key: str, epic_key: str) -> bool:
        """Link a story to an epic."""
        pass


class MockJiraClient(JiraClient):
    """
    Mock JIRA client for development and testing.
    Simulates API calls without actual external requests.
    """
    
    def __init__(self):
        """Initialize mock client with counter for IDs."""
        self.epic_counter = 1000
        self.story_counter = 2000
        self.created_items = []
    
    def create_epic(self, epic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate creating an epic in JIRA.
        
        Args:
            epic_data: Epic information (summary, description, etc.)
            
        Returns:
            Mock response with epic key and link
        """
        epic_key = f"LOG-{self.epic_counter}"
        self.epic_counter += 1
        
        result = {
            "key": epic_key,
            "id": str(self.epic_counter),
            "url": f"https://salling-group.atlassian.net/browse/{epic_key}",
            "summary": epic_data.get("summary", "Untitled Epic"),
            "status": "To Do",
            "created": True
        }
        
        self.created_items.append({
            "type": "epic",
            "data": result,
            "payload": epic_data
        })
        
        return result
    
    def create_story(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate creating a story in JIRA.
        
        Args:
            story_data: Story information (summary, description, etc.)
            
        Returns:
            Mock response with story key and link
        """
        story_key = f"LOG-{self.story_counter}"
        self.story_counter += 1
        
        result = {
            "key": story_key,
            "id": str(self.story_counter),
            "url": f"https://salling-group.atlassian.net/browse/{story_key}",
            "summary": story_data.get("summary", "Untitled Story"),
            "status": "To Do",
            "created": True
        }
        
        self.created_items.append({
            "type": "story",
            "data": result,
            "payload": story_data
        })
        
        return result
    
    def link_story_to_epic(self, story_key: str, epic_key: str) -> bool:
        """
        Simulate linking a story to an epic.
        
        Args:
            story_key: Story identifier
            epic_key: Epic identifier
            
        Returns:
            True if successful
        """
        # In mock mode, always succeed
        self.created_items.append({
            "type": "link",
            "story": story_key,
            "epic": epic_key
        })
        return True
    
    def get_created_items(self) -> List[Dict[str, Any]]:
        """Get list of all items created in this session."""
        return self.created_items.copy()
    
    def get_api_payload_preview(self, epic_data: Dict[str, Any]) -> str:
        """
        Generate a preview of what would be sent to real JIRA API.
        Useful for testing and validation.
        """
        payload = {
            "fields": {
                "project": {"key": "LOG"},
                "summary": epic_data.get("summary", ""),
                "description": epic_data.get("description", ""),
                "issuetype": {"name": "Epic"},
                "customfield_10011": epic_data.get("epic_name", ""),  # Epic Name field
                "labels": epic_data.get("labels", []),
                "priority": {"name": epic_data.get("priority", "Medium")}
            }
        }
        return json.dumps(payload, indent=2)


class RealJiraClient(JiraClient):
    """
    Real JIRA client using requests library.
    Requires authentication credentials in environment variables.
    """
    
    def __init__(self):
        """Initialize with credentials from environment."""
        self.base_url = os.getenv("JIRA_URL", "")
        self.email = os.getenv("JIRA_EMAIL", "")
        self.api_token = os.getenv("JIRA_API_TOKEN", "")
        
        if not all([self.base_url, self.email, self.api_token]):
            raise ValueError("JIRA credentials not configured. Set JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN")
        
        self.auth = (self.email, self.api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def create_epic(self, epic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an epic via JIRA REST API."""
        import requests
        
        url = f"{self.base_url}/rest/api/3/issue"
        
        payload = {
            "fields": {
                "project": {"key": epic_data.get("project_key", "LOG")},
                "summary": epic_data.get("summary", ""),
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": epic_data.get("description", "")}
                            ]
                        }
                    ]
                },
                "issuetype": {"name": "Epic"},
                "customfield_10011": epic_data.get("epic_name", epic_data.get("summary", "")),
            }
        }
        
        try:
            response = requests.post(url, json=payload, auth=self.auth, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            return {
                "key": result.get("key"),
                "id": result.get("id"),
                "url": f"{self.base_url}/browse/{result.get('key')}",
                "created": True
            }
        except Exception as e:
            return {
                "created": False,
                "error": str(e)
            }
    
    def create_story(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a story via JIRA REST API."""
        import requests
        
        url = f"{self.base_url}/rest/api/3/issue"
        
        payload = {
            "fields": {
                "project": {"key": story_data.get("project_key", "LOG")},
                "summary": story_data.get("summary", ""),
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": story_data.get("description", "")}
                            ]
                        }
                    ]
                },
                "issuetype": {"name": "Story"},
            }
        }
        
        try:
            response = requests.post(url, json=payload, auth=self.auth, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            return {
                "key": result.get("key"),
                "id": result.get("id"),
                "url": f"{self.base_url}/browse/{result.get('key')}",
                "created": True
            }
        except Exception as e:
            return {
                "created": False,
                "error": str(e)
            }
    
    def link_story_to_epic(self, story_key: str, epic_key: str) -> bool:
        """Link story to epic via JIRA REST API."""
        import requests
        
        url = f"{self.base_url}/rest/api/3/issue/{story_key}"
        
        payload = {
            "fields": {
                "parent": {"key": epic_key}
            }
        }
        
        try:
            response = requests.put(url, json=payload, auth=self.auth, headers=self.headers, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error linking story to epic: {e}")
            return False
