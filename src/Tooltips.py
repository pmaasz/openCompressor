"""
Parameter Tooltips and Descriptions for CompPy
Provides helpful tooltips for all input fields
"""
from __future__ import annotations

# Detailed tooltips for each parameter
PARAMETER_TOOLTIPS: dict[str, str] = {
    # Universal Coefficients
    "Reaction (R)": "Reaction coefficient (0.0 - 1.0)\nDefines the pressure rise split between rotor and stator.\n0.5 = equal pressure rise in rotor and stator",
    "Loading (Psi)": "Loading coefficient (0.0 - 1.0)\nIndicates how much work the stage does.\nHigher values mean more work but potential for flow separation",
    "Flow (Phi)": "Flow coefficient (0.0 - 1.0)\nRatio of axial velocity to blade tip speed.\nAffects the blade angles and efficiency",
    "RPM": "Rotational speed (1 - 100,000 RPM)\nRotor rotation speed in revolutions per minute.\nHigher speeds increase pressure ratio but stress",
    "Mean Line Radius": "Mean line radius (0.0 - 1000.0 mm)\nRadius at the midpoint of the blade height.\nUsed for mean-line calculations",
    
    # Rotor Specifications
    "Rotor Diameter": "Outer diameter of rotor (0.0 - 1000.0 mm)\nDefines the tip of the rotor blades",
    "Hub Diameter": "Hub diameter (0.0 - 10,000.0 mm)\nInner diameter where blades attach to hub.\nMust be less than rotor diameter",
    "Hub Length": "Hub axial length (0.0 - 1000.0 mm)\nLength of the hub along the axis",
    "Num of Blade (Rotor)": "Number of rotor blades (1 - 1000)\nMore blades increase solidity and pressure rise.\nTypically 12-24 for small compressors",
    "Root Chord (Rotor)": "Blade chord at root (0.0 - 1000.0 mm)\nLength of blade section at the hub",
    "Tip Chord (Rotor)": "Blade chord at tip (0.0 - 1000.0 mm)\nLength of blade section at the tip",
    "Blade Thickness (Rotor)": "Maximum blade thickness (0.0 - 1000.0 mm)\nThickness as percentage of chord.\nAffects strength and aerodynamic performance",
    "Blade Clearance": "Tip clearance (0.0 - 10.0 mm)\nGap between blade tip and casing.\nSmaller gaps improve efficiency but risk contact",
    "X Twist (Rotor)": "X-axis twist angle (0.0 - 100.0°)\nTwist angle in the axial direction.\nControls flow turning",
    "Y Twist (Rotor)": "Y-axis twist center (0.0 - 100.0°)\nLocation of maximum twist along the blade.\nTypically 30-50% from root",
    
    # Stator Specifications  
    "Duct ID": "Inner diameter of duct (0.0 - 1000.0 mm)\nInner wall of the stator duct",
    "Duct Length": "Axial length of duct (0.0 - 1000.0 mm)\nLength of the stator section",
    "Duct Thickness": "Wall thickness (0.0 - 100.0 mm)\nThickness of the duct walls",
    "Num of Blade (Stator)": "Number of stator vanes (1 - 1000)\nTypically 1.5x rotor blade count.\nMore vanes reduce swirl more effectively",
    "Mount Can Length": "Mounting can length (0.0 - 1000.0 mm)\nLength of the central mounting can",
    "Mount Can Dia": "Mounting can diameter (0.0 - 1000.0 mm)\nDiameter of central support structure",
    "Mount Can Loc": "Mounting can position (0.0 - 1000.0 mm)\nAxial location of mounting can",
    "Blade Thickness (Stator)": "Maximum vane thickness (0.0 - 100.0 mm)\nThickness of stator vanes",
    "Root Chord (Stator)": "Vane chord at root (0.0 - 1000.0 mm)\nChord length at inner diameter",
    "Tip Chord (Stator)": "Vane chord at tip (0.0 - 1000.0 mm)\nChord length at outer diameter",
    "X Twist (Stator)": "X-axis twist angle (0.0 - 1000.0°)\nStator vane twist in axial direction",
    "Y Twist (Stator)": "Y-axis twist center (0.0 - 1000.0°)\nLocation of maximum stator twist"
}

# Helpful explanations for validation failures
VALIDATION_MESSAGES: dict[str, str] = {
    "empty": "This field is required",
    "out_of_range": "Value must be within valid range",
    "not_number": "Please enter a valid number",
    "not_integer": "Please enter a whole number",
}


def get_tooltip(field_name: str) -> str:
    """Get tooltip for a given field name."""
    return PARAMETER_TOOLTIPS.get(field_name, "")


def get_validation_message(field_name: str, error_type: str) -> str:
    """Get a user-facing validation message for a field and error type."""
    base_msg = VALIDATION_MESSAGES.get(error_type, "Invalid value")
    tooltip = PARAMETER_TOOLTIPS.get(field_name, "")
    if tooltip:
        # Extract just the range from the first line.
        first_line = tooltip.split('\n')[0]
        return f"{base_msg}\n{first_line}"
    return base_msg
