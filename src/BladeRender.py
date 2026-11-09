import matplotlib
# Backend is selected by the Qt binding in use; comppy.py sets QT_API.
# Do not call matplotlib.use() on import (was a global side effect).
import matplotlib.pyplot as plt
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from BladeCalc import StageCalc, FindBounds, camber_from_turning
from StlUtils import drawBlade, drawCylinder, drawDuct
from stl import mesh
import numpy as np
from MplTheme import apply_figure_theme

# NACA 4-digit max-camber position (fraction of chord). Was a bare
# magic 0.35 in four places; single source of truth now.
CAMBER_POS = 0.35
# Blade is generated longer than the exposed height so the root stays
# buried in the hub. Replaces magic 1.7 divisor.
BLADE_EMBED_FACTOR = 1.7


################################
##Function: RenderRotor
#Builds and Renders Rotor Object
##Inputs: 
#parent: parent (obj)
#common: common properties (dict)
#object: rotor properties (dict)
##Returns:
#self.rotorHub: completed rotor obj to be exported
################################
class RenderRotor(QWidget):
    def __init__(self, parent, common, object, checked):
        super(RenderRotor, self).__init__(parent)
        
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
    
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
       
        #Change Strings to Floats in Dicts
        self.commonVars = {k : float(v) for k, v in common.items()}
        self.rotorVars = {k : float(v) for k, v in object.items()}
        
        #If Rotor Endwall Was Checked
        self.endWall = checked
        
        #Caculate Rotor Using...Math
        self.objCalc()
    
    
    def objCalc(self):
        #Create Rotor Object
        self.stageProps = StageCalc(r = self.commonVars['Reaction (R)'], 
                                                phi = self.commonVars['Flow (Phi)'], 
                                                psi = self.commonVars['Loading (Psi)'], 
                                                rpm = self.commonVars['RPM'], 
                                                rootRadius = self.rotorVars['Hub Diameter'] / 2, 
                                                tipRadius = self.rotorVars['Rotor Diameter'] / 2)
        #Rotor Root Properties
        rotorRoot = self.stageProps.rootProps
        avgBetaRoot = (rotorRoot.beta2 + rotorRoot.beta1) / 2
        deltaBetaRoot = rotorRoot.beta2 - rotorRoot.beta1
        rootCamber = camber_from_turning(
            self.rotorVars['Root Chord (Rotor)'], deltaBetaRoot)

        #Rotor Tip Properties
        rotorTip = self.stageProps.tipProps
        avgBetaTip = (rotorTip.beta2 + rotorTip.beta1) / 2
        deltaBetaTip = rotorTip.beta2 - rotorTip.beta1
        tipCamber = camber_from_turning(
            self.rotorVars['Tip Chord (Rotor)'], deltaBetaTip)
        
        #Draw Hub Cylinder
        self.rotorHub = drawCylinder(dia = self.rotorVars['Hub Diameter'],
                                               height = self.rotorVars['Hub Length'])
        #Hub Bounds
        hminx, hmaxx, hminy, hmaxy, hminz, hmaxz = FindBounds(self.rotorHub)
        #Rotate the Hub About the Y Axis 90 Deg
        self.rotorHub.rotate([0, 1, 0], np.deg2rad(90))
        #Move it Back to Center
        self.rotorHub.x += (hmaxz - hminz) / 2
        
        rootAngle = np.rad2deg(avgBetaRoot)
        
        #Two different blade heights
        #Relative is for posistioning, to make sure some of the blade is within the rotor hub
        #It's the blade height that's exposed
        relativeBladeHeight = (self.rotorVars['Rotor Diameter'] / 2 - self.rotorVars['Hub Diameter'] / 2)
        if relativeBladeHeight <= 0:
            raise ValueError("Rotor diameter must be greater than hub diameter")
        #Actual height is the actual length of the blade that is created, not all is exposed
        cos_root = np.cos(np.deg2rad(rootAngle))
        if abs(cos_root) < 1e-6:
            raise ValueError("root stagger angle near 90 deg; blade height undefined")
        actualBladeHeight = (self.rotorVars['Rotor Diameter'] / BLADE_EMBED_FACTOR - self.rotorVars['Hub Diameter'] / 2) / cos_root
        if actualBladeHeight <= 0:
            raise ValueError("Invalid blade geometry")

        #Generate Blades
        num_blades = int(self.rotorVars['Num of Blade (Rotor)'])
        if num_blades < 1:
            raise ValueError("Num of Blade (Rotor) must be >= 1")
        self.blades = []
        for i in range(num_blades):
            blade = drawBlade(camberRoot = rootCamber,
                                    camberTip = tipCamber,
                                    camberPos = CAMBER_POS,
                                    thickness = self.rotorVars['Blade Thickness (Rotor)'] / 100,
                                    bladeHeight = actualBladeHeight,
                                    twistAngle = np.rad2deg(avgBetaRoot - avgBetaTip),
                                    rootChord = self.rotorVars['Root Chord (Rotor)'],
                                    tipChord = self.rotorVars['Tip Chord (Rotor)'],
                                    cot = [self.rotorVars['X Twist (Rotor)'], self.rotorVars['Y Twist (Rotor)']])

            #Rotate, Move, and Rotate the Blade
            blade.rotate([0, 0, 1], np.deg2rad(-rootAngle))
            blade.y += (((hmaxx - hminx)) / 2) - (relativeBladeHeight / 2)
            blade.z += (((hmaxy - hminy)) / 2) - (relativeBladeHeight / 2)
            blade.rotate([1, 0, 0], np.deg2rad(rootAngle + ((360.0 / num_blades) * i)))

            self.blades.append(blade)       
        
        #Create a Combined Mesh of All Objects in a single concat
        # (was O(n^2) per-blade reallocation).
        if self.blades:
            self.rotorHub = mesh.Mesh(np.concatenate(
                [self.rotorHub.data] + [b.data for b in self.blades]))
        
        #If End Wall Was Checked
        if self.endWall:
            #Create EndWall Mesh
            endWall = drawDuct(innerDia = self.rotorVars['Rotor Diameter'], thickness = 2, height = self.rotorVars['Hub Length'])
            endWall.rotate([0, 1, 0], np.deg2rad(90))
            endWall.x += (hmaxz - hminz) / 2
            self.rotorHub = mesh.Mesh(np.concatenate([self.rotorHub.data, endWall.data]))
        
        tminx, tmaxx, tminy, tmaxy, tminz, tmaxz = FindBounds(self.rotorHub)
        
        #print(tmaxz - tminz)
        #print(tmaxx - tminx)
        #print(tmaxy - tminy)
        
        #Render That Shiz
        self.render()
        
        
    def render(self):
        from matplotlib import pyplot
        from mpl_toolkits import mplot3d

        # Clear the figure first
        self.figure.clear()
        
        # Create a new plot
        axes = self.figure.add_subplot(111, projection='3d')

        # Render the Rotor
        axes.add_collection3d(mplot3d.art3d.Poly3DCollection(self.rotorHub.vectors))

        # Auto scale to the mesh size
        scale = self.rotorHub.points.flatten()
        axes.auto_scale_xyz(scale, scale, scale)
        
        xLabel = axes.set_xlabel('X')
        yLabel = axes.set_ylabel('Y')
        zLabel = axes.set_zlabel('Z')
        axes.set_xticklabels([])
        axes.set_yticklabels([])
        axes.set_zticklabels([])
        
        apply_figure_theme(self.figure)
        # Force canvas update
        self.canvas.draw()
        self.canvas.flush_events()
        
        
    def getObj(self):
        return self.rotorHub
        
################################
##Function: RenderStator
#Builds and Renders Stator Object
##Inputs: 
#parent: parent (obj)
#common: common properties (dict)
#object: stator properties (dict)
##Returns:
#self.statorHub: completed stator obj to be exported
################################
class RenderStator(QWidget):
    def __init__(self, parent, common, object):
        super(RenderStator, self).__init__(parent)
        
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
    
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        #Change Strings to Floats in Dicts
        self.commonVars = {k : float(v) for k, v in common.items()}
        self.statorVars = {k : float(v) for k, v in object.items()}

        #Caculate Stator 
        self.objCalc()
        
        
    def objCalc(self):
        #Create Stator Object
        self.stageProps = StageCalc(r = self.commonVars['Reaction (R)'], 
                                                phi = self.commonVars['Flow (Phi)'], 
                                                psi = self.commonVars['Loading (Psi)'], 
                                                rpm = self.commonVars['RPM'], 
                                                rootRadius = self.statorVars['Mount Can Dia'] / 2, 
                                                tipRadius = self.statorVars['Duct ID'] / 2)
        #Stator Root Properties
        rotorRoot = self.stageProps.rootProps
        avgBetaRoot = (rotorRoot.beta2 + rotorRoot.beta1) / 2
        deltaBetaRoot = rotorRoot.beta2 - rotorRoot.beta1
        rootCamber = camber_from_turning(
            self.statorVars['Root Chord (Stator)'], deltaBetaRoot)

        #Stator Tip Properties
        rotorTip = self.stageProps.tipProps
        avgBetaTip = (rotorTip.beta2 + rotorTip.beta1) / 2
        deltaBetaTip = rotorTip.beta2 - rotorTip.beta1
        tipCamber = camber_from_turning(
            self.statorVars['Tip Chord (Stator)'], deltaBetaTip)
            
        #Draw Hub Cylinder
        self.mountCan = drawCylinder(dia = self.statorVars['Mount Can Dia'],
                                                    height = self.statorVars['Mount Can Length'])
        
        #Hub Bounds
        hminx, hmaxx, hminy, hmaxy, hminz, hmaxz = FindBounds(self.mountCan)
        #Rotate the Hub About the Y Axis 90 Deg
        self.mountCan.rotate([0, 1, 0], np.deg2rad(90))
        #Move Can to Specified Location
        self.mountCan.x += (hmaxz - hminz) / 2  + self.statorVars['Mount Can Loc']
        
        #Draw and Transform the Duct
        duct = drawDuct(innerDia = self.statorVars['Duct ID'],
                                        thickness = self.statorVars['Duct Thickness'],
                                        height = self.statorVars['Duct Length'])
                                        
        duct.rotate([0, 1, 0], np.deg2rad(90))
        #Move to Center
        duct.x += ((hmaxz - hminz) / 2)
        
        rootAngle = np.rad2deg(avgBetaRoot)
        
        #Two different blade heights
        #Relative is for posistioning, to make sure some of the blade is within the rotor hub
        #It's the blade height that's exposed
        relativeBladeHeight = (self.statorVars['Duct ID'] / 2 - self.statorVars['Mount Can Dia'] / 2)
        if relativeBladeHeight <= 0:
            raise ValueError("Duct ID must be greater than mount can diameter")
        #Actual height is the actual length of the blade that is created, not all is exposed
        cos_root = np.cos(np.deg2rad(rootAngle))
        if abs(cos_root) < 1e-6:
            raise ValueError("root stagger angle near 90 deg; blade height undefined")
        actualBladeHeight = (self.statorVars['Duct ID'] / BLADE_EMBED_FACTOR - self.statorVars['Mount Can Dia'] / 2) / cos_root
        if actualBladeHeight <= 0:
            raise ValueError("Invalid blade geometry")

        #Generate Blades
        num_blades = int(self.statorVars['Num of Blade (Stator)'])
        if num_blades < 1:
            raise ValueError("Num of Blade (Stator) must be >= 1")
        blades = []
        for i in range(num_blades):
            blade = drawBlade(camberRoot = rootCamber,
                                    camberTip = tipCamber,
                                    camberPos = CAMBER_POS,
                                    thickness = self.statorVars['Blade Thickness (Stator)'] / 100,
                                    bladeHeight = actualBladeHeight,
                                    twistAngle = np.rad2deg(avgBetaRoot - avgBetaTip),
                                    rootChord = self.statorVars['Root Chord (Stator)'],
                                    tipChord = self.statorVars['Tip Chord (Stator)'],
                                    cot = [self.statorVars['X Twist (Stator)'], self.statorVars['Y Twist (Stator)']])

            #Rotate, Move, and Rotate the Blade
            blade.rotate([0, 0, 1], np.deg2rad(-rootAngle))
            blade.y += (((hmaxx - hminx)) / 2) - (relativeBladeHeight / 2)
            blade.z += (((hmaxy - hminy)) / 2) - (relativeBladeHeight / 2)
            blade.rotate([1, 0, 0], np.deg2rad(rootAngle + ((360.0 / num_blades) * i)))

            #Move to Specified Location
            blade.x += self.statorVars['Mount Can Loc']
            blades.append(blade)

        #Join Blades and Mount Can + Duct in a single concat
        parts = [self.mountCan.data] + [b.data for b in blades] + [duct.data]
        self.mountCan = mesh.Mesh(np.concatenate(parts))
            
        #Render That 
        self.render()
        
        
    def render(self):
        from matplotlib import pyplot
        from mpl_toolkits import mplot3d

        # Clear the figure first
        self.figure.clear()
        
        # Create a new plot
        axes = self.figure.add_subplot(111, projection='3d')

        # Render the Stator
        axes.add_collection3d(mplot3d.art3d.Poly3DCollection(self.mountCan.vectors))

        # Auto scale to the mesh size
        scale = self.mountCan.points.flatten()
        axes.auto_scale_xyz(scale, scale, scale)
        
        xLabel = axes.set_xlabel('X')
        yLabel = axes.set_ylabel('Y')
        zLabel = axes.set_zlabel('Z')
        axes.set_xticklabels([])
        axes.set_yticklabels([])
        axes.set_zticklabels([])
        
        apply_figure_theme(self.figure)
        # Force canvas update
        self.canvas.draw()
        self.canvas.flush_events()
        
        
    def getObj(self):
        return self.mountCan
                
                
    
    
    
    
    