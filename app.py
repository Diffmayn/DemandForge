"""
DemandForge - Comprehensive IT Demand Lifecycle Management Platform
A Streamlit-based application for managing IT demands from ideation to closing.
Built for Salling Group to centralize documentation, stakeholder inputs, and artifacts.
"""

import streamlit as st
import uuid
from datetime import datetime
import json
import html
from typing import Dict, Any, List, Optional

# Import local modules
from models.demand import (
    Demand, IdeationTab, RequirementsTab, AssessmentTab, DesignTab,
    BuildTab, ValidationTab, DeploymentTab, ImplementationTab, ClosingTab,
    Stakeholder, AuditLogEntry, PowerInterest, RiskSeverity
)
from agents.mock_agent import MockAgent
from integrations.jira_client import MockJiraClient
from integrations.confluence_client import MockConfluenceClient
from utils.progress import calculate_progress, is_tab_complete, get_completion_details
from utils.export import export_to_json, export_to_markdown, generate_pdf_content
from utils.validation import sanitize_html, validate_session_ttl, validate_input_length
from utils.logging_config import setup_logging, StructuredLogger

# Page configuration
st.set_page_config(
    page_title="DemandForge - IT Demand Management",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .demand-id {
        font-size: 1.2rem;
        color: #666;
        font-family: monospace;
    }
    .progress-text {
        font-size: 0.9rem;
        color: #888;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
    .ai-response {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize session state with default values."""
    if "initialized" not in st.session_state:
        # Generate unique demand ID
        st.session_state.demand_id = f"LOG-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
        st.session_state.start_time = datetime.now()
        st.session_state.last_modified = datetime.now()
        st.session_state.status = "Draft"
        
        # Initialize tab data
        st.session_state.ideation = {}
        st.session_state.requirements = {"stakeholders": []}
        st.session_state.assessment = {}
        st.session_state.design = {"wireframes_paths": []}
        st.session_state.build = {"tasks": [], "jira_story_ids": []}
        st.session_state.validation = {"bug_log": []}
        st.session_state.deployment = {"training_materials": []}
        st.session_state.implementation = {"success_metrics": {}}
        st.session_state.closing = {"sign_offs": {}}
        
        # Chat and audit
        st.session_state.chat_history = []
        st.session_state.audit_log = []
        
        # Progress
        st.session_state.progress_percentage = 0
        
        # Agents and clients
        st.session_state.agent = MockAgent()
        st.session_state.jira_client = MockJiraClient()
        st.session_state.confluence_client = MockConfluenceClient()
        
        # Logger
        logger = setup_logging(trace_id=st.session_state.demand_id)
        st.session_state.logger = StructuredLogger(logger, st.session_state.demand_id)
        st.session_state.logger.info("Session initialized", demand_id=st.session_state.demand_id)
        
        st.session_state.initialized = True


def add_audit_entry(action: str, tab_name: Optional[str] = None, field_name: Optional[str] = None):
    """Add an entry to the audit log."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user": "POC-User",  # Future: Get from auth
        "action": action,
        "trace_id": st.session_state.demand_id,
        "tab_name": tab_name,
        "field_name": field_name
    }
    st.session_state.audit_log.append(entry)
    st.session_state.last_modified = datetime.now()


def update_progress():
    """Update overall progress based on tab completion."""
    tabs_data = {
        "ideation": st.session_state.ideation,
        "requirements": st.session_state.requirements,
        "assessment": st.session_state.assessment,
        "design": st.session_state.design,
        "build": st.session_state.build,
        "validation": st.session_state.validation,
        "deployment": st.session_state.deployment,
        "implementation": st.session_state.implementation,
        "closing": st.session_state.closing
    }
    st.session_state.progress_percentage = calculate_progress(tabs_data)


# ============================================================================
# HEADER
# ============================================================================

def render_header():
    """Render the application header with progress."""
    # Check session TTL
    is_valid, warning = validate_session_ttl(st.session_state.start_time)
    
    if not is_valid:
        st.error(warning)
        if st.button("🔄 Start New Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.stop()
    elif warning:
        st.warning(warning)
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f'<div class="main-header">🔨 DemandForge</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="demand-id">Demand ID: {st.session_state.demand_id}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"**Status:** {st.session_state.status}")
        st.markdown(f"**Last Modified:** {st.session_state.last_modified.strftime('%H:%M:%S')}")
    
    # Progress bar
    st.progress(st.session_state.progress_percentage / 100)
    completed_tabs = int(st.session_state.progress_percentage / 100 * 9)
    st.markdown(
        f'<div class="progress-text">Progress: {completed_tabs}/9 Tabs Complete ({st.session_state.progress_percentage}%)</div>',
        unsafe_allow_html=True
    )
    
    st.divider()


# ============================================================================
# SIDEBAR - AI CO-PILOT
# ============================================================================

def render_sidebar():
    """Render the AI co-pilot sidebar."""
    with st.sidebar:
        st.header("🤖 AI Co-Pilot")
        st.caption("Brainstorm, Generate, Refine")
        
        # Chat container
        chat_container = st.container(height=400)
        
        with chat_container:
            # Display recent messages (last 20)
            for msg in st.session_state.chat_history[-20:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                with st.chat_message(role):
                    st.markdown(sanitize_html(content), unsafe_allow_html=False)
        
        # Chat input
        user_query = st.chat_input("Ask me anything...", max_chars=1000)
        
        if user_query:
            # Add user message
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_query,
                "timestamp": datetime.now().isoformat()
            })
            
            # Generate AI response
            context = {
                "demand_id": st.session_state.demand_id,
                "ideation": st.session_state.ideation,
                "requirements": st.session_state.requirements,
                "assessment": st.session_state.assessment,
                "design": st.session_state.design,
                "build": st.session_state.build,
                "validation": st.session_state.validation,
                "deployment": st.session_state.deployment,
                "implementation": st.session_state.implementation,
                "closing": st.session_state.closing,
                "current_tab": st.session_state.get("current_tab", "Ideation")
            }
            
            response = st.session_state.agent.generate(
                user_query,
                context,
                st.session_state.chat_history
            )
            
            # Add AI response
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            add_audit_entry(f"AI query: {user_query[:50]}...")
            st.rerun()
        
        st.divider()
        
        # Quick actions
        st.subheader("Quick Actions")
        
        if st.button("💡 Generate User Stories"):
            goals = st.session_state.ideation.get("goals", "")
            stories = st.session_state.agent.suggest_stories(goals, context={})
            st.session_state.requirements["user_stories"] = "\n\n".join(stories)
            add_audit_entry("Generated user stories", "requirements", "user_stories")
            st.success("User stories generated!")
            st.rerun()
        
        if st.button("⚠️ Predict Risks"):
            project_data = {
                "assessment": st.session_state.assessment,
                "requirements": st.session_state.requirements,
                "design": st.session_state.design
            }
            risks = st.session_state.agent.predict_risks(project_data)
            st.session_state.assessment["risks"] = risks
            add_audit_entry("Generated risk predictions", "assessment", "risks")
            st.success("Risk predictions generated!")
            st.rerun()
        
        if st.button("🧪 Generate Test Cases"):
            requirements = st.session_state.requirements.get("acceptance_criteria", "")
            stories = st.session_state.requirements.get("user_stories", "")
            tests = st.session_state.agent.generate_test_cases(requirements, stories)
            st.session_state.validation["test_cases"] = tests
            add_audit_entry("Generated test cases", "validation", "test_cases")
            st.success("Test cases generated!")
            st.rerun()


# ============================================================================
# TAB 1: IDEATION
# ============================================================================

def render_ideation_tab():
    """Render the Ideation phase tab."""
    st.session_state.current_tab = "Ideation"
    
    st.header("💡 Phase 1: Ideation")
    st.markdown("*Define the problem, goals, and context for this demand.*")
    
    with st.form("ideation_form"):
        st.subheader("Problem Statement")
        problem = st.text_area(
            "What problem are you solving?",
            value=st.session_state.ideation.get("problem_statement", ""),
            height=150,
            max_chars=2000,
            help="Clearly describe the business problem or opportunity"
        )
        
        st.subheader("Goals & Objectives")
        goals = st.text_area(
            "What are the key goals?",
            value=st.session_state.ideation.get("goals", ""),
            height=100,
            max_chars=1000,
            help="Specific, measurable objectives"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Background & Context")
            background = st.text_area(
                "Relevant background information",
                value=st.session_state.ideation.get("background", ""),
                height=100,
                max_chars=1500
            )
        
        with col2:
            st.subheader("Constraints")
            constraints = st.text_area(
                "Known constraints or limitations",
                value=st.session_state.ideation.get("constraints", ""),
                height=100,
                max_chars=1000
            )
        
        submitted = st.form_submit_button("💾 Save Ideation", use_container_width=True)
        
        if submitted:
            st.session_state.ideation["problem_statement"] = problem
            st.session_state.ideation["goals"] = goals
            st.session_state.ideation["background"] = background
            st.session_state.ideation["constraints"] = constraints
            
            add_audit_entry("Updated ideation data", "ideation")
            update_progress()
            st.success("✅ Ideation data saved!")
            st.rerun()
    
    # AI assistance
    if st.button("🤖 Refine Problem Statement (5 Whys)"):
        query = f"Apply 5 Whys analysis to: {problem[:200]}"
        context = {"ideation": st.session_state.ideation}
        response = st.session_state.agent.generate(query, context)
        
        with st.expander("💡 AI Suggestion", expanded=True):
            st.markdown(response)


# ============================================================================
# TAB 2: REQUIREMENTS
# ============================================================================

def render_requirements_tab():
    """Render the Requirements phase tab."""
    st.session_state.current_tab = "Requirements"
    
    st.header("📋 Phase 2: Requirements")
    st.markdown("*Define stakeholders, user stories, and acceptance criteria.*")
    
    # Stakeholders section
    st.subheader("Stakeholders")
    
    with st.expander("➕ Add Stakeholder", expanded=len(st.session_state.requirements.get("stakeholders", [])) == 0):
        with st.form("add_stakeholder"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                name = st.text_input("Name", max_chars=100)
            with col2:
                role = st.text_input("Role", max_chars=100)
            with col3:
                power_interest = st.selectbox(
                    "Power/Interest",
                    options=[e.value for e in PowerInterest]
                )
            
            email = st.text_input("Email (optional)", max_chars=200)
            
            if st.form_submit_button("Add Stakeholder"):
                if name and role:
                    stakeholder = {
                        "name": name,
                        "role": role,
                        "power_interest": power_interest,
                        "email": email
                    }
                    
                    if "stakeholders" not in st.session_state.requirements:
                        st.session_state.requirements["stakeholders"] = []
                    
                    st.session_state.requirements["stakeholders"].append(stakeholder)
                    add_audit_entry(f"Added stakeholder: {name}", "requirements", "stakeholders")
                    update_progress()
                    st.success(f"✅ Added {name}")
                    st.rerun()
                else:
                    st.error("Name and Role are required")
    
    # Display stakeholders
    stakeholders = st.session_state.requirements.get("stakeholders", [])
    if stakeholders:
        st.dataframe(
            stakeholders,
            column_config={
                "name": "Name",
                "role": "Role",
                "power_interest": "Power/Interest",
                "email": "Email"
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No stakeholders added yet")
    
    st.divider()
    
    # User Stories and Features
    with st.form("requirements_form"):
        st.subheader("User Stories")
        user_stories = st.text_area(
            "Define user stories (As a... I want... so that...)",
            value=st.session_state.requirements.get("user_stories", ""),
            height=200,
            max_chars=5000,
            help="Each story should follow the template: As a [role], I want [feature], so that [benefit]"
        )
        
        st.subheader("Acceptance Criteria")
        acceptance_criteria = st.text_area(
            "What defines 'done' for each story?",
            value=st.session_state.requirements.get("acceptance_criteria", ""),
            height=150,
            max_chars=3000
        )
        
        st.subheader("Non-Functional Requirements")
        nfr = st.text_area(
            "Performance, security, scalability requirements",
            value=st.session_state.requirements.get("non_functional_requirements", ""),
            height=100,
            max_chars=2000
        )
        
        submitted = st.form_submit_button("💾 Save Requirements", use_container_width=True)
        
        if submitted:
            st.session_state.requirements["user_stories"] = user_stories
            st.session_state.requirements["acceptance_criteria"] = acceptance_criteria
            st.session_state.requirements["non_functional_requirements"] = nfr
            
            # Auto-generate features from goals
            goals = st.session_state.ideation.get("goals", "")
            if goals:
                features = [line.strip() for line in goals.split("\n") if line.strip()]
                st.session_state.requirements["features"] = features[:20]  # Limit to 20
            
            add_audit_entry("Updated requirements data", "requirements")
            update_progress()
            st.success("✅ Requirements saved!")
            st.rerun()


# ============================================================================
# TAB 3: ASSESSMENT
# ============================================================================

def render_assessment_tab():
    """Render the Assessment phase tab."""
    st.session_state.current_tab = "Assessment"
    
    st.header("📊 Phase 3: Assessment")
    st.markdown("*Business case, ROI, risks, and feasibility.*")
    
    with st.form("assessment_form"):
        st.subheader("Business Case")
        business_case = st.text_area(
            "Why should we invest in this?",
            value=st.session_state.assessment.get("business_case", ""),
            height=150,
            max_chars=2000
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            roi = st.number_input(
                "Expected ROI (%)",
                min_value=0.0,
                max_value=1000.0,
                value=float(st.session_state.assessment.get("roi_percentage", 0)),
                step=5.0
            )
        
        with col2:
            cost = st.number_input(
                "Estimated Cost (€)",
                min_value=0.0,
                value=float(st.session_state.assessment.get("estimated_cost", 0)),
                step=1000.0
            )
        
        with col3:
            duration = st.number_input(
                "Duration (weeks)",
                min_value=0,
                max_value=520,
                value=int(st.session_state.assessment.get("estimated_duration_weeks", 0)),
                step=1
            )
        
        st.subheader("Risks & Mitigation")
        risks = st.text_area(
            "Identify key risks and mitigation strategies",
            value=st.session_state.assessment.get("risks", ""),
            height=150,
            max_chars=3000,
            help="Format: [Severity] Risk description -> Mitigation"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Dependencies")
            dependencies = st.text_area(
                "External dependencies",
                value=st.session_state.assessment.get("dependencies", ""),
                height=100,
                max_chars=2000
            )
        
        with col2:
            st.subheader("Assumptions")
            assumptions = st.text_area(
                "Key assumptions",
                value=st.session_state.assessment.get("assumptions", ""),
                height=100,
                max_chars=2000
            )
        
        submitted = st.form_submit_button("💾 Save Assessment", use_container_width=True)
        
        if submitted:
            st.session_state.assessment["business_case"] = business_case
            st.session_state.assessment["roi_percentage"] = roi
            st.session_state.assessment["estimated_cost"] = cost
            st.session_state.assessment["estimated_duration_weeks"] = duration
            st.session_state.assessment["risks"] = risks
            st.session_state.assessment["dependencies"] = dependencies
            st.session_state.assessment["assumptions"] = assumptions
            
            add_audit_entry("Updated assessment data", "assessment")
            update_progress()
            st.success("✅ Assessment saved!")
            st.rerun()
    
    # ROI Calculator
    if cost > 0 and roi > 0:
        expected_return = cost * (1 + roi / 100)
        payback_months = duration * 4.33 if duration > 0 else 0
        
        st.info(f"💰 **ROI Summary:** Initial investment of €{cost:,.0f} with {roi}% ROI = €{expected_return:,.0f} return. Payback period: ~{payback_months:.0f} months")


# ============================================================================
# TAB 4: DESIGN
# ============================================================================

def render_design_tab():
    """Render the Design phase tab."""
    st.session_state.current_tab = "Design"
    
    st.header("🎨 Phase 4: Design")
    st.markdown("*Architecture, technical design, and wireframes.*")
    
    with st.form("design_form"):
        st.subheader("Architecture Overview")
        architecture = st.text_area(
            "High-level architecture and patterns",
            value=st.session_state.design.get("architecture_overview", ""),
            height=150,
            max_chars=5000
        )
        
        st.subheader("Technical Stack")
        tech_stack = st.text_area(
            "Technologies, frameworks, and tools",
            value=st.session_state.design.get("technical_stack", ""),
            height=100,
            max_chars=1500
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Data Model")
            data_model = st.text_area(
                "Key entities and relationships",
                value=st.session_state.design.get("data_model", ""),
                height=100,
                max_chars=3000
            )
        
        with col2:
            st.subheader("Integration Points")
            integrations = st.text_area(
                "External systems and APIs",
                value=st.session_state.design.get("integration_points", ""),
                height=100,
                max_chars=2000
            )
        
        st.subheader("Security Considerations")
        security = st.text_area(
            "Authentication, authorization, data protection",
            value=st.session_state.design.get("security_considerations", ""),
            height=100,
            max_chars=2000
        )
        
        submitted = st.form_submit_button("💾 Save Design", use_container_width=True)
        
        if submitted:
            st.session_state.design["architecture_overview"] = architecture
            st.session_state.design["technical_stack"] = tech_stack
            st.session_state.design["data_model"] = data_model
            st.session_state.design["integration_points"] = integrations
            st.session_state.design["security_considerations"] = security
            
            add_audit_entry("Updated design data", "design")
            update_progress()
            st.success("✅ Design saved!")
            st.rerun()
    
    # Wireframes section
    st.subheader("Wireframes & Mockups")
    uploaded_file = st.file_uploader("Upload wireframe/diagram", type=["png", "jpg", "jpeg", "pdf"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Wireframe", use_container_width=True)
        st.info("💡 In production, files would be stored in cloud storage (Azure Blob, S3)")


# ============================================================================
# TAB 5: BUILD
# ============================================================================

def render_build_tab():
    """Render the Build phase tab."""
    st.session_state.current_tab = "Build"
    
    st.header("🔨 Phase 5: Build")
    st.markdown("*Development tasks, sprints, and JIRA integration.*")
    
    # Tasks management
    st.subheader("Development Tasks")
    
    with st.form("add_task"):
        new_task = st.text_input("Add a task", max_chars=200)
        if st.form_submit_button("➕ Add Task"):
            if new_task:
                if "tasks" not in st.session_state.build:
                    st.session_state.build["tasks"] = []
                
                st.session_state.build["tasks"].append(new_task)
                add_audit_entry(f"Added task: {new_task[:50]}", "build", "tasks")
                update_progress()
                st.success("✅ Task added!")
                st.rerun()
    
    # Display tasks
    tasks = st.session_state.build.get("tasks", [])
    if tasks:
        for i, task in enumerate(tasks[-100:], 1):  # Show last 100
            st.text(f"{i}. {task}")
    else:
        st.info("No tasks added yet")
    
    st.divider()
    
    # Sprint planning
    with st.form("sprint_form"):
        st.subheader("Sprint Plan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sprint_start = st.date_input("Sprint Start Date")
        
        with col2:
            sprint_end = st.date_input("Sprint End Date")
        
        sprint_plan = st.text_area(
            "Sprint details and milestones",
            value=st.session_state.build.get("sprint_plan", ""),
            height=150,
            max_chars=3000
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            repo_url = st.text_input(
                "Repository URL",
                value=st.session_state.build.get("repository_url", ""),
                max_chars=500
            )
        
        with col2:
            branch = st.text_input(
                "Branch Name",
                value=st.session_state.build.get("branch_name", ""),
                max_chars=100
            )
        
        submitted = st.form_submit_button("💾 Save Build Plan", use_container_width=True)
        
        if submitted:
            st.session_state.build["sprint_start_date"] = str(sprint_start)
            st.session_state.build["sprint_end_date"] = str(sprint_end)
            st.session_state.build["sprint_plan"] = sprint_plan
            st.session_state.build["repository_url"] = repo_url
            st.session_state.build["branch_name"] = branch
            
            add_audit_entry("Updated build data", "build")
            update_progress()
            st.success("✅ Build plan saved!")
            st.rerun()
    
    st.divider()
    
    # JIRA Integration
    st.subheader("🔗 JIRA Integration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Create JIRA Epic", use_container_width=True):
            epic_data = {
                "summary": st.session_state.ideation.get("goals", "")[:100],
                "description": st.session_state.ideation.get("problem_statement", "")[:500],
                "epic_name": st.session_state.demand_id,
                "labels": ["demandforge", "logistics"]
            }
            
            result = st.session_state.jira_client.create_epic(epic_data)
            
            if result.get("created"):
                st.session_state.build["jira_epic_id"] = result["key"]
                add_audit_entry(f"Created JIRA epic: {result['key']}", "build", "jira_epic_id")
                st.success(f"✅ Created Epic: [{result['key']}]({result['url']})")
                
                with st.expander("API Payload Preview"):
                    st.code(st.session_state.jira_client.get_api_payload_preview(epic_data), language="json")
            else:
                st.error("Failed to create epic")
    
    with col2:
        if st.button("📊 View JIRA Items", use_container_width=True):
            items = st.session_state.jira_client.get_created_items()
            with st.expander("Created JIRA Items", expanded=True):
                for item in items[-10:]:  # Show last 10
                    st.json(item)


# ============================================================================
# TAB 6: VALIDATION
# ============================================================================

def render_validation_tab():
    """Render the Validation phase tab."""
    st.session_state.current_tab = "Validation"
    
    st.header("🧪 Phase 6: Validation")
    st.markdown("*Test cases, QA, and defect tracking.*")
    
    with st.form("validation_form"):
        st.subheader("Test Cases")
        test_cases = st.text_area(
            "Define test scenarios and expected outcomes",
            value=st.session_state.validation.get("test_cases", ""),
            height=200,
            max_chars=5000
        )
        
        st.subheader("Test Results")
        test_results = st.text_area(
            "Test execution results and findings",
            value=st.session_state.validation.get("test_results", ""),
            height=150,
            max_chars=3000
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            coverage = st.number_input(
                "Automated Test Coverage (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.validation.get("automated_test_coverage", 0)),
                step=5.0
            )
        
        with col2:
            qa_signoff = st.checkbox(
                "QA Sign-Off",
                value=st.session_state.validation.get("qa_sign_off", False)
            )
        
        manual_status = st.text_area(
            "Manual Test Status",
            value=st.session_state.validation.get("manual_test_status", ""),
            height=100,
            max_chars=1000
        )
        
        submitted = st.form_submit_button("💾 Save Validation", use_container_width=True)
        
        if submitted:
            st.session_state.validation["test_cases"] = test_cases
            st.session_state.validation["test_results"] = test_results
            st.session_state.validation["automated_test_coverage"] = coverage
            st.session_state.validation["qa_sign_off"] = qa_signoff
            st.session_state.validation["manual_test_status"] = manual_status
            
            add_audit_entry("Updated validation data", "validation")
            update_progress()
            st.success("✅ Validation saved!")
            st.rerun()
    
    # Bug log
    st.divider()
    st.subheader("🐛 Bug Log")
    
    with st.expander("➕ Add Bug"):
        with st.form("add_bug"):
            bug_id = st.text_input("Bug ID", max_chars=50)
            severity = st.selectbox("Severity", ["Critical", "High", "Medium", "Low"])
            description = st.text_area("Description", max_chars=500)
            status = st.selectbox("Status", ["Open", "In Progress", "Fixed", "Closed"])
            
            if st.form_submit_button("Add Bug"):
                if bug_id and description:
                    bug = {
                        "id": bug_id,
                        "severity": severity,
                        "description": description,
                        "status": status,
                        "created": datetime.now().isoformat()
                    }
                    
                    if "bug_log" not in st.session_state.validation:
                        st.session_state.validation["bug_log"] = []
                    
                    st.session_state.validation["bug_log"].append(bug)
                    add_audit_entry(f"Added bug: {bug_id}", "validation", "bug_log")
                    st.success(f"✅ Bug {bug_id} added!")
                    st.rerun()
    
    bugs = st.session_state.validation.get("bug_log", [])
    if bugs:
        st.dataframe(bugs, use_container_width=True)
    else:
        st.info("No bugs logged yet")


# ============================================================================
# TAB 7: DEPLOYMENT
# ============================================================================

def render_deployment_tab():
    """Render the Deployment phase tab."""
    st.session_state.current_tab = "Deployment"
    
    st.header("🚀 Phase 7: Deployment")
    st.markdown("*Deployment planning, rollout, and training.*")
    
    with st.form("deployment_form"):
        st.subheader("Deployment Schedule")
        deployment_date = st.date_input("Target Deployment Date")
        
        st.subheader("Rollout Plan")
        rollout = st.text_area(
            "Phased rollout strategy",
            value=st.session_state.deployment.get("rollout_plan", ""),
            height=150,
            max_chars=3000
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Environment Configuration")
            env_config = st.text_area(
                "Production environment setup",
                value=st.session_state.deployment.get("environment_config", ""),
                height=100,
                max_chars=2000
            )
        
        with col2:
            st.subheader("Rollback Plan")
            rollback = st.text_area(
                "Emergency rollback procedure",
                value=st.session_state.deployment.get("rollback_plan", ""),
                height=100,
                max_chars=2000
            )
        
        st.subheader("Communication Plan")
        communication = st.text_area(
            "Stakeholder communication strategy",
            value=st.session_state.deployment.get("communication_plan", ""),
            height=100,
            max_chars=1500
        )
        
        st.subheader("Deployment Checklist")
        checklist = st.text_area(
            "Pre-deployment verification items",
            value=st.session_state.deployment.get("deployment_checklist", ""),
            height=100,
            max_chars=2000
        )
        
        submitted = st.form_submit_button("💾 Save Deployment Plan", use_container_width=True)
        
        if submitted:
            st.session_state.deployment["deployment_schedule"] = str(deployment_date)
            st.session_state.deployment["rollout_plan"] = rollout
            st.session_state.deployment["environment_config"] = env_config
            st.session_state.deployment["rollback_plan"] = rollback
            st.session_state.deployment["communication_plan"] = communication
            st.session_state.deployment["deployment_checklist"] = checklist
            
            add_audit_entry("Updated deployment data", "deployment")
            update_progress()
            st.success("✅ Deployment plan saved!")
            st.rerun()
    
    st.divider()
    st.subheader("📚 Training Materials")
    st.info("💡 Upload training docs, videos, or user guides. In production, these would be stored in Azure Blob/SharePoint.")


# ============================================================================
# TAB 8: IMPLEMENTATION
# ============================================================================

def render_implementation_tab():
    """Render the Implementation monitoring tab."""
    st.session_state.current_tab = "Implementation"
    
    st.header("📈 Phase 8: Implementation")
    st.markdown("*Post-deployment monitoring, metrics, and issues.*")
    
    # Metrics Dashboard (Simulated)
    st.subheader("📊 Success Metrics Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    uptime = st.session_state.implementation.get("uptime_percentage", 99.5)
    adoption = st.session_state.implementation.get("adoption_rate", 75.0)
    
    with col1:
        st.metric("Uptime", f"{uptime}%", "+0.2%")
    
    with col2:
        st.metric("Adoption Rate", f"{adoption}%", "+5%")
    
    with col3:
        st.metric("Active Users", "1,234", "+89")
    
    with col4:
        st.metric("Avg Response Time", "245ms", "-15ms")
    
    st.divider()
    
    with st.form("implementation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            uptime_input = st.number_input(
                "System Uptime (%)",
                min_value=0.0,
                max_value=100.0,
                value=uptime,
                step=0.1
            )
        
        with col2:
            adoption_input = st.number_input(
                "User Adoption Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=adoption,
                step=1.0
            )
        
        st.subheader("Issue Log")
        issues = st.text_area(
            "Post-deployment issues and resolutions",
            value=st.session_state.implementation.get("issue_log", ""),
            height=150,
            max_chars=3000
        )
        
        st.subheader("User Feedback")
        feedback = st.text_area(
            "User comments and feedback",
            value=st.session_state.implementation.get("user_feedback", ""),
            height=150,
            max_chars=2000
        )
        
        st.subheader("Performance Data")
        performance = st.text_area(
            "System performance observations",
            value=st.session_state.implementation.get("performance_data", ""),
            height=100,
            max_chars=2000
        )
        
        submitted = st.form_submit_button("💾 Save Implementation Data", use_container_width=True)
        
        if submitted:
            st.session_state.implementation["uptime_percentage"] = uptime_input
            st.session_state.implementation["adoption_rate"] = adoption_input
            st.session_state.implementation["issue_log"] = issues
            st.session_state.implementation["user_feedback"] = feedback
            st.session_state.implementation["performance_data"] = performance
            
            add_audit_entry("Updated implementation data", "implementation")
            update_progress()
            st.success("✅ Implementation data saved!")
            st.rerun()


# ============================================================================
# TAB 9: CLOSING
# ============================================================================

def render_closing_tab():
    """Render the Closing phase tab."""
    st.session_state.current_tab = "Closing"
    
    st.header("🎯 Phase 9: Closing")
    st.markdown("*Retrospective, lessons learned, and project finalization.*")
    
    with st.form("closing_form"):
        st.subheader("Retrospective")
        retrospective = st.text_area(
            "What went well? What could be improved?",
            value=st.session_state.closing.get("retrospective", ""),
            height=200,
            max_chars=5000
        )
        
        st.subheader("Lessons Learned")
        lessons = st.text_area(
            "Key takeaways for future projects",
            value=st.session_state.closing.get("lessons_learned", ""),
            height=150,
            max_chars=3000
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            final_cost = st.number_input(
                "Final Cost (€)",
                min_value=0.0,
                value=float(st.session_state.closing.get("final_costs", 0)),
                step=1000.0
            )
        
        with col2:
            final_roi = st.number_input(
                "Actual ROI (%)",
                value=float(st.session_state.closing.get("final_roi", 0)),
                step=5.0
            )
        
        st.subheader("Knowledge Transfer")
        knowledge_transfer = st.text_area(
            "Documentation handoff and training completed",
            value=st.session_state.closing.get("knowledge_transfer", ""),
            height=100,
            max_chars=2000
        )
        
        archive_location = st.text_input(
            "Archive Location (Confluence/SharePoint)",
            value=st.session_state.closing.get("archive_location", ""),
            max_chars=500
        )
        
        submitted = st.form_submit_button("💾 Save Closing Data", use_container_width=True)
        
        if submitted:
            st.session_state.closing["retrospective"] = retrospective
            st.session_state.closing["lessons_learned"] = lessons
            st.session_state.closing["final_costs"] = final_cost
            st.session_state.closing["final_roi"] = final_roi
            st.session_state.closing["knowledge_transfer"] = knowledge_transfer
            st.session_state.closing["archive_location"] = archive_location
            
            add_audit_entry("Updated closing data", "closing")
            update_progress()
            st.success("✅ Closing data saved!")
            st.rerun()
    
    st.divider()
    
    # Sign-offs
    st.subheader("✍️ Stakeholder Sign-Offs")
    
    stakeholders = st.session_state.requirements.get("stakeholders", [])
    if stakeholders:
        sign_offs = st.session_state.closing.get("sign_offs", {})
        
        for sh in stakeholders:
            name = sh.get("name", "Unknown")
            signed = st.checkbox(
                f"{name} ({sh.get('role', 'N/A')})",
                value=sign_offs.get(name, False),
                key=f"signoff_{name}"
            )
            sign_offs[name] = signed
        
        st.session_state.closing["sign_offs"] = sign_offs
    else:
        st.info("No stakeholders defined in Requirements phase")
    
    st.divider()
    
    # Finalize button
    if st.button("🎉 Finalize Demand", use_container_width=True, type="primary"):
        st.session_state.status = "Closed"
        add_audit_entry("Demand finalized and closed", "closing")
        st.balloons()
        st.success("🎉 Demand finalized! Ready for export and archival.")
        
        # Save to historical for RAG (simulated)
        demand_export = {
            "demand_id": st.session_state.demand_id,
            "closed_date": datetime.now().isoformat(),
            "ideation": st.session_state.ideation,
            "requirements": st.session_state.requirements,
            "assessment": st.session_state.assessment,
            "design": st.session_state.design,
            "closing": st.session_state.closing
        }
        
        st.info("💡 In production, this demand would be saved to historical_demands.json for RAG indexing")


# ============================================================================
# GLOBAL ACTIONS
# ============================================================================

def render_global_actions():
    """Render global export and audit actions."""
    st.divider()
    st.header("🌐 Global Actions")
    
    col1, col2, col3 = st.columns(3)
    
    # Export JSON
    with col1:
        if st.button("📥 Export as JSON", use_container_width=True):
            demand_data = {
                "demand_id": st.session_state.demand_id,
                "created_at": st.session_state.start_time.isoformat(),
                "last_modified": st.session_state.last_modified.isoformat(),
                "status": st.session_state.status,
                "progress_percentage": st.session_state.progress_percentage,
                "ideation": st.session_state.ideation,
                "requirements": st.session_state.requirements,
                "assessment": st.session_state.assessment,
                "design": st.session_state.design,
                "build": st.session_state.build,
                "validation": st.session_state.validation,
                "deployment": st.session_state.deployment,
                "implementation": st.session_state.implementation,
                "closing": st.session_state.closing,
                "audit_log": st.session_state.audit_log
            }
            
            json_str = export_to_json(demand_data)
            
            st.download_button(
                label="💾 Download JSON",
                data=json_str,
                file_name=f"{st.session_state.demand_id}_demand.json",
                mime="application/json"
            )
    
    # Export Markdown
    with col2:
        if st.button("📄 Export as Markdown", use_container_width=True):
            demand_data = {
                "demand_id": st.session_state.demand_id,
                "created_at": st.session_state.start_time.isoformat(),
                "status": st.session_state.status,
                "progress_percentage": st.session_state.progress_percentage,
                "ideation": st.session_state.ideation,
                "requirements": st.session_state.requirements,
                "assessment": st.session_state.assessment,
                "design": st.session_state.design,
                "build": st.session_state.build,
                "validation": st.session_state.validation,
                "deployment": st.session_state.deployment,
                "implementation": st.session_state.implementation,
                "closing": st.session_state.closing
            }
            
            md_str = export_to_markdown(demand_data)
            
            st.download_button(
                label="💾 Download Markdown",
                data=md_str,
                file_name=f"{st.session_state.demand_id}_report.md",
                mime="text/markdown"
            )
    
    # View Audit Log
    with col3:
        if st.button("📋 View Audit Log", use_container_width=True):
            with st.expander("🔍 Audit Trail", expanded=True):
                if st.session_state.audit_log:
                    for entry in st.session_state.audit_log[-50:]:  # Show last 50
                        st.text(f"{entry['timestamp']} | {entry['action']}")
                else:
                    st.info("No audit entries yet")
    
    # Completion details
    with st.expander("📊 Completion Details"):
        tabs_data = {
            "ideation": st.session_state.ideation,
            "requirements": st.session_state.requirements,
            "assessment": st.session_state.assessment,
            "design": st.session_state.design,
            "build": st.session_state.build,
            "validation": st.session_state.validation,
            "deployment": st.session_state.deployment,
            "implementation": st.session_state.implementation,
            "closing": st.session_state.closing
        }
        
        details = get_completion_details(tabs_data)
        
        for tab_name, info in details.items():
            status_icon = "✅" if info["is_complete"] else "⏳"
            st.text(f"{status_icon} {tab_name.title()}: {info['filled_fields']}/{info['total_fields']} fields ({info['completion_percentage']}%)")


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    # Initialize
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar()
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "💡 Ideation",
        "📋 Requirements",
        "📊 Assessment",
        "🎨 Design",
        "🔨 Build",
        "🧪 Validation",
        "🚀 Deployment",
        "📈 Implementation",
        "🎯 Closing"
    ])
    
    with tab1:
        render_ideation_tab()
    
    with tab2:
        render_requirements_tab()
    
    with tab3:
        render_assessment_tab()
    
    with tab4:
        render_design_tab()
    
    with tab5:
        render_build_tab()
    
    with tab6:
        render_validation_tab()
    
    with tab7:
        render_deployment_tab()
    
    with tab8:
        render_implementation_tab()
    
    with tab9:
        render_closing_tab()
    
    # Global actions
    render_global_actions()
    
    # Footer
    st.divider()
    st.caption(f"DemandForge v1.0 | © 2025 Salling Group | Demand ID: {st.session_state.demand_id}")


if __name__ == "__main__":
    main()
