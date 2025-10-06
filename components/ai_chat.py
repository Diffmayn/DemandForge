"""
AI Chat Component - Modern right-side chat interface
"""

import streamlit as st
from datetime import datetime
from utils.validation import sanitize_html
from utils.document_reader import get_attachment_content


def render_ai_chat():
    """Main function to render AI chat - switches between left and right based on state."""
    # Initialize chat position state (default to right)
    if "chat_on_right" not in st.session_state:
        st.session_state.chat_on_right = True
    
    # Render in appropriate location
    if st.session_state.chat_on_right:
        render_chat_right_panel()
    else:
        render_chat_sidebar()


def render_chat_right_panel():
    """Render chat as a floating panel on the right side."""
    # Add custom CSS for right panel
    st.markdown("""
    <style>
        /* Adjust main content to make room for right panel */
        section[data-testid="stSidebar"] {
            position: fixed !important;
            right: 0 !important;
            left: auto !important;
            width: 400px !important;
        }
        
        /* Fix collapse button to collapse to the right */
        section[data-testid="stSidebar"] > div:first-child {
            transform: scaleX(-1) !important;
        }
        
        section[data-testid="stSidebar"] > div:first-child > div {
            transform: scaleX(-1) !important;
        }
        
        /* Ensure sidebar collapses to the right */
        section[data-testid="stSidebar"][aria-expanded="false"] {
            transform: translateX(100%) !important;
            right: -400px !important;
        }
        
        .main .block-container {
            margin-right: 420px !important;
            margin-left: 20px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Use the sidebar to render on the right
    render_chat_sidebar()


def render_chat_interface():
    """Render a modern, collapsible chat interface on the right side."""
    
    # Initialize chat visibility state
    if "chat_visible" not in st.session_state:
        st.session_state.chat_visible = True
    if "chat_minimized" not in st.session_state:
        st.session_state.chat_minimized = False
    
    # Add custom CSS for right panel chat interface
    st.markdown("""
    <style>
        /* Right panel chat container */
        .right-chat-panel {
            position: fixed;
            right: 0;
            top: 60px;
            bottom: 0;
            width: 400px;
            background: white;
            border-left: 2px solid #e2e8f0;
            box-shadow: -4px 0 12px rgba(0,0,0,0.1);
            z-index: 999;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        /* Adjust main content to not overlap with chat */
        .main .block-container {
            margin-right: 420px !important;
        }
        
        /* Chat toggle button - floating on right */
        .chat-fab {
            position: fixed;
            right: 20px;
            bottom: 20px;
            z-index: 1001;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            cursor: pointer;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        .chat-fab:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(0,0,0,0.2);
        }
        
        /* Chat panel - slides in from right */
        .chat-panel {
            position: fixed;
            right: 0;
            top: 0;
            height: 100vh;
            width: 400px;
            background: white;
            border-left: 1px solid #e2e8f0;
            box-shadow: -2px 0 8px rgba(0,0,0,0.1);
            z-index: 1000;
            display: flex;
            flex-direction: column;
            transition: transform 0.3s ease;
        }
        .chat-panel.hidden {
            transform: translateX(100%);
        }
        .chat-panel.minimized {
            height: 60px;
            bottom: 0;
            top: auto;
            border-radius: 12px 0 0 0;
        }
        
        /* Chat header */
        .chat-header {
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .chat-header-title {
            font-size: 1rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .chat-header-actions {
            display: flex;
            gap: 0.5rem;
        }
        .chat-header-btn {
            background: rgba(255,255,255,0.2);
            border: none;
            border-radius: 6px;
            padding: 0.25rem 0.5rem;
            color: white;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background 0.2s;
        }
        .chat-header-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        
        /* Make main content aware of chat panel */
        .main .block-container {
            margin-right: 0;
            transition: margin-right 0.3s ease;
        }
        .main .block-container.chat-open {
            margin-right: 400px;
        }
        
        /* Agent badge */
        .agent-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.25rem 0.5rem;
            background: rgba(255,255,255,0.2);
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        /* Quick action buttons */
        .quick-actions {
            padding: 0.75rem;
            border-top: 1px solid #e2e8f0;
            background: #f8fafc;
        }
        .quick-action-btn {
            width: 100%;
            margin-bottom: 0.5rem;
            font-size: 0.85rem;
            padding: 0.5rem;
            border-radius: 6px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Determine chat state CSS classes
    chat_class = "chat-panel"
    if not st.session_state.chat_visible:
        chat_class += " hidden"
    elif st.session_state.chat_minimized:
        chat_class += " minimized"
    
    # Right panel HTML container
    st.markdown('''
        <div class="right-chat-panel" id="rightChatPanel">
            <div style="padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 1.1rem; font-weight: 600;">🤖 AI Co-Pilot</span>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
def render_chat_sidebar():
    """Render the chat sidebar in Streamlit's sidebar (left or right side)."""
    with st.sidebar:
        # Header with controls
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 🤖 AI Co-Pilot")
        with col2:
            # Position toggle - universal switch button
            current_side = "right" if st.session_state.get("chat_on_right", True) else "left"
            switch_icon = "🔄"
            help_text = f"Switch to {'left' if current_side == 'right' else 'right'} side"
            
            if st.button(switch_icon, help=help_text, key="chat_switch_side"):
                st.session_state.chat_on_right = not st.session_state.get("chat_on_right", True)
                st.rerun()
        
        # Show which AI is active
        agent_type = st.session_state.get("agent_type", "Mock")
        if "Gemini" in agent_type:
            st.success(f"✅ {agent_type}")
        else:
            st.info(f"ℹ️ {agent_type}")
        
        # Show system statistics
        stats = st.session_state.get("storage_stats", {})
        if stats and stats.get('total_demands', 0) > 0:
            st.caption(f"📊 {stats['total_demands']} demands | Avg: {stats['average_progress']:.0f}%")
        
        st.divider()
        
        # Chat container with reduced height for cleaner look
        chat_container = st.container(height=300)
        
        with chat_container:
            # Display recent messages (last 15 for cleaner view)
            for msg in st.session_state.chat_history[-15:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                with st.chat_message(role):
                    # Simple markdown without HTML sanitization for now
                    st.markdown(content)
        
        # Chat input
        user_query = st.chat_input("Ask me anything...", max_chars=1000)
        
        if user_query:
            # Add user message
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_query,
                "timestamp": datetime.now().isoformat()
            })
            
            # Get current tab's attachments for context
            current_tab_key = st.session_state.get("current_tab", "ideation").lower()
            attachments = st.session_state.get("attachments", {})
            tab_attachments = attachments.get(current_tab_key, {"files": [], "urls": []})
            
            # Extract content from attachments
            with st.spinner("🤖 Reading documents..."):
                from utils.document_reader import get_attachment_content
                attachment_content = get_attachment_content(
                    tab_attachments.get("files", []),
                    tab_attachments.get("urls", [])
                )
            
            # Build context with historical demands for RAG
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
                "current_tab": st.session_state.get("current_tab", "Ideation"),
                "historical_demands": st.session_state.get("historical_demands", []),
                "attachments": attachment_content
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
            
            # Add to audit log directly
            entry = {
                "timestamp": datetime.now().isoformat(),
                "user": "POC-User",
                "action": f"AI query: {user_query[:50]}...",
                "trace_id": st.session_state.demand_id,
                "tab_name": None,
                "field_name": None
            }
            st.session_state.audit_log.append(entry)
            st.session_state.last_modified = datetime.now()
            st.rerun()
        
        st.divider()
        
        # Compact quick actions
        st.markdown("**Quick Actions**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💡 Stories", help="Generate User Stories", use_container_width=True):
                goals = st.session_state.ideation.get("goals", "")
                context = {"historical_demands": st.session_state.get("historical_demands", [])}
                stories = st.session_state.agent.suggest_stories(goals, context)
                st.session_state.requirements["user_stories"] = "\n\n".join(stories)
                # Add to audit log directly
                entry = {
                    "timestamp": datetime.now().isoformat(),
                    "user": "POC-User",
                    "action": "Generated user stories",
                    "trace_id": st.session_state.demand_id,
                    "tab_name": "requirements",
                    "field_name": "user_stories"
                }
                st.session_state.audit_log.append(entry)
                st.session_state.last_modified = datetime.now()
                st.success("Stories generated!")
                st.rerun()
        
        with col2:
            if st.button("⚠️ Risks", help="Predict Risks", use_container_width=True):
                project_data = {
                    "assessment": st.session_state.assessment,
                    "requirements": st.session_state.requirements,
                    "design": st.session_state.design,
                    "historical_demands": st.session_state.get("historical_demands", [])
                }
                risks = st.session_state.agent.predict_risks(project_data)
                st.session_state.assessment["risks"] = risks
                # Add to audit log directly
                entry = {
                    "timestamp": datetime.now().isoformat(),
                    "user": "POC-User",
                    "action": "Generated risk predictions",
                    "trace_id": st.session_state.demand_id,
                    "tab_name": "assessment",
                    "field_name": "risks"
                }
                st.session_state.audit_log.append(entry)
                st.session_state.last_modified = datetime.now()
                st.success("Risks generated!")
                st.rerun()
        
        if st.button("🧪 Test Cases", help="Generate Test Cases", use_container_width=True):
            requirements = st.session_state.requirements.get("acceptance_criteria", "")
            stories = st.session_state.requirements.get("user_stories", "")
            tests = st.session_state.agent.generate_test_cases(requirements, stories)
            st.session_state.validation["test_cases"] = tests
            # Add to audit log directly
            entry = {
                "timestamp": datetime.now().isoformat(),
                "user": "POC-User",
                "action": "Generated test cases",
                "trace_id": st.session_state.demand_id,
                "tab_name": "validation",
                "field_name": "test_cases"
            }
            st.session_state.audit_log.append(entry)
            st.session_state.last_modified = datetime.now()
            st.success("Tests generated!")
            st.rerun()
