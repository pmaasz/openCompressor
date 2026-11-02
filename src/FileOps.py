import json
from collections import OrderedDict


################################
##Function: StageOpen
#Opens Saved Compressor Json File
##Inputs: 
#file: path to file (str)
##Returns:
#data: full compressor params (dict)
################################
def StageOpen(file):
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
            

################################
##Function: StageSave
#Saves Compressor Params Json File
##Inputs: 
#file: path to file (str)
#common: common vars (dict)
#rotor: rotor vars (dict)
#stator: stator vars (dict)
##Returns:
#None
################################
def StageSave(file, common, rotor, stator):
    if not (len(common) == len(rotor) == len(stator)):
        raise ValueError("common/rotor/stator lists must have equal length")
    if not common:
        raise ValueError("nothing to save: no stages")
    try:
        with open(file, 'w', encoding='utf-8') as dataFile:
            stages = {}

            #Prepare indvidual sections
            for stage in range(1, len(common) + 1):
                stages['Stage ' + str(stage)] = {'Stage': common[stage - 1], 'Rotor': rotor[stage - 1], 'Stator': stator[stage - 1]}

            #Dump dictionary
            json.dump(stages, dataFile, indent=4, sort_keys=True, ensure_ascii=True)
    except (OSError, PermissionError) as e:
        raise ValueError(f"Cannot save file: {e}") from e