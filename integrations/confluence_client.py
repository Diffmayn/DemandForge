"""Confluence integration client for document export."""
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import os


class ConfluenceClient(ABC):
    """Abstract base class for Confluence integration."""
    
    @abstractmethod
    def create_page(self, space_key: str, title: str, content: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a page in Confluence."""
        pass
    
    @abstractmethod
    def update_page(self, page_id: str, title: str, content: str, version: int) -> Dict[str, Any]:
        """Update an existing Confluence page."""
        pass


class MockConfluenceClient(ConfluenceClient):
    """
    Mock Confluence client for development and testing.
    Simulates document creation without actual API calls.
    """
    
    def __init__(self):
        """Initialize mock client with page counter."""
        self.page_counter = 1000
        self.created_pages = []
    
    def create_page(self, space_key: str, title: str, content: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulate creating a Confluence page.
        
        Args:
            space_key: Confluence space identifier
            title: Page title
            content: Page content (HTML or markdown)
            parent_id: Optional parent page ID
            
        Returns:
            Mock response with page details
        """
        page_id = str(self.page_counter)
        self.page_counter += 1
        
        result = {
            "id": page_id,
            "title": title,
            "url": f"https://salling-group.atlassian.net/wiki/spaces/{space_key}/pages/{page_id}/{title.replace(' ', '+')}",
            "space": space_key,
            "version": 1,
            "created": True
        }
        
        self.created_pages.append({
            "type": "create",
            "data": result,
            "content_preview": content[:200]
        })
        
        return result
    
    def update_page(self, page_id: str, title: str, content: str, version: int) -> Dict[str, Any]:
        """
        Simulate updating a Confluence page.
        
        Args:
            page_id: Page identifier
            title: Updated title
            content: Updated content
            version: Current version number (will be incremented)
            
        Returns:
            Mock response with updated page details
        """
        new_version = version + 1
        
        result = {
            "id": page_id,
            "title": title,
            "version": new_version,
            "updated": True
        }
        
        self.created_pages.append({
            "type": "update",
            "data": result,
            "content_preview": content[:200]
        })
        
        return result
    
    def get_created_pages(self) -> list:
        """Get list of all pages created/updated in this session."""
        return self.created_pages.copy()
    
    def convert_markdown_to_confluence(self, markdown: str) -> str:
        """
        Convert markdown to Confluence wiki markup (simplified).
        Real implementation would use a library like markdown2confluence.
        """
        # Simple conversions for demo
        content = markdown
        content = content.replace("# ", "h1. ")
        content = content.replace("## ", "h2. ")
        content = content.replace("### ", "h3. ")
        content = content.replace("**", "*")
        content = content.replace("- ", "* ")
        
        return content


class RealConfluenceClient(ConfluenceClient):
    """
    Real Confluence client using requests library.
    Requires authentication credentials in environment variables.
    """
    
    def __init__(self):
        """Initialize with credentials from environment."""
        self.base_url = os.getenv("CONFLUENCE_URL", "")
        self.api_token = os.getenv("CONFLUENCE_API_TOKEN", "")
        self.email = os.getenv("JIRA_EMAIL", "")  # Often same as JIRA
        
        if not all([self.base_url, self.api_token, self.email]):
            raise ValueError("Confluence credentials not configured")
        
        self.auth = (self.email, self.api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def create_page(self, space_key: str, title: str, content: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a page via Confluence REST API."""
        import requests
        
        url = f"{self.base_url}/rest/api/content"
        
        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }
        
        if parent_id:
            payload["ancestors"] = [{"id": parent_id}]
        
        try:
            response = requests.post(url, json=payload, auth=self.auth, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            return {
                "id": result.get("id"),
                "title": result.get("title"),
                "url": f"{self.base_url}{result.get('_links', {}).get('webui', '')}",
                "version": result.get("version", {}).get("number", 1),
                "created": True
            }
        except Exception as e:
            return {
                "created": False,
                "error": str(e)
            }
    
    def update_page(self, page_id: str, title: str, content: str, version: int) -> Dict[str, Any]:
        """Update a page via Confluence REST API."""
        import requests
        
        url = f"{self.base_url}/rest/api/content/{page_id}"
        
        payload = {
            "type": "page",
            "title": title,
            "version": {"number": version + 1},
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }
        
        try:
            response = requests.put(url, json=payload, auth=self.auth, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            return {
                "id": result.get("id"),
                "title": result.get("title"),
                "version": result.get("version", {}).get("number"),
                "updated": True
            }
        except Exception as e:
            return {
                "updated": False,
                "error": str(e)
            }
