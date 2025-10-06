# Demand Name and Number Feature Implementation

## Overview
Added the ability to assign a **friendly demand name** and **sequential demand number** to each demand, making it easier to reference and track demands throughout the organization.

## Features Implemented

### 1. **Demand Identification Fields**
Two new fields added to the demand data structure:
- **Demand Number**: Sequential identifier (e.g., 10001, 10002, 10003)
- **Demand Name**: Descriptive, user-friendly name (e.g., "Commercial Planning Tool Enhancement")

### 2. **Editable in Ideation Tab**
Both fields are prominently displayed and editable at the top of the Ideation tab:
- **Location**: First section of the Ideation form
- **Input Type**: Text input fields with placeholders
- **Max Length**: 
  - Demand Number: 20 characters
  - Demand Name: 200 characters
- **Validation**: Both optional, but recommended for better organization

### 3. **Displayed in Header**
The demand name and number are now the primary identifier shown in the app header:
- **Format**: `{Demand Number} - {Demand Name}`
- **Fallback**: If not set, displays the technical Demand ID (LOG-2025-XXXXX)
- **Caption**: Technical ID shown as secondary information

### 4. **Enhanced Demands Overview**
The "📂 All Demands" tab now displays demands using their name and number:
- **Primary Display**: Shows demand number and name
- **Metadata**: Technical ID, title (from ideation), and description shown as captions
- **Search**: Can search by demand number, name, title, ID, or description

### 5. **Persistent Storage**
Demand name and number are:
- Saved automatically with every demand update
- Loaded when switching between demands
- Preserved across sessions
- Included in all export and audit operations

## Updated Mock Demands

All 5 mock demands have been updated with names and numbers:

| Number | Name | ID | Status |
|--------|------|-----|--------|
| **10001** | Commercial Planning Tool Enhancement | LOG-2025-CPT001 | ✅ Completed |
| **10002** | PMR Promotion Integration | LOG-2025-PMR002 | ✅ Completed |
| **10003** | Vendor Bonus Automation | LOG-2025-VBP003 | ✅ Completed |
| **10004** | Leaflet Agency Integration | LOG-2025-LFT004 | 🟡 In Progress (75%) |
| **10005** | Event Preview with ML Forecasting | LOG-2025-CPT005 | 🟡 In Progress (45%) |

## Technical Implementation

### Session State Changes
Added to `initialize_session_state()`:
```python
st.session_state.demand_name = ""
st.session_state.demand_number = ""
```

### Header Display Logic
```python
demand_display = f"{st.session_state.demand_number} - {st.session_state.demand_name}" \
                 if st.session_state.demand_number and st.session_state.demand_name \
                 else st.session_state.demand_id
```

### Ideation Form Fields
```python
with col1:
    demand_number = st.text_input(
        "Demand Number",
        value=st.session_state.demand_number,
        placeholder="e.g., 10001",
        max_chars=20,
        help="Sequential demand number for tracking"
    )

with col2:
    demand_name = st.text_input(
        "Demand Name",
        value=st.session_state.demand_name,
        placeholder="e.g., Promotion Process Enhancement",
        max_chars=200,
        help="Descriptive name for this demand"
    )
```

### Save/Load Operations
All save and load functions updated to include:
```python
'demand_name': st.session_state.get('demand_name', ''),
'demand_number': st.session_state.get('demand_number', ''),
```

### Demands Overview Display
Smart display logic:
```python
if demand_name and demand_number:
    display_name = f"{demand_number} - {demand_name}"
elif demand_name:
    display_name = demand_name
elif title and title != 'Untitled':
    display_name = title
else:
    display_name = demand_id
```

## User Workflow

### Creating a New Demand
1. Click "➕ Create New Demand" in the All Demands tab
2. Go to "💡 Ideation" tab
3. Fill in **Demand Number** (e.g., 10006)
4. Fill in **Demand Name** (e.g., "Customer Feedback Integration")
5. Complete the rest of the ideation form
6. Click "💾 Save Ideation"
7. The header and demand list now show your custom name/number

### Editing Existing Demand Names
1. Load the demand from "📂 All Demands" tab
2. Go to "💡 Ideation" tab
3. Update the **Demand Number** or **Demand Name** fields
4. Click "💾 Save Ideation"
5. Changes are immediately reflected throughout the app

### Viewing Demands by Name
1. Go to "📂 All Demands" tab
2. See all demands listed with their number and name
3. Use search box to find demands by:
   - Demand number (e.g., "10001")
   - Demand name (e.g., "Planning Tool")
   - Technical ID (e.g., "CPT001")
   - Title or description

## Benefits

### 1. **Human-Readable References**
- "Demand 10001" is easier to remember than "LOG-2025-CPT001"
- "Commercial Planning Tool Enhancement" is more descriptive

### 2. **Better Communication**
- Stakeholders can reference demands by familiar names
- Meeting discussions are clearer
- Email threads are more understandable

### 3. **Sequential Tracking**
- Demand numbers follow a logical sequence
- Easy to see demand order and volume
- Simple counting and reporting

### 4. **Backwards Compatible**
- Existing demands without names/numbers still work
- Technical IDs remain the primary key
- Gradual adoption possible

### 5. **Flexible Naming**
- Organizations can establish their own numbering schemes
- Names can be descriptive or follow templates
- Both fields optional but recommended

## Files Modified

### 1. `app.py` (Main Application)
- **Session initialization**: Added demand_name and demand_number
- **Header rendering**: Display name/number prominently
- **Ideation tab**: Added input fields for both
- **Save functions**: Include name/number in all save operations
- **Load functions**: Load name/number when switching demands
- **Demands overview**: Display name/number in demand list

### 2. Mock Demand JSON Files
- `LOG-2025-CPT001.json` - Added: name="Commercial Planning Tool Enhancement", number="10001"
- `LOG-2025-PMR002.json` - Added: name="PMR Promotion Integration", number="10002"
- `LOG-2025-VBP003.json` - Added: name="Vendor Bonus Automation", number="10003"
- `LOG-2025-LFT004.json` - Added: name="Leaflet Agency Integration", number="10004"
- `LOG-2025-CPT005.json` - Added: name="Event Preview with ML Forecasting", number="10005"

### 3. `demands_index.json`
Updated all 5 mock demands with demand_name and demand_number fields

## Best Practices

### Demand Numbering
- **Sequential**: Start from 10001 and increment
- **Prefix by Year**: Use 2025-001, 2025-002, etc.
- **Category Prefix**: CPT-001, PMR-001, VBP-001, etc.
- **Department Code**: IT-001, FIN-001, etc.

### Demand Naming
- **Descriptive**: Clearly state what the demand is about
- **Concise**: Keep under 50 characters if possible
- **Consistent**: Follow organizational conventions
- **No Jargon**: Use terms everyone understands

### Examples
| Number | Good Name | Bad Name |
|--------|-----------|----------|
| 10001 | Customer Portal Redesign | New Portal |
| 10002 | Inventory API Integration | API Stuff |
| 10003 | Sales Dashboard Enhancement | Dashboard v2 |
| 10004 | Mobile App Push Notifications | Push Feature |

## Testing Checklist

✅ **Create New Demand**
- [ ] Demand starts with empty name/number
- [ ] Can set both fields in Ideation
- [ ] Fields save correctly
- [ ] Header displays correctly

✅ **Edit Existing Demand**
- [ ] Load demand shows current name/number
- [ ] Can edit both fields
- [ ] Changes persist after save
- [ ] Header updates immediately

✅ **Demands Overview**
- [ ] All demands show name/number
- [ ] Search finds by name/number
- [ ] Can load demand by clicking
- [ ] Display falls back to ID if name not set

✅ **Data Persistence**
- [ ] Name/number saved to JSON
- [ ] Name/number loaded correctly
- [ ] Works after app restart
- [ ] Included in demand exports

## Future Enhancements (Optional)

1. **Auto-Numbering**: Generate next available demand number automatically
2. **Number Validation**: Enforce unique demand numbers
3. **Name Templates**: Provide naming conventions/templates
4. **Bulk Rename**: Change multiple demand names at once
5. **Number History**: Track number changes over time
6. **Search by Number**: Dedicated search filter
7. **Number Ranges**: Assign ranges to departments/teams
8. **Import/Export**: Support name/number in bulk operations

## Migration Guide

### For New Demands
- Simply fill in the demand number and name when creating
- Both fields are in the Ideation tab at the top

### For Existing Demands
1. Go to "📂 All Demands"
2. Load each demand one by one
3. Go to "💡 Ideation" tab
4. Add demand number and name
5. Click "💾 Save Ideation"
6. Repeat for all demands

### Recommended Numbering Scheme
- Start from 10001 for first demand
- Increment by 1 for each new demand
- Reserve number ranges if needed:
  - 10000-19999: IT demands
  - 20000-29999: Finance demands
  - 30000-39999: Operations demands

---

**Version**: 1.3  
**Date**: 2025-10-05  
**Status**: ✅ Production Ready  
**App URL**: http://localhost:8501  

## Summary

The demand name and number feature makes DemandForge more user-friendly and professional by:
- ✅ Providing human-readable identifiers
- ✅ Enabling better communication and tracking
- ✅ Supporting organizational numbering schemes
- ✅ Maintaining backwards compatibility
- ✅ Being fully editable and searchable

Users can now reference "Demand 10001 - Commercial Planning Tool Enhancement" instead of "LOG-2025-CPT001", making the system more intuitive for all stakeholders! 🎉
