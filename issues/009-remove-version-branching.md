# Issue 009: Remove PyQt version branching code

**Type:** Cleanup - P2  
**Component:** UI  
**Location:** `src/MainWindow.py:7, 918-940, 1005-1030`

## Description
```python
version = 5
...
if version == 5:
    if not name[0]:
        return
    filename = name[0]
```
PyQt5 API is consistent; this branching is unnecessary and confusing.

## Suggested Fix
Remove `version` variable and just use PyQt5 API directly.

## Acceptance Criteria
- [ ] Remove version variable and branching
- [ ] Code cleaner and simpler
