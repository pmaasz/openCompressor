# Issue 005: Memory leak when re-rendering - old widgets not removed

**Type:** Bug - P1  
**Component:** UI/MainWindow  
**Locations:** `src/MainWindow.py:1415-1460`

## Description
When rendering rotor/stator, new widgets are added to layout without removing old ones:
```python
rend = RenderWindow(...)
self.R_FrameLayout.addWidget(rend)
self.R_Frame.setLayout(self.R_FrameLayout)
```
Previous render widgets remain in memory/layout causing accumulation on repeated renders.

## Impact
Memory usage grows with each render; potential performance degradation.

## Suggested Fix
Clear the layout before adding new widget:
```python
# Clear existing widgets
for i in reversed(range(self.R_FrameLayout.count())): 
    widget = self.R_FrameLayout.itemAt(i).widget()
    if widget: 
        widget.setParent(None)
        widget.deleteLater()
self.R_FrameLayout.addWidget(rend)
```

## Acceptance Criteria
- [ ] Old render widgets properly removed before adding new ones
- [ ] No memory accumulation on repeated renders
