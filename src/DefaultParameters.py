"""
Default Parameters for CompPy
Smart defaults based on typical compressor designs
"""
from __future__ import annotations

import copy
from typing import Any

# Default parameters for a new stage - educational/small compressor
DEFAULT_STAGE_PARAMETERS: dict[str, dict[str, str]] = {
    "Stage": {
        "Reaction (R)": "0.5",
        "Loading (Psi)": "0.5",
        "Flow (Phi)": "0.6",
        "RPM": "10000",
        "Mean Line Radius": "50.0"
    },
    "Rotor": {
        "Rotor Diameter": "100.0",
        "Hub Diameter": "50.0",
        "Hub Length": "30.0",
        "Num of Blade (Rotor)": "12",
        "Root Chord (Rotor)": "20.0",
        "Tip Chord (Rotor)": "15.0",
        "Blade Thickness (Rotor)": "2.0",
        "Blade Clearance": "0.5",
        "X Twist (Rotor)": "30.0",
        "Y Twist (Rotor)": "40.0"
    },
    "Stator": {
        "Duct ID": "110.0",
        "Duct Length": "40.0",
        "Duct Thickness": "3.0",
        "Num of Blade (Stator)": "18",
        "Mount Can Length": "20.0",
        "Mount Can Dia": "30.0",
        "Mount Can Loc": "15.0",
        "Blade Thickness (Stator)": "2.0",
        "Root Chord (Stator)": "22.0",
        "Tip Chord (Stator)": "18.0",
        "X Twist (Stator)": "25.0",
        "Y Twist (Stator)": "35.0"
    }
}

# Recommended parameter ranges for validation
RECOMMENDED_RANGES: dict[str, tuple[float, float]] = {
    # Universal parameters
    "Reaction (R)": (0.4, 0.6),  # Typical range for good efficiency
    "Loading (Psi)": (0.3, 0.6),  # Avoid too high (separation) or too low (inefficient)
    "Flow (Phi)": (0.5, 0.8),  # Typical operating range
    "RPM": (1000, 100000),  # Wide range for different applications
    "Mean Line Radius": (10.0, 500.0),  # Typical sizes
    
    # Rotor parameters
    "Rotor Diameter": (20.0, 1000.0),
    "Hub Diameter": (10.0, 800.0),
    "Hub Length": (5.0, 200.0),
    "Num of Blade (Rotor)": (6, 30),  # Too few or too many blades
    "Root Chord (Rotor)": (5.0, 150.0),
    "Tip Chord (Rotor)": (3.0, 100.0),
    "Blade Thickness (Rotor)": (0.5, 20.0),
    "Blade Clearance": (0.1, 2.0),  # Small for efficiency
    "X Twist (Rotor)": (15.0, 60.0),
    "Y Twist (Rotor)": (20.0, 60.0),
    
    # Stator parameters
    "Duct ID": (25.0, 1100.0),
    "Duct Length": (10.0, 300.0),
    "Duct Thickness": (1.0, 20.0),
    "Num of Blade (Stator)": (8, 40),  # Typically 1.3-1.8x rotor blades
    "Mount Can Length": (5.0, 200.0),
    "Mount Can Dia": (5.0, 500.0),
    "Mount Can Loc": (0.0, 200.0),
    "Blade Thickness (Stator)": (0.5, 15.0),
    "Root Chord (Stator)": (5.0, 150.0),
    "Tip Chord (Stator)": (3.0, 120.0),
    "X Twist (Stator)": (10.0, 50.0),
    "Y Twist (Stator)": (15.0, 50.0)
}

# Design rules and relationships
DESIGN_RULES: dict[str, tuple[float, float]] = {
    # Hub diameter should be less than rotor diameter
    "hub_to_rotor_ratio": (0.3, 0.7),  # Hub/Rotor diameter ratio
    
    # Blade count relationship
    "stator_to_rotor_blade_ratio": (1.3, 1.8),  # Stator/Rotor blade count
    
    # Chord ratios
    "tip_to_root_chord_ratio": (0.5, 1.0),  # Tip chord usually less than root
    
    # Clearance ratio
    "clearance_to_height_ratio": (0.01, 0.03),  # Clearance as fraction of blade height
    
    # Duct ID should be larger than rotor diameter
    "duct_to_rotor_ratio": (1.05, 1.20)  # Duct ID / Rotor diameter
}


def get_default_parameters() -> dict[str, dict[str, str]]:
    """Return a deep copy of default parameters for a new stage."""
    return copy.deepcopy(DEFAULT_STAGE_PARAMETERS)


def get_recommended_range(parameter_name: str) -> tuple[float, float] | None:
    """Return the recommended (min, max) range for a parameter, if defined."""
    return RECOMMENDED_RANGES.get(parameter_name)


def validate_design_rules(
    stage_params: dict[str, Any],
    rotor_params: dict[str, Any],
    stator_params: dict[str, Any],
) -> list[str]:
    """Validate design relationships and return warning messages."""
    warnings: list[str] = []
    
    try:
        # Check hub to rotor ratio
        rotor_dia = float(rotor_params.get('Rotor Diameter', 0))
        hub_dia = float(rotor_params.get('Hub Diameter', 0))
        if rotor_dia > 0:
            ratio = hub_dia / rotor_dia
            min_ratio, max_ratio = DESIGN_RULES['hub_to_rotor_ratio']
            if ratio < min_ratio or ratio > max_ratio:
                warnings.append(
                    f"Hub/Rotor diameter ratio ({ratio:.2f}) is outside typical range "
                    f"({min_ratio}-{max_ratio}). May affect performance."
                )
        
        # Check blade count ratio
        rotor_blades = int(rotor_params.get('Num of Blade (Rotor)', 1))
        stator_blades = int(stator_params.get('Num of Blade (Stator)', 1))
        if rotor_blades > 0:
            ratio = stator_blades / rotor_blades
            min_ratio, max_ratio = DESIGN_RULES['stator_to_rotor_blade_ratio']
            if ratio < min_ratio or ratio > max_ratio:
                warnings.append(
                    f"Stator/Rotor blade count ratio ({ratio:.2f}) is outside typical range "
                    f"({min_ratio}-{max_ratio}). Consider adjusting blade counts."
                )
        
        # Check clearance ratio
        blade_height = (rotor_dia - hub_dia) / 2
        clearance = float(rotor_params.get('Blade Clearance', 0))
        if blade_height > 0:
            ratio = clearance / blade_height
            min_ratio, max_ratio = DESIGN_RULES['clearance_to_height_ratio']
            if ratio > max_ratio:
                warnings.append(
                    f"Blade clearance ({clearance:.2f} mm) is large relative to blade height. "
                    f"Will reduce efficiency significantly."
                )
        
        # Check duct to rotor ratio
        duct_id = float(stator_params.get('Duct ID', 0))
        if rotor_dia > 0 and duct_id > 0:
            ratio = duct_id / rotor_dia
            min_ratio, max_ratio = DESIGN_RULES['duct_to_rotor_ratio']
            if ratio < min_ratio:
                warnings.append(
                    f"Duct ID ({duct_id:.1f} mm) is too close to rotor diameter. "
                    f"Increase duct ID for proper clearance."
                )
    
    except (ValueError, TypeError):
        # If parameters aren't valid numbers yet, skip validation.
        pass

    return warnings


def apply_defaults_to_stage(
    stage_dict: dict[str, Any],
    rotor_dict: dict[str, Any],
    stator_dict: dict[str, Any],
) -> None:
    """Fill empty/missing fields in stage dictionaries with defaults (in place)."""
    defaults = get_default_parameters()
    
    # Apply stage defaults
    for key, value in defaults['Stage'].items():
        if key not in stage_dict or stage_dict[key] == '':
            stage_dict[key] = value
    
    # Apply rotor defaults
    for key, value in defaults['Rotor'].items():
        if key not in rotor_dict or rotor_dict[key] == '':
            rotor_dict[key] = value
    
    # Apply stator defaults
    for key, value in defaults['Stator'].items():
        if key not in stator_dict or stator_dict[key] == '':
            stator_dict[key] = value
