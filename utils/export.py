"""Export utilities for demand data."""
import json
from typing import Dict, Any
from datetime import datetime


def export_to_json(demand_data: Dict[str, Any]) -> str:
    """
    Export demand data to JSON string.
    
    Args:
        demand_data: Complete demand data dictionary
        
    Returns:
        JSON string
    """
    # Create a serializable copy
    export_data = _prepare_for_export(demand_data)
    
    return json.dumps(export_data, indent=2, default=str)


def export_to_markdown(demand_data: Dict[str, Any]) -> str:
    """
    Export demand data to markdown format.
    
    Args:
        demand_data: Complete demand data dictionary
        
    Returns:
        Markdown formatted string
    """
    demand_id = demand_data.get("demand_id", "UNKNOWN")
    created_at = demand_data.get("created_at", datetime.now())
    
    md = f"""# Demand Report: {demand_id}

**Created:** {created_at}  
**Status:** {demand_data.get('status', 'Draft')}  
**Progress:** {demand_data.get('progress_percentage', 0)}%

---

## 1. Ideation

### Problem Statement
{demand_data.get('ideation', {}).get('problem_statement', 'Not provided')}

### Goals
{demand_data.get('ideation', {}).get('goals', 'Not provided')}

### Background
{demand_data.get('ideation', {}).get('background', 'Not provided')}

---

## 2. Requirements

### Stakeholders
"""
    
    stakeholders = demand_data.get('requirements', {}).get('stakeholders', [])
    if stakeholders:
        for sh in stakeholders:
            md += f"- **{sh.get('name', 'N/A')}** ({sh.get('role', 'N/A')}) - {sh.get('power_interest', 'N/A')}\n"
    else:
        md += "No stakeholders defined\n"
    
    md += f"""
### User Stories
{demand_data.get('requirements', {}).get('user_stories', 'Not provided')}

### Acceptance Criteria
{demand_data.get('requirements', {}).get('acceptance_criteria', 'Not provided')}

---

## 3. Assessment

### Business Case
{demand_data.get('assessment', {}).get('business_case', 'Not provided')}

### ROI
{demand_data.get('assessment', {}).get('roi_percentage', 'N/A')}%

### Risks
{demand_data.get('assessment', {}).get('risks', 'Not provided')}

---

## 4. Design

### Architecture Overview
{demand_data.get('design', {}).get('architecture_overview', 'Not provided')}

### Technical Stack
{demand_data.get('design', {}).get('technical_stack', 'Not provided')}

---

## 5. Build

### Sprint Plan
{demand_data.get('build', {}).get('sprint_plan', 'Not provided')}

### JIRA Epic
{demand_data.get('build', {}).get('jira_epic_id', 'Not created')}

---

## 6. Validation

### Test Cases
{demand_data.get('validation', {}).get('test_cases', 'Not provided')}

### QA Sign-Off
{'✅ Approved' if demand_data.get('validation', {}).get('qa_sign_off') else '❌ Pending'}

---

## 7. Deployment

### Schedule
{demand_data.get('deployment', {}).get('deployment_schedule', 'Not scheduled')}

### Rollout Plan
{demand_data.get('deployment', {}).get('rollout_plan', 'Not provided')}

---

## 8. Implementation

### Success Metrics
"""
    
    metrics = demand_data.get('implementation', {}).get('success_metrics', {})
    if metrics:
        for key, value in metrics.items():
            md += f"- {key}: {value}\n"
    else:
        md += "No metrics defined\n"
    
    md += f"""
---

## 9. Closing

### Retrospective
{demand_data.get('closing', {}).get('retrospective', 'Not completed')}

### Lessons Learned
{demand_data.get('closing', {}).get('lessons_learned', 'Not documented')}

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return md


def generate_pdf_content(demand_data: Dict[str, Any]) -> str:
    """
    Generate HTML content suitable for PDF conversion.
    Uses markdown as base and adds styling.
    
    Args:
        demand_data: Complete demand data dictionary
        
    Returns:
        HTML string with embedded CSS
    """
    markdown_content = export_to_markdown(demand_data)
    
    # Convert markdown to HTML (simplified - in production use markdown library)
    html_content = markdown_content.replace("\n", "<br>")
    html_content = html_content.replace("# ", "<h1>")
    html_content = html_content.replace("## ", "<h2>")
    html_content = html_content.replace("### ", "<h3>")
    html_content = html_content.replace("**", "<strong>").replace("**", "</strong>")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Demand Report - {demand_data.get('demand_id', 'UNKNOWN')}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 900px;
                margin: 40px auto;
                padding: 20px;
                line-height: 1.6;
                color: #333;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                margin-top: 30px;
                border-left: 4px solid #3498db;
                padding-left: 10px;
            }}
            h3 {{
                color: #7f8c8d;
            }}
            hr {{
                border: none;
                border-top: 1px solid #ecf0f1;
                margin: 30px 0;
            }}
            .metadata {{
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    return html


def _prepare_for_export(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare data for JSON export by handling non-serializable types.
    
    Args:
        data: Raw data dictionary
        
    Returns:
        Serializable dictionary
    """
    if isinstance(data, dict):
        return {k: _prepare_for_export(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_prepare_for_export(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    elif hasattr(data, '__dict__'):
        return _prepare_for_export(data.__dict__)
    else:
        return data
