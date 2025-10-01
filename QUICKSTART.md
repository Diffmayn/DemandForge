# 🚀 Quick Start Guide

## Immediate Steps to Run DemandForge

### Option 1: PowerShell Script (Recommended)
```powershell
.\setup_and_run.ps1
```

### Option 2: Direct Run
```powershell
streamlit run app.py
```

### Option 3: Step-by-Step
```powershell
# 1. Verify installation
pip list | Select-String -Pattern "streamlit|pydantic|pytest"

# 2. Run tests (optional)
pytest tests/ -v

# 3. Launch app
streamlit run app.py
```

## What to Expect

1. **Browser Opens**: Streamlit will automatically open `http://localhost:8501`
2. **Demand ID Generated**: You'll see a unique ID like `LOG-2025-A1B2C3D4`
3. **9 Tabs Available**: Navigate through Ideation → Closing
4. **AI Co-Pilot**: Sidebar chat for assistance
5. **Progress Tracking**: Automatic updates as you fill tabs

## First-Time Flow

### 5-Minute Demo Flow:

1. **Ideation Tab**:
   - Problem: "Manual reporting takes 10 hours/week"
   - Goals: "Automate 80% of reports"
   - Click "Save Ideation"

2. **AI Co-Pilot** (Sidebar):
   - Type: "Generate user stories"
   - Click the quick action button
   - Stories auto-populate in Requirements

3. **Requirements Tab**:
   - Add stakeholder: John Doe, Business Analyst
   - View auto-generated stories
   - Click "Save Requirements"

4. **Assessment Tab**:
   - ROI: 50%
   - Cost: €50,000
   - Duration: 12 weeks
   - Click AI "Predict Risks"
   - Save

5. **Build Tab**:
   - Add tasks: "API development", "Database design"
   - Click "Create JIRA Epic"
   - See mock JIRA response

6. **Export**:
   - Scroll to bottom
   - Click "Export as JSON"
   - Download complete demand data

## Troubleshooting

### Port Already in Use
```powershell
streamlit run app.py --server.port 8502
```

### Import Errors
```powershell
pip install --upgrade -r requirements.txt
```

### Session State Reset
- Refresh browser (F5)
- Or click "Start New Session" if TTL expired

## Testing

### Run All Tests
```powershell
pytest tests/ -v
```

### Run Specific Test
```powershell
pytest tests/test_agent.py -v
```

### With Coverage
```powershell
pytest --cov=. --cov-report=html tests/
# Open htmlcov/index.html in browser
```

## Environment Configuration

### For Real JIRA Integration:
1. Copy `.env.example` to `.env`
2. Add your credentials:
```env
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your_token_here
```

3. Update `app.py` line 87 to use `RealJiraClient`

## Tips

- **Save Often**: Click save buttons in each tab
- **Use AI**: The co-pilot improves with more context
- **Export Regularly**: Download JSON backups
- **Check Progress**: Watch the progress bar at top
- **Audit Trail**: Click "View Audit Log" to see all changes

## Next Steps

1. ✅ **Explore All Tabs**: Click through all 9 phases
2. ✅ **Test AI Features**: Try different queries
3. ✅ **Export Data**: Download JSON and Markdown
4. ✅ **Run Tests**: Verify everything works
5. ✅ **Customize**: Modify for your needs

## Support

- **README.md**: Full documentation
- **Tests**: See `tests/` for usage examples
- **Code Comments**: Inline documentation throughout

---

**Ready to Build?** Run `streamlit run app.py` now! 🚀
