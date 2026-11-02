# Issue 001: Application close event incorrectly ignores close and calls quit

**Type:** Bug - P0 Critical  
**Component:** UI/MainWindow  
**Location:** `src/MainWindow.py:1949-1952`

## Description
```python
def closeEvent(self, event):
    qApp.quit()
    event.ignore()
```
The close event handler calls `qApp.quit()` (which terminates the application) but immediately calls `event.ignore()`, which tells Qt to ignore the close event. Also `qApp` is not imported/defined in this scope. This creates conflicting/undefined behavior - the window may not close properly, resources may not clean up, and app termination behavior is unpredictable.

## Impact
- Unclean application shutdown
- Potential resource leaks
- Incorrect event handling

## Reproduction
1. Launch the application
2. Close the window via window manager/Close button
3. Observe behavior

## Suggested Fix
```python
def closeEvent(self, event):
    # Accept the close event and let the app quit gracefully
    event.accept()
    QApplication.quit()
```
Or simply `event.accept()` if the main app already handles termination.

## Acceptance Criteria
- [ ] Window closes cleanly when user requests close
- [ ] No conflicting quit/ignore calls
- [ ] Proper imports used (QApplication)
