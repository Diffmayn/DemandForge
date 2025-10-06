# JIRA Test Case Integration - User Guide

## 📋 Overview

DemandForge now integrates with JIRA to automatically generate and upload test cases. The AI analyzes your requirements and design documentation to create comprehensive test plans with both manual and automated test cases.

## 🚀 Getting Started

### Step 1: Get Your JIRA API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Give it a name (e.g., "DemandForge")
4. Click **"Create"**
5. **Copy the token** (you won't be able to see it again!)

### Step 2: Connect to JIRA

1. Navigate to the **Validation** tab in DemandForge
2. Scroll down to **"🔗 JIRA Connection Setup"**
3. Click **"⚙️ Configure JIRA Connection"** to expand
4. Fill in the form:
   - **JIRA Base URL**: Your JIRA instance URL
     - Cloud: `https://your-domain.atlassian.net`
     - Server: `https://jira.your-company.com`
   - **Email**: Your JIRA account email
   - **API Token**: Paste the token you copied
   - **Project Key**: The JIRA project key (e.g., PROJ, TEST, DEV)
5. Click **"💾 Save & Test Connection"**
6. You should see: ✅ **"Connected to JIRA as [Your Name]"**

## 🤖 Generating Test Cases

### Manual Test Cases

**When to use:** For user acceptance testing, exploratory testing, and tests that require human judgment.

1. **Prerequisites:**
   - Fill in the **Requirements** tab with:
     - User stories
     - Acceptance criteria
     - Business requirements
   
2. **Generate:**
   - Go to **Validation** tab → **"🤖 AI Test Case Generator"**
   - Click **"📝 Manual Test Cases"** tab
   - Review the displayed requirements
   - Set **"Number of Test Cases"** (1-20)
   - Choose **"Default Priority"** (High/Medium/Low)
   - Click **"🤖 Generate Manual Test Cases"**
   
3. **Review & Edit:**
   - AI generates test cases in ~10-30 seconds
   - Each test case shows:
     - Test summary/title
     - Test type (Manual)
     - Priority level
     - Labels for organization
     - Detailed test steps
   - Click on each test case to review
   - **Edit the description** if needed before uploading
   
4. **Upload:**
   - Click **"📤 Upload All to JIRA"**
   - Test cases are created as issues in JIRA
   - Links to created issues are displayed
   - Click links to view in JIRA

### Automated Test Cases

**When to use:** For API testing, regression testing, performance testing, and tests that need to run frequently.

1. **Prerequisites:**
   - Fill in the **Design** tab with:
     - Architecture design
     - Technical stack
     - API specifications
     - Database schema
   
2. **Generate:**
   - Go to **Validation** tab → **"🤖 AI Test Case Generator"**
   - Click **"⚙️ Automated Test Cases"** tab
   - Review the displayed design information
   - Set **"Number of Test Cases"** (1-30)
   - Choose **"Test Framework"** (pytest, selenium, playwright, etc.)
   - Click **"🤖 Generate Automated Test Cases"**
   
3. **Review & Edit:**
   - AI generates test cases with code snippets
   - Each test case includes:
     - Test summary
     - Test type (Automated)
     - Priority
     - Labels
     - Test code/pseudocode
     - Setup instructions
   - Edit descriptions if needed
   
4. **Upload:**
   - Click **"📤 Upload All to JIRA"**
   - Test cases are created in JIRA
   - Links provided for each created issue

## 📋 Creating Test Plans

**Test Plans** organize multiple test cases into a cohesive testing strategy.

1. **Generate test cases first** (manual and/or automated)
2. Review the count: "📊 Ready to create test plan with X manual and Y automated test cases"
3. Fill in the form:
   - **Test Plan Name**: Default is "Test Plan - [Demand Name]"
   - **Test Plan Description**: Overview of testing approach
   - **Generate AI Test Strategy**: ✅ Checked (recommended)
     - AI creates comprehensive test strategy
     - Includes risk analysis
     - Defines test scope and approach
     - Suggests test sequences
4. Click **"📋 Create Test Plan in JIRA"**
5. Test plan is created as an **Epic** in JIRA
6. Link is provided to view the test plan

### Linking Test Cases to Test Plans

After creating a test plan:
1. Upload test cases to JIRA first
2. Create the test plan (it becomes an Epic)
3. In JIRA, link test case issues to the Epic manually
   - Or use the JIRA API to link them programmatically (future feature)

## 💡 Tips & Best Practices

### For Better Test Generation

1. **Detailed Requirements = Better Tests**
   - The more detailed your requirements, the better the test cases
   - Include acceptance criteria for each user story
   - Attach specification documents

2. **Use Attachments**
   - Upload PDFs, Word docs with detailed specs
   - Add links to API documentation
   - Include design diagrams

3. **Iterative Approach**
   - Generate a few test cases first (5-10)
   - Review quality and adjust
   - Generate more if needed

4. **Edit Before Upload**
   - Always review AI-generated test cases
   - Add specific data points
   - Clarify ambiguous steps
   - Adjust priority levels

### Test Organization

1. **Use Labels Effectively**
   - AI adds labels automatically: `ai-generated`, `manual`, `automated`
   - Add your own labels in JIRA after upload
   - Use labels for: test types, sprints, releases, components

2. **Set Priorities Wisely**
   - **High**: Critical path, security, data integrity
   - **Medium**: Important features, common workflows
   - **Low**: Edge cases, nice-to-have features

3. **Test Case Naming**
   - AI generates descriptive names
   - Keep them consistent
   - Include feature/component name

## 🔧 Troubleshooting

### Connection Issues

**Problem:** "❌ Connection failed: Unauthorized"
- **Solution:** 
  - Verify email matches your JIRA account
  - Regenerate API token and try again
  - Check JIRA URL format (no trailing slash)

**Problem:** "❌ Connection failed: Not Found"
- **Solution:**
  - Verify JIRA Base URL is correct
  - For cloud: must be `https://your-domain.atlassian.net`
  - For server: check with your JIRA admin

**Problem:** "Project key not found"
- **Solution:**
  - Verify project key is uppercase (e.g., "PROJ", not "proj")
  - Ensure you have access to the project
  - Check project exists in JIRA

### Generation Issues

**Problem:** Test cases are too generic
- **Solution:**
  - Add more detail to requirements/design
  - Upload specification documents as attachments
  - Include specific business rules

**Problem:** Not enough test cases generated
- **Solution:**
  - Increase the "Number of Test Cases" setting
  - Break down requirements into smaller user stories
  - Generate multiple batches

**Problem:** Test cases missing critical scenarios
- **Solution:**
  - Review and edit generated test cases
  - Add custom test cases manually in JIRA
  - Regenerate with more context

### Upload Issues

**Problem:** "Failed to upload test cases"
- **Solution:**
  - Check JIRA connection is still active
  - Verify project permissions (can you create issues?)
  - Check issue type "Test" exists in project
  - Try uploading one test case at a time

**Problem:** Test cases created but missing information
- **Solution:**
  - Check required fields in your JIRA project
  - Update jira_test_client.py to include required fields
  - Add missing data in JIRA after upload

## 🔐 Security Notes

1. **API Token Storage:**
   - Tokens are stored in session state (memory only)
   - Not saved to disk or committed to Git
   - Must re-enter token after browser refresh
   
2. **Best Practices:**
   - Don't share your API token
   - Regenerate tokens periodically
   - Use tokens with minimal required permissions
   - Revoke tokens when not needed

3. **Future Enhancement:**
   - Store tokens in `.env` file locally
   - Never commit `.env` to Git
   - Use environment variables in production

## 📚 JIRA Configuration

### Issue Types

DemandForge creates test cases as **"Test"** issue type. If this doesn't exist:

1. **Option A: Create "Test" Issue Type**
   - Go to JIRA Settings → Issues → Issue Types
   - Create new issue type called "Test"
   - Add to your project

2. **Option B: Use Existing Issue Type**
   - Modify `jira_test_client.py`
   - Change `issue_type = "Test"` to your preferred type (e.g., "Task", "Story")
   - Line ~150 in `create_test_case()` method

### Custom Fields

If your JIRA project requires custom fields:

1. Identify required fields in JIRA
2. Update `create_test_case()` method
3. Add custom field values to the `fields` dictionary

Example:
```python
"fields": {
    "project": {"key": project_key},
    "summary": summary,
    "description": description,
    "issuetype": {"name": "Test"},
    "priority": {"name": priority},
    "labels": labels,
    # Add custom field
    "customfield_10001": "Custom Value"
}
```

## 🔮 Future Enhancements

Planned features for JIRA integration:

1. **Automatic Test-Epic Linking**
   - Auto-link test cases to test plan Epic
   - Bulk linking operation

2. **Test Execution Tracking**
   - Update test results from DemandForge
   - Mark tests as Pass/Fail
   - Track test runs

3. **Defect Linking**
   - Link bugs to failing test cases
   - Auto-create defects from test failures

4. **Test Coverage Dashboard**
   - Visualize test coverage
   - Track pass/fail rates
   - Identify untested areas

5. **Bi-directional Sync**
   - Import test cases from JIRA
   - Update existing test cases
   - Sync test results

## 📞 Support

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review JIRA API logs (contact JIRA admin)
3. Check DemandForge logs in terminal
4. Verify JIRA permissions with your admin
5. Test JIRA connection with Postman/curl first

## 📖 Example Workflow

**Complete test case generation workflow:**

### Day 1: Requirements Phase
1. Create new demand in DemandForge
2. Fill in **Ideation** tab
3. Complete **Requirements** tab:
   - User stories
   - Acceptance criteria
   - Business rules
4. Upload requirements document (PDF/Word)
5. Save and move to Design

### Day 2: Design Phase
1. Complete **Design** tab:
   - Architecture design
   - Technical stack
   - API specifications
2. Upload design diagrams
3. Save and move to Validation

### Day 3: Test Generation
1. Connect to JIRA (one-time setup)
2. Generate **10 manual test cases**:
   - Review and edit
   - Upload to JIRA
   - Verify in JIRA
3. Generate **15 automated test cases**:
   - Review code snippets
   - Adjust priorities
   - Upload to JIRA
4. Create **Test Plan**:
   - Include all 25 test cases
   - AI generates test strategy
   - Upload to JIRA as Epic

### Day 4: Test Execution
1. QA team executes tests from JIRA
2. Log bugs in DemandForge Bug Log
3. Update test results
4. Track progress in Validation tab

---

**Version:** 1.0  
**Last Updated:** January 2025  
**Requires:** DemandForge v2.0+, JIRA Cloud/Server

