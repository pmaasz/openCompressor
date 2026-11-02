# Issue 002: Dark mode setting not persisted

**Type:** Enhancement/Bug - P0  
**Component:** UI/Settings  
**Location:** `src/MainWindow.py:69, 1462-1520`

## Description
Dark mode is toggled via `self.darkMode` flag but:
- `self.darkMode` defaults to `True` with no way to load user preference
- Toggling doesn't save to disk
- No configuration file/settings persistence

README documents dark mode toggle but doesn't mention persistence - users expect preference to be remembered.

## Impact
Poor UX - users have to re-toggle dark mode every session.

## Suggested Fix
1. Create settings manager to save/load from `~/.config/comppy/settings.json` (or platform-appropriate location)
2. Load settings on startup
3. Save on toggle
4. Apply theme based on saved preference

## Acceptance Criteria
- [ ] Dark mode preference persisted across sessions
- [ ] Settings file created if missing with sensible defaults
- [ ] Backwards compatible if settings file corrupted
