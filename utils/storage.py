"""Persistent storage for demands using JSON files."""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


class DemandStorage:
    """Simple JSON-based storage for all demands."""
    
    def __init__(self, storage_dir: str = "data"):
        """
        Initialize storage.
        
        Args:
            storage_dir: Directory to store demand JSON files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.index_file = self.storage_dir / "demands_index.json"
        
        # Create index if doesn't exist
        if not self.index_file.exists():
            self._save_index([])
    
    def _save_index(self, index: List[Dict[str, Any]]):
        """Save the demands index."""
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2, default=str)
    
    def _load_index(self) -> List[Dict[str, Any]]:
        """Load the demands index."""
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_demand(self, demand_data: Dict[str, Any]) -> bool:
        """
        Save a demand to storage.
        
        Args:
            demand_data: Complete demand data including all phases
            
        Returns:
            True if successful
        """
        try:
            demand_id = demand_data.get('demand_id', 'UNKNOWN')
            
            # Save full demand data to individual file
            demand_file = self.storage_dir / f"{demand_id}.json"
            with open(demand_file, 'w') as f:
                json.dump(demand_data, f, indent=2, default=str)
            
            # Update index with summary info
            index = self._load_index()
            
            # Remove old entry if exists
            index = [d for d in index if d.get('demand_id') != demand_id]
            
            # Add new entry
            summary = {
                'demand_id': demand_id,
                'title': demand_data.get('ideation', {}).get('title', 'Untitled'),
                'description': demand_data.get('ideation', {}).get('description', ''),
                'status': demand_data.get('status', 'Draft'),
                'start_time': demand_data.get('start_time'),
                'last_modified': demand_data.get('last_modified'),
                'progress_percentage': demand_data.get('progress_percentage', 0),
                'stakeholders': [s.get('name', '') for s in demand_data.get('requirements', {}).get('stakeholders', [])],
                'user_stories': demand_data.get('requirements', {}).get('user_stories', ''),
                'test_cases_count': len(demand_data.get('validation', {}).get('test_cases', '').split('\n')),
                'risks': demand_data.get('assessment', {}).get('risks', ''),
            }
            
            index.append(summary)
            self._save_index(index)
            
            return True
            
        except Exception as e:
            print(f"Error saving demand: {e}")
            return False
    
    def load_demand(self, demand_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a specific demand.
        
        Args:
            demand_id: ID of the demand to load
            
        Returns:
            Demand data or None if not found
        """
        try:
            demand_file = self.storage_dir / f"{demand_id}.json"
            if demand_file.exists():
                with open(demand_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading demand {demand_id}: {e}")
        
        return None
    
    def get_all_demands_summary(self) -> List[Dict[str, Any]]:
        """
        Get summary of all demands (from index).
        
        Returns:
            List of demand summaries
        """
        return self._load_index()
    
    def get_all_demands_full(self) -> List[Dict[str, Any]]:
        """
        Get full data for all demands.
        Warning: Can be memory intensive for large datasets.
        
        Returns:
            List of complete demand data
        """
        demands = []
        index = self._load_index()
        
        for summary in index:
            demand_id = summary.get('demand_id')
            if demand_id:
                demand = self.load_demand(demand_id)
                if demand:
                    demands.append(demand)
        
        return demands
    
    def search_demands(self, query: str) -> List[Dict[str, Any]]:
        """
        Search demands by keyword.
        
        Args:
            query: Search query
            
        Returns:
            List of matching demand summaries
        """
        query_lower = query.lower()
        index = self._load_index()
        
        results = []
        for demand in index:
            # Search in title, description, user stories, risks
            searchable = f"{demand.get('title', '')} {demand.get('description', '')} {demand.get('user_stories', '')} {demand.get('risks', '')}".lower()
            
            if query_lower in searchable:
                results.append(demand)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all demands.
        
        Returns:
            Statistics dictionary
        """
        index = self._load_index()
        
        total = len(index)
        by_status = {}
        total_progress = 0
        
        for demand in index:
            status = demand.get('status', 'Unknown')
            by_status[status] = by_status.get(status, 0) + 1
            total_progress += demand.get('progress_percentage', 0)
        
        avg_progress = total_progress / total if total > 0 else 0
        
        return {
            'total_demands': total,
            'by_status': by_status,
            'average_progress': avg_progress,
            'most_recent': index[-1] if index else None
        }
    
    def delete_demand(self, demand_id: str) -> bool:
        """
        Delete a demand.
        
        Args:
            demand_id: ID of demand to delete
            
        Returns:
            True if successful
        """
        try:
            # Delete file
            demand_file = self.storage_dir / f"{demand_id}.json"
            if demand_file.exists():
                demand_file.unlink()
            
            # Update index
            index = self._load_index()
            index = [d for d in index if d.get('demand_id') != demand_id]
            self._save_index(index)
            
            return True
            
        except Exception as e:
            print(f"Error deleting demand {demand_id}: {e}")
            return False


# Global storage instance
_storage = None

def get_storage() -> DemandStorage:
    """Get or create the global storage instance."""
    global _storage
    if _storage is None:
        _storage = DemandStorage()
    return _storage
