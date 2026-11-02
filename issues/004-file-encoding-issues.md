# Issue 004: File I/O missing explicit encoding

**Type:** Bug - P1  
**Component:** FileOps/MainWindow  
**Locations:** `src/FileOps.py:14, 51`

## Description
Files are opened without explicit encoding:
```python
with open(file) as dataFile:  # no encoding
...
with open(file, 'w') as dataFile:  # no encoding
```
On some systems (especially Windows) default encoding differs from UTF-8. Also no explicit handling of permission errors with user-friendly messages in all code paths.

## Impact
- File read/write may fail or corrupt data on non-UTF-8 default locales
- Less clear error messages

## Suggested Fix
```python
with open(file, encoding='utf-8') as dataFile:
    ...
with open(file, 'w', encoding='utf-8') as dataFile:
    ...
```

Also add specific exception handling for PermissionError, OSError.

## Acceptance Criteria
- [ ] All file operations use explicit UTF-8 encoding
- [ ] Better error messages for permission/file access issues
