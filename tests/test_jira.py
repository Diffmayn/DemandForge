"""Tests for JIRA integration."""
import pytest
from integrations.jira_client import MockJiraClient


class TestMockJiraClient:
    """Test suite for MockJiraClient."""
    
    @pytest.fixture
    def client(self):
        """Create client instance for testing."""
        return MockJiraClient()
    
    def test_create_epic(self, client):
        """Test epic creation."""
        epic_data = {
            "summary": "Test Epic",
            "description": "Epic description",
            "epic_name": "TEST-001",
            "labels": ["test"]
        }
        
        result = client.create_epic(epic_data)
        
        assert result["created"] is True
        assert "key" in result
        assert result["key"].startswith("LOG-")
        assert "url" in result
        assert "salling-group.atlassian.net" in result["url"]
    
    def test_create_story(self, client):
        """Test story creation."""
        story_data = {
            "summary": "Test Story",
            "description": "Story description"
        }
        
        result = client.create_story(story_data)
        
        assert result["created"] is True
        assert "key" in result
        assert result["key"].startswith("LOG-")
        assert result["status"] == "To Do"
    
    def test_link_story_to_epic(self, client):
        """Test linking story to epic."""
        result = client.link_story_to_epic("LOG-2001", "LOG-1001")
        
        assert result is True
    
    def test_get_created_items(self, client):
        """Test retrieving created items."""
        # Create some items
        client.create_epic({"summary": "Epic 1"})
        client.create_story({"summary": "Story 1"})
        
        items = client.get_created_items()
        
        assert len(items) >= 2
        assert any(item["type"] == "epic" for item in items)
        assert any(item["type"] == "story" for item in items)
    
    def test_get_api_payload_preview(self, client):
        """Test API payload preview generation."""
        epic_data = {
            "summary": "Test Epic",
            "description": "Description",
            "epic_name": "TEST",
            "labels": ["label1"],
            "priority": "High"
        }
        
        payload = client.get_api_payload_preview(epic_data)
        
        assert "fields" in payload
        assert "project" in payload
        assert "TEST" in payload
    
    def test_multiple_epics_unique_ids(self, client):
        """Test that multiple epics get unique IDs."""
        result1 = client.create_epic({"summary": "Epic 1"})
        result2 = client.create_epic({"summary": "Epic 2"})
        
        assert result1["key"] != result2["key"]
        assert result1["id"] != result2["id"]
