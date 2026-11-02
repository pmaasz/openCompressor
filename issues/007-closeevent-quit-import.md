# Issue 007: closeEvent uses undefined qApp

**Type:** Bug - P1  
**Component:** UI/MainWindow  
**Location:** `src/MainWindow.py:1949-1952`

## Description
`closeEvent` calls `qApp.quit()` but `qApp` is not imported or defined. Should use `QApplication.quit()` or `QApplication.instance().quit()`.

## Impact
NameError when closing window.

## Suggested Fix
Import QApplication if needed and use proper API, or just `event.accept()`.
