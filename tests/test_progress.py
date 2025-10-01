"""Tests for progress calculation utilities."""
import pytest
from utils.progress import calculate_progress, is_tab_complete, get_completion_details


class TestIsTabComplete:
    """Test tab completion detection."""
    
    def test_empty_tab(self):
        """Test empty tab is not complete."""
        tab_data = {}
        assert is_tab_complete(tab_data) is False
    
    def test_partially_filled_tab(self):
        """Test partially filled tab."""
        tab_data = {
            "field1": "value",
            "field2": "",
            "field3": None,
            "field4": ""
        }
        assert is_tab_complete(tab_data, threshold=0.3) is False
    
    def test_mostly_filled_tab(self):
        """Test mostly filled tab is complete."""
        tab_data = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3",
            "field4": ""
        }
        assert is_tab_complete(tab_data, threshold=0.5) is True
    
    def test_fully_filled_tab(self):
        """Test fully filled tab."""
        tab_data = {
            "field1": "value1",
            "field2": "value2",
            "field3": 123,
            "field4": ["item"]
        }
        assert is_tab_complete(tab_data) is True
    
    def test_list_field(self):
        """Test tab with list field."""
        tab_data = {
            "field1": "value",
            "field2": ["item1", "item2"]
        }
        assert is_tab_complete(tab_data) is True
    
    def test_dict_field(self):
        """Test tab with dict field."""
        tab_data = {
            "field1": "value",
            "field2": {"key": "value"}
        }
        assert is_tab_complete(tab_data) is True
    
    def test_metadata_fields_ignored(self):
        """Test that _metadata fields are ignored."""
        tab_data = {
            "_internal": "ignored",
            "field1": "value"
        }
        # Only field1 counts, and it's filled
        assert is_tab_complete(tab_data) is True


class TestCalculateProgress:
    """Test overall progress calculation."""
    
    def test_no_tabs_complete(self):
        """Test with no tabs filled."""
        tabs_data = {
            "ideation": {},
            "requirements": {},
            "assessment": {},
            "design": {},
            "build": {},
            "validation": {},
            "deployment": {},
            "implementation": {},
            "closing": {}
        }
        progress = calculate_progress(tabs_data)
        assert progress == 0
    
    def test_all_tabs_complete(self):
        """Test with all tabs filled."""
        filled_tab = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        }
        tabs_data = {
            "ideation": filled_tab.copy(),
            "requirements": filled_tab.copy(),
            "assessment": filled_tab.copy(),
            "design": filled_tab.copy(),
            "build": filled_tab.copy(),
            "validation": filled_tab.copy(),
            "deployment": filled_tab.copy(),
            "implementation": filled_tab.copy(),
            "closing": filled_tab.copy()
        }
        progress = calculate_progress(tabs_data)
        assert progress == 100.0
    
    def test_partial_progress(self):
        """Test with some tabs complete."""
        filled_tab = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        }
        tabs_data = {
            "ideation": filled_tab.copy(),
            "requirements": filled_tab.copy(),
            "assessment": {},
            "design": {},
            "build": {},
            "validation": {},
            "deployment": {},
            "implementation": {},
            "closing": {}
        }
        progress = calculate_progress(tabs_data)
        # 2 out of 9 tabs = ~22%
        assert 20 <= progress <= 25


class TestGetCompletionDetails:
    """Test detailed completion information."""
    
    def test_get_details_empty_tabs(self):
        """Test details for empty tabs."""
        tabs_data = {
            "ideation": {},
            "requirements": {}
        }
        details = get_completion_details(tabs_data)
        
        assert "ideation" in details
        assert details["ideation"]["total_fields"] == 0
        assert details["ideation"]["filled_fields"] == 0
    
    def test_get_details_filled_tabs(self):
        """Test details for filled tabs."""
        tabs_data = {
            "ideation": {
                "problem_statement": "Test problem",
                "goals": "Test goals",
                "background": ""
            }
        }
        details = get_completion_details(tabs_data)
        
        assert details["ideation"]["total_fields"] == 3
        assert details["ideation"]["filled_fields"] == 2
        assert details["ideation"]["completion_percentage"] > 0
    
    def test_get_details_all_tabs(self):
        """Test details for all standard tabs."""
        filled_tab = {"field1": "value", "field2": "value"}
        tabs_data = {
            "ideation": filled_tab.copy(),
            "requirements": filled_tab.copy(),
            "assessment": filled_tab.copy(),
            "design": filled_tab.copy(),
            "build": filled_tab.copy(),
            "validation": filled_tab.copy(),
            "deployment": filled_tab.copy(),
            "implementation": filled_tab.copy(),
            "closing": filled_tab.copy()
        }
        details = get_completion_details(tabs_data)
        
        assert len(details) == 9
        for tab_name in tabs_data.keys():
            assert tab_name in details
            assert details[tab_name]["is_complete"] is True
