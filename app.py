"""
DemandForge - Comprehensive IT Demand Lifecycle Management Platform
A Streamlit-based application for managing IT demands from ideation to closing.
Built for Salling Group to centralize documentation, stakeholder inputs, and artifacts.
"""

import streamlit as st
import uuid
import os
import random
from datetime import datetime
import json
import html
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import local modules
from utils.document_reader import DocumentReader, get_attachment_content
from utils.gantt_chart import render_gantt_tab
from components.jira_test_ui import (
    render_jira_test_setup,
    render_test_case_generator,
    render_test_plan_generator
)
from components.ai_chat import render_ai_chat
from models.demand import (
    Demand, IdeationTab, RequirementsTab, AssessmentTab, DesignTab,
    BuildTab, ValidationTab, DeploymentTab, ImplementationTab, ClosingTab,
    Stakeholder, AuditLogEntry, PowerInterest, RiskSeverity
)
from agents.mock_agent import MockAgent
try:
    from agents.gemini_agent import GeminiAgent
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    
from integrations.jira_client import MockJiraClient
from integrations.confluence_client import MockConfluenceClient
from utils.progress import calculate_progress, is_tab_complete, get_completion_details
from utils.export import export_to_json, export_to_markdown, generate_pdf_content
from utils.validation import sanitize_html, validate_session_ttl, validate_input_length
from utils.logging_config import setup_logging, StructuredLogger
from utils.storage import get_storage

# Page configuration
st.set_page_config(
    page_title="DemandForge - IT Demand Management",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, clean UI
st.markdown("""
<style>
    /* Modern color scheme - Light Mode */
    :root {
        --primary: #2563eb;
        --primary-dark: #1e40af;
        --secondary: #64748b;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --bg-card: #ffffff;
        --bg-hover: #f1f5f9;
        --border: #e2e8f0;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
    }
    
    /* Dark Mode Colors */
    [data-theme="dark"] {
        --primary: #60a5fa;
        --primary-dark: #3b82f6;
        --secondary: #94a3b8;
        --success: #34d399;
        --warning: #fbbf24;
        --danger: #f87171;
        --bg-card: #1e293b;
        --bg-hover: #334155;
        --border: #475569;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
    }
    
    /* Auto-detect dark mode from Streamlit */
    @media (prefers-color-scheme: dark) {
        :root {
            --primary: #60a5fa;
            --primary-dark: #3b82f6;
            --secondary: #94a3b8;
            --success: #34d399;
            --warning: #fbbf24;
            --danger: #f87171;
            --bg-card: #1e293b;
            --bg-hover: #334155;
            --border: #475569;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
        }
    }
    
    /* Compact header - top left */
    .main-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--primary);
        margin: 0;
        padding: 0;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }
    .main-header-emoji {
        font-size: 1rem;
    }
    .demand-id {
        font-size: 0.75rem;
        color: var(--secondary);
        font-family: 'Courier New', monospace;
        font-weight: 500;
    }
    .progress-text {
        font-size: 0.75rem;
        color: var(--secondary);
        font-weight: 500;
    }
    
    /* Reduce main content padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }
    
    /* Modern tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: var(--bg-hover);
        padding: 4px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 6px 12px;
        font-size: 0.85rem;
        border-radius: 6px;
        font-weight: 500;
        background-color: transparent;
        color: var(--text-primary);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--bg-card);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: var(--bg-card);
    }
    
    /* Clean card styling */
    .stForm {
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        background: var(--bg-card) !important;
    }
    
    /* Ensure all input fields respect dark mode */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stNumberInput > div > div > input {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border-color: var(--border) !important;
    }
    
    /* Compact headers */
    h1 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    h2 {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    h3 {
        font-size: 1rem !important;
        font-weight: 600 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Clean dividers */
    hr {
        margin: 1rem 0 !important;
        border-color: var(--border) !important;
    }
    
    /* AI response styling */
    .ai-response {
        background-color: var(--bg-hover);
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid var(--primary);
        font-size: 0.9rem;
        color: var(--text-primary);
    }
    .warning-box {
        background-color: rgba(251, 191, 36, 0.1);
        padding: 0.75rem;
        border-radius: 8px;
        border-left: 3px solid var(--warning);
        margin: 0.5rem 0;
        font-size: 0.85rem;
        color: var(--text-primary);
    }
    .success-box {
        background-color: rgba(52, 211, 153, 0.1);
        padding: 0.75rem;
        border-radius: 8px;
        border-left: 3px solid var(--success);
        margin: 0.5rem 0;
        font-size: 0.85rem;
        color: var(--text-primary);
    }
    
    /* Ensure Streamlit widgets respect theme */
    .stButton > button {
        background-color: var(--bg-card);
        color: var(--text-primary);
        border: 1px solid var(--border);
    }
    .stButton > button:hover {
        background-color: var(--bg-hover);
        border-color: var(--primary);
    }
    
    /* Compact buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.9rem;
        padding: 0.5rem 1rem;
    }
    
    /* Chat container - right side */
    .chat-sidebar {
        position: fixed;
        right: 0;
        top: 0;
        height: 100vh;
        width: 380px;
        background: white;
        border-left: 1px solid var(--border);
        z-index: 999;
        transition: transform 0.3s ease;
        display: flex;
        flex-direction: column;
    }
    .chat-sidebar.minimized {
        transform: translateX(340px);
    }
    .chat-toggle {
        position: fixed;
        right: 20px;
        top: 20px;
        z-index: 1000;
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 50%;
        width: 48px;
        height: 48px;
        cursor: pointer;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-size: 1.2rem;
        transition: all 0.3s ease;
    }
    .chat-toggle:hover {
        background: var(--primary-dark);
        transform: scale(1.05);
    }
    
    /* Reduce spacing */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize session state with default values."""
    if "initialized" not in st.session_state:
        # Track actual session start time (not demand start time)
        st.session_state.session_start_time = datetime.now()
        
        # Generate unique demand ID
        st.session_state.demand_id = f"LOG-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
        st.session_state.demand_name = ""
        st.session_state.demand_number = ""
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
        
        # Initialize attachments for each phase
        st.session_state.attachments = {
            "ideation": {"files": [], "urls": []},
            "requirements": {"files": [], "urls": []},
            "assessment": {"files": [], "urls": []},
            "design": {"files": [], "urls": []},
            "build": {"files": [], "urls": []},
            "validation": {"files": [], "urls": []},
            "deployment": {"files": [], "urls": []},
            "implementation": {"files": [], "urls": []},
            "closing": {"files": [], "urls": []}
        }
        
        # Chat and audit
        st.session_state.chat_history = []
        st.session_state.audit_log = []
        
        # Progress
        st.session_state.progress_percentage = 0
        
        # Initialize storage
        st.session_state.storage = get_storage()
        
        # Load ALL historical demands for AI context
        st.session_state.historical_demands = st.session_state.storage.get_all_demands_summary()
        st.session_state.storage_stats = st.session_state.storage.get_statistics()
        
        # Initialize Logger FIRST (before agent initialization)
        logger = setup_logging(trace_id=st.session_state.demand_id)
        st.session_state.logger = StructuredLogger(logger, st.session_state.demand_id)
        
        # Initialize AI Agent (Gemini if available, else Mock)
        use_gemini = os.getenv("USE_GEMINI", "false").lower() == "true"
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        if GEMINI_AVAILABLE and use_gemini and gemini_key:
            try:
                st.session_state.agent = GeminiAgent(api_key=gemini_key)
                st.session_state.agent_type = "Gemini AI"
                st.session_state.logger.info("Initialized Gemini AI agent")
            except Exception as e:
                st.session_state.agent = MockAgent()
                st.session_state.agent_type = "Mock (Gemini failed)"
                st.session_state.logger.warning(f"Gemini init failed, using mock: {e}")
        else:
            st.session_state.agent = MockAgent()
            st.session_state.agent_type = "Mock"
            st.session_state.logger.info("Using Mock AI agent")
        
        # Other clients (don't override agent!)
        st.session_state.jira_client = MockJiraClient()
        st.session_state.confluence_client = MockConfluenceClient()
        
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
    
    # Auto-save after each change
    save_current_demand()


def save_current_demand():
    """Save the current demand to persistent storage."""
    demand_data = {
        'demand_id': st.session_state.demand_id,
        'demand_name': st.session_state.get('demand_name', ''),
        'demand_number': st.session_state.get('demand_number', ''),
        'start_time': st.session_state.start_time.isoformat() if hasattr(st.session_state.start_time, 'isoformat') else str(st.session_state.start_time),
        'last_modified': st.session_state.last_modified.isoformat() if hasattr(st.session_state.last_modified, 'isoformat') else str(st.session_state.last_modified),
        'status': st.session_state.status,
        'progress_percentage': st.session_state.progress_percentage,
        'ideation': st.session_state.ideation,
        'requirements': st.session_state.requirements,
        'assessment': st.session_state.assessment,
        'design': st.session_state.design,
        'build': st.session_state.build,
        'validation': st.session_state.validation,
        'deployment': st.session_state.deployment,
        'implementation': st.session_state.implementation,
        'closing': st.session_state.closing,
        'attachments': st.session_state.get('attachments', {}),
        'audit_log': st.session_state.audit_log,
        'chat_history': st.session_state.chat_history,
    }
    
    st.session_state.storage.save_demand(demand_data)
    
    # Refresh historical demands for AI context
    st.session_state.historical_demands = st.session_state.storage.get_all_demands_summary()
    st.session_state.storage_stats = st.session_state.storage.get_statistics()


def load_demand_by_id(demand_id: str):
    """Load an existing demand by ID into session state."""
    try:
        # Only save current demand if it has been modified (has content or audit entries)
        # This prevents creating empty demand files when just browsing
        has_content = (
            st.session_state.get('demand_name', '') or
            st.session_state.ideation or
            st.session_state.requirements.get('stakeholders') or
            st.session_state.assessment or
            st.session_state.design or
            st.session_state.build.get('tasks') or
            st.session_state.validation or
            st.session_state.deployment or
            st.session_state.implementation or
            st.session_state.closing or
            len(st.session_state.audit_log) > 0 or
            len(st.session_state.chat_history) > 0
        )
        
        if has_content:
            # Save current demand first (without triggering auto-save chain)
            current_demand_data = {
                'demand_id': st.session_state.demand_id,
                'start_time': st.session_state.start_time.isoformat() if hasattr(st.session_state.start_time, 'isoformat') else str(st.session_state.start_time),
                'last_modified': st.session_state.last_modified.isoformat() if hasattr(st.session_state.last_modified, 'isoformat') else str(st.session_state.last_modified),
                'status': st.session_state.status,
                'progress_percentage': st.session_state.progress_percentage,
                'ideation': st.session_state.ideation,
                'requirements': st.session_state.requirements,
                'assessment': st.session_state.assessment,
                'design': st.session_state.design,
                'build': st.session_state.build,
                'validation': st.session_state.validation,
                'deployment': st.session_state.deployment,
                'implementation': st.session_state.implementation,
                'closing': st.session_state.closing,
                'audit_log': st.session_state.audit_log,
                'chat_history': st.session_state.chat_history,
            }
            st.session_state.storage.save_demand(current_demand_data)
        
        # Load the new demand
        demand_data = st.session_state.storage.load_demand(demand_id)
        
        if demand_data:
            # Parse timestamps
            start_time = demand_data.get('start_time')
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            
            last_modified = demand_data.get('last_modified')
            if isinstance(last_modified, str):
                last_modified = datetime.fromisoformat(last_modified)
            
            # Update session state - do this without triggering reruns
            st.session_state.demand_id = demand_data.get('demand_id')
            st.session_state.demand_name = demand_data.get('demand_name', '')
            st.session_state.demand_number = demand_data.get('demand_number', '')
            st.session_state.start_time = start_time
            st.session_state.last_modified = last_modified
            st.session_state.status = demand_data.get('status', 'Draft')
            st.session_state.progress_percentage = demand_data.get('progress_percentage', 0)
            st.session_state.ideation = demand_data.get('ideation', {})
            st.session_state.requirements = demand_data.get('requirements', {})
            st.session_state.assessment = demand_data.get('assessment', {})
            st.session_state.design = demand_data.get('design', {})
            st.session_state.build = demand_data.get('build', {})
            st.session_state.validation = demand_data.get('validation', {})
            st.session_state.deployment = demand_data.get('deployment', {})
            st.session_state.implementation = demand_data.get('implementation', {})
            st.session_state.closing = demand_data.get('closing', {})
            st.session_state.attachments = demand_data.get('attachments', {
                "ideation": {"files": [], "urls": []},
                "requirements": {"files": [], "urls": []},
                "assessment": {"files": [], "urls": []},
                "design": {"files": [], "urls": []},
                "build": {"files": [], "urls": []},
                "validation": {"files": [], "urls": []},
                "deployment": {"files": [], "urls": []},
                "implementation": {"files": [], "urls": []},
                "closing": {"files": [], "urls": []}
            })
            st.session_state.audit_log = demand_data.get('audit_log', [])
            st.session_state.chat_history = demand_data.get('chat_history', [])
            
            # Refresh historical demands
            st.session_state.historical_demands = st.session_state.storage.get_all_demands_summary()
            st.session_state.storage_stats = st.session_state.storage.get_statistics()
            
            # Set a flag to show success message after rerun
            st.session_state.load_success_message = f"✅ Successfully loaded demand: {demand_id}"
            
            return True
        else:
            st.session_state.load_error_message = f"❌ Could not load demand: {demand_id}"
            return False
    except Exception as e:
        st.session_state.load_error_message = f"❌ Error loading demand: {str(e)}"
        return False


def create_new_demand():
    """Create a new demand and reset session state."""
    try:
        # Only save current demand if it has been modified (has content or audit entries)
        # This prevents creating empty demand files when just browsing
        has_content = (
            st.session_state.get('demand_name', '') or
            st.session_state.ideation or
            st.session_state.requirements.get('stakeholders') or
            st.session_state.assessment or
            st.session_state.design or
            st.session_state.build.get('tasks') or
            st.session_state.validation or
            st.session_state.deployment or
            st.session_state.implementation or
            st.session_state.closing or
            len(st.session_state.audit_log) > 0 or
            len(st.session_state.chat_history) > 0
        )
        
        if has_content:
            # Save current demand first (without triggering auto-save chain)
            current_demand_data = {
                'demand_id': st.session_state.demand_id,
                'demand_name': st.session_state.get('demand_name', ''),
                'demand_number': st.session_state.get('demand_number', ''),
                'start_time': st.session_state.start_time.isoformat() if hasattr(st.session_state.start_time, 'isoformat') else str(st.session_state.start_time),
                'last_modified': st.session_state.last_modified.isoformat() if hasattr(st.session_state.last_modified, 'isoformat') else str(st.session_state.last_modified),
                'status': st.session_state.status,
                'progress_percentage': st.session_state.progress_percentage,
                'ideation': st.session_state.ideation,
                'requirements': st.session_state.requirements,
                'assessment': st.session_state.assessment,
                'design': st.session_state.design,
                'build': st.session_state.build,
                'validation': st.session_state.validation,
                'deployment': st.session_state.deployment,
                'implementation': st.session_state.implementation,
                'closing': st.session_state.closing,
                'audit_log': st.session_state.audit_log,
                'chat_history': st.session_state.chat_history,
            }
            st.session_state.storage.save_demand(current_demand_data)
        
        # Generate new demand ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
        new_demand_id = f"LOG-{datetime.now().year}-{random_suffix}"
        
        # Reset session state
        st.session_state.demand_id = new_demand_id
        st.session_state.demand_name = ""
        st.session_state.demand_number = ""
        st.session_state.start_time = datetime.now()
        st.session_state.last_modified = datetime.now()
        st.session_state.status = "Draft"
        st.session_state.progress_percentage = 0
        st.session_state.ideation = {}
        st.session_state.requirements = {}
        st.session_state.assessment = {}
        st.session_state.design = {}
        st.session_state.build = {}
        st.session_state.validation = {}
        st.session_state.deployment = {}
        st.session_state.implementation = {}
        st.session_state.closing = {}
        st.session_state.attachments = {
            "ideation": {"files": [], "urls": []},
            "requirements": {"files": [], "urls": []},
            "assessment": {"files": [], "urls": []},
            "design": {"files": [], "urls": []},
            "build": {"files": [], "urls": []},
            "validation": {"files": [], "urls": []},
            "deployment": {"files": [], "urls": []},
            "implementation": {"files": [], "urls": []},
            "closing": {"files": [], "urls": []}
        }
        st.session_state.audit_log = []
        st.session_state.chat_history = []
        
        # Save the new empty demand
        new_demand_data = {
            'demand_id': new_demand_id,
            'demand_name': '',
            'demand_number': '',
            'start_time': st.session_state.start_time.isoformat(),
            'last_modified': st.session_state.last_modified.isoformat(),
            'status': st.session_state.status,
            'progress_percentage': st.session_state.progress_percentage,
            'ideation': st.session_state.ideation,
            'requirements': st.session_state.requirements,
            'assessment': st.session_state.assessment,
            'design': st.session_state.design,
            'build': st.session_state.build,
            'validation': st.session_state.validation,
            'deployment': st.session_state.deployment,
            'implementation': st.session_state.implementation,
            'closing': st.session_state.closing,
            'attachments': st.session_state.attachments,
            'audit_log': st.session_state.audit_log,
            'chat_history': st.session_state.chat_history,
        }
        st.session_state.storage.save_demand(new_demand_data)
        
        # Refresh historical demands
        st.session_state.historical_demands = st.session_state.storage.get_all_demands_summary()
        st.session_state.storage_stats = st.session_state.storage.get_statistics()
        
        # Set success message
        st.session_state.create_success_message = f"✅ Created new demand: {new_demand_id}"
        
        return new_demand_id
    except Exception as e:
        st.session_state.load_error_message = f"❌ Error creating demand: {str(e)}"
        return None


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
# ATTACHMENT MANAGEMENT
# ============================================================================

def save_uploaded_file(uploaded_file, phase_name: str):
    """Save an uploaded file to the attachments directory."""
    try:
        # Create demand-specific directory
        demand_dir = os.path.join("data", "attachments", st.session_state.demand_id)
        os.makedirs(demand_dir, exist_ok=True)
        
        # Generate safe filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{uploaded_file.name}"
        file_path = os.path.join(demand_dir, safe_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Create metadata
        file_metadata = {
            "filename": uploaded_file.name,
            "stored_filename": safe_filename,
            "file_path": file_path,
            "file_size": uploaded_file.size,
            "file_type": uploaded_file.type,
            "uploaded_at": datetime.now().isoformat(),
            "uploaded_by": "POC-User",
            "phase": phase_name
        }
        
        return file_metadata
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None


def render_attachments_section(phase_name: str):
    """Render the attachments section for a phase tab."""
    st.divider()
    st.subheader("📎 Attachments & References")
    
    # Initialize attachments if not exists
    if phase_name not in st.session_state.attachments:
        st.session_state.attachments[phase_name] = {"files": [], "urls": []}
    
    # Create two columns for files and URLs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📁 File Uploads**")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload documents (Word, Excel, PDF, etc.)",
            type=["pdf", "docx", "xlsx", "pptx", "txt", "csv", "jpg", "png"],
            accept_multiple_files=True,
            key=f"file_upload_{phase_name}",
            help="Upload relevant documents for this phase"
        )
        
        if uploaded_files:
            if st.button(f"💾 Save Files to {phase_name.title()}", key=f"save_files_{phase_name}"):
                for uploaded_file in uploaded_files:
                    file_metadata = save_uploaded_file(uploaded_file, phase_name)
                    if file_metadata:
                        st.session_state.attachments[phase_name]["files"].append(file_metadata)
                
                add_audit_entry(f"Added {len(uploaded_files)} file(s)", phase_name, "attachments")
                st.success(f"✅ Saved {len(uploaded_files)} file(s)!")
                st.rerun()
        
        # Display existing files
        if st.session_state.attachments[phase_name]["files"]:
            st.markdown("**Uploaded Files:**")
            for idx, file_meta in enumerate(st.session_state.attachments[phase_name]["files"]):
                with st.expander(f"📄 {file_meta['filename']} ({file_meta['file_size'] // 1024} KB)"):
                    st.caption(f"Uploaded: {file_meta['uploaded_at'][:19]}")
                    st.caption(f"Type: {file_meta['file_type']}")
                    
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        if os.path.exists(file_meta['file_path']):
                            with open(file_meta['file_path'], "rb") as f:
                                st.download_button(
                                    "⬇️ Download",
                                    data=f.read(),
                                    file_name=file_meta['filename'],
                                    key=f"download_{phase_name}_{idx}"
                                )
                    with col_b:
                        if st.button("🗑️ Remove", key=f"remove_file_{phase_name}_{idx}"):
                            # Remove file from filesystem
                            if os.path.exists(file_meta['file_path']):
                                os.remove(file_meta['file_path'])
                            # Remove from metadata
                            st.session_state.attachments[phase_name]["files"].pop(idx)
                            add_audit_entry(f"Removed file: {file_meta['filename']}", phase_name, "attachments")
                            st.rerun()
        else:
            st.caption("No files uploaded yet.")
    
    with col2:
        st.markdown("**🔗 URL References**")
        
        # URL input form
        with st.form(f"url_form_{phase_name}"):
            url_title = st.text_input(
                "Reference Title",
                placeholder="e.g., API Documentation",
                max_chars=200,
                key=f"url_title_{phase_name}"
            )
            url_link = st.text_input(
                "URL",
                placeholder="https://...",
                max_chars=500,
                key=f"url_link_{phase_name}"
            )
            url_description = st.text_area(
                "Description (optional)",
                placeholder="Brief description of what this reference contains",
                max_chars=500,
                key=f"url_desc_{phase_name}",
                height=80
            )
            
            submitted = st.form_submit_button("➕ Add URL")
            
            if submitted and url_title and url_link:
                url_metadata = {
                    "title": url_title,
                    "url": url_link,
                    "description": url_description,
                    "added_at": datetime.now().isoformat(),
                    "added_by": "POC-User",
                    "phase": phase_name
                }
                
                st.session_state.attachments[phase_name]["urls"].append(url_metadata)
                add_audit_entry(f"Added URL: {url_title}", phase_name, "attachments")
                st.success(f"✅ Added URL reference!")
                st.rerun()
        
        # Display existing URLs
        if st.session_state.attachments[phase_name]["urls"]:
            st.markdown("**Saved References:**")
            for idx, url_meta in enumerate(st.session_state.attachments[phase_name]["urls"]):
                with st.expander(f"🔗 {url_meta['title']}"):
                    st.markdown(f"**URL:** [{url_meta['url']}]({url_meta['url']})")
                    if url_meta.get('description'):
                        st.caption(f"Description: {url_meta['description']}")
                    st.caption(f"Added: {url_meta['added_at'][:19]}")
                    
                    if st.button("🗑️ Remove", key=f"remove_url_{phase_name}_{idx}"):
                        st.session_state.attachments[phase_name]["urls"].pop(idx)
                        add_audit_entry(f"Removed URL: {url_meta['title']}", phase_name, "attachments")
                        st.rerun()
        else:
            st.caption("No URL references added yet.")
    
    # AI assistance for reading attachments
    st.divider()
    if st.session_state.attachments[phase_name]["files"] or st.session_state.attachments[phase_name]["urls"]:
        st.markdown("### 🤖 AI Document Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"� Ask AI about attachments", key=f"ai_read_{phase_name}"):
                with st.spinner("🤖 Reading documents and URLs..."):
                    attachment_content = get_attachment_content(
                        st.session_state.attachments[phase_name]["files"],
                        st.session_state.attachments[phase_name]["urls"]
                    )
                    
                    if attachment_content:
                        query = f"Please summarize the key points from the attached documents and URLs in the {phase_name} phase."
                        context = {
                            "attachments": attachment_content,
                            "phase": phase_name
                        }
                        
                        response = st.session_state.agent.generate(query, context)
                        
                        with st.expander("📋 AI Summary", expanded=True):
                            st.markdown(response)
                            
                        # Add to chat history
                        st.session_state.chat_history.append({
                            "role": "user",
                            "content": query,
                            "timestamp": datetime.now().isoformat()
                        })
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response,
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        st.warning("Could not read attachment content")
        
        with col2:
            st.caption("💡 **Tip:** The AI can now read your PDFs, Word docs, Excel files, and fetch web page content! Ask questions in the sidebar chat.")
    else:
        st.info("💡 Upload files or add URLs above, then use AI to analyze them!")


# ============================================================================
# HEADER
# ============================================================================

def render_header():
    """Render the application header with progress."""
    # Check session TTL using actual session start time (not demand start time)
    session_start = st.session_state.get('session_start_time', datetime.now())
    is_valid, warning = validate_session_ttl(session_start)
    
    if not is_valid:
        st.error(warning)
        if st.button("🔄 Start New Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.stop()
    elif warning:
        st.warning(warning)
    
    # Compact header - top left
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col1:
        st.markdown('<div class="main-header"><span class="main-header-emoji">🔨</span> DemandForge</div>', unsafe_allow_html=True)
        demand_display = f"{st.session_state.demand_number} - {st.session_state.demand_name}" if st.session_state.demand_number and st.session_state.demand_name else st.session_state.demand_id
        st.markdown(f'<div class="demand-id">{demand_display}</div>', unsafe_allow_html=True)
    
    with col2:
        # Progress bar - centered
        st.progress(st.session_state.progress_percentage / 100)
        completed_tabs = int(st.session_state.progress_percentage / 100 * 9)
        st.markdown(
            f'<div class="progress-text" style="text-align: center;">Progress: {completed_tabs}/9 Tabs ({st.session_state.progress_percentage}%)</div>',
            unsafe_allow_html=True
        )
    
    with col3:
        # Status - right aligned
        st.markdown(f'<div style="text-align: right; font-size: 0.8rem;"><strong>Status:</strong> {st.session_state.status}<br/><strong>Modified:</strong> {st.session_state.last_modified.strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)


# ============================================================================
# SIDEBAR - AI CO-PILOT
# ============================================================================

def render_sidebar():
    """Render the modern AI co-pilot sidebar."""
    render_ai_chat()


# ============================================================================
# TAB 1: IDEATION
# ============================================================================

def render_ideation_tab():
    """Render the Ideation phase tab."""
    st.session_state.current_tab = "Ideation"
    
    st.header("💡 Phase 1: Ideation")
    st.markdown("*Define the problem, goals, and context for this demand.*")
    
    with st.form("ideation_form"):
        st.subheader("Demand Identification")
        col1, col2 = st.columns(2)
        
        with col1:
            demand_number = st.text_input(
                "Demand Number",
                value=st.session_state.demand_number,
                placeholder="e.g., 10001",
                max_chars=20,
                help="Sequential demand number for tracking"
            )
        
        with col2:
            demand_name = st.text_input(
                "Demand Name",
                value=st.session_state.demand_name,
                placeholder="e.g., Promotion Process Enhancement",
                max_chars=200,
                help="Descriptive name for this demand"
            )
        
        st.divider()
        
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
            st.session_state.demand_number = demand_number
            st.session_state.demand_name = demand_name
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
    
    # Attachments section
    render_attachments_section("ideation")


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
    
    # Attachments section
    render_attachments_section("requirements")


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
    
    # Attachments section
    render_attachments_section("assessment")


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
    
    # Attachments section
    render_attachments_section("design")


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
    
    # Attachments section
    render_attachments_section("build")


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
    
    # JIRA Test Case Integration
    st.divider()
    render_jira_test_setup()
    render_test_case_generator()
    render_test_plan_generator()
    
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
    
    # Attachments section
    render_attachments_section("validation")


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
    
    # Attachments section
    render_attachments_section("deployment")


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
    
    # Attachments section
    render_attachments_section("implementation")


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
    
    # Attachments section
    render_attachments_section("closing")


# ============================================================================
# DEMANDS OVERVIEW PAGE
# ============================================================================

def render_demands_overview():
    """Render the demands overview page with all demands."""
    st.header("📂 All Demands")
    st.caption("Browse, search, and manage all demands in the system")
    
    # Display success/error messages from demand loading
    if hasattr(st.session_state, 'load_success_message'):
        st.success(st.session_state.load_success_message)
        del st.session_state.load_success_message
    
    if hasattr(st.session_state, 'load_error_message'):
        st.error(st.session_state.load_error_message)
        del st.session_state.load_error_message
    
    if hasattr(st.session_state, 'create_success_message'):
        st.success(st.session_state.create_success_message)
        del st.session_state.create_success_message
    
    # Action buttons at the top
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search demands", placeholder="Search by title, ID, or description...")
    
    with col2:
        status_filter = st.selectbox("Filter by Status", 
                                     ["All", "Draft", "In Progress", "Under Review", "Approved", "Rejected", "On Hold", "Completed", "Cancelled"])
    
    with col3:
        if st.button("➕ Create New Demand", use_container_width=True, type="primary"):
            new_id = create_new_demand()
            st.rerun()
    
    st.divider()
    
    # Get all demands
    all_demands = st.session_state.storage.get_all_demands_summary()
    
    # Apply filters
    filtered_demands = all_demands
    
    if status_filter != "All":
        filtered_demands = [d for d in filtered_demands if d.get('status') == status_filter]
    
    if search_query:
        search_lower = search_query.lower()
        filtered_demands = [d for d in filtered_demands if 
                          search_lower in d.get('demand_id', '').lower() or
                          search_lower in d.get('ideation', {}).get('title', '').lower() or
                          search_lower in d.get('ideation', {}).get('description', '').lower()]
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Demands", len(all_demands))
    
    with col2:
        avg_progress = sum(d.get('progress_percentage', 0) for d in all_demands) / len(all_demands) if all_demands else 0
        st.metric("Avg Progress", f"{avg_progress:.0f}%")
    
    with col3:
        completed = len([d for d in all_demands if d.get('status') == 'Completed'])
        st.metric("Completed", completed)
    
    with col4:
        in_progress = len([d for d in all_demands if d.get('status') == 'In Progress'])
        st.metric("In Progress", in_progress)
    
    st.divider()
    
    # Display demands
    if not filtered_demands:
        st.info("No demands found matching your criteria.")
    else:
        # Sort by last modified (most recent first)
        filtered_demands = sorted(filtered_demands, 
                                 key=lambda x: x.get('last_modified', ''), 
                                 reverse=True)
        
        for demand in filtered_demands:
            demand_id = demand.get('demand_id', 'Unknown')
            demand_name = demand.get('demand_name', '')
            demand_number = demand.get('demand_number', '')
            title = demand.get('ideation', {}).get('title', 'Untitled')
            description = demand.get('ideation', {}).get('description', 'No description')
            status = demand.get('status', 'Draft')
            progress = demand.get('progress_percentage', 0)
            last_modified = demand.get('last_modified', '')
            
            # Parse last modified
            try:
                if isinstance(last_modified, str):
                    last_modified_dt = datetime.fromisoformat(last_modified)
                    last_modified_str = last_modified_dt.strftime("%Y-%m-%d %H:%M")
                else:
                    last_modified_str = str(last_modified)
            except:
                last_modified_str = str(last_modified)
            
            # Status color
            status_colors = {
                'Draft': '🔵',
                'In Progress': '🟡',
                'Under Review': '🟠',
                'Approved': '🟢',
                'Rejected': '🔴',
                'On Hold': '⚪',
                'Completed': '✅',
                'Cancelled': '⚫'
            }
            status_icon = status_colors.get(status, '⚪')
            
            # Current demand indicator
            is_current = (demand_id == st.session_state.demand_id)
            current_badge = " **[CURRENT]**" if is_current else ""
            
            # Display name - use demand name/number if available, otherwise title
            if demand_name and demand_number:
                display_name = f"{demand_number} - {demand_name}"
            elif demand_name:
                display_name = demand_name
            elif title and title != 'Untitled':
                display_name = title
            else:
                display_name = demand_id
            
            # Create demand card
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"### {status_icon} {display_name}{current_badge}")
                    st.caption(f"**ID:** {demand_id}")
                    if demand_number or demand_name:
                        if demand_number:
                            st.caption(f"**Number:** {demand_number}")
                        if title and title != 'Untitled':
                            st.caption(f"**Title:** {title}")
                    st.caption(f"**Description:** {description[:150]}{'...' if len(description) > 150 else ''}")
                
                with col2:
                    st.metric("Progress", f"{progress}%")
                    st.caption(f"Status: **{status}**")
                
                with col3:
                    st.caption(f"Modified: {last_modified_str}")
                    
                    if not is_current:
                        if st.button(f"📂 Load", key=f"load_{demand_id}", use_container_width=True):
                            if load_demand_by_id(demand_id):
                                st.rerun()
                    else:
                        st.info("Active")
                
                # Progress bar
                st.progress(progress / 100)
                
                st.divider()


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
    
    # Main tabs - Add Demands Overview as first tab, Timeline as last
    tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "📂 All Demands",
        "💡 Ideation",
        "📋 Requirements",
        "📊 Assessment",
        "🎨 Design",
        "🔨 Build",
        "🧪 Validation",
        "🚀 Deployment",
        "📈 Implementation",
        "🎯 Closing",
        "📅 Timeline"
    ])
    
    with tab0:
        render_demands_overview()
    
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
    
    with tab10:
        render_gantt_tab()
    
    # Global actions
    render_global_actions()
    
    # Footer
    st.divider()
    st.caption(f"DemandForge v1.0 | © 2025 Salling Group | Demand ID: {st.session_state.demand_id}")


if __name__ == "__main__":
    main()
