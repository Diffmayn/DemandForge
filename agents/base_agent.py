"""Base agent interface for AI assistance."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseAgent(ABC):
    """Abstract base class for AI agents."""
    
    @abstractmethod
    def generate(
        self,
        query: str,
        context: Dict[str, Any],
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Generate AI response based on query and context.
        
        Args:
            query: User's question or request
            context: Current demand data and tab information
            chat_history: Previous conversation messages
            
        Returns:
            Generated response string
        """
        pass
    
    @abstractmethod
    def suggest_stories(self, goals: str, context: Dict[str, Any]) -> List[str]:
        """
        Generate user story suggestions based on goals.
        
        Args:
            goals: Project goals text
            context: Additional context
            
        Returns:
            List of suggested user stories
        """
        pass
    
    @abstractmethod
    def predict_risks(self, project_data: Dict[str, Any]) -> str:
        """
        Predict potential risks based on project data.
        
        Args:
            project_data: Current demand information
            
        Returns:
            Risk prediction text
        """
        pass
    
    @abstractmethod
    def generate_test_cases(self, requirements: str, stories: str) -> str:
        """
        Generate test cases from requirements and user stories.
        
        Args:
            requirements: Requirements text
            stories: User stories text
            
        Returns:
            Generated test cases
        """
        pass
