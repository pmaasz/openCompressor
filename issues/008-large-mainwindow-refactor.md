# Issue 008: MainWindow is too large and tightly coupled

**Type:** Refactoring - P2  
**Component:** Architecture  
**Location:** `src/MainWindow.py` (1961 lines)

## Description
MainWindow does everything: UI setup, validation, event handling, file I/O, rendering coordination, theming, undo/redo integration, etc. This makes it hard to test, maintain, and extend.

## Suggested Approach
Split into:
- UI setup (or use generated UI)
- ValidationController
- FileController  
- RenderController
- ThemeManager
- etc.

## Impact
Technical debt, harder onboarding, more bugs.

## Acceptance Criteria
- [ ] Reduce MainWindow responsibility
- [ ] Improve testability
- [ ] Better separation of concerns
