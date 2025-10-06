# DemandForge 🔨

**Comprehensive IT Demand Lifecycle Management Platform**

A production-ready Streamlit application for managing IT demands from ideation to closing. Built for Salling Group's retail operations to centralize documentation, stakeholder collaboration, and project artifacts across the entire demand lifecycle.

## 🎯 Features

### Core Capabilities
- **9-Phase Demand Lifecycle**: Ideation → Requirements → Assessment → Design → Build → Validation → Deployment → Implementation → Closing
- **AI Co-Pilot**: Context-aware assistance for problem analysis, user stories, risk prediction, and test case generation
- **AI-Powered Test Case Generation**: Automatically generate manual and automated test cases from requirements and design ⭐ NEW
- **JIRA Test Integration**: Upload AI-generated test cases directly to JIRA with test plan management ⭐ NEW
- **AI Document Reading**: Extract text from PDFs, Word docs, Excel files, and web pages for AI context ⭐ NEW
- **Interactive Gantt Charts**: Visualize demand timeline with Plotly-based interactive charts ⭐ NEW
- **Stakeholder Management**: Track power/interest matrix, roles, and sign-offs
- **Progress Tracking**: Automatic calculation based on tab completion
- **Audit Logging**: Full change history with timestamps and trace IDs
- **Multi-Format Export**: JSON, Markdown, and PDF-ready HTML exports
- **Confluence Integration**: Document export capabilities
- **Session Management**: TTL-based with warning system
- **Security**: Input validation, HTML escaping, sanitization

### Tab-by-Tab Features

1. **💡 Ideation**: Problem statements, goals, background, constraints
2. **📋 Requirements**: Stakeholders, user stories, acceptance criteria, features
3. **📊 Assessment**: Business case, ROI calculator, risks, dependencies
4. **🎨 Design**: Architecture, tech stack, data models, security
5. **🔨 Build**: Task tracking, sprint planning, JIRA integration
6. **🧪 Validation**: Test cases, AI test generation, JIRA test upload, bug log, QA sign-off ⭐ ENHANCED
7. **🚀 Deployment**: Rollout plans, environment config, training materials
8. **📈 Implementation**: Metrics dashboard, issue tracking, user feedback
9. **🎯 Closing**: Retrospective, lessons learned, stakeholder sign-offs
10. **📅 Timeline**: Interactive Gantt charts with milestones and progress visualization ⭐ NEW

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Installation

1. **Clone or navigate to the repository**:
```powershell
cd c:\Users\248075\.vscode\cli\DemandForge
```

2. **Install dependencies**:
```powershell
pip install -r requirements.txt
```

3. **Configure environment (optional)**:
```powershell
cp .env.example .env
# Edit .env with your credentials (for real JIRA/Confluence integration)
```

4. **Run the application**:
```powershell
streamlit run app.py
```

5. **Open your browser** to `http://localhost:8501`

## 📁 Project Structure

```
DemandForge/
├── app.py                      # Main Streamlit application (2,000+ lines)
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # This file
├── JIRA_INTEGRATION_GUIDE.md  # JIRA test case integration guide ⭐ NEW
├── JIRA_IMPLEMENTATION_SUMMARY.md  # Technical implementation details ⭐ NEW
├── JIRA_ARCHITECTURE.md       # Architecture diagrams ⭐ NEW
├── OPTION4_COMPLETE.md        # AI document reading & Gantt features ⭐ NEW
├── TEST_GUIDE.md              # Testing instructions ⭐ NEW
├── models/
│   ├── __init__.py
│   └── demand.py              # Pydantic models for all tabs
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Abstract agent interface
│   ├── mock_agent.py          # Mock AI agent implementation
│   └── gemini_agent.py        # Gemini 2.5 Flash integration ⭐ NEW
├── integrations/
│   ├── __init__.py
│   ├── jira_client.py         # JIRA API integration (Build phase)
│   ├── jira_test_client.py    # JIRA test case integration ⭐ NEW
│   └── confluence_client.py   # Confluence API integration
├── components/
│   ├── __init__.py
│   └── jira_test_ui.py        # JIRA test UI components ⭐ NEW
├── utils/
│   ├── __init__.py
│   ├── progress.py            # Progress calculation
│   ├── export.py              # Export to JSON/Markdown/PDF
│   ├── validation.py          # Security and validation
│   ├── logging_config.py      # Structured logging
│   ├── storage.py             # JSON file storage
│   ├── document_reader.py     # AI document reading ⭐ NEW
│   └── gantt_chart.py         # Interactive Gantt charts ⭐ NEW
├── data/                      # Demand storage (JSON files)
│   ├── demands_index.json     # Fast lookup index
│   └── demands/               # Individual demand files
└── tests/
    ├── __init__.py
    ├── test_agent.py          # Agent tests
    ├── test_validation.py     # Validation tests
    ├── test_progress.py       # Progress calculation tests
    └── test_jira.py           # JIRA integration tests
```

## 🧪 Testing

Run the full test suite:

```powershell
pytest tests/ -v
```

Run specific test file:

```powershell
pytest tests/test_agent.py -v
```

Run with coverage:

```powershell
pytest --cov=. --cov-report=html tests/
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```env
# JIRA Configuration
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your_token_here

# Confluence Configuration
CONFLUENCE_URL=https://your-company.atlassian.net/wiki
CONFLUENCE_API_TOKEN=your_token_here

# Session Configuration
SESSION_TTL_MINUTES=60

# Role-Based Access (Future)
ENABLE_ROLE_CHECK=false
```

### Real JIRA/Confluence Integration

To enable real API calls (instead of mocks):

1. Set up API tokens in Atlassian
2. Configure `.env` with your credentials
3. Update `app.py` to use `RealJiraClient` and `RealConfluenceClient`

## 💡 Usage Guide

### Creating a New Demand

1. **Launch the app** - A unique demand ID is auto-generated (e.g., LOG-2025-A1B2C3D4)
2. **Use the AI Co-Pilot** - Ask questions, generate content, get suggestions
3. **Fill tabs sequentially** - Data flows forward (e.g., goals → features)
4. **Track progress** - Progress bar updates automatically
5. **Export anytime** - JSON for data, Markdown for reports

### 🤖 AI Test Case Generation (NEW!)

**Automatically generate and upload test cases to JIRA:**

1. **Setup JIRA Connection** (one-time):
   - Go to Validation tab
   - Expand "🔗 JIRA Connection Setup"
   - Get your API token from https://id.atlassian.com/manage-profile/security/api-tokens
   - Enter JIRA URL, email, token, and project key
   - Click "Save & Test Connection"

2. **Generate Manual Test Cases**:
   - Fill in Requirements tab first (user stories, acceptance criteria)
   - Go to Validation → "📝 Manual Test Cases"
   - Set number of test cases (1-20)
   - Choose default priority
   - Click "🤖 Generate Manual Test Cases"
   - Review and edit generated tests
   - Click "📤 Upload All to JIRA"

3. **Generate Automated Test Cases**:
   - Fill in Design tab first (architecture, tech stack)
   - Go to Validation → "⚙️ Automated Test Cases"
   - Choose test framework (pytest, selenium, etc.)
   - Set number of test cases (1-30)
   - Click "🤖 Generate Automated Test Cases"
   - Review test code snippets
   - Click "📤 Upload All to JIRA"

4. **Create Test Plan**:
   - Generate test cases first (manual and/or automated)
   - Scroll to "📋 Test Plan Generator"
   - Enter test plan name and description
   - Enable "Generate AI Test Strategy" for comprehensive plan
   - Click "📋 Create Test Plan in JIRA"
   - Test plan is created as an Epic in JIRA

**See [JIRA_INTEGRATION_GUIDE.md](JIRA_INTEGRATION_GUIDE.md) for detailed instructions.**

### 📄 AI Document Reading (NEW!)

**Extract text from documents for AI context:**

- **Supported formats**: PDF, Word (.docx), Excel (.xlsx), Images (metadata), URLs
- **How to use**:
  1. Go to any phase tab (Requirements, Design, etc.)
  2. Scroll to "Attachments" section
  3. Upload files or add URLs
  4. Files are automatically read when using AI assistant
  5. Click "Ask AI about attachments" for document-specific questions

**Examples:**
- Upload requirements PDF → AI generates test cases from it
- Add API documentation URL → AI generates automated tests
- Upload design diagrams → AI analyzes architecture

### 📅 Interactive Timeline (NEW!)

**Visualize your demand timeline:**

1. Go to **Timeline** tab (new 10th tab)
2. View three visualization types:
   - **Timeline View**: Gantt chart with all 9 phases
   - **Milestones View**: Key deliverables with diamond markers
   - **Progress View**: Horizontal bar chart of completion %
3. Customize:
   - Set project start date
   - Adjust phase durations
   - Add custom milestones
4. Export timeline as image or interactive HTML

### AI Co-Pilot Commands

The AI assistant responds to:
- "Analyze the problem" → 5 Whys analysis
- "Generate user stories" → INVEST-format stories
- "What are the risks?" → RAG-based risk analysis
- "Create test cases" → Test scenarios from requirements
- "Suggest architecture" → Design patterns and best practices
- "Help with estimation" → Effort and cost guidance
- "Summarize this document" → Extract key points from attachments
- "Generate automated tests" → Code-based test cases

### Best Practices

1. **Start with Ideation**: Clearly define the problem before moving forward
2. **Add Stakeholders Early**: Identify all affected parties in Requirements
3. **Quantify Everything**: Use specific metrics for goals and ROI
4. **Link Phases**: Reference earlier tabs (e.g., link tests to acceptance criteria)
5. **Save Frequently**: Each tab has a save button - use it
6. **Export for Backup**: Download JSON periodically
7. **Complete Closing**: Capture lessons learned while fresh

## 🔒 Security Features

- **Input Validation**: Pydantic models with max lengths
- **Output Escaping**: HTML sanitization for all user content
- **Session TTL**: Automatic timeout after 60 minutes
- **Audit Logging**: All changes tracked with trace IDs
- **PII Protection**: Structured logger redacts sensitive fields
- **Path Sanitization**: Filename validation prevents traversal

## 🚀 Deployment

### Local Development
```powershell
streamlit run app.py
```

### Production (Streamlit Cloud)
1. Push to GitHub
2. Connect repository in Streamlit Cloud
3. Add secrets (JIRA tokens, etc.)
4. Deploy

### Docker (Future)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

## 📈 Roadmap

### Phase 1 (Current - POC)
- ✅ All 9 tabs with full functionality
- ✅ Mock AI agent
- ✅ Session state persistence
- ✅ Mock JIRA/Confluence integration
- ✅ Export to JSON/Markdown

### Phase 2 (Next)
- [ ] PostgreSQL persistence
- [ ] Real Watsonx AI integration
- [ ] RAG from historical demands
- [ ] Real-time collaboration (WebSockets)
- [ ] Role-based access control

### Phase 3 (Future)
- [ ] API for cross-app integration
- [ ] Webhook triggers
- [ ] Mobile app
- [ ] Advanced analytics dashboard
- [ ] ML-powered recommendations

## 🤝 Contributing

### Development Setup

1. **Create virtual environment**:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. **Install dev dependencies**:
```powershell
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy
```

3. **Run code formatters**:
```powershell
black . --line-length 100
flake8 . --max-line-length=100
mypy . --ignore-missing-imports
```

### Code Style

- **PEP 8** compliance
- **Type hints** on all functions
- **Docstrings** (Google style)
- **Max line length**: 100 characters
- **Imports**: stdlib → third-party → local

## 📄 License

© 2025 Salling Group. Internal use only.

## 🆘 Support

### Common Issues

**Q: "Import errors when running app"**  
A: Install dependencies: `pip install -r requirements.txt`

**Q: "Session expires too quickly"**  
A: Adjust `SESSION_TTL_MINUTES` in `.env` (default: 60)

**Q: "AI responses are generic"**  
A: Fill more tabs to provide context. The AI uses all available data.

**Q: "JIRA integration doesn't work"**  
A: Currently using mock mode. Configure `.env` for real integration.

### Contact

- **Technical Lead**: [Your Name]
- **Project**: DemandForge
- **Organization**: Salling Group IT

## 🎓 Tutorial

### Example: Complete Demand Flow

```python
# 1. IDEATION
Problem: "Manual promotion setup takes 4 hours per campaign"
Goals: "Automate 80% of promo setup, reduce time to 30 minutes"

# 2. REQUIREMENTS  
Stakeholders: [Marketing Manager, IT Lead, Store Ops]
User Stories: "As a Marketing Manager, I want to clone previous promos..."

# 3. ASSESSMENT
ROI: 45% (€150K investment → €217K return)
Risks: "Integration with legacy promo system may cause delays"

# 4. DESIGN
Architecture: "REST API → Azure Functions → SQL Database"
Stack: "Python 3.10, FastAPI, Azure, Postgres"

# 5. BUILD
Tasks: ["API endpoints", "DB migrations", "UI components"]
JIRA: Create Epic LOG-1234

# 6. VALIDATION
Tests: 45 test cases, 87% coverage
QA: ✅ Signed off

# 7. DEPLOYMENT
Date: 2025-11-01
Rollout: "Pilot with 10 stores, then full rollout"

# 8. IMPLEMENTATION
Metrics: Uptime 99.7%, Adoption 82%, Time saved: 3.5 hrs/campaign

# 9. CLOSING
Retrospective: "Great collaboration. Need better test data next time."
Sign-offs: ✅ All stakeholders approved
```

---

**Built with ❤️ using Streamlit, Python, and AI**

*DemandForge v1.0 - October 2025*
