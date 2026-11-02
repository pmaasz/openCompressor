# Issue 006: Drag-and-drop stage reordering doesn't update data structures

**Type:** Bug - P1  
**Component:** UI/MainWindow  
**Locations:** `src/MainWindow.py:841-843` (drag-drop enabled), missing handler

## Description
Drag and drop reordering is enabled on the stage list:
```python
self.listWidget.setDragDropMode(QAbstractItemView.InternalMove)
```
But there's no code to handle reordering of `self.commonVars`, `self.rotorVars`, `self.statorVars` lists when items are moved. This causes the data structures to become out of sync with the UI order.

## Impact
- Reordered stages won't save correctly
- Data corruption/mismatch between UI and internal state
- Confusing behavior for users

## Suggested Fix
Connect to `model().rowsMoved` or handle drop event. Need to reorder all three lists to match new order.

## Acceptance Criteria
- [ ] Drag-and-drop reordering updates all data lists consistently
- [ ] Order preserved on save/load
- [ ] No data/UI mismatch
