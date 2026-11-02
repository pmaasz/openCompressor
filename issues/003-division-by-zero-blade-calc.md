# Issue 003: Potential division by zero in blade geometry calculations

**Type:** Bug - P0  
**Component:** BladeRender/BladePlot  
**Locations:** `src/BladeRender.py:95-98, 257-261`

## Description
In blade height calculations:
```python
cos_root = np.cos(np.deg2rad(rootAngle))
if abs(cos_root) < 1e-6:
    raise ValueError("root stagger angle near 90 deg; blade height undefined")
actualBladeHeight = (self.rotorVars['Rotor Diameter'] / BLADE_EMBED_FACTOR - self.rotorVars['Hub Diameter'] / 2) / cos_root
```
Good guard exists for root stagger near 90°. But there may be other cases where division by zero can occur from invalid user inputs (e.g., hub diameter equals rotor diameter, negative values not caught, etc.). Also in general calculations need more defensive checks.

## Impact
Application crash with confusing errors or unhandled exceptions.

## Suggested Fix
- Add more validation for geometric constraints (hub < rotor diameter, blade clearance reasonable, etc.)
- Improve error messages to guide user
- Add validation in UI layer before attempting calculations

## Acceptance Criteria
- [ ] All division operations guarded or validated
- [ ] Clear error messages for invalid geometry
- [ ] No crashes on invalid inputs
