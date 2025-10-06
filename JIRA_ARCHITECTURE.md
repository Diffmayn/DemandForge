# JIRA Integration Architecture

## System Overview

```
DemandForge Application (Streamlit)
         ↓
Validation Tab UI
         ↓
JIRA Test Components
         ↓
    ┌────┴────┐
    ↓         ↓
JIRA API   Gemini AI
```

## Component Architecture

### 1. UI Layer (components/jira_test_ui.py)
- Connection setup UI
- Test generation UI
- Test plan creation UI
- Upload handlers

### 2. Business Logic (integrations/jira_test_client.py)
- JiraClient class (JIRA API wrapper)
- TestCaseGenerator class (AI integration)
- Authentication management
- Error handling

### 3. Integration Layer
- JIRA REST API v3
- Gemini 2.5 Flash AI
- Document reader utilities

## Data Flow

### Connection Flow
```
User Input → Session State → JiraClient → JIRA API → Validation → UI Update
```

### Test Generation Flow
```
Requirements/Design → Context Assembly → AI Agent → Parse Response → Session State → UI Display
```

### Upload Flow
```
Generated Tests → User Edits → JiraClient → JIRA API → Success/Failure → UI Feedback
```

## Authentication

```
Email + API Token → Base64 Encoding → Basic Auth Header → HTTPS → JIRA API
```

## Security

- Tokens stored in session state (memory only)
- No disk persistence
- HTTPS for all API calls
- Basic authentication with JIRA

## State Management

Session state stores:
- Connection credentials
- JiraClient instance
- Generated test cases
- JIRA projects list
- Connection status

## Error Handling

All errors are caught and displayed in the UI with:
- User-friendly messages
- Actionable suggestions
- Debug information when available

