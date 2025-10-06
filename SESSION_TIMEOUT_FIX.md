# Session Timeout Fix for Loading Old Demands

## Problem
When loading old demands (created weeks or months ago), users were seeing:
```
Session expired after 60 minutes. Please refresh to start a new session.
```

This prevented users from viewing or editing historical demands.

## Root Cause
The session timeout validation was checking against the **demand's creation time** (`start_time`) instead of the **actual user session start time**.

### Before (Broken)
```python
# render_header() was using demand creation time
is_valid, warning = validate_session_ttl(st.session_state.start_time)
```

When you loaded a demand created 3 months ago, the system thought your session started 3 months ago and immediately expired it.

## Solution
Added a separate `session_start_time` field to track when the user's current session actually started, independent of when any specific demand was created.

### After (Fixed)
```python
# Track actual session start time (not demand start time)
st.session_state.session_start_time = datetime.now()

# Use session start time for TTL validation
session_start = st.session_state.get('session_start_time', datetime.now())
is_valid, warning = validate_session_ttl(session_start)
```

## Changes Made

### 1. Session State Initialization
**File**: `app.py` - `initialize_session_state()`

```python
def initialize_session_state():
    """Initialize session state with default values."""
    if "initialized" not in st.session_state:
        # Track actual session start time (not demand start time)
        st.session_state.session_start_time = datetime.now()
        
        # Generate unique demand ID
        st.session_state.demand_id = f"LOG-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
        st.session_state.demand_name = ""
        st.session_state.demand_number = ""
        st.session_state.start_time = datetime.now()  # Demand creation time
        # ... rest of initialization
```

### 2. Header Validation
**File**: `app.py` - `render_header()`

```python
def render_header():
    """Render the application header with progress."""
    # Check session TTL using actual session start time (not demand start time)
    session_start = st.session_state.get('session_start_time', datetime.now())
    is_valid, warning = validate_session_ttl(session_start)
    
    if not is_valid:
        st.error(warning)
        # ... handle session expiration
```

## Key Concepts

### Two Different Times
1. **`start_time`** - When the **demand** was created
   - Stored with demand data
   - Could be weeks or months ago
   - Used for demand metadata and audit trail

2. **`session_start_time`** - When the **user session** began
   - Always set to current time when app loads
   - Resets with each new browser session
   - Used for session timeout validation

### Fallback Logic
```python
session_start = st.session_state.get('session_start_time', datetime.now())
```
If `session_start_time` doesn't exist (shouldn't happen), defaults to current time, preventing false expiration errors.

## Testing

### Before Fix ❌
1. Create a demand today
2. Close browser
3. Open tomorrow (25 hours later)
4. Load the old demand
5. **Result**: "Session expired after 60 minutes" error
6. **Problem**: Cannot access old demands

### After Fix ✅
1. Create a demand today
2. Close browser
3. Open tomorrow (25 hours later)
4. Load the old demand
5. **Result**: Demand loads successfully
6. **Session timer**: Starts from when you opened the browser (now)
7. **Can work for**: Full 60 minutes from current time

## Session Flow

### Loading an Old Demand
```
1. User opens app → session_start_time = 2025-10-05 20:12:00
2. Initialize session → Session valid until 21:12:00 (60 min)
3. User loads demand from 2024-11-15
4. Demand data: start_time = 2024-11-15 09:00:00
5. Header checks: session_start_time (20:12) vs now (20:12)
6. Validation: ✅ Session is fresh, 60 minutes remaining
7. User can edit and work normally
```

### Creating a New Demand
```
1. User opens app → session_start_time = 2025-10-05 20:12:00
2. Creates new demand → start_time = 2025-10-05 20:15:00
3. Both times are similar (within same session)
4. Session valid until 21:12:00
5. Everything works as expected
```

## Benefits

✅ **Can Load Old Demands**: Historical demands are accessible  
✅ **No False Expiration**: Session timer based on actual session  
✅ **60-Minute Window**: Users have full time to work  
✅ **Backwards Compatible**: Works with existing demands  
✅ **Clear Separation**: Demand time ≠ Session time  

## User Experience

### Before
- ❌ Could only work with recently created demands
- ❌ Old demands immediately expired
- ❌ Confusing error messages
- ❌ Data seemed "locked"

### After
- ✅ Can load any demand regardless of age
- ✅ Session timer starts fresh each visit
- ✅ Clear 60-minute working window
- ✅ Full access to historical data

## Technical Details

### Session Lifetime
- **Default**: 60 minutes (configurable via `SESSION_TTL_MINUTES` env variable)
- **Warning**: At 80% (48 minutes) - "Session expires in 12 minutes"
- **Expiration**: At 100% (60 minutes) - "Session expired, refresh to start new"

### What Triggers Session Reset
- Opening the app in a new browser session
- Clicking "🔄 Start New Session" after expiration
- Manually refreshing the page

### What Doesn't Trigger Reset
- Loading different demands
- Switching between tabs
- Auto-saving demands
- Creating new demands

## Files Modified

- ✅ `app.py` - `initialize_session_state()` function
- ✅ `app.py` - `render_header()` function

## Verification

To verify the fix is working:

1. **Load an old demand**:
   - Go to "📂 All Demands"
   - Click "📂 Load" on demand 10001 (created in November 2024)
   - ✅ Should load without "Session expired" error

2. **Check session timer**:
   - After loading old demand
   - Look for warning after ~48 minutes of activity
   - Should show remaining time, not instant expiration

3. **Work normally**:
   - Edit demand fields
   - Switch between tabs
   - Save changes
   - ✅ Everything should work for full 60 minutes

## Troubleshooting

### If you still see session expiration:
1. **Clear browser cache** - Old session might be cached
2. **Hard refresh** - Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
3. **Check time**: Ensure you haven't actually been working for 60+ minutes
4. **Verify fix**: Check that `session_start_time` exists in session state

### To disable session timeout entirely:
Add to `.env` file:
```
SESSION_TTL_MINUTES=999999
```

---

**Status**: ✅ Fixed and Tested  
**Version**: 1.4  
**Date**: 2025-10-05  
**Impact**: Can now load and work with demands of any age!  

## Summary

The session timeout issue is **completely fixed**. You can now:
- ✅ Load demands from November 2024
- ✅ Load demands from any date
- ✅ Work with historical data
- ✅ Edit old demands
- ✅ Full 60-minute session from your actual login time

The app is running at **http://localhost:8501** - try loading demand 10001 now! 🎉
