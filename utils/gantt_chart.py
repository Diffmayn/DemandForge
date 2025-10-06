"""
Gantt Chart Utilities
Create interactive project timelines using Plotly.
"""

import plotly.figure_factory as ff
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import streamlit as st


class GanttChartBuilder:
    """Build interactive Gantt charts for demand project timelines."""
    
    # Phase colors mapping
    PHASE_COLORS = {
        'Ideation': '#FFE5CC',
        'Requirements': '#CCE5FF',
        'Assessment': '#E5CCFF',
        'Design': '#FFCCF2',
        'Build': '#CCFFCC',
        'Validation': '#FFFFCC',
        'Deployment': '#FFD9CC',
        'Implementation': '#CCFFFF',
        'Closing': '#E6E6E6'
    }
    
    # Status colors for task-based Gantt charts
    STATUS_COLORS = {
        'Completed': '#10b981',    # Green
        'In Progress': '#f59e0b',  # Orange
        'Planned': '#3b82f6',      # Blue
        'Blocked': '#ef4444'       # Red
    }
    
    @staticmethod
    def create_default_timeline(start_date: datetime) -> List[Dict]:
        """Create default timeline with all 9 phases.
        
        Args:
            start_date: Project start date
            
        Returns:
            List of task dictionaries
        """
        tasks = []
        current_date = start_date
        
        # Define default durations (in days)
        phase_durations = {
            'Ideation': 7,
            'Requirements': 14,
            'Assessment': 10,
            'Design': 21,
            'Build': 60,
            'Validation': 14,
            'Deployment': 7,
            'Implementation': 30,
            'Closing': 5
        }
        
        for phase_name, duration in phase_durations.items():
            end_date = current_date + timedelta(days=duration)
            
            tasks.append({
                'Task': phase_name,
                'Start': current_date.strftime('%Y-%m-%d'),
                'Finish': end_date.strftime('%Y-%m-%d'),
                'Resource': 'Phase',
                'Description': f'{phase_name} phase',
                'Duration': duration
            })
            
            current_date = end_date
        
        return tasks
    
    @staticmethod
    def create_gantt_from_demand(demand_data: Dict, tasks_data: List[Dict] = None) -> go.Figure:
        """Create Gantt chart from demand data.
        
        Args:
            demand_data: Demand session state data
            tasks_data: Optional custom tasks data
            
        Returns:
            Plotly figure object
        """
        # Get start date
        start_time = demand_data.get('start_time')
        if isinstance(start_time, str):
            start_date = datetime.fromisoformat(start_time)
        elif isinstance(start_time, datetime):
            start_date = start_time
        else:
            start_date = datetime.now()
        
        # Use provided tasks or create default
        if tasks_data:
            tasks = tasks_data
        else:
            tasks = GanttChartBuilder.create_default_timeline(start_date)
        
        # Check if tasks are in new format (with task_id, name, etc.)
        if tasks and 'task_id' in tasks[0]:
            return GanttChartBuilder.create_task_gantt(tasks, demand_data.get('demand_id', 'Unnamed'))
        
        # Create DataFrame for phase-based timeline
        df = pd.DataFrame(tasks)
        
        # Create Gantt chart
        fig = ff.create_gantt(
            df,
            colors=GanttChartBuilder.PHASE_COLORS,
            index_col='Resource',
            show_colorbar=True,
            group_tasks=True,
            showgrid_x=True,
            showgrid_y=True,
            title=f"Project Timeline: {demand_data.get('demand_name', 'Unnamed Demand')}"
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title="Timeline",
            yaxis_title="Phase",
            height=500,
            hovermode='closest',
            font=dict(size=12)
        )
        
        return fig
    
    @staticmethod
    def create_task_gantt(tasks: List[Dict], demand_id: str) -> go.Figure:
        """Create Gantt chart from detailed task data.
        
        Args:
            tasks: List of task dictionaries with task_id, name, start_date, end_date, status, assigned_to, progress
            demand_id: Demand identifier for title
            
        Returns:
            Plotly figure object
        """
        # Convert tasks to DataFrame format expected by plotly
        gantt_data = []
        
        for task in tasks:
            gantt_data.append({
                'Task': task.get('name', task.get('task_id', 'Unnamed')),
                'Start': task.get('start_date'),
                'Finish': task.get('end_date'),
                'Resource': task.get('status', 'Planned'),  # Use status for coloring
                'Description': f"{task.get('description', '')}\nAssigned: {task.get('assigned_to', 'Unassigned')}\nProgress: {task.get('progress', 0)}%"
            })
        
        # Create DataFrame
        df = pd.DataFrame(gantt_data)
        
        # Create Gantt chart without color mapping (will use default colors)
        fig = ff.create_gantt(
            df,
            index_col='Resource',
            show_colorbar=True,
            group_tasks=True,
            showgrid_x=True,
            showgrid_y=True,
            title=f"Project Timeline: {demand_id}"
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title="Timeline",
            yaxis_title="Tasks",
            height=max(500, len(tasks) * 40),  # Dynamic height based on number of tasks
            hovermode='closest',
            font=dict(size=10),
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_milestone_chart(milestones: List[Dict]) -> go.Figure:
        """Create milestone visualization.
        
        Args:
            milestones: List of milestone dictionaries with date and description
            
        Returns:
            Plotly figure object
        """
        if not milestones:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No milestones defined yet",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        # Sort by date
        sorted_milestones = sorted(milestones, key=lambda x: x['date'])
        
        dates = [m['date'] for m in sorted_milestones]
        descriptions = [m['description'] for m in sorted_milestones]
        
        fig = go.Figure()
        
        # Add scatter plot for milestones
        fig.add_trace(go.Scatter(
            x=dates,
            y=[1] * len(dates),
            mode='markers+text',
            marker=dict(
                size=20,
                color='red',
                symbol='diamond',
                line=dict(width=2, color='darkred')
            ),
            text=descriptions,
            textposition='top center',
            hovertemplate='<b>%{text}</b><br>Date: %{x}<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title="Project Milestones",
            xaxis_title="Date",
            yaxis=dict(
                showticklabels=False,
                range=[0.5, 1.5]
            ),
            height=300,
            hovermode='closest'
        )
        
        return fig
    
    @staticmethod
    def calculate_progress_bars(demand_data: Dict) -> go.Figure:
        """Create progress visualization for all phases.
        
        Args:
            demand_data: Demand session state data
            
        Returns:
            Plotly figure object with horizontal bar chart
        """
        phases = [
            'Ideation',
            'Requirements',
            'Assessment',
            'Design',
            'Build',
            'Validation',
            'Deployment',
            'Implementation',
            'Closing'
        ]
        
        # Calculate completion for each phase (simplified)
        progress = []
        for phase in phases:
            phase_key = phase.lower()
            phase_data = demand_data.get(phase_key, {})
            
            # Simple heuristic: if data exists, consider it partially complete
            if isinstance(phase_data, dict):
                field_count = len([v for v in phase_data.values() if v])
                if field_count > 0:
                    completion = min(100, field_count * 20)  # 20% per field, max 100%
                else:
                    completion = 0
            else:
                completion = 0
            
            progress.append(completion)
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=phases,
            x=progress,
            orientation='h',
            marker=dict(
                color=progress,
                colorscale='RdYlGn',
                showscale=False
            ),
            text=[f'{p}%' for p in progress],
            textposition='inside',
            hovertemplate='<b>%{y}</b><br>Progress: %{x}%<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title="Phase Completion Progress",
            xaxis_title="Completion %",
            xaxis=dict(range=[0, 100]),
            yaxis_title="Phase",
            height=400,
            hovermode='closest'
        )
        
        return fig
    
    @staticmethod
    def create_task_dependency_chart(tasks: List[Dict]) -> go.Figure:
        """Create task dependency network visualization.
        
        Args:
            tasks: List of tasks with dependencies
            
        Returns:
            Plotly figure object
        """
        # This is a placeholder for future enhancement
        # Would require networkx for proper dependency graphs
        fig = go.Figure()
        fig.add_annotation(
            text="Task Dependency View - Coming Soon",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        return fig


def render_gantt_tab():
    """Render the Project Timeline / Gantt chart tab."""
    st.header("📊 Project Timeline & Gantt Chart")
    st.markdown("*Visualize project phases, milestones, and progress.*")
    
    # Add tabs for different views
    view_tab1, view_tab2, view_tab3 = st.tabs(["📅 Timeline", "🎯 Milestones", "📈 Progress"])
    
    with view_tab1:
        st.subheader("Project Timeline (Gantt Chart)")
        
        # Check if we have detailed task data in build section
        has_build_tasks = False
        build_tasks = []
        
        if 'build' in st.session_state and 'tasks' in st.session_state.build:
            build_tasks = st.session_state.build['tasks']
            # Check if tasks are detailed objects (not just strings)
            if build_tasks and isinstance(build_tasks[0], dict) and 'task_id' in build_tasks[0]:
                has_build_tasks = True
        
        # Choose visualization mode
        if has_build_tasks:
            st.info(f"📋 Found {len(build_tasks)} detailed tasks in Build section")
            viz_mode = st.radio(
                "Visualization mode",
                ["Detailed Tasks", "Phase Timeline"],
                horizontal=True
            )
        else:
            viz_mode = "Phase Timeline"
            st.info("💡 Using phase-based timeline. Add detailed tasks in Build section to see task-level Gantt chart.")
        
        if viz_mode == "Detailed Tasks" and has_build_tasks:
            # Display task-based Gantt chart
            try:
                fig = GanttChartBuilder.create_task_gantt(build_tasks, st.session_state.demand_id)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show task statistics
                completed = sum(1 for t in build_tasks if t.get('status') == 'Completed')
                in_progress = sum(1 for t in build_tasks if t.get('status') == 'In Progress')
                planned = sum(1 for t in build_tasks if t.get('status') == 'Planned')
                avg_progress = sum(t.get('progress', 0) for t in build_tasks) / len(build_tasks)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("✅ Completed", completed)
                with col2:
                    st.metric("🔄 In Progress", in_progress)
                with col3:
                    st.metric("📅 Planned", planned)
                with col4:
                    st.metric("📊 Avg Progress", f"{avg_progress:.0f}%")
                    
            except Exception as e:
                st.error(f"Error creating task Gantt chart: {str(e)}")
                st.exception(e)
                st.info("Falling back to phase timeline")
                viz_mode = "Phase Timeline"
        
        if viz_mode == "Phase Timeline":
            # Option to use custom dates or defaults
            use_custom = st.checkbox("Customize phase dates", value=False)
            
            if use_custom:
                st.info("💡 Customize individual phase durations below")
                
                # Create editable timeline
                col1, col2 = st.columns(2)
                
                with col1:
                    ideation_days = st.number_input("Ideation (days)", min_value=1, value=7)
                    requirements_days = st.number_input("Requirements (days)", min_value=1, value=14)
                    assessment_days = st.number_input("Assessment (days)", min_value=1, value=10)
                    design_days = st.number_input("Design (days)", min_value=1, value=21)
                    build_days = st.number_input("Build (days)", min_value=1, value=60)
                
                with col2:
                    validation_days = st.number_input("Validation (days)", min_value=1, value=14)
                    deployment_days = st.number_input("Deployment (days)", min_value=1, value=7)
                    implementation_days = st.number_input("Implementation (days)", min_value=1, value=30)
                    closing_days = st.number_input("Closing (days)", min_value=1, value=5)
                
                # Build custom timeline
                custom_durations = {
                    'Ideation': ideation_days,
                    'Requirements': requirements_days,
                    'Assessment': assessment_days,
                    'Design': design_days,
                    'Build': build_days,
                    'Validation': validation_days,
                    'Deployment': deployment_days,
                    'Implementation': implementation_days,
                    'Closing': closing_days
                }
                
                # Create tasks with custom durations
                start_date = st.session_state.start_time
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date)
                
                current_date = start_date
                tasks = []
                
                for phase_name, duration in custom_durations.items():
                    end_date = current_date + timedelta(days=duration)
                    tasks.append({
                        'Task': phase_name,
                        'Start': current_date.strftime('%Y-%m-%d'),
                        'Finish': end_date.strftime('%Y-%m-%d'),
                        'Resource': 'Phase',
                        'Description': f'{phase_name} phase',
                        'Duration': duration
                    })
                    current_date = end_date
                
                # Store in session state
                st.session_state['timeline_tasks'] = tasks
            else:
                # Use default timeline
                tasks = GanttChartBuilder.create_default_timeline(st.session_state.start_time)
                st.session_state['timeline_tasks'] = tasks
            
            # Create and display Gantt chart
            try:
                fig = GanttChartBuilder.create_gantt_from_demand(
                    st.session_state.to_dict(),
                    tasks
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Show total duration
                total_days = sum(task['Duration'] for task in tasks)
                total_weeks = total_days / 7
                st.info(f"📅 **Total Project Duration:** {total_days} days (~{total_weeks:.1f} weeks)")
                
            except Exception as e:
                st.error(f"Error creating Gantt chart: {str(e)}")
                st.info("Using default visualization")
    
    with view_tab2:
        st.subheader("🎯 Project Milestones")
        
        # Initialize milestones in session state
        if 'milestones' not in st.session_state:
            st.session_state.milestones = []
        
        # Add milestone form
        with st.form("add_milestone"):
            col1, col2 = st.columns(2)
            
            with col1:
                milestone_date = st.date_input("Milestone Date")
            
            with col2:
                milestone_desc = st.text_input("Description", placeholder="e.g., Requirements Approval")
            
            submitted = st.form_submit_button("➕ Add Milestone")
            
            if submitted and milestone_desc:
                st.session_state.milestones.append({
                    'date': milestone_date.strftime('%Y-%m-%d'),
                    'description': milestone_desc
                })
                st.success("✅ Milestone added!")
                st.rerun()
        
        # Display milestones
        if st.session_state.milestones:
            fig = GanttChartBuilder.create_milestone_chart(st.session_state.milestones)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show list
            st.markdown("**Defined Milestones:**")
            for idx, milestone in enumerate(st.session_state.milestones):
                col1, col2, col3 = st.columns([2, 4, 1])
                with col1:
                    st.text(milestone['date'])
                with col2:
                    st.text(milestone['description'])
                with col3:
                    if st.button("🗑️", key=f"del_milestone_{idx}"):
                        st.session_state.milestones.pop(idx)
                        st.rerun()
        else:
            st.info("No milestones defined yet. Add your first milestone above!")
    
    with view_tab3:
        st.subheader("📈 Phase Completion Progress")
        
        # Create progress visualization
        fig = GanttChartBuilder.calculate_progress_bars(st.session_state.to_dict())
        st.plotly_chart(fig, use_container_width=True)
        
        # Overall progress
        overall = st.session_state.get('progress_percentage', 0)
        st.metric("Overall Progress", f"{overall}%", delta=None)
