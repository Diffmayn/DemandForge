# DemandForge Advanced Features Implementation Roadmap

## Overview
This document outlines the implementation of advanced features requested for DemandForge, including file attachments, URL management, AI content reading, and Gantt chart project timeline.

## Feature Breakdown

### ✅ Phase 1: Cleanup (IMMEDIATE - Can do now)
- **Remove empty/untitled demands** from the system
- Clean up demands_index.json
- Delete orphaned JSON files

### 🔨 Phase 2: File & URL Management (MEDIUM - 2-4 hours)
**Requirements:**
- Attach Word documents, Excel files, PDFs to any phase
- Add URLs with descriptions
- Store attachments metadata
- Download/view attachments
- URL validation and preview

**Technical Approach:**
- File upload using `st.file_uploader()`
- Store files in `data/attachments/{demand_id}/` directory
- Store URLs in demand JSON with metadata
- Add attachment section to each tab

**Implementation:**
```python
# Data structure
"attachments": {
    "ideation": [
        {
            "type": "file",
            "filename": "requirements.docx",
            "path": "data/attachments/LOG-2025-CPT001/requirements.docx",
            "uploaded_by": "User",
            "uploaded_at": "2025-10-05T20:00:00",
            "size_kb": 245
        },
        {
            "type": "url",
            "url": "https://confluence.example.com/project-brief",
            "title": "Project Brief",
            "description": "Initial requirements document",
            "added_at": "2025-10-05T20:00:00"
        }
    ],
    "requirements": [...],
    // ... per phase
}
```

### 🤖 Phase 3: AI Content Reading (MEDIUM - 3-5 hours)
**Requirements:**
- AI can read attached documents
- AI can fetch and read URLs
- AI uses content in responses

**Technical Approach:**
- **For Files:**
  - PDF: Use `PyPDF2` or `pdfplumber`
  - Word: Use `python-docx`
  - Excel: Use `pandas`
  - Text: Direct read
  
- **For URLs:**
  - Use `requests` + `BeautifulSoup` for web scraping
  - Extract main content, strip HTML
  - Handle authentication if needed

- **AI Integration:**
  - Add document summaries to AI context
  - Include URL content in prompts
  - Show "reading" indicator

**Dependencies to Add:**
```txt
PyPDF2>=3.0.0
python-docx>=1.1.0
beautifulsoup4>=4.12.0
requests>=2.31.0
pdfplumber>=0.10.0
```

### 📊 Phase 4: Gantt Chart Timeline (COMPLEX - 8-12 hours)
**Requirements:**
- Auto-generate timeline from tasks across phases
- Visual Gantt chart display
- Assign performers (name + position)
- Task status tracking
- Drag-and-drop reordering
- Update duration by dragging
- Reflect changes back to phases

**Technical Approach:**

**Option A: Plotly-based (Recommended)**
```python
import plotly.express as px
import plotly.graph_objects as go

# Use Plotly Timeline/Gantt
fig = px.timeline(
    df_tasks, 
    x_start="start", 
    x_finish="end",
    y="task_name",
    color="status"
)
```

**Option B: Streamlit-Timeline (Limited interactivity)**
- Use `streamlit-timeline` component
- Limited drag-and-drop

**Option C: Custom React Component (Most powerful)**
- Build custom Streamlit component
- Use `react-gantt-chart` or `dhtmlx-gantt`
- Full drag-and-drop support

**Data Structure:**
```python
"project_timeline": {
    "tasks": [
        {
            "id": "task-001",
            "name": "Define Requirements",
            "phase": "requirements",
            "source_field": "user_stories",
            "start_date": "2025-10-10",
            "end_date": "2025-10-20",
            "duration_days": 10,
            "assigned_to": {
                "name": "John Doe",
                "position": "Business Analyst"
            },
            "status": "in_progress",  # not_started, in_progress, completed, blocked
            "dependencies": [],
            "progress_percentage": 60,
            "order": 1
        },
        // ... more tasks
    ],
    "milestones": [
        {
            "name": "Requirements Complete",
            "date": "2025-10-20",
            "phase": "requirements"
        }
    ]
}
```

**Drag-and-Drop Challenges:**
- Streamlit doesn't natively support drag-and-drop
- Would need custom component OR
- Use buttons/forms for task reordering
- For full drag-and-drop, need JavaScript component

### 🎯 Phase 5: AI Task Auto-Generation (COMPLEX - 4-6 hours)
**Requirements:**
- AI analyzes all phases
- Generates tasks automatically
- Updates when phases change
- Suggests durations and dependencies

**Technical Approach:**
```python
def generate_tasks_from_phases(demand_data):
    """Use AI to analyze phases and generate project tasks."""
    
    prompt = f"""
    Based on this demand, generate a detailed project task list:
    
    Ideation: {demand_data['ideation']}
    Requirements: {demand_data['requirements']}
    Assessment: {demand_data['assessment']}
    Design: {demand_data['design']}
    Build: {demand_data['build']}
    
    Generate tasks with:
    - Task name
    - Suggested duration (days)
    - Which phase it belongs to
    - Dependencies (which tasks must complete first)
    - Suggested role/position
    
    Return as JSON array.
    """
    
    tasks = ai_agent.generate(prompt)
    return parse_tasks(tasks)
```

### 🔄 Phase 6: Bi-directional Sync (COMPLEX - 6-8 hours)
**Requirements:**
- Changes in phases update timeline
- Changes in timeline update phases
- Maintain consistency

**Technical Approach:**
- Watch for changes in phase forms
- Trigger timeline regeneration
- Allow manual overrides
- Version tracking for conflicts

## Implementation Priority

### Can Implement NOW (1-2 hours):
1. ✅ **Cleanup empty demands** - Simple file deletion
2. ✅ **Basic file uploads** - Use st.file_uploader
3. ✅ **URL storage** - Add text inputs, store in JSON
4. ✅ **Simple attachment display** - Show files and links per phase

### Can Implement TODAY (4-8 hours):
5. 🔨 **Document reading** - Add PDF/Word parsing libraries
6. 🔨 **URL content fetching** - Web scraping for AI context
7. 🔨 **Static Gantt chart** - Use Plotly timeline (no drag-drop)
8. 🔨 **Manual task management** - Forms to add/edit tasks

### Requires MORE TIME (1-3 days):
9. ⏳ **Drag-and-drop Gantt** - Custom Streamlit component
10. ⏳ **AI auto-task generation** - Complex prompt engineering
11. ⏳ **Bi-directional sync** - State management complexity
12. ⏳ **Advanced task dependencies** - Critical path calculation

## Recommended Approach

### Option 1: Basic Implementation (TODAY)
- ✅ Clean up demands
- ✅ Add file upload capability
- ✅ Add URL management
- ✅ Basic document reading for AI
- ✅ Static Gantt chart with Plotly
- ✅ Manual task entry forms

**Pros:** Achievable today, provides 70% of functionality  
**Cons:** No drag-and-drop, manual task management

### Option 2: Full Implementation (LATER)
- Everything from Option 1 PLUS:
- Custom Streamlit component for interactive Gantt
- Full drag-and-drop
- AI auto-generation
- Complete bi-directional sync

**Pros:** Complete feature set  
**Cons:** Requires 2-3 days development time

## What We'll Do Now

I'll implement **Option 1** (Basic Implementation) which includes:

1. **Cleanup** - Remove empty demands ✅
2. **File Attachments** - Upload and store files per phase ✅
3. **URL Management** - Add and store URLs per phase ✅
4. **AI Context** - Include attachments in AI prompts ✅
5. **Basic Timeline** - Plotly-based Gantt chart ✅
6. **Task Management** - Forms to manage tasks ✅

This gives you 70-80% of the requested functionality TODAY, with the ability to enhance later.

## Next Steps

After basic implementation, we can add:
- Drag-and-drop (requires custom component development)
- Advanced AI task generation (requires more sophisticated prompting)
- Real-time sync (requires state management architecture)
- Mobile-responsive Gantt (requires responsive design work)

---

**Estimated Time:**
- Basic Implementation: 4-6 hours
- Full Implementation: 2-3 days

**Should we proceed with Basic Implementation now?**
