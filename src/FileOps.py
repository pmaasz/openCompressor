from __future__ import annotations

import json
import os
from collections import OrderedDict
from collections.abc import Iterator
from typing import Any


StageDict = dict[str, Any]
StageTriple = tuple[StageDict, StageDict, StageDict]


def StageOpen(file: os.PathLike[str] | str) -> Iterator[StageTriple]:
    """Open a saved compressor JSON file and yield (Stage, Rotor, Stator) per stage.

    Raises ValueError for unreadable or invalid CompPy stage data.
    """
    try:
        with open(file, encoding='utf-8') as dataFile:
            try:
                data = json.load(dataFile, object_pairs_hook=OrderedDict)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid CompPy JSON file: {e}") from e
    except (OSError, PermissionError) as e:
        raise ValueError(f"Cannot open file: {e}") from e

    if not isinstance(data, dict) or not data:
        raise ValueError("Invalid CompPy file: expected non-empty stage dict")

    for stage in data:
        entry = data[stage]
        if not isinstance(entry, dict):
            raise ValueError(f"Invalid stage entry {stage!r}: expected dict")
        for key in ('Stage', 'Rotor', 'Stator'):
            if key not in entry:
                raise ValueError(f"Invalid stage {stage!r}: missing {key!r}")
            if not isinstance(entry[key], dict):
                raise ValueError(f"Invalid stage {stage!r}: {key!r} must be a dict")
        yield entry['Stage'], entry['Rotor'], entry['Stator']


def StageSave(
    file: os.PathLike[str] | str,
    common: list[StageDict],
    rotor: list[StageDict],
    stator: list[StageDict],
) -> None:
    """Save compressor stage parameters to a JSON file."""
    if not (len(common) == len(rotor) == len(stator)):
        raise ValueError("common/rotor/stator lists must have equal length")
    if not common:
        raise ValueError("nothing to save: no stages")
    try:
        with open(file, 'w', encoding='utf-8') as dataFile:
            stages: dict[str, dict[str, StageDict]] = {}

            # Prepare individual sections.
            for stage in range(1, len(common) + 1):
                stages['Stage ' + str(stage)] = {
                    'Stage': common[stage - 1],
                    'Rotor': rotor[stage - 1],
                    'Stator': stator[stage - 1],
                }

            # Dump dictionary.
            json.dump(stages, dataFile, indent=4, sort_keys=True, ensure_ascii=True)
    except (OSError, PermissionError) as e:
        raise ValueError(f"Cannot save file: {e}") from e