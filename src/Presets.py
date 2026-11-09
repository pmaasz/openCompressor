"""
Parameter Presets for CompPy
Library of common compressor configurations
"""
from __future__ import annotations

import copy
from typing import Any

PRESETS: dict[str, dict[str, Any]] = {
    "Micro Turbine - Single Stage": {
        "description": "Small single-stage compressor for micro gas turbine applications",
        "Stage": {
            "Reaction (R)": "0.5",
            "Loading (Psi)": "0.45",
            "Flow (Phi)": "0.6",
            "RPM": "80000",
            "Mean Line Radius": "25.0"
        },
        "Rotor": {
            "Rotor Diameter": "50.0",
            "Hub Diameter": "30.0",
            "Hub Length": "15.0",
            "Num of Blade (Rotor)": "16",
            "Root Chord (Rotor)": "12.0",
            "Tip Chord (Rotor)": "8.0",
            "Blade Thickness (Rotor)": "1.5",
            "Blade Clearance": "0.2",
            "X Twist (Rotor)": "35.0",
            "Y Twist (Rotor)": "40.0"
        },
        "Stator": {
            "Duct ID": "55.0",
            "Duct Length": "20.0",
            "Duct Thickness": "2.0",
            "Num of Blade (Stator)": "24",
            "Mount Can Length": "10.0",
            "Mount Can Dia": "15.0",
            "Mount Can Loc": "10.0",
            "Blade Thickness (Stator)": "1.5",
            "Root Chord (Stator)": "12.0",
            "Tip Chord (Stator)": "10.0",
            "X Twist (Stator)": "30.0",
            "Y Twist (Stator)": "35.0"
        }
    },
    
    "RC Ducted Fan - High Speed": {
        "description": "High-performance ducted fan for RC aircraft (no stator needed)",
        "Stage": {
            "Reaction (R)": "0.5",
            "Loading (Psi)": "0.5",
            "Flow (Phi)": "0.7",
            "RPM": "30000",
            "Mean Line Radius": "40.0"
        },
        "Rotor": {
            "Rotor Diameter": "80.0",
            "Hub Diameter": "40.0",
            "Hub Length": "25.0",
            "Num of Blade (Rotor)": "12",
            "Root Chord (Rotor)": "18.0",
            "Tip Chord (Rotor)": "12.0",
            "Blade Thickness (Rotor)": "2.0",
            "Blade Clearance": "0.3",
            "X Twist (Rotor)": "40.0",
            "Y Twist (Rotor)": "45.0"
        },
        "Stator": {
            "Duct ID": "90.0",
            "Duct Length": "30.0",
            "Duct Thickness": "2.5",
            "Num of Blade (Stator)": "18",
            "Mount Can Length": "15.0",
            "Mount Can Dia": "25.0",
            "Mount Can Loc": "12.0",
            "Blade Thickness (Stator)": "2.0",
            "Root Chord (Stator)": "16.0",
            "Tip Chord (Stator)": "14.0",
            "X Twist (Stator)": "35.0",
            "Y Twist (Stator)": "40.0"
        }
    },
    
    "Industrial Compressor - Low Speed": {
        "description": "Large industrial compressor stage with low speed and high efficiency",
        "Stage": {
            "Reaction (R)": "0.5",
            "Loading (Psi)": "0.4",
            "Flow (Phi)": "0.65",
            "RPM": "15000",
            "Mean Line Radius": "150.0"
        },
        "Rotor": {
            "Rotor Diameter": "300.0",
            "Hub Diameter": "180.0",
            "Hub Length": "80.0",
            "Num of Blade (Rotor)": "20",
            "Root Chord (Rotor)": "70.0",
            "Tip Chord (Rotor)": "50.0",
            "Blade Thickness (Rotor)": "5.0",
            "Blade Clearance": "0.5",
            "X Twist (Rotor)": "30.0",
            "Y Twist (Rotor)": "35.0"
        },
        "Stator": {
            "Duct ID": "320.0",
            "Duct Length": "100.0",
            "Duct Thickness": "5.0",
            "Num of Blade (Stator)": "30",
            "Mount Can Length": "50.0",
            "Mount Can Dia": "100.0",
            "Mount Can Loc": "40.0",
            "Blade Thickness (Stator)": "4.0",
            "Root Chord (Stator)": "65.0",
            "Tip Chord (Stator)": "55.0",
            "X Twist (Stator)": "25.0",
            "Y Twist (Stator)": "30.0"
        }
    },
    
    "High Pressure Ratio - Multi-Stage": {
        "description": "Aggressive design for high pressure ratio applications",
        "Stage": {
            "Reaction (R)": "0.6",
            "Loading (Psi)": "0.6",
            "Flow (Phi)": "0.55",
            "RPM": "50000",
            "Mean Line Radius": "60.0"
        },
        "Rotor": {
            "Rotor Diameter": "120.0",
            "Hub Diameter": "70.0",
            "Hub Length": "35.0",
            "Num of Blade (Rotor)": "18",
            "Root Chord (Rotor)": "28.0",
            "Tip Chord (Rotor)": "18.0",
            "Blade Thickness (Rotor)": "3.0",
            "Blade Clearance": "0.3",
            "X Twist (Rotor)": "45.0",
            "Y Twist (Rotor)": "50.0"
        },
        "Stator": {
            "Duct ID": "130.0",
            "Duct Length": "45.0",
            "Duct Thickness": "3.0",
            "Num of Blade (Stator)": "27",
            "Mount Can Length": "20.0",
            "Mount Can Dia": "40.0",
            "Mount Can Loc": "18.0",
            "Blade Thickness (Stator)": "2.5",
            "Root Chord (Stator)": "26.0",
            "Tip Chord (Stator)": "20.0",
            "X Twist (Stator)": "38.0",
            "Y Twist (Stator)": "42.0"
        }
    },
    
    "Educational Example - Simple": {
        "description": "Simple parameters for learning compressor design basics",
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
}

def get_preset_names() -> list[str]:
    """Return all preset names."""
    return list(PRESETS.keys())


def get_preset(name: str) -> dict[str, Any] | None:
    """Return a deep copy of a preset by name, or None if unknown."""
    preset = PRESETS.get(name)
    return copy.deepcopy(preset) if preset is not None else None


def get_preset_description(name: str) -> str:
    """Return the description for a preset, or empty string if unknown."""
    preset = PRESETS.get(name)
    if preset:
        return str(preset.get("description", ""))
    return ""
