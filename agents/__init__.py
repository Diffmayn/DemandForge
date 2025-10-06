"""AI agent modules for DemandForge."""
from .mock_agent import MockAgent
from .base_agent import BaseAgent

# Try to import GeminiAgent (optional dependency)
try:
    from .gemini_agent import GeminiAgent
    __all__ = ["MockAgent", "BaseAgent", "GeminiAgent"]
except ImportError:
    __all__ = ["MockAgent", "BaseAgent"]
