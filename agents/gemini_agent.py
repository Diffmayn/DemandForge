"""Google Gemini AI agent with RAG capabilities."""
import os
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from .base_agent import BaseAgent


class GeminiAgent(BaseAgent):
    """
    Google Gemini AI agent with full context awareness.
    Has access to all demands, stories, test cases, etc. via RAG.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini agent with API key.
        
        Args:
            api_key: Google API key (if None, reads from GEMINI_API_KEY env var)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-genai not installed. Run: pip install google-genai"
            )
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize the client (automatically uses GEMINI_API_KEY env var)
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"
        
        # Generation config (disable thinking for speed)
        self.config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
            thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking for speed
        )
    
    def _build_context_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build comprehensive context from all demand data.
        
        Args:
            context: Current demand and historical data
            
        Returns:
            Formatted context string
        """
        prompt_parts = [
            "# DemandForge AI Co-Pilot - System-Wide Context",
            "",
            "You are an expert AI assistant for DemandForge, the IT demand management system at Salling Group.",
            "You have COMPLETE ACCESS to ALL demands across the entire system, including:",
            "- Every demand ever created (current and historical)",
            "- All user stories, features, tasks, and test cases",
            "- All stakeholders, assessments, risks, and designs",
            "- Complete audit trails and chat histories",
            "",
            "## System-Wide Statistics:",
            ""
        ]
        
        # Add system statistics
        historical_demands = context.get("historical_demands", [])
        if historical_demands:
            total_demands = len(historical_demands)
            statuses = {}
            for demand in historical_demands:
                status = demand.get('status', 'Unknown')
                statuses[status] = statuses.get(status, 0) + 1
            
            prompt_parts.append(f"**Total Demands in System**: {total_demands}")
            prompt_parts.append(f"**Demand Status Breakdown**: {', '.join([f'{k}: {v}' for k, v in statuses.items()])}")
            prompt_parts.append("")
            
            # Show recent demands
            prompt_parts.append("**Recent Demands** (last 5):")
            for demand in historical_demands[-5:]:
                prompt_parts.append(f"- {demand.get('demand_id', 'N/A')}: {demand.get('title', 'Untitled')} ({demand.get('status', 'Unknown')}) - {demand.get('progress_percentage', 0)}% complete")
            prompt_parts.append("")
        
        prompt_parts.extend([
            "## Current Demand Information:",
            ""
        ])
        
        # Current demand ID
        if "demand_id" in context:
            prompt_parts.append(f"**Demand ID**: {context['demand_id']}")
            prompt_parts.append("")
        
        # Ideation phase
        if "ideation" in context and context["ideation"]:
            prompt_parts.append("### Ideation Phase:")
            ideation = context["ideation"]
            if ideation.get("title"):
                prompt_parts.append(f"- Title: {ideation['title']}")
            if ideation.get("problem_statement"):
                prompt_parts.append(f"- Problem: {ideation['problem_statement'][:200]}")
            if ideation.get("goals"):
                prompt_parts.append(f"- Goals: {ideation['goals'][:200]}")
            prompt_parts.append("")
        
        # Requirements phase
        if "requirements" in context and context["requirements"]:
            req = context["requirements"]
            prompt_parts.append("### Requirements Phase:")
            
            stakeholders = req.get("stakeholders", [])
            if stakeholders:
                prompt_parts.append(f"- Stakeholders: {len(stakeholders)} defined")
                for sh in stakeholders[:3]:  # Show first 3
                    prompt_parts.append(f"  - {sh.get('name', 'N/A')}: {sh.get('role', 'N/A')}")
            
            if req.get("user_stories"):
                stories = req["user_stories"][:300]
                prompt_parts.append(f"- User Stories: {stories}")
            
            if req.get("features"):
                prompt_parts.append(f"- Features: {len(req['features'])} defined")
            
            prompt_parts.append("")
        
        # Assessment phase
        if "assessment" in context and context["assessment"]:
            assess = context["assessment"]
            prompt_parts.append("### Assessment Phase:")
            
            if assess.get("roi_percentage"):
                prompt_parts.append(f"- ROI: {assess['roi_percentage']}%")
            if assess.get("estimated_duration_weeks"):
                prompt_parts.append(f"- Duration: {assess['estimated_duration_weeks']} weeks")
            if assess.get("risks"):
                prompt_parts.append(f"- Risks identified: Yes")
            
            prompt_parts.append("")
        
        # Design phase
        if "design" in context and context["design"]:
            design = context["design"]
            prompt_parts.append("### Design Phase:")
            
            if design.get("technical_stack"):
                prompt_parts.append(f"- Tech Stack: {design['technical_stack'][:150]}")
            if design.get("architecture_overview"):
                prompt_parts.append(f"- Architecture: {design['architecture_overview'][:150]}")
            
            prompt_parts.append("")
        
        # Build phase
        if "build" in context and context["build"]:
            build = context["build"]
            prompt_parts.append("### Build Phase:")
            
            tasks = build.get("tasks", [])
            if tasks:
                prompt_parts.append(f"- Tasks: {len(tasks)} defined")
                for task in tasks[:3]:
                    prompt_parts.append(f"  - {task}")
            
            if build.get("jira_epic_id"):
                prompt_parts.append(f"- JIRA Epic: {build['jira_epic_id']}")
            
            prompt_parts.append("")
        
        # Validation phase
        if "validation" in context and context["validation"]:
            val = context["validation"]
            prompt_parts.append("### Validation Phase:")
            
            if val.get("test_cases"):
                prompt_parts.append(f"- Test Cases: Defined")
            if val.get("qa_sign_off"):
                prompt_parts.append(f"- QA Sign-off: {'✅ Approved' if val['qa_sign_off'] else '⏳ Pending'}")
            
            prompt_parts.append("")
        
        prompt_parts.extend([
            "## Your Capabilities & Role:",
            "",
            "You have FULL ACCESS to:",
            "1. **All Demands**: You can see and reference ANY demand in the system by ID",
            "2. **Complete History**: All user stories, test cases, features from all demands",
            "3. **System Statistics**: Total count of demands, status breakdowns, progress metrics",
            "4. **Cross-Demand Analysis**: Compare and learn from similar past demands",
            "",
            "When answering questions:",
            "- If asked about system totals, reference the System-Wide Statistics above",
            "- If asked about other demands, search through historical_demands data",
            "- If asked about patterns, analyze multiple demands to provide insights",
            "- Always be specific and reference actual data when available",
            "- Provide actionable, specific advice based on the complete context",
            "- Use markdown formatting for clarity",
            "",
            "**IMPORTANT**: You can answer questions about:",
            "- How many total demands exist in the system",
            "- Statistics about all demands (status, progress, etc.)",
            "- Specific details from any demand by ID",
            "- Patterns and trends across multiple demands",
            "- Comparisons between current and historical demands",
            "",
            "Now respond to the user's query below:",
            ""
        ])
        
        return "\n".join(prompt_parts)
    
    def generate(
        self,
        query: str,
        context: Dict[str, Any],
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Generate AI response using Gemini with full context.
        
        Args:
            query: User's question or request
            context: Current demand data and historical context
            chat_history: Previous conversation messages
            
        Returns:
            Generated response string
        """
        try:
            # Build context-aware prompt
            context_prompt = self._build_context_prompt(context)
            full_prompt = f"{context_prompt}\n**User Query**: {query}"
            
            # Generate response using new API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=self.config
            )
            
            return response.text
            
        except Exception as e:
            return f"❌ Error generating response: {str(e)}\n\nPlease check your API key and try again."
    
    def suggest_stories(self, goals: str, context: Dict[str, Any]) -> List[str]:
        """
        Generate user story suggestions using Gemini.
        
        Args:
            goals: Project goals text
            context: Additional context including historical demands
            
        Returns:
            List of suggested user stories
        """
        try:
            prompt = f"""Based on the following project goals, generate 5 user stories in INVEST format:

Goals: {goals}

Context:
- Company: Salling Group (Danish retail)
- Format: "As a [role], I want [feature], so that [benefit]"
- Make them specific, actionable, and measurable

Historical similar demands:
{json.dumps(context.get('historical_demands', [])[:2], indent=2)}

Generate 5 user stories:"""
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.config
            )
            
            # Parse response into list
            stories_text = response.text
            stories = [line.strip() for line in stories_text.split('\n') if line.strip() and ('As a' in line or line[0].isdigit())]
            
            return stories[:5] if stories else [stories_text]
            
        except Exception as e:
            return [f"❌ Error: {str(e)}"]
    
    def predict_risks(self, project_data: Dict[str, Any]) -> str:
        """
        Predict risks using Gemini with historical context.
        
        Args:
            project_data: Current demand information
            
        Returns:
            Risk prediction text
        """
        try:
            prompt = f"""Analyze the following IT project and identify key risks with mitigation strategies:

Project Data:
{json.dumps(project_data, indent=2, default=str)}

Provide risks in this format:
🔴 CRITICAL: [risk] → [mitigation]
🟡 MEDIUM: [risk] → [mitigation]
🟢 LOW: [risk] → [mitigation]

Focus on: integration complexity, timeline, scope creep, resource availability, and technical challenges."""
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.config
            )
            return response.text
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def generate_test_cases(self, requirements: str, stories: str) -> str:
        """
        Generate test cases using Gemini.
        
        Args:
            requirements: Requirements text
            stories: User stories text
            
        Returns:
            Generated test cases
        """
        try:
            prompt = f"""Generate comprehensive test cases for the following requirements and user stories:

Requirements:
{requirements[:500]}

User Stories:
{stories[:500]}

Generate test cases covering:
1. Happy path scenarios (3-5 cases)
2. Edge cases (2-3 cases)
3. Error handling (2-3 cases)
4. Security tests (1-2 cases)

Format each as:
**Test Case N**: [Description]
- **Given**: [precondition]
- **When**: [action]
- **Then**: [expected result]"""
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.config
            )
            return response.text
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def search_historical_demands(
        self,
        query: str,
        all_demands: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Search historical demands for similar patterns (simple keyword matching).
        In production, this would use vector embeddings.
        
        Args:
            query: Search query
            all_demands: List of all historical demands
            
        Returns:
            List of relevant demands
        """
        query_lower = query.lower()
        keywords = query_lower.split()
        
        scored_demands = []
        for demand in all_demands:
            score = 0
            
            # Check problem statement
            problem = demand.get("ideation", {}).get("problem_statement", "").lower()
            score += sum(2 for kw in keywords if kw in problem)
            
            # Check goals
            goals = demand.get("ideation", {}).get("goals", "").lower()
            score += sum(2 for kw in keywords if kw in goals)
            
            # Check tech stack
            tech = demand.get("design", {}).get("technical_stack", "").lower()
            score += sum(1 for kw in keywords if kw in tech)
            
            if score > 0:
                scored_demands.append((score, demand))
        
        # Sort by score and return top 5
        scored_demands.sort(reverse=True, key=lambda x: x[0])
        return [d[1] for d in scored_demands[:5]]
