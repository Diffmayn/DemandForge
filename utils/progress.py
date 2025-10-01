"""Progress calculation utilities for demand completion tracking."""
from typing import Dict, Any, List


def calculate_progress(tabs_data: Dict[str, Any]) -> float:
    """
    Calculate overall demand progress based on tab completion.
    
    Args:
        tabs_data: Dictionary containing all tab data
        
    Returns:
        Progress percentage (0-100)
    """
    tab_names = [
        "ideation", "requirements", "assessment", "design",
        "build", "validation", "deployment", "implementation", "closing"
    ]
    
    completed_tabs = 0
    
    for tab_name in tab_names:
        if is_tab_complete(tabs_data.get(tab_name, {})):
            completed_tabs += 1
    
    progress = (completed_tabs / len(tab_names)) * 100
    return round(progress, 1)


def is_tab_complete(tab_data: Dict[str, Any], threshold: float = 0.5) -> bool:
    """
    Determine if a tab is considered complete based on filled fields.
    
    Args:
        tab_data: Tab data dictionary
        threshold: Percentage of fields that must be filled (default 50%)
        
    Returns:
        True if tab meets completion threshold
    """
    if not tab_data or not isinstance(tab_data, dict):
        return False
    
    # Count non-empty fields
    total_fields = 0
    filled_fields = 0
    
    for key, value in tab_data.items():
        # Skip metadata fields
        if key.startswith("_"):
            continue
            
        total_fields += 1
        
        # Check if field has meaningful content
        if value is None:
            continue
        elif isinstance(value, str) and len(value.strip()) > 0:
            filled_fields += 1
        elif isinstance(value, (list, dict)) and len(value) > 0:
            filled_fields += 1
        elif isinstance(value, (int, float)) and value != 0:
            filled_fields += 1
        elif isinstance(value, bool):
            filled_fields += 1  # Booleans count if set
    
    if total_fields == 0:
        return False
    
    completion_rate = filled_fields / total_fields
    return completion_rate >= threshold


def get_completion_details(tabs_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get detailed completion information for all tabs.
    
    Args:
        tabs_data: Dictionary containing all tab data
        
    Returns:
        Dictionary with completion details per tab
    """
    tab_names = [
        "ideation", "requirements", "assessment", "design",
        "build", "validation", "deployment", "implementation", "closing"
    ]
    
    details = {}
    
    for tab_name in tab_names:
        tab_data = tabs_data.get(tab_name, {})
        
        if not isinstance(tab_data, dict):
            continue
        
        total = sum(1 for k in tab_data.keys() if not k.startswith("_"))
        filled = sum(
            1 for k, v in tab_data.items()
            if not k.startswith("_") and _is_field_filled(v)
        )
        
        details[tab_name] = {
            "total_fields": total,
            "filled_fields": filled,
            "completion_percentage": round((filled / total * 100) if total > 0 else 0, 1),
            "is_complete": is_tab_complete(tab_data)
        }
    
    return details


def _is_field_filled(value: Any) -> bool:
    """Helper to check if a field has meaningful content."""
    if value is None:
        return False
    elif isinstance(value, str):
        return len(value.strip()) > 0
    elif isinstance(value, (list, dict)):
        return len(value) > 0
    elif isinstance(value, (int, float)):
        return value != 0
    elif isinstance(value, bool):
        return True
    return False
