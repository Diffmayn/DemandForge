"""Mock AI agent for development and testing."""
import re
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent


class MockAgent(BaseAgent):
    """
    Mock AI agent that provides simulated intelligent responses.
    Future: Replace with real Watsonx/LangChain integration.
    """
    
    def __init__(self):
        """Initialize mock agent with response templates."""
        self.response_templates = {
            "ideation": [
                "Consider breaking down the problem using the 5 Whys technique.",
                "Have you identified all key stakeholders affected by this change?",
                "What metrics will define success for this initiative?"
            ],
            "requirements": [
                "Ensure each user story follows the format: As a [role], I want [feature], so that [benefit].",
                "Consider edge cases and error scenarios in your acceptance criteria.",
                "Have you validated these requirements with all stakeholder groups?"
            ],
            "assessment": [
                "Based on similar logistics demands, consider 15-20% contingency for scope creep.",
                "Integration points with external systems often introduce hidden complexity.",
                "Ensure your ROI calculation includes ongoing maintenance costs."
            ],
            "risks": [
                "High risk: Third-party API dependencies may cause delays",
                "Medium risk: Data migration complexity from legacy systems",
                "Low risk: Training requirements for end users"
            ]
        }
        
    def generate(
        self,
        query: str,
        context: Dict[str, Any],
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Generate contextual response based on query and current tab data.
        
        Args:
            query: User's question or request
            context: Current demand data
            chat_history: Previous messages (optional)
            
        Returns:
            Simulated AI response
        """
        query_lower = query.lower()
        
        # Check for specific keywords and provide relevant responses
        if any(word in query_lower for word in ["problem", "issue", "challenge"]):
            return self._generate_problem_analysis(query, context)
        
        elif any(word in query_lower for word in ["story", "stories", "requirement"]):
            return self._generate_user_stories(context)
        
        elif any(word in query_lower for word in ["risk", "threat", "concern"]):
            return self._generate_risk_analysis(context)
        
        elif any(word in query_lower for word in ["test", "testing", "qa"]):
            return self._generate_test_suggestions(context)
        
        elif any(word in query_lower for word in ["architecture", "design", "technical"]):
            return self._generate_architecture_advice(context)
        
        elif any(word in query_lower for word in ["estimate", "cost", "timeline"]):
            return self._generate_estimation_advice(context)
        
        else:
            return self._generate_general_response(query, context)
    
    def _generate_problem_analysis(self, query: str, context: Dict[str, Any]) -> str:
        """Generate problem analysis using 5 Whys approach."""
        problem = context.get("ideation", {}).get("problem_statement", "")
        
        if problem:
            return f"""Based on your problem statement, let's apply the 5 Whys:

**Root Cause Analysis:**
1. Why does this problem exist? → Likely process inefficiency or system limitation
2. Why hasn't it been solved? → May lack visibility or prioritization
3. Why is it critical now? → Business impact or compliance requirement
4. Why will the solution work? → Addresses root cause, not symptoms
5. Why invest resources here? → Measurable ROI and strategic alignment

**Recommendation:** Focus on quantifying the business impact with specific metrics (e.g., "reduces processing time by X hours/week" or "prevents €Y in lost sales")."""
        else:
            return "Start by clearly defining the problem statement. What specific pain point are you solving? Who experiences it and how frequently?"
    
    def _generate_user_stories(self, context: Dict[str, Any]) -> str:
        """Generate user story suggestions."""
        goals = context.get("ideation", {}).get("goals", "")
        
        stories = """**Suggested User Stories:**

📝 **As a** Business Analyst, **I want** to document all demand requirements in one place, **so that** stakeholders have a single source of truth.

📝 **As a** Product Owner, **I want** to track the status of IT demands in real-time, **so that** I can prioritize effectively.

📝 **As a** Developer, **I want** to access clear acceptance criteria, **so that** I can implement features correctly.

📝 **As a** Stakeholder, **I want** to receive automated updates on demand progress, **so that** I stay informed without manual check-ins.

**Tips:**
- Each story should be independently valuable
- Include acceptance criteria with measurable outcomes
- Consider both happy path and edge cases"""

        if goals:
            stories += f"\n\n**Context from your goals:** Based on '{goals[:100]}...', also consider stories around integration points and data migration."
        
        return stories
    
    def _generate_risk_analysis(self, context: Dict[str, Any]) -> str:
        """Predict risks based on project context."""
        assessment = context.get("assessment", {})
        
        risks = """**Risk Assessment (RAG Analysis):**

🔴 **Critical Risks:**
- Integration dependencies with external systems (JIRA, Confluence, promo tools)
- Data quality and migration from legacy sources
- Mitigation: Early POC, data audit, fallback plans

🟡 **Medium Risks:**
- Stakeholder availability for requirements validation
- Scope creep due to evolving business needs
- Mitigation: Fixed review cadence, change control board

🟢 **Low Risks:**
- Technology stack maturity (Streamlit, Python)
- Team skill set alignment
- Mitigation: Standard best practices, code reviews

**Similar Project Insight:** Logistics demands typically experience 20% timeline extension due to integration complexity. Plan accordingly."""
        
        if assessment.get("estimated_duration_weeks", 0) > 26:
            risks += "\n\n⚠️ **Duration Alert:** Projects over 6 months have higher risk of requirement drift. Consider phased delivery."
        
        return risks
    
    def _generate_test_suggestions(self, context: Dict[str, Any]) -> str:
        """Generate test case suggestions."""
        requirements = context.get("requirements", {})
        stories = requirements.get("user_stories", "")
        
        tests = """**Suggested Test Cases:**

✅ **Functional Tests:**
1. Test: Create new demand with all required fields → Verify UUID generation and persistence
2. Test: Update demand in each tab → Verify cross-tab data flow and audit logging
3. Test: Export demand to JSON/PDF → Verify data completeness and format

✅ **Integration Tests:**
4. Test: Push epic to JIRA (mock) → Verify correct API payload and response handling
5. Test: AI agent query with context → Verify response relevance and sanitization

✅ **Edge Cases:**
6. Test: Session timeout after 1 hour → Verify data preservation and user warning
7. Test: Invalid input (XSS attempt) → Verify escaping and validation
8. Test: Maximum field lengths → Verify truncation and error messages

✅ **Performance Tests:**
9. Test: Load 100 historical demands → Verify caching and response time <2s
10. Test: Generate AI response with large context → Verify memory limits"""

        if stories:
            # Extract first story if present
            story_match = re.search(r'As a.*?so that.*?\.', stories, re.IGNORECASE | re.DOTALL)
            if story_match:
                first_story = story_match.group(0)[:100]
                tests += f"\n\n**Custom Test:** Based on '{first_story}...', ensure you test the complete workflow end-to-end."
        
        return tests
    
    def _generate_architecture_advice(self, context: Dict[str, Any]) -> str:
        """Provide architecture suggestions."""
        return """**Architecture Recommendations:**

🏗️ **Layered Design:**
- **Presentation:** Streamlit UI (tabs, forms, chat)
- **Business Logic:** Pydantic models, validation, cross-tab flows
- **Data Access:** Session state → SQLite → PostgreSQL (migration path)
- **Integrations:** Abstract clients for JIRA, Confluence, Watsonx

🔌 **Integration Patterns:**
- Use adapter pattern for external APIs (easy mocking/swapping)
- Implement circuit breaker for external calls (timeout, retry with backoff)
- Queue webhook triggers for async processing

🔐 **Security Considerations:**
- Input validation at model level (Pydantic)
- Output escaping (html.escape) for all user content
- Secrets in environment variables, never in code
- Audit log for GDPR compliance (who changed what, when)

📈 **Scalability Path:**
- POC: Session state (ephemeral)
- Stage 1: SQLite with file locking
- Stage 2: PostgreSQL with connection pooling
- Stage 3: Microservices for integrations (FastAPI)

**Pattern Example:** Use repository pattern for data access - abstract `DemandRepository` interface with implementations for session, SQLite, Postgres."""
    
    def _generate_estimation_advice(self, context: Dict[str, Any]) -> str:
        """Provide estimation guidance."""
        assessment = context.get("assessment", {})
        duration = assessment.get("estimated_duration_weeks", 0)
        
        advice = """**Estimation Best Practices:**

📊 **Effort Breakdown (Rule of Thumb):**
- Requirements & Design: 20%
- Development: 40%
- Testing & QA: 20%
- Deployment & Training: 10%
- Contingency: 10%

💰 **Cost Considerations:**
- Direct: Dev team time, infrastructure (Azure/AWS)
- Indirect: Stakeholder time, training, change management
- Hidden: Maintenance (15-20% of dev cost annually)

⏱️ **Timeline Factors:**
- Integration complexity: +25% per major external system
- Team availability: Adjust for holidays, concurrent projects
- Dependency chains: Identify critical path, parallelize where possible"""

        if duration > 0:
            adjusted = duration * 1.15
            advice += f"\n\n**Your Estimate:** {duration} weeks. With 15% contingency: ~{adjusted:.1f} weeks."
            
            if duration > 26:
                advice += "\n\n⚠️ Consider breaking into phases. Deliver MVP in 8-12 weeks, iterate based on feedback."
        
        return advice
    
    def _generate_general_response(self, query: str, context: Dict[str, Any]) -> str:
        """Generate general contextual response."""
        current_tab = context.get("current_tab", "Ideation")
        
        responses = {
            "Ideation": "Focus on clearly defining the problem and business value. Use specific metrics and stakeholder quotes.",
            "Requirements": "Ensure user stories are INVEST (Independent, Negotiable, Valuable, Estimable, Small, Testable).",
            "Assessment": "Quantify ROI with both hard savings (cost reduction) and soft benefits (efficiency, morale).",
            "Design": "Document key decisions and trade-offs. Future teams will thank you!",
            "Build": "Break tasks into <2-day increments for better tracking and risk visibility.",
            "Validation": "Test not just happy paths but failure modes. What happens when external APIs are down?",
            "Deployment": "Always have a rollback plan. Practice it before go-live.",
            "Implementation": "Define success metrics upfront. Monitor actively in first 30 days.",
            "Closing": "Capture lessons learned while fresh. They're valuable for RAG/future projects."
        }
        
        base_response = responses.get(current_tab, "How can I assist you with this demand?")
        
        return f"""💡 **Context-Aware Suggestion:**

{base_response}

**Your Query:** "{query}"

I can help you with:
- Generating user stories and requirements
- Identifying risks and mitigation strategies
- Creating test cases and acceptance criteria
- Providing architecture and design guidance
- Estimating effort and costs
- Best practices for each phase

Ask me specific questions like:
- "What risks should I consider?"
- "Generate user stories for this feature"
- "What test cases do I need?"
- "How should I structure the architecture?"
"""
    
    def suggest_stories(self, goals: str, context: Dict[str, Any]) -> List[str]:
        """Generate user story suggestions from goals."""
        stories = [
            f"As a user, I want to achieve {goals[:50] if goals else 'the stated objectives'}, so that business value is delivered.",
            "As a stakeholder, I want to receive progress updates, so that I can track project status.",
            "As a developer, I want clear acceptance criteria, so that I can implement correctly.",
            "As a QA engineer, I want comprehensive test cases, so that I can validate the solution."
        ]
        return stories
    
    def predict_risks(self, project_data: Dict[str, Any]) -> str:
        """Predict risks based on project characteristics."""
        risks = []
        
        # Analyze duration
        duration = project_data.get("assessment", {}).get("estimated_duration_weeks", 0)
        if duration > 26:
            risks.append("HIGH: Extended timeline increases risk of requirement changes and team turnover")
        elif duration > 12:
            risks.append("MEDIUM: Timeline requires careful milestone tracking")
        
        # Analyze stakeholders
        stakeholder_count = len(project_data.get("requirements", {}).get("stakeholders", []))
        if stakeholder_count > 10:
            risks.append("MEDIUM: Large stakeholder group may slow decision-making")
        elif stakeholder_count < 2:
            risks.append("LOW: Limited stakeholder input may miss requirements")
        
        # Check for integration mentions
        design = project_data.get("design", {}).get("integration_points", "").lower()
        if "api" in design or "integration" in design:
            risks.append("MEDIUM: External API dependencies may cause delays or failures")
        
        risks.append("GENERAL: All projects face scope creep - establish change control process")
        
        return "\n".join(f"• {risk}" for risk in risks)
    
    def generate_test_cases(self, requirements: str, stories: str) -> str:
        """Generate test cases from requirements and stories."""
        test_cases = []
        
        # Extract potential test scenarios from stories
        story_lines = [line.strip() for line in stories.split("\n") if line.strip()]
        
        for i, story in enumerate(story_lines[:5], 1):  # Limit to first 5 stories
            if "as a" in story.lower():
                # Extract role and action
                parts = story.split("I want")
                if len(parts) > 1:
                    action = parts[1].split("so that")[0].strip()
                    test_cases.append(f"Test Case {i}: Verify {action}")
        
        # Add generic test cases
        test_cases.extend([
            f"Test Case {len(test_cases) + 1}: Verify input validation for all form fields",
            f"Test Case {len(test_cases) + 2}: Verify error handling for invalid data",
            f"Test Case {len(test_cases) + 3}: Verify data persistence across sessions",
            f"Test Case {len(test_cases) + 4}: Verify security - XSS and injection prevention"
        ])
        
        return "\n".join(test_cases)
