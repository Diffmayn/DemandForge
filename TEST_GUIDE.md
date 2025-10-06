# Quick Test Guide - Option 4 Features

## 🚀 App is Running!
**URL:** http://localhost:8501

---

## Test 1: AI Document Reading (5 minutes)

### Test PDF Reading:
1. **Load an existing demand** (e.g., 10001 - Commercial Planning Tool)
2. **Go to "💡 Ideation" tab**
3. **Scroll down** to "📎 Attachments & References"
4. **Upload a test PDF** (any PDF file you have)
5. **Click "📄 Ask AI about attachments"**
6. **Verify:** AI should summarize the PDF content
7. **Alternative:** Ask in sidebar: "What's in the PDF?"

### Test Excel Reading:
1. **Stay on same demand**
2. **Upload an Excel file** (.xlsx)
3. **Click "📄 Ask AI about attachments"** again
4. **Verify:** AI should mention both PDF and Excel
5. **Ask specific**: "What data is in the Excel file?"

### Test URL Fetching:
1. **Add a URL** reference (e.g., https://www.example.com)
2. **Click "📄 Ask AI about attachments"**
3. **Verify:** AI should fetch and summarize the web page
4. **Try:** Add https://en.wikipedia.org/wiki/Agile_software_development
5. **Ask:** "Summarize the Agile methodology from the URL"

---

## Test 2: Gantt Chart Timeline (3 minutes)

### View Default Timeline:
1. **Click "📅 Timeline" tab** (last tab in navigation)
2. **Verify:** See Gantt chart with all 9 phases
3. **Check:** Start dates and durations look correct
4. **Look for:** Color-coded phases
5. **Bottom:** Should show total project duration

### Customize Timeline:
1. **Check** "Customize phase dates" checkbox
2. **Change some durations** (e.g., Build: 60 → 90 days)
3. **Verify:** Gantt chart updates automatically
4. **Check:** Total duration increases

### Test Milestones:
1. **Click "🎯 Milestones" sub-tab**
2. **Add a milestone:**
   - Date: Pick any future date
   - Description: "Requirements Sign-off"
3. **Click "➕ Add Milestone"**
4. **Verify:** Milestone appears on timeline with diamond marker
5. **Try:** Add 2-3 more milestones
6. **Check:** They're sorted by date

### Test Progress View:
1. **Click "📈 Progress" sub-tab**
2. **Verify:** See horizontal bars for all phases
3. **Check:** Overall progress percentage shown
4. **Note:** Progress calculated from phase data

---

## Test 3: AI Context Integration (2 minutes)

### Test Automatic Context:
1. **Go back to "💡 Ideation" tab** (with attachments)
2. **Open sidebar AI Co-Pilot**
3. **Ask:** "What documents do we have in this phase?"
4. **Verify:** AI lists the attachments
5. **Ask:** "Summarize all the attachments"
6. **Verify:** AI automatically reads and summarizes ALL documents

### Test Phase-Specific Context:
1. **Switch to "📋 Requirements" tab**
2. **Upload different files** here
3. **Ask AI:** "What's in my attachments?"
4. **Verify:** AI only mentions Requirements phase attachments
5. **Confirms:** Context is phase-specific

---

## Test 4: Full Workflow (10 minutes)

### Complete Demand with AI:
1. **Load demand 10001** or create new one
2. **Ideation Phase:**
   - Upload: Problem statement PDF
   - Add URL: Relevant article
   - Ask AI: "Help me refine the problem statement"
3. **Requirements Phase:**
   - Upload: Stakeholder presentation
   - Ask AI: "Extract key requirements"
4. **Assessment Phase:**
   - Upload: Budget Excel file
   - Ask AI: "Analyze the budget"
5. **Design Phase:**
   - Upload: Technical design doc
   - Ask AI: "Review the architecture"
6. **Timeline Tab:**
   - Customize durations based on AI recommendations
   - Add milestones for key deliverables

---

## Expected Results

### ✅ Success Indicators:

#### Document Reading:
- [  ] PDF text extracted and readable by AI
- [  ] Excel data shown in AI responses
- [  ] Word documents parsed correctly
- [  ] URLs fetched and summarized
- [  ] "Ask AI about attachments" button works
- [  ] Sidebar chat includes document content
- [  ] Multiple documents handled together

#### Gantt Chart:
- [  ] Timeline tab visible and functional
- [  ] Default Gantt chart displays
- [  ] Custom durations update chart
- [  ] Milestones show on timeline
- [  ] Progress bars display correctly
- [  ] All visualizations interactive

#### Integration:
- [  ] No errors in terminal
- [  ] No errors in browser console (F12)
- [  ] App responsive and fast
- [  ] All tabs navigate smoothly
- [  ] Data saves automatically

---

## Common Issues & Solutions

### Issue: AI says "Could not read document"
**Solutions:**
- Check file is supported type (PDF, DOCX, XLSX)
- Verify file isn't password-protected
- Try a different file
- Check file isn't corrupted

### Issue: Gantt chart not displaying
**Solutions:**
- Check Plotly installed: `python -m pip show plotly`
- Refresh browser page
- Check browser console for JavaScript errors
- Try different browser (Chrome recommended)

### Issue: "File path does not exist" error
**Solutions:**
- File may have been moved/deleted
- Check `data/attachments/{demand_id}/` exists
- Try re-uploading the file

### Issue: URL fetch timeout
**Solutions:**
- URL might be slow or down
- Try different URL
- Check internet connection
- Some sites block scraping (use alternative)

---

## Performance Notes

### Document Reading:
- **PDF**: ~1-3 seconds for 10-page PDF
- **Excel**: ~1-2 seconds for typical spreadsheet
- **Word**: ~1 second for normal document
- **URL**: ~2-5 seconds depending on page size

### Gantt Chart:
- **Rendering**: Instant for default timeline
- **Customization**: Real-time updates
- **Milestones**: Instant addition/removal

### AI Responses:
- **With attachments**: 5-10 seconds (reads docs first)
- **Without attachments**: 2-3 seconds (normal speed)
- **Multiple documents**: 10-15 seconds (reads all)

---

## Advanced Testing

### Test Error Handling:
1. Upload very large file (>100MB) - should handle gracefully
2. Add invalid URL - should show error message
3. Upload unsupported file type - should notify user
4. Disconnect internet, try URL - should timeout gracefully

### Test Edge Cases:
1. Upload 10 documents to one phase
2. Add 20 milestones to timeline
3. Customize all phase durations to 1 day
4. Ask AI very complex multi-document question

### Test Persistence:
1. Upload files and add URLs
2. Switch to different demand
3. Switch back to original
4. Verify: All attachments still there
5. Verify: Milestones saved

---

## What to Report

### If Everything Works ✅:
"All features tested successfully! Ready for production use."

### If Issues Found ❌:
Please note:
1. **What you were doing** (specific steps)
2. **What happened** (error message or unexpected behavior)
3. **What you expected** (correct behavior)
4. **Which demand** (ID number)
5. **File details** (if relevant: type, size, name)
6. **Screenshot** (if visual issue)

---

## Next Actions

### After Successful Testing:
1. ✅ **Celebrate!** 🎉 Option 4 is complete!
2. ✅ **Train your team** on new features
3. ✅ **Upload real documents** to existing demands
4. ✅ **Set up project timelines** for active demands
5. ✅ **Deploy to Streamlit Cloud** (if needed)
6. ✅ **Gather user feedback**

### For Production:
1. Set up proper cloud storage (Azure Blob)
2. Configure authentication
3. Set up backup strategy
4. Add monitoring/logging
5. Scale resources as needed

---

## Support Reminders

### If You Get Stuck:
- Check this test guide
- Review OPTION4_COMPLETE.md for detailed docs
- Check browser console (F12) for JavaScript errors
- Check terminal output for Python errors
- Try refreshing the page

### Tips:
- **Start simple** - Test with small files first
- **One feature at a time** - Don't test everything simultaneously
- **Save often** - Data auto-saves but good habit
- **Use AI Co-Pilot** - Ask it for help using features!

---

**Testing Time Estimate**: 20 minutes for complete test suite  
**Critical Tests**: Document Reading (5 min) + Gantt Chart (3 min)  
**Status**: Ready to test! 🚀

---

**Last Updated:** October 5, 2025  
**App Version:** v2.0 (Option 4 Complete)  
**URL:** http://localhost:8501
