#!/usr/bin/env python3
"""
Streamlit Web Interface for Dev Orchestrator
Provides a user-friendly web interface for task orchestration
"""

import streamlit as st
import asyncio
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dev_orchestrator import DevOrchestrator

# Page configuration
st.set_page_config(
    page_title="Dev Orchestrator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .task-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = DevOrchestrator()
if 'task_history' not in st.session_state:
    st.session_state.task_history = []
if 'current_tasks' not in st.session_state:
    st.session_state.current_tasks = []

def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">🚀 Dev Orchestrator</h1>', unsafe_allow_html=True)
    st.markdown("### Intelligent Task Routing & Execution System")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model provider selection
        model_provider = st.selectbox(
            "Model Provider",
            ["LM Studio (Local)", "OpenAI", "Anthropic", "Azure OpenAI"]
        )
        
        if model_provider == "LM Studio (Local)":
            endpoint = st.text_input("LM Studio Endpoint", value="http://localhost:1234")
        
        # Execution settings
        st.subheader("Execution Settings")
        parallel_execution = st.checkbox("Parallel Execution", value=True)
        save_history = st.checkbox("Save History", value=True)
        max_workers = st.slider("Max Parallel Workers", 1, 10, 3)
        
        # Quick actions
        st.subheader("Quick Actions")
        if st.button("Clear History", type="secondary"):
            st.session_state.task_history = []
            st.success("History cleared!")
        
        if st.button("Export History", type="secondary"):
            if st.session_state.task_history:
                history_json = json.dumps(st.session_state.task_history, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=history_json,
                    file_name=f"task_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Task Input", "📊 Dashboard", "📜 History", "⚡ Templates"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Enter Tasks")
            
            # Task input methods
            input_method = st.radio(
                "Input Method",
                ["Text Area", "Individual Tasks", "File Upload"],
                horizontal=True
            )
            
            tasks_to_process = []
            
            if input_method == "Text Area":
                task_text = st.text_area(
                    "Enter tasks (one per line or comma-separated)",
                    height=200,
                    placeholder="Example:\nRefactor authentication module with SOLID principles\nAdd unit tests with >80% coverage\nUpdate technical documentation"
                )
                if task_text:
                    tasks_to_process = task_text.split('\n') if '\n' in task_text else task_text.split(',')
            
            elif input_method == "Individual Tasks":
                num_tasks = st.number_input("Number of tasks", min_value=1, max_value=20, value=3)
                tasks_to_process = []
                for i in range(num_tasks):
                    task = st.text_input(f"Task {i+1}", key=f"task_{i}")
                    if task:
                        tasks_to_process.append(task)
            
            else:  # File Upload
                uploaded_file = st.file_uploader("Choose a file", type=['txt', 'json'])
                if uploaded_file:
                    content = uploaded_file.read().decode('utf-8')
                    if uploaded_file.name.endswith('.json'):
                        tasks_to_process = json.loads(content)
                    else:
                        tasks_to_process = content.split('\n')
        
        with col2:
            st.subheader("Task Preview")
            if tasks_to_process:
                st.write("**Tasks to execute:**")
                for i, task in enumerate(tasks_to_process, 1):
                    if task.strip():
                        task_type = st.session_state.orchestrator._identify_task_type(task)
                        priority = st.session_state.orchestrator._estimate_priority(task)
                        
                        # Task card
                        st.markdown(f"""
                        <div class="task-card">
                            <b>Task {i}</b><br>
                            📌 Type: {task_type}<br>
                            ⭐ Priority: {'⭐' * priority}<br>
                            📝 {task[:50]}{'...' if len(task) > 50 else ''}
                        </div>
                        """, unsafe_allow_html=True)
        
        # Execute button
        if st.button("🚀 Execute Tasks", type="primary", disabled=not tasks_to_process):
            with st.spinner("Processing tasks..."):
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Parse tasks
                parsed_tasks = st.session_state.orchestrator.parse_tasks('\n'.join(tasks_to_process))
                st.session_state.current_tasks = parsed_tasks
                
                # Simulate execution (replace with actual async execution)
                for i, task in enumerate(parsed_tasks):
                    progress = (i + 1) / len(parsed_tasks)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing: {task['description'][:50]}...")
                    
                    # Add to history
                    result = {
                        'task': task['description'],
                        'type': task['type'],
                        'priority': task['priority'],
                        'status': 'completed',
                        'timestamp': datetime.now().isoformat(),
                        'duration': 2.5  # Simulated
                    }
                    st.session_state.task_history.append(result)
                
                progress_bar.progress(1.0)
                status_text.text("All tasks completed!")
                st.success(f"✅ Successfully executed {len(parsed_tasks)} tasks!")
                st.balloons()
    
    with tab2:
        st.subheader("📊 Execution Dashboard")
        
        if st.session_state.task_history:
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Tasks", len(st.session_state.task_history))
            with col2:
                completed = sum(1 for t in st.session_state.task_history if t['status'] == 'completed')
                st.metric("Completed", completed)
            with col3:
                avg_duration = sum(t.get('duration', 0) for t in st.session_state.task_history) / len(st.session_state.task_history)
                st.metric("Avg Duration", f"{avg_duration:.1f}s")
            with col4:
                success_rate = (completed / len(st.session_state.task_history)) * 100
                st.metric("Success Rate", f"{success_rate:.0f}%")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Task type distribution
                df = pd.DataFrame(st.session_state.task_history)
                if 'type' in df.columns:
                    type_counts = df['type'].value_counts()
                    fig = px.pie(
                        values=type_counts.values,
                        names=type_counts.index,
                        title="Task Distribution by Type"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Priority distribution
                if 'priority' in df.columns:
                    priority_counts = df['priority'].value_counts().sort_index()
                    fig = px.bar(
                        x=priority_counts.index,
                        y=priority_counts.values,
                        title="Task Priority Distribution",
                        labels={'x': 'Priority', 'y': 'Count'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Timeline
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=range(len(df)),
                    mode='lines+markers',
                    name='Tasks',
                    line=dict(color='blue', width=2),
                    marker=dict(size=8)
                ))
                fig.update_layout(
                    title="Task Execution Timeline",
                    xaxis_title="Time",
                    yaxis_title="Task Count",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No task history available. Execute some tasks to see the dashboard.")
    
    with tab3:
        st.subheader("📜 Task History")
        
        if st.session_state.task_history:
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_type = st.selectbox("Filter by Type", ["All"] + list(set(t.get('type', 'general') for t in st.session_state.task_history)))
            with col2:
                filter_status = st.selectbox("Filter by Status", ["All", "completed", "failed", "pending"])
            with col3:
                sort_order = st.selectbox("Sort by", ["Newest First", "Oldest First", "Priority"])
            
            # Filter and sort history
            filtered_history = st.session_state.task_history.copy()
            
            if filter_type != "All":
                filtered_history = [t for t in filtered_history if t.get('type') == filter_type]
            
            if filter_status != "All":
                filtered_history = [t for t in filtered_history if t.get('status') == filter_status]
            
            if sort_order == "Newest First":
                filtered_history.reverse()
            elif sort_order == "Priority":
                filtered_history.sort(key=lambda x: x.get('priority', 0), reverse=True)
            
            # Display history
            for task in filtered_history:
                with st.expander(f"{task['task'][:50]}..." if len(task['task']) > 50 else task['task']):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Type:** {task.get('type', 'general')}")
                        st.write(f"**Priority:** {'⭐' * task.get('priority', 1)}")
                        st.write(f"**Status:** {task.get('status', 'unknown')}")
                    with col2:
                        st.write(f"**Timestamp:** {task.get('timestamp', 'N/A')}")
                        st.write(f"**Duration:** {task.get('duration', 0):.1f}s")
                    
                    st.write("**Full Description:**")
                    st.code(task['task'])
        else:
            st.info("No task history available.")
    
    with tab4:
        st.subheader("⚡ Task Templates")
        
        templates = {
            "Full Stack Development": [
                "Refactor authentication module with SOLID principles",
                "Add unit tests with coverage >80%",
                "Update API documentation",
                "Optimize database queries",
                "Create pull request with conventional commits"
            ],
            "Bug Fix Workflow": [
                "Analyze bug report and reproduce issue",
                "Identify root cause in codebase",
                "Implement fix with minimal changes",
                "Add regression tests",
                "Update changelog and create PR"
            ],
            "Feature Development": [
                "Design feature architecture",
                "Implement core functionality",
                "Add comprehensive tests",
                "Write user documentation",
                "Update API endpoints if needed",
                "Create feature flag for rollout"
            ],
            "Code Quality": [
                "Run static analysis and fix issues",
                "Refactor complex functions",
                "Add missing type hints",
                "Update outdated dependencies",
                "Improve error handling"
            ],
            "Performance Optimization": [
                "Profile application performance",
                "Identify bottlenecks",
                "Optimize critical paths",
                "Add caching where appropriate",
                "Validate improvements with benchmarks"
            ]
        }
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            selected_template = st.selectbox("Select Template", list(templates.keys()))
        
        with col2:
            if st.button("Load Template"):
                st.session_state.loaded_template = templates[selected_template]
                st.success(f"Loaded {selected_template} template!")
        
        if 'loaded_template' in st.session_state:
            st.write("**Template Tasks:**")
            for i, task in enumerate(st.session_state.loaded_template, 1):
                st.write(f"{i}. {task}")
            
            if st.button("Use This Template", type="primary"):
                st.info("Template loaded! Go to the Task Input tab to execute.")

if __name__ == "__main__":
    main()