# Issue 012: Add comprehensive test coverage for UI and integration paths

**Type:** Testing - P1  
**Component:** Tests  
**Labels:** test, P1

## Description
Current tests cover core calculations, STL utils, file ops, and regression cases well (57 tests passing). But there are gaps:
- UI components (MainWindow logic) not unit tested - hard to test due to Qt
- Integration tests for full workflow (create stage → render → export)
- Edge cases in validation logic
- Error handling paths
- Theme/dark mode behavior

## Suggested Approach
1. Add pytest + pytest-qt for UI testing where possible
2. Add integration tests that test logic without full GUI display
3. Add tests for DefaultParameters, Presets, UndoRedo, Tooltips
4. Add tests for AssemblyViewer logic paths
5. Add coverage reporting (pytest-cov)

## Acceptance Criteria
- [ ] Increase coverage of src/ modules
- [ ] Add UI logic unit tests (separable from display)
- [ ] Add integration test suite
- [ ] Add coverage reporting to CI
