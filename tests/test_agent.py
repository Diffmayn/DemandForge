"""Tests for AI agent functionality."""
import pytest
from agents.mock_agent import MockAgent


class TestMockAgent:
    """Test suite for MockAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        return MockAgent()
    
    @pytest.fixture
    def sample_context(self):
        """Sample context data."""
        return {
            "ideation": {
                "problem_statement": "Inefficient logistics tracking",
                "goals": "Improve delivery accuracy by 20%"
            },
            "assessment": {
                "estimated_duration_weeks": 12,
                "roi_percentage": 25.0
            },
            "requirements": {
                "stakeholders": [
                    {"name": "John Doe", "role": "BA"},
                    {"name": "Jane Smith", "role": "PO"}
                ],
                "user_stories": "As a user, I want to track shipments"
            }
        }
    
    def test_generate_problem_analysis(self, agent, sample_context):
        """Test problem analysis generation."""
        query = "analyze the problem"
        response = agent.generate(query, sample_context)
        
        assert response is not None
        assert len(response) > 0
        assert "5 Whys" in response or "problem" in response.lower()
    
    def test_generate_user_stories(self, agent, sample_context):
        """Test user story generation."""
        query = "generate user stories"
        response = agent.generate(query, sample_context)
        
        assert response is not None
        assert "As a" in response
        assert "I want" in response
        assert "so that" in response
    
    def test_generate_risk_analysis(self, agent, sample_context):
        """Test risk prediction."""
        query = "what are the risks?"
        response = agent.generate(query, sample_context)
        
        assert response is not None
        assert "risk" in response.lower()
        assert any(severity in response for severity in ["Critical", "High", "Medium", "Low"])
    
    def test_generate_test_suggestions(self, agent, sample_context):
        """Test test case generation."""
        query = "create test cases"
        response = agent.generate(query, sample_context)
        
        assert response is not None
        assert "test" in response.lower()
    
    def test_suggest_stories(self, agent):
        """Test story suggestion method."""
        goals = "Improve system performance and user experience"
        stories = agent.suggest_stories(goals, {})
        
        assert isinstance(stories, list)
        assert len(stories) > 0
        assert all("As a" in story for story in stories)
    
    def test_predict_risks_long_duration(self, agent, sample_context):
        """Test risk prediction for long projects."""
        sample_context["assessment"]["estimated_duration_weeks"] = 30
        risks = agent.predict_risks(sample_context)
        
        assert isinstance(risks, str)
        assert "HIGH" in risks or "Extended timeline" in risks
    
    def test_predict_risks_many_stakeholders(self, agent, sample_context):
        """Test risk prediction with many stakeholders."""
        sample_context["requirements"]["stakeholders"] = [
            {"name": f"Person {i}", "role": "Role"} for i in range(15)
        ]
        risks = agent.predict_risks(sample_context)
        
        assert "stakeholder" in risks.lower()
    
    def test_generate_test_cases(self, agent):
        """Test test case generation from requirements."""
        requirements = "System must handle 1000 concurrent users"
        stories = "As a user, I want fast response times\nAs a admin, I want to monitor system health"
        
        test_cases = agent.generate_test_cases(requirements, stories)
        
        assert isinstance(test_cases, str)
        assert "Test Case" in test_cases
        assert len(test_cases) > 0
    
    def test_generate_architecture_advice(self, agent, sample_context):
        """Test architecture guidance."""
        query = "suggest architecture"
        response = agent.generate(query, sample_context)
        
        assert response is not None
        assert any(word in response.lower() for word in ["architecture", "design", "pattern"])
    
    def test_generate_estimation_advice(self, agent, sample_context):
        """Test estimation guidance."""
        query = "help with estimation"
        response = agent.generate(query, sample_context)
        
        assert response is not None
        assert any(word in response.lower() for word in ["cost", "estimate", "timeline"])
    
    def test_generate_with_empty_context(self, agent):
        """Test generation with minimal context."""
        query = "help me get started"
        response = agent.generate(query, {})
        
        assert response is not None
        assert len(response) > 0
    
    def test_response_sanitization(self, agent, sample_context):
        """Test that responses don't contain sensitive info."""
        query = "what should I do?"
        response = agent.generate(query, sample_context)
        
        # Should not contain placeholder tokens
        assert "[REDACTED]" not in response
        assert "TODO" not in response
