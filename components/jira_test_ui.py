"""
JIRA Test Case Management UI Component
UI for generating and uploading test cases to JIRA.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any
import os


def render_jira_test_setup():
    """Render JIRA connection setup section."""
    st.subheader("🔗 JIRA Connection Setup")
    
    with st.expander("⚙️ Configure JIRA Connection", expanded=not st.session_state.get('jira_connected', False)):
        st.markdown("""
        **How to get your JIRA API Token:**
        1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
        2. Click "Create API token"
        3. Give it a name (e.g., "DemandForge")
        4. Copy the token and paste below
        
        **JIRA Base URL Format:**
        - Cloud: `https://your-domain.atlassian.net`
        - Server: `https://jira.your-company.com`
        """)
        
        with st.form("jira_connection_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                jira_url = st.text_input(
                    "JIRA Base URL",
                    value=st.session_state.get('jira_url', ''),
                    placeholder="https://your-domain.atlassian.net",
                    help="Your JIRA instance URL"
                )
                
                jira_email = st.text_input(
                    "Email",
                    value=st.session_state.get('jira_email', ''),
                    placeholder="your-email@company.com",
                    help="Email associated with your JIRA account"
                )
            
            with col2:
                jira_token = st.text_input(
                    "API Token",
                    type="password",
                    value=st.session_state.get('jira_token', ''),
                    placeholder="Your JIRA API token",
                    help="API token from JIRA settings"
                )
                
                jira_project = st.text_input(
                    "Project Key",
                    value=st.session_state.get('jira_project_key', ''),
                    placeholder="PROJ",
                    help="JIRA project key (e.g., PROJ, TEST, DEV)"
                )
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                save_connection = st.form_submit_button("💾 Save & Test Connection", use_container_width=True)
            
            if save_connection:
                if jira_url and jira_email and jira_token:
                    # Store in session state
                    st.session_state.jira_url = jira_url
                    st.session_state.jira_email = jira_email
                    st.session_state.jira_token = jira_token
                    st.session_state.jira_project_key = jira_project
                    
                    # Test connection
                    from integrations.jira_test_client import JiraClient
                    
                    try:
                        jira = JiraClient(jira_url, jira_token, jira_email)
                        result = jira.test_connection()
                        
                        if result.get('success'):
                            st.session_state.jira_connected = True
                            st.session_state.jira_client = jira
                            st.success(f"✅ Connected to JIRA as {result.get('user', 'Unknown')}")
                            
                            # Get projects
                            projects = jira.get_projects()
                            if projects:
                                st.session_state.jira_projects = projects
                                st.info(f"📂 Found {len(projects)} project(s)")
                        else:
                            st.error(f"❌ Connection failed: {result.get('message', 'Unknown error')}")
                            st.session_state.jira_connected = False
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.session_state.jira_connected = False
                else:
                    st.warning("⚠️ Please fill in all connection details")
    
    # Show connection status
    if st.session_state.get('jira_connected'):
        st.success(f"✅ Connected to JIRA: {st.session_state.get('jira_url', 'Unknown')}")
        
        if st.button("🔌 Disconnect"):
            st.session_state.jira_connected = False
            st.session_state.jira_client = None
            st.rerun()
    else:
        st.warning("⚠️ JIRA not connected. Configure connection above to use test case features.")


def render_test_case_generator():
    """Render AI test case generation section."""
    if not st.session_state.get('jira_connected'):
        st.info("💡 Connect to JIRA first to enable test case generation")
        return
    
    st.divider()
    st.subheader("🤖 AI Test Case Generator")
    
    # Generate test cases
    tab1, tab2 = st.tabs(["📝 Manual Test Cases", "⚙️ Automated Test Cases"])
    
    with tab1:
        render_manual_test_generation()
    
    with tab2:
        render_automated_test_generation()


def render_manual_test_generation():
    """Render manual test case generation UI."""
    st.markdown("**Generate Manual Test Cases from Requirements**")
    
    # Check if requirements exist
    requirements = st.session_state.get('requirements', {})
    user_stories = requirements.get('user_stories', '')
    acceptance_criteria = requirements.get('acceptance_criteria', '')
    
    if not user_stories and not acceptance_criteria:
        st.warning("⚠️ No requirements found. Please fill in the Requirements tab first.")
        return
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.text_area(
            "User Stories",
            value=user_stories,
            height=100,
            disabled=True,
            help="From Requirements phase"
        )
        
        st.text_area(
            "Acceptance Criteria",
            value=acceptance_criteria,
            height=100,
            disabled=True,
            help="From Requirements phase"
        )
    
    with col2:
        num_tests = st.number_input(
            "Number of Test Cases",
            min_value=1,
            max_value=20,
            value=5,
            help="How many test cases to generate"
        )
        
        priority = st.selectbox(
            "Default Priority",
            ["High", "Medium", "Low"],
            index=1
        )
    
    if st.button("🤖 Generate Manual Test Cases", type="primary", use_container_width=True):
        with st.spinner("🤖 AI is generating manual test cases..."):
            from integrations.jira_test_client import TestCaseGenerator
            
            # Get attachment content for context
            from utils.document_reader import get_attachment_content
            
            attachments = st.session_state.get("attachments", {})
            req_attachments = attachments.get("requirements", {"files": [], "urls": []})
            attachment_content = get_attachment_content(
                req_attachments.get("files", []),
                req_attachments.get("urls", [])
            )
            
            context = {
                "demand_name": st.session_state.get('demand_name', ''),
                "ideation": st.session_state.get('ideation', {}),
                "requirements": requirements,
                "attachments": attachment_content,
                "num_tests": num_tests
            }
            
            test_cases = TestCaseGenerator.generate_manual_test_cases(
                st.session_state.agent,
                user_stories,
                acceptance_criteria,
                context
            )
            
            # Store generated test cases
            st.session_state.generated_manual_tests = test_cases
            st.success(f"✅ Generated {len(test_cases)} manual test cases!")
            st.rerun()
    
    # Display generated test cases
    if st.session_state.get('generated_manual_tests'):
        st.divider()
        st.markdown("### 📋 Generated Manual Test Cases")
        
        test_cases = st.session_state.generated_manual_tests
        
        for idx, test in enumerate(test_cases):
            with st.expander(f"Test Case {idx + 1}: {test.get('summary', 'Untitled')}"):
                st.markdown(f"**Type:** {test.get('test_type', 'Manual')}")
                st.markdown(f"**Priority:** {test.get('priority', 'Medium')}")
                st.markdown(f"**Labels:** {', '.join(test.get('labels', []))}")
                st.markdown("**Description:**")
                st.text_area(
                    "Test Steps",
                    value=test.get('description', ''),
                    height=200,
                    key=f"manual_test_{idx}",
                    help="Edit if needed before uploading"
                )
        
        # Upload to JIRA
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            if st.button("📤 Upload All to JIRA", type="primary", use_container_width=True):
                upload_test_cases_to_jira(test_cases, "Manual")
        
        with col2:
            if st.button("🗑️ Clear Generated Tests", use_container_width=True):
                del st.session_state.generated_manual_tests
                st.rerun()


def render_automated_test_generation():
    """Render automated test case generation UI."""
    st.markdown("**Generate Automated Test Cases from Design**")
    
    # Check if design exists
    design = st.session_state.get('design', {})
    architecture = design.get('architecture_design', '')
    tech_stack = design.get('technical_stack', '')
    
    if not architecture and not tech_stack:
        st.warning("⚠️ No design information found. Please fill in the Design tab first.")
        return
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.text_area(
            "Architecture Design",
            value=architecture,
            height=100,
            disabled=True,
            help="From Design phase"
        )
        
        st.text_area(
            "Technical Stack",
            value=tech_stack,
            height=80,
            disabled=True,
            help="From Design phase"
        )
    
    with col2:
        num_tests = st.number_input(
            "Number of Test Cases",
            min_value=1,
            max_value=30,
            value=10,
            help="How many automated tests to generate"
        )
        
        test_framework = st.selectbox(
            "Test Framework",
            ["pytest", "unittest", "selenium", "playwright", "cypress"],
            help="Preferred testing framework"
        )
    
    if st.button("🤖 Generate Automated Test Cases", type="primary", use_container_width=True):
        with st.spinner("🤖 AI is generating automated test cases..."):
            from integrations.jira_test_client import TestCaseGenerator
            from utils.document_reader import get_attachment_content
            
            # Get attachment content for context
            attachments = st.session_state.get("attachments", {})
            design_attachments = attachments.get("design", {"files": [], "urls": []})
            attachment_content = get_attachment_content(
                design_attachments.get("files", []),
                design_attachments.get("urls", [])
            )
            
            context = {
                "demand_name": st.session_state.get('demand_name', ''),
                "design": design,
                "attachments": attachment_content,
                "num_tests": num_tests,
                "framework": test_framework
            }
            
            test_cases = TestCaseGenerator.generate_automated_test_cases(
                st.session_state.agent,
                architecture,
                tech_stack,
                context
            )
            
            # Store generated test cases
            st.session_state.generated_automated_tests = test_cases
            st.success(f"✅ Generated {len(test_cases)} automated test cases!")
            st.rerun()
    
    # Display generated test cases
    if st.session_state.get('generated_automated_tests'):
        st.divider()
        st.markdown("### ⚙️ Generated Automated Test Cases")
        
        test_cases = st.session_state.generated_automated_tests
        
        for idx, test in enumerate(test_cases):
            with st.expander(f"Test Case {idx + 1}: {test.get('summary', 'Untitled')}"):
                st.markdown(f"**Type:** {test.get('test_type', 'Automated')}")
                st.markdown(f"**Priority:** {test.get('priority', 'Medium')}")
                st.markdown(f"**Labels:** {', '.join(test.get('labels', []))}")
                st.markdown("**Description:**")
                st.text_area(
                    "Test Implementation",
                    value=test.get('description', ''),
                    height=250,
                    key=f"auto_test_{idx}",
                    help="Edit if needed before uploading"
                )
        
        # Upload to JIRA
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            if st.button("📤 Upload All to JIRA", type="primary", use_container_width=True, key="upload_auto"):
                upload_test_cases_to_jira(test_cases, "Automated")
        
        with col2:
            if st.button("🗑️ Clear Generated Tests", use_container_width=True, key="clear_auto"):
                del st.session_state.generated_automated_tests
                st.rerun()


def upload_test_cases_to_jira(test_cases: List[Dict[str, Any]], test_type: str):
    """Upload test cases to JIRA."""
    jira_client = st.session_state.get('jira_client')
    project_key = st.session_state.get('jira_project_key')
    
    if not jira_client or not project_key:
        st.error("❌ JIRA not connected or project key not set")
        return
    
    with st.spinner(f"📤 Uploading {len(test_cases)} {test_type} test cases to JIRA..."):
        # Update test cases with edited content from text areas
        for idx, test in enumerate(test_cases):
            # Get edited content from session state if exists
            if test_type == "Manual":
                key = f"manual_test_{idx}"
            else:
                key = f"auto_test_{idx}"
            
            # Streamlit stores widget values in session state
            if key in st.session_state:
                test['description'] = st.session_state[key]
        
        result = jira_client.bulk_create_test_cases(project_key, test_cases)
        
        if result['created'] > 0:
            st.success(f"✅ Successfully created {result['created']} test case(s) in JIRA!")
            
            # Show links to created test cases
            with st.expander("📋 Created Test Cases", expanded=True):
                for item in result['created_items']:
                    st.markdown(f"- [{item['key']}]({item['url']})")
            
            # Save to audit log
            from app import add_audit_entry
            add_audit_entry(
                f"Uploaded {result['created']} {test_type} test cases to JIRA",
                "validation",
                "jira_upload"
            )
        
        if result['failed'] > 0:
            st.warning(f"⚠️ {result['failed']} test case(s) failed to upload")
            with st.expander("❌ Failed Test Cases"):
                for item in result['failed_items']:
                    st.error(f"- {item['summary']}: {item['error']}")


def render_test_plan_generator():
    """Render test plan generation UI."""
    if not st.session_state.get('jira_connected'):
        return
    
    st.divider()
    st.subheader("📋 Test Plan Generator")
    
    manual_count = len(st.session_state.get('generated_manual_tests', []))
    auto_count = len(st.session_state.get('generated_automated_tests', []))
    total_count = manual_count + auto_count
    
    if total_count == 0:
        st.info("💡 Generate some test cases first, then create a test plan to organize them")
        return
    
    st.info(f"📊 Ready to create test plan with {manual_count} manual and {auto_count} automated test cases")
    
    with st.form("test_plan_form"):
        plan_name = st.text_input(
            "Test Plan Name",
            value=f"Test Plan - {st.session_state.get('demand_name', 'Unknown')}",
            help="Name for the test plan Epic in JIRA"
        )
        
        plan_description = st.text_area(
            "Test Plan Description",
            value="Comprehensive test plan generated by DemandForge AI",
            height=100,
            help="Description for the test plan"
        )
        
        include_strategy = st.checkbox(
            "Generate AI Test Strategy",
            value=True,
            help="Let AI generate a comprehensive test strategy"
        )
        
        submitted = st.form_submit_button("📋 Create Test Plan in JIRA", type="primary")
        
        if submitted:
            with st.spinner("🤖 Generating test plan..."):
                from integrations.jira_test_client import TestCaseGenerator
                
                # Generate test plan with AI
                if include_strategy:
                    plan_data = TestCaseGenerator.generate_test_plan(
                        st.session_state.agent,
                        st.session_state.to_dict(),
                        st.session_state.get('generated_manual_tests', []) + 
                        st.session_state.get('generated_automated_tests', [])
                    )
                    full_description = plan_description + "\n\n" + plan_data['description']
                else:
                    full_description = plan_description
                
                # Create test plan in JIRA
                jira_client = st.session_state.get('jira_client')
                project_key = st.session_state.get('jira_project_key')
                
                # Note: You'll need to upload test cases first to get their keys
                result = jira_client.create_test_plan(
                    project_key=project_key,
                    name=plan_name,
                    description=full_description,
                    labels=["test-plan", "ai-generated", st.session_state.get('demand_id', '')]
                )
                
                if result.get('success'):
                    st.success(f"✅ Test plan created: [{result['key']}]({result['url']})")
                    
                    from app import add_audit_entry
                    add_audit_entry(
                        f"Created test plan {result['key']} in JIRA",
                        "validation",
                        "test_plan"
                    )
                else:
                    st.error(f"❌ Failed to create test plan: {result.get('error', 'Unknown error')}")
