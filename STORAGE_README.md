# DemandForge Storage System

## Overview
DemandForge now includes persistent storage that automatically saves all demands and makes them available to the AI Co-Pilot.

## Features

### 🗄️ Persistent Storage
- **Auto-save**: Every change is automatically saved to `data/` directory
- **JSON-based**: Simple, portable JSON file storage
- **Index System**: Fast lookups with `demands_index.json`

### 🤖 AI System-Wide Knowledge

The AI Co-Pilot now has complete access to:
- ✅ **All Demands**: Every demand created in the system
- ✅ **Complete History**: User stories, test cases, features from all demands
- ✅ **System Statistics**: Total counts, status breakdowns, progress metrics
- ✅ **Cross-Demand Analysis**: Compare and learn from similar demands

### 📊 What the AI Can Do

Ask the AI questions like:
- "How many total demands are in the system?"
- "Show me all demands with status 'In Progress'"
- "What are the common risks across all demands?"
- "Find demands similar to the current one"
- "What's the average completion rate?"
- "Show me user stories from demand LOG-2025-XXXXX"

### 🔍 Storage Structure

```
data/
├── demands_index.json          # Fast lookup index
├── LOG-2025-XXXXX.json        # Individual demand files
├── LOG-2025-YYYYY.json
└── ...
```

### 💾 Data Saved

Each demand includes:
- All 9 phase data (Ideation → Closing)
- Complete audit log
- Chat history with AI
- Timestamps and progress
- Stakeholders and user stories
- Test cases and validation
- Deployment and implementation details

### 🔐 Privacy & Security

- Data stored locally in `data/` directory
- Not committed to Git (excluded in `.gitignore`)
- JSON format for easy backup/export
- Can be deleted/migrated as needed

## Usage

### For Users
- Just use the app normally - everything auto-saves!
- Ask AI about system-wide stats and other demands
- Create multiple demands - they're all tracked

### For Developers

```python
from utils.storage import get_storage

# Get storage instance
storage = get_storage()

# Get all demands
all_demands = storage.get_all_demands_summary()

# Load specific demand
demand = storage.load_demand("LOG-2025-XXXXX")

# Search demands
results = storage.search_demands("customer portal")

# Get statistics
stats = storage.get_statistics()
# Returns: {total_demands, by_status, average_progress, most_recent}
```

## AI Context Enhancement

The AI now receives:
1. **System Statistics** - Total demands, status breakdown
2. **Recent Demands** - Last 5 demands for context
3. **Current Demand** - Full details of active demand
4. **Historical Context** - All past demands for RAG

This enables the AI to:
- Answer questions about the entire system
- Find patterns across multiple demands
- Provide insights based on historical data
- Compare current work to past projects

## Example AI Queries

```
User: "How many demands do we have in total?"
AI: "Based on the system statistics, we have X total demands..."

User: "What are common risks in our projects?"
AI: "Analyzing all demands, the most common risks are..."

User: "Show me similar demands to this one"
AI: "I found 3 similar demands: LOG-2025-ABC, LOG-2025-DEF..."
```

## Backup & Migration

To backup your data:
```bash
# Copy the entire data directory
cp -r data/ backup/data_$(date +%Y%m%d)/
```

To migrate to a new instance:
```bash
# Copy data directory to new installation
cp -r data/ /path/to/new/demandforge/data/
```

## Storage Limits

- **No hard limits** - grows with usage
- **Recommended**: Monitor `data/` directory size
- **Performance**: System handles 1000s of demands efficiently
- **Cleanup**: Implement archival for very old demands if needed

## Future Enhancements

Planned features:
- 🔄 Export to database (PostgreSQL, MongoDB)
- 📤 Bulk export/import tools
- 🔍 Advanced search with filters
- 📈 Analytics dashboard
- 🗂️ Demand categories/tags
- 👥 Multi-user support with permissions
