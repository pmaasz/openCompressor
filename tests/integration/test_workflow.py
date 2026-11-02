"""Integration tests for full workflow"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from FileOps import StageSave, StageOpen
from BladeCalc import StageCalc
from DefaultParameters import get_default_parameters


class TestFullWorkflow(unittest.TestCase):
    """Test complete workflow from parameters to save/load"""
    
    def test_create_stage_save_load(self):
        """Test creating a stage, saving, and loading it back"""
        defaults = get_default_parameters()
        common = [defaults['Stage']]
        rotor = [defaults['Rotor']]
        stator = [defaults['Stator']]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filename = f.name
        
        try:
            StageSave(filename, common, rotor, stator)
            loaded_common, loaded_rotor, loaded_stator = map(list, zip(*list(StageOpen(filename))))
            
            self.assertEqual(len(loaded_common), 1)
            self.assertEqual(loaded_common[0], common[0])
            self.assertEqual(loaded_rotor[0], rotor[0])
            self.assertEqual(loaded_stator[0], stator[0])
        finally:
            os.unlink(filename)
    
    def test_multi_stage_workflow(self):
        """Test multi-stage compressor workflow"""
        defaults = get_default_parameters()
        common = []
        rotor = []
        stator = []
        
        for i in range(3):
            common.append(dict(defaults['Stage']))
            rotor.append(dict(defaults['Rotor']))
            stator.append(dict(defaults['Stator']))
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filename = f.name
        
        try:
            StageSave(filename, common, rotor, stator)
            loaded_common, loaded_rotor, loaded_stator = map(list, zip(*list(StageOpen(filename))))
            
            self.assertEqual(len(loaded_common), 3)
            self.assertEqual(len(loaded_rotor), 3)
            self.assertEqual(len(loaded_stator), 3)
        finally:
            os.unlink(filename)
    
    def test_stage_calculation_workflow(self):
        """Test stage calculation with realistic values"""
        stage_props = StageCalc(r=0.5, phi=0.6, psi=0.8, rpm=15000,
                                rootRadius=20.0, tipRadius=40.0)
        
        self.assertIsNotNone(stage_props)
        self.assertIsNotNone(stage_props.rootProps)
        self.assertIsNotNone(stage_props.meanProps)
        self.assertIsNotNone(stage_props.tipProps)
        # Verify free-vortex condition
        self.assertAlmostEqual(stage_props.rootProps.cx, stage_props.meanProps.cx, places=1)


if __name__ == '__main__':
    unittest.main()
