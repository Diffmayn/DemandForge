# 📎 User Guide: File Attachments & URL References

## Quick Start (30 seconds)

1. **Open DemandForge** → http://localhost:8501
2. **Navigate to any phase tab** (e.g., Ideation, Requirements, Design...)
3. **Scroll down** to see "📎 Attachments & References" section
4. **Upload files OR add URLs** → That's it!

---

## Feature 1: File Uploads 📁

### How to Upload Files

1. **Find the attachments section** at the bottom of any phase tab
2. **Click "Browse files"** button in the left column (📁 File Uploads)
3. **Select one or more files** from your computer
   - Supported: PDF, Word, Excel, PowerPoint, TXT, CSV, Images
4. **Click "💾 Save Files to [Phase]"** button
5. **Done!** Your files are now saved

### What Happens
- Files are stored in `data/attachments/[demand_id]/`
- Each file gets a timestamp prefix to prevent conflicts
- Metadata is tracked (name, size, type, upload date)
- Files are linked to the specific demand and phase

### How to Download Files

1. **Look for your uploaded file** in the "Uploaded Files" list
2. **Click the expander** to open file details
3. **Click "⬇️ Download"** button
4. **File will download** to your browser's default location

### How to Remove Files

1. **Open the file** in the expander
2. **Click "🗑️ Remove"** button
3. **File is deleted** from both filesystem and metadata
4. **Confirm** in the audit log

### File Information Displayed
- 📄 **Filename** (original name)
- **File size** (shown in KB)
- **Upload date** (timestamp)
- **File type** (MIME type)
- **Actions** (Download, Remove)

---

## Feature 2: URL References 🔗

### How to Add URLs

1. **Find the attachments section** at the bottom of any phase tab
2. **Fill out the URL form** in the right column (🔗 URL References):
   - **Reference Title** (required): e.g., "API Documentation"
   - **URL** (required): e.g., "https://api.example.com/docs"
   - **Description** (optional): Brief note about the reference
3. **Click "➕ Add URL"** button
4. **Done!** Your URL is now saved

### What Happens
- URL metadata is stored in the demand's JSON file
- No external files created (lightweight)
- URLs are linked to the specific demand and phase
- Metadata includes title, URL, description, and timestamp

### How to Access URLs

1. **Look for your URL** in the "Saved References" list
2. **Click the expander** to open URL details
3. **Click the URL link** to open in new browser tab
4. **View description** if you added one

### How to Remove URLs

1. **Open the URL** in the expander
2. **Click "🗑️ Remove"** button
3. **URL is deleted** from metadata
4. **Confirm** in the audit log

### URL Information Displayed
- 🔗 **Title** (your custom name)
- **URL** (clickable link)
- **Description** (if provided)
- **Add date** (timestamp)
- **Actions** (Remove)

---

## Common Use Cases

### Use Case 1: Requirements Phase
**Scenario:** You have a stakeholder presentation PDF and a link to competitor analysis

**Steps:**
1. Go to **Requirements** tab
2. Scroll to **Attachments** section
3. **Upload** the presentation PDF
4. **Add URL** for competitor analysis website
5. **Result:** All requirements documentation in one place

### Use Case 2: Design Phase
**Scenario:** You have wireframe images and Figma links

**Steps:**
1. Go to **Design** tab
2. **Upload** wireframe PNG/JPG files
3. **Add URL** for Figma prototype
4. **Result:** Complete design assets organized by phase

### Use Case 3: Build Phase
**Scenario:** You have technical specs PDF and GitHub repository link

**Steps:**
1. Go to **Build** tab
2. **Upload** technical specification document
3. **Add URL** for GitHub repo
4. **Add URL** for CI/CD pipeline
5. **Result:** Development resources centralized

### Use Case 4: Validation Phase
**Scenario:** You have test results Excel and bug tracker links

**Steps:**
1. Go to **Validation** tab
2. **Upload** test results spreadsheet
3. **Add URL** for bug tracking board
4. **Result:** QA documentation all together

---

## Tips & Best Practices

### 📌 Organization Tips
- **One phase, one purpose**: Upload files relevant to that specific phase
- **Descriptive titles**: Use clear, searchable names for files and URLs
- **Add descriptions**: Brief notes help you remember why you added it
- **Clean up regularly**: Remove outdated attachments

### 🚀 Productivity Tips
- **Upload multiple files**: Select all related files at once
- **Use URL descriptions**: Add context so others understand the reference
- **Download for offline**: Keep local copies of critical documents
- **Check before closing**: Ensure all documents are uploaded before finalizing

### ⚠️ Important Notes
- **Files are stored locally**: In `data/attachments/` directory
- **Not version controlled**: Due to .gitignore settings (by design)
- **Per-demand storage**: Each demand has its own attachment folder
- **Auto-save**: Changes saved immediately after upload/add
- **Persistence**: Attachments load automatically when switching demands

---

## Troubleshooting

### Problem: Can't upload file
**Possible causes:**
- File type not supported → Check supported types list
- File too large → No explicit limit yet, but very large files may fail
- Permission issues → Check write access to `data/attachments/`

**Solution:**
- Try a different file type (e.g., PDF instead of unknown format)
- Reduce file size (compress images, split large files)
- Check folder permissions

### Problem: File won't download
**Possible causes:**
- File was moved or deleted from filesystem
- Path has changed
- Browser blocked download

**Solution:**
- Check if file exists in `data/attachments/[demand_id]/`
- Try different browser
- Check browser download settings

### Problem: URL won't open
**Possible causes:**
- URL is malformed (missing https://)
- Website is down
- Network connectivity issue

**Solution:**
- Check URL format (should start with http:// or https://)
- Test URL in separate browser tab
- Check internet connection

### Problem: Attachments disappeared
**Possible causes:**
- Switched to different demand (attachments are per-demand)
- Data file was corrupted or deleted
- Session state reset

**Solution:**
- Verify you're viewing the correct demand (check demand ID in header)
- Check `data/` directory for JSON files
- If data lost, restore from backup (not yet implemented)

---

## Future Enhancements (Coming Soon)

### Phase 3: AI Document Reading
- 🤖 **AI will read your PDFs** and extract key information
- 🤖 **AI will analyze Excel files** for data insights
- 🤖 **AI will fetch web pages** and summarize content
- 🤖 **AI will reference attachments** in responses

**Example:**
> "What are the key requirements from the uploaded specification document?"
> 
> AI: "Based on your PDF 'Requirements_Spec_v2.pdf', the key requirements are..."

### Phase 4: Timeline/Gantt Chart
- 📊 **Visual project timeline** showing all phases
- 📅 **Task scheduling** with dependencies
- 🎯 **Milestone tracking** with deadlines
- 📈 **Progress visualization** across the demand lifecycle

### Phase 5: Advanced Features
- 🔄 **Version control** for attachments (track changes over time)
- 🔍 **Full-text search** across all uploaded documents
- 📧 **Email attachments** directly to demands
- ☁️ **Cloud storage integration** (Azure Blob, OneDrive, SharePoint)
- 👥 **Attachment sharing** with stakeholder permissions

---

## Keyboard Shortcuts

Currently no keyboard shortcuts implemented, but planned:

- `Ctrl+U` → Open file upload dialog
- `Ctrl+L` → Focus URL input
- `Ctrl+S` → Save current phase (already implemented)

---

## FAQ

**Q: How many files can I upload?**  
A: No hard limit currently. Be reasonable with file sizes.

**Q: Are files shared across demands?**  
A: No, each demand has its own attachment folder. Files are isolated.

**Q: Can I upload the same file to multiple phases?**  
A: Yes! Upload to each phase where it's relevant.

**Q: What happens to attachments when I delete a demand?**  
A: Currently, files remain in `data/attachments/`. Manual cleanup needed.

**Q: Can I rename uploaded files?**  
A: Not yet. You'll need to delete and re-upload with correct name.

**Q: Are attachments backed up?**  
A: Only if you backup the `data/` directory manually. Auto-backup not yet implemented.

**Q: Can I share attachments with others?**  
A: Currently, files are local only. In production, this would integrate with cloud storage.

**Q: Does the AI read my uploaded files?**  
A: Not yet! The AI knows files exist but can't read content. Coming in Phase 3.

**Q: Can I attach videos?**  
A: Not currently supported. Supported types: PDF, Word, Excel, PowerPoint, TXT, CSV, Images.

**Q: What's the file size limit?**  
A: No explicit limit set yet. Streamlit may timeout on very large files (>200MB).

---

## Support & Feedback

### Need Help?
- Check this guide first
- Look at the troubleshooting section
- Test in different browser
- Check browser console for errors (F12)

### Report Issues
- Note the demand ID
- Describe what you were doing
- Include any error messages
- Mention browser and version

### Request Features
- Use the AI Co-Pilot to suggest improvements
- Document your use case
- Explain why the feature would help

---

**Last Updated:** October 5, 2025  
**Version:** 1.0 (Option A - Basic Implementation)  
**Status:** ✅ Production Ready

---

## Quick Reference Card

### File Upload (3 steps)
1. Browse files → Select file(s)
2. Click "Save Files to [Phase]"
3. Done! Download anytime

### URL Add (3 steps)
1. Fill form: Title + URL + Description
2. Click "Add URL"
3. Done! Click to open

### Remove Attachment (2 steps)
1. Open expander
2. Click "Remove" button

**That's it! Happy attaching! 🎉**
