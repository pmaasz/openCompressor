# Code Review Findings - CompPy

All findings from a 10x engineer code review. Each item formatted as an issue draft.

## P0 - Critical (Security/Correctness/Data Loss)

### Issue 1: Application close ignores close event and calls `qApp.quit()` incorrectly
- **Location:** `src/MainWindow.py:1949-1952`
```python
def closeEvent(self, event):
    qApp.quit()
    event.ignore()
```
- **Issue:** The `closeEvent` ignores the close event (prevents window close) but still calls `qApp.quit()` which terminates the app. This is backwards - `event.ignore()` blocks closing while `qApp.quit()` immediately exits. Also `qApp` is not imported in scope. Behavior is unpredictable. 
- **Impact:** Application may not close cleanly; could leak resources; user interaction broken. 
- **Fix:** If you want to quit on close, call `event.accept()` and optionally `QApplication.quit()`. Or just `event.accept()` and let the event loop end.

### Issue 2: Hardcoded dark mode theme ignores user preference persistence
- **Location:** `src/MainWindow.py:69`, `src/MainWindow.py:1522-1530` (retranslateUi applies theme)
- **Issue:** `self.darkMode = True` hardcoded, and theme is applied on startup every time. No way to persist preference; toggle exists in menu but state isn't saved/restored. Also README says "To toggle dark mode: View > Dark Mode" but implementation just toggles flag.
- **Impact:** Poor UX, no persistence across sessions.
- **Fix:** Save to config file (e.g., `~/.config/comppy/settings.json`) and load on startup.

### Issue 3: Potential division by zero / invalid geometry in blade calculations
- **Locations:** `src/BladeRender.py:95-98`, `src/BladeRender.py:257-261`, `src/BladePlot.py` calculations
- **Issue:** While some guards added (e.g., cos_root near 90° raises), there may be cases where invalid inputs cause issues. Also in `NACA4Blade`, camberPos bounds checked, but other parameters less validated. Division by zero risks if values come from bad data.
- **Impact:** Crash on invalid/unexpected input values.
- **Fix:** More defensive validation, better error messages.

## P1 - High (Bugs/Reliability)

### Issue 4: Incomplete error handling in file save/open paths
- **Locations:** `src/MainWindow.py:898-980`, `src/FileOps.py:13-59`
- **Issue:** `StageSave` opens file without `encoding='utf-8'` (and on some systems default encoding differs). Also doesn't handle permission errors explicitly with user-friendly messages in all cases. `StageOpen` reads without encoding specified.
- **Impact:** May fail on non-ASCII systems or produce garbled errors.
- **Fix:** Use `encoding='utf-8'` explicitly, catch specific exceptions.

### Issue 5: Memory/efficiency issues with mesh concatenation
- **Location:** `src/BladeRender.py:126-136` (fixed to use np.concatenate once - good), but pattern still exists elsewhere. Also in `AssemblyViewer.py`, creating many renderers could accumulate memory.
- **Issue:** The codebase does concatenate meshes efficiently in places now, but if user renders multiple times without clearing, old widgets stay attached? `self.R_FrameLayout.addWidget(rend)` adds widgets but doesn't remove previous ones - could leak. Also in `MainWindow`, when rendering again, previous render widget not removed.
- **Impact:** Memory leaks on repeated renders.
- **Fix:** Clear layout before adding new widget: `clearLayout(self.R_FrameLayout)`

### Issue 6: Unsafe widget lookup by objectName without null checks
- **Location:** `src/MainWindow.py:1142-1170` (ListClicked), `src/MainWindow.py:955-980` (OpenFile)
- **Issue:** Using `self.MainWindow.findChild(QLineEdit, obj)` and assuming found; if name mismatches, silently fails. Also in many places no checks.
- **Impact:** Data not loaded/saved correctly if UI names change.
- **Fix:** Better validation, explicit mapping.

### Issue 7: Stage removal/reordering logic
- **Location:** `src/MainWindow.py:1036-1093` (RemoveStage) - fixed to use row index (good). But drag-and-drop reordering mentioned in features - does reordering update internal lists? The drag-drop is enabled on listWidget but I don't see code handling `itemMoved` to reorder `commonVars/rotorVars/statorVars`. That could cause data/UI mismatch.
- **Impact:** Reordering stages via drag-drop may not persist to data structures.
- **Fix:** Implement handler for drop/move to reorder the lists accordingly.

## P2 - Medium (Code Quality/UX)

### Issue 8: Global state and tight coupling
- **Issue:** MainWindow is very large (1961 lines), does everything - UI, validation, rendering coordination, file I/O. Hard to test/maintain.
- **Fix:** Split into controllers/services.

### Issue 9: Magic numbers throughout
- **Locations:** `BladeRender.py` has some constants now (good), but others like `2` for endwall thickness, `1.7` factor etc. could be centralized.
- **Fix:** Move to config/constants.

### Issue 10: Inconsistent exception handling
- **Locations:** Many broad `except Exception as e:` that log and show dialogs. Some places catch specific exceptions. Better to catch specific exceptions where possible.
- **Fix:** Refine exception handling.

### Issue 11: Tests require GUI/display
- **Issue:** Some tests might need display server (matplotlib with Qt backend). Tests run fine headlessly in environment? They passed - maybe using non-interactive backend.
- **Fix:** Ensure tests set matplotlib backend to 'Agg' if needed.

### Issue 12: Missing type hints, docstrings incomplete
- **Issue:** Codebase lacks type hints throughout; docstrings exist but not comprehensive.
- **Fix:** Add type hints for better maintainability.

### Issue 13: Version checking with global `version = 5` 
- **Location:** `src/MainWindow.py:7`, used in file dialogs
- **Issue:** PyQt5 is used, version check is odd. Just use PyQt5 API directly.
- **Fix:** Remove version branching.

### Issue 14: Dark mode implementation incomplete
- **Issue:** Theme applied but some widgets might not be styled consistently; also matplotlib plots don't change theme. README mentions dark mode but implementation may not be complete.
- **Fix:** Style matplotlib figures based on theme.

### Issue 15: Error logging writes to home directory
- **Location:** `src/ErrorLogger.py` - logs to `~/.comppy/logs/`
- **Issue:** Creates directories in home dir without checking permissions; could fail silently.
- **Fix:** Better error handling, fallback to temp dir.
