"""
Real JIRA Integration Client
Connects to JIRA Cloud/Server via REST API for test case management.
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class JiraClient:
    """Real JIRA client for test case and test plan management."""
    
    def __init__(self, base_url: str, api_token: str, email: str):
        """
        Initialize JIRA client.
        
        Args:
            base_url: JIRA instance URL (e.g., https://your-domain.atlassian.net)
            api_token: JIRA API token
            email: Email address associated with the token
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.email = email
        self.session = requests.Session()
        self.session.auth = (email, api_token)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the JIRA connection.
        
        Returns:
            Dictionary with connection status and user info
        """
        try:
            response = self.session.get(f"{self.base_url}/rest/api/3/myself")
            response.raise_for_status()
            user_info = response.json()
            
            return {
                "success": True,
                "message": "Connection successful",
                "user": user_info.get('displayName', 'Unknown'),
                "email": user_info.get('emailAddress', 'Unknown')
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"JIRA connection test failed: {str(e)}")
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get list of available JIRA projects.
        
        Returns:
            List of project dictionaries
        """
        try:
            response = self.session.get(f"{self.base_url}/rest/api/3/project")
            response.raise_for_status()
            projects = response.json()
            
            return [
                {
                    "key": p.get("key"),
                    "name": p.get("name"),
                    "id": p.get("id")
                }
                for p in projects
            ]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get JIRA projects: {str(e)}")
            return []
    
    def get_issue_types(self, project_key: str) -> List[Dict[str, Any]]:
        """
        Get available issue types for a project.
        
        Args:
            project_key: JIRA project key
            
        Returns:
            List of issue type dictionaries
        """
        try:
            response = self.session.get(
                f"{self.base_url}/rest/api/3/project/{project_key}"
            )
            response.raise_for_status()
            project_data = response.json()
            
            return project_data.get('issueTypes', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get issue types: {str(e)}")
            return []
    
    def create_test_case(
        self,
        project_key: str,
        summary: str,
        description: str,
        test_type: str = "Manual",
        priority: str = "Medium",
        labels: List[str] = None,
        custom_fields: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a test case in JIRA.
        
        Args:
            project_key: JIRA project key
            summary: Test case title
            description: Test case description with steps
            test_type: "Manual" or "Automated"
            priority: Test priority
            labels: List of labels
            custom_fields: Additional custom fields
            
        Returns:
            Created issue details
        """
        try:
            # Build issue data
            issue_data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": description
                                    }
                                ]
                            }
                        ]
                    },
                    "issuetype": {"name": "Test"},  # Adjust based on your JIRA setup
                    "priority": {"name": priority},
                    "labels": labels or []
                }
            }
            
            # Add test type label
            issue_data["fields"]["labels"].append(f"test-type-{test_type.lower()}")
            
            # Add custom fields if provided
            if custom_fields:
                issue_data["fields"].update(custom_fields)
            
            response = self.session.post(
                f"{self.base_url}/rest/api/3/issue",
                json=issue_data
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "key": result.get("key"),
                "id": result.get("id"),
                "url": f"{self.base_url}/browse/{result.get('key')}"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create test case: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_test_plan(
        self,
        project_key: str,
        name: str,
        description: str,
        test_cases: List[str] = None,
        labels: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create a test plan (Epic) in JIRA.
        
        Args:
            project_key: JIRA project key
            name: Test plan name
            description: Test plan description
            test_cases: List of test case keys to link
            labels: List of labels
            
        Returns:
            Created epic details
        """
        try:
            # Create Epic for test plan
            epic_data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": name,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": description
                                    }
                                ]
                            }
                        ]
                    },
                    "issuetype": {"name": "Epic"},
                    "labels": labels or ["test-plan"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/rest/api/3/issue",
                json=epic_data
            )
            response.raise_for_status()
            result = response.json()
            
            epic_key = result.get("key")
            
            # Link test cases to epic if provided
            if test_cases and epic_key:
                for test_case_key in test_cases:
                    self.link_issue_to_epic(test_case_key, epic_key)
            
            return {
                "success": True,
                "key": epic_key,
                "id": result.get("id"),
                "url": f"{self.base_url}/browse/{epic_key}",
                "linked_tests": len(test_cases) if test_cases else 0
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create test plan: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def link_issue_to_epic(self, issue_key: str, epic_key: str) -> bool:
        """
        Link an issue to an epic.
        
        Args:
            issue_key: Key of issue to link
            epic_key: Key of epic
            
        Returns:
            Success status
        """
        try:
            # Update the issue to set parent epic
            update_data = {
                "fields": {
                    "parent": {"key": epic_key}
                }
            }
            
            response = self.session.put(
                f"{self.base_url}/rest/api/3/issue/{issue_key}",
                json=update_data
            )
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to link issue to epic: {str(e)}")
            return False
    
    def bulk_create_test_cases(
        self,
        project_key: str,
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create multiple test cases at once.
        
        Args:
            project_key: JIRA project key
            test_cases: List of test case dictionaries
            
        Returns:
            Summary of created test cases
        """
        created = []
        failed = []
        
        for test_case in test_cases:
            result = self.create_test_case(
                project_key=project_key,
                summary=test_case.get("summary", ""),
                description=test_case.get("description", ""),
                test_type=test_case.get("test_type", "Manual"),
                priority=test_case.get("priority", "Medium"),
                labels=test_case.get("labels", []),
                custom_fields=test_case.get("custom_fields")
            )
            
            if result.get("success"):
                created.append(result)
            else:
                failed.append({
                    "summary": test_case.get("summary"),
                    "error": result.get("error")
                })
        
        return {
            "total": len(test_cases),
            "created": len(created),
            "failed": len(failed),
            "created_items": created,
            "failed_items": failed
        }
    
    def search_issues(
        self,
        jql: str,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search JIRA issues using JQL.
        
        Args:
            jql: JIRA Query Language string
            max_results: Maximum number of results
            
        Returns:
            List of matching issues
        """
        try:
            response = self.session.get(
                f"{self.base_url}/rest/api/3/search",
                params={
                    "jql": jql,
                    "maxResults": max_results
                }
            )
            response.raise_for_status()
            result = response.json()
            
            return result.get("issues", [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to search issues: {str(e)}")
            return []


class TestCaseGenerator:
    """Generate test cases using AI based on requirements and design."""
    
    @staticmethod
    def generate_manual_test_cases(
        agent,
        requirements: str,
        acceptance_criteria: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate manual test cases using AI.
        
        Args:
            agent: AI agent instance
            requirements: Requirements text
            acceptance_criteria: Acceptance criteria
            context: Additional context
            
        Returns:
            List of test case dictionaries
        """
        prompt = f"""
Generate comprehensive manual test cases for the following requirements:

REQUIREMENTS:
{requirements}

ACCEPTANCE CRITERIA:
{acceptance_criteria}

Generate 5-10 detailed manual test cases. For each test case, provide:
1. Test Case Title (concise, descriptive)
2. Test Objective (what we're testing)
3. Preconditions (setup required)
4. Test Steps (numbered, clear steps)
5. Expected Results (what should happen)
6. Priority (High/Medium/Low)
7. Test Data (if applicable)

Format each test case clearly and ensure they cover:
- Happy path scenarios
- Edge cases
- Error handling
- User interface validation
- Data validation

Return the test cases in a structured format.
"""
        
        response = agent.generate(prompt, context)
        
        # Parse AI response into structured test cases
        # This is a simplified parser - you may need to enhance it
        test_cases = TestCaseGenerator._parse_test_cases(response, "Manual")
        
        return test_cases
    
    @staticmethod
    def generate_automated_test_cases(
        agent,
        technical_design: str,
        api_endpoints: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate automated test cases using AI.
        
        Args:
            agent: AI agent instance
            technical_design: Technical design document
            api_endpoints: API endpoint documentation
            context: Additional context
            
        Returns:
            List of automated test case dictionaries
        """
        prompt = f"""
Generate automated test cases for the following technical design:

TECHNICAL DESIGN:
{technical_design}

API ENDPOINTS:
{api_endpoints}

Generate 10-15 automated test cases suitable for:
- Unit testing
- Integration testing
- API testing
- End-to-end testing

For each automated test case, provide:
1. Test Case Title
2. Test Type (Unit/Integration/API/E2E)
3. Test Description
4. Test Setup (fixtures, mocks)
5. Test Assertions
6. Expected Behavior
7. Test Framework Suggestions (pytest, unittest, selenium, etc.)
8. Priority (High/Medium/Low)

Focus on:
- API contract testing
- Data validation
- Error handling
- Performance edge cases
- Security validation

Return in structured format.
"""
        
        response = agent.generate(prompt, context)
        
        # Parse AI response
        test_cases = TestCaseGenerator._parse_test_cases(response, "Automated")
        
        return test_cases
    
    @staticmethod
    def _parse_test_cases(ai_response: str, test_type: str) -> List[Dict[str, Any]]:
        """
        Parse AI-generated test cases into structured format.
        
        Args:
            ai_response: Raw AI response
            test_type: "Manual" or "Automated"
            
        Returns:
            List of structured test case dictionaries
        """
        # This is a simple parser - enhance based on your AI's output format
        test_cases = []
        
        # Split by test case markers (adjust based on AI output)
        lines = ai_response.split('\n')
        current_case = {}
        
        for line in lines:
            line = line.strip()
            
            # Detect new test case (various markers)
            if any(marker in line.lower() for marker in ['test case', 'tc-', '### test']):
                if current_case:
                    test_cases.append(current_case)
                current_case = {
                    "test_type": test_type,
                    "summary": line,
                    "description": "",
                    "priority": "Medium",
                    "labels": [test_type.lower(), "generated-by-ai"]
                }
            elif current_case:
                # Append to current description
                current_case["description"] += line + "\n"
        
        # Add last test case
        if current_case:
            test_cases.append(current_case)
        
        return test_cases
    
    @staticmethod
    def generate_test_plan(
        agent,
        demand_data: Dict[str, Any],
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive test plan.
        
        Args:
            agent: AI agent instance
            demand_data: Full demand information
            test_cases: List of test cases
            
        Returns:
            Test plan dictionary
        """
        prompt = f"""
Create a comprehensive test plan for this demand:

DEMAND: {demand_data.get('demand_name', 'Unknown')}
DESCRIPTION: {demand_data.get('ideation', {}).get('problem_statement', '')}
REQUIREMENTS: {demand_data.get('requirements', {})}

NUMBER OF TEST CASES: {len(test_cases)}

Generate a test plan that includes:
1. Test Plan Overview
2. Testing Scope (in-scope and out-of-scope)
3. Test Strategy
4. Test Schedule
5. Resource Requirements
6. Entry and Exit Criteria
7. Risk Assessment
8. Test Environment Requirements
9. Test Deliverables

Format as a structured document.
"""
        
        response = agent.generate(prompt, {})
        
        return {
            "name": f"Test Plan - {demand_data.get('demand_name', 'Unknown')}",
            "description": response,
            "test_case_count": len(test_cases),
            "created_date": datetime.now().isoformat()
        }
