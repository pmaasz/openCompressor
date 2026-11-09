import os
import json

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import BladePlot
import RenderWindow
from FileOps import StageOpen, StageSave
from UndoRedo import UndoRedoManager
from Tooltips import get_tooltip, get_validation_message
from Presets import get_preset_names, get_preset, get_preset_description
from AssemblyViewer import AssemblyViewer
from RecentFiles import RecentFilesManager
from ErrorLogger import logger
from DefaultParameters import get_default_parameters, validate_design_rules, apply_defaults_to_stage


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow  # Store reference to MainWindow instance
        MainWindow.setObjectName("CompPy")
        MainWindow.resize(805, 583)

        self.commonVars = []
        self.rotorVars = []
        self.statorVars = []
        
        self.commonValidators = {"RPM" : None, "Loading (Psi)" : None, "Flow (Phi)" : None, "Reaction (R)" : None, "Mean Line Radius" : None}
        self.rotorValidators = {"Y Twist (Rotor)" : None, "X Twist (Rotor)" : None, "Tip Chord (Rotor)" : None, "Rotor Diameter" : None, "Root Chord (Rotor)" : None, "Blade Thickness (Rotor)" : None, "Hub Diameter" : None, "Hub Length" : None, "Blade Clearance" : None, "Num of Blade (Rotor)" : None}
        self.statorValidators = {"Duct ID" : None, "Duct Length" : None, "Duct Thickness" : None, "Num of Blade (Stator)" : None, "Mount Can Length" : None, "Mount Can Dia" : None, "Mount Can Loc" : None, "Blade Thickness (Stator)" : None, "Root Chord (Stator)" : None, "Tip Chord (Stator)" : None, "X Twist (Stator)" : None, "Y Twist (Stator)" : None}
        
        # Valid ranges for each field to provide helpful suggestions
        self.validRanges = {
            "RPM": "1 - 100,000",
            "Loading (Psi)": "0.0 - 1.0",
            "Flow (Phi)": "0.0 - 1.0",
            "Reaction (R)": "0.0 - 1.0",
            "Mean Line Radius": "0.0 - 1000.0 mm",
            "Y Twist (Rotor)": "0.0 - 100.0 degrees",
            "X Twist (Rotor)": "0.0 - 100.0 degrees",
            "Tip Chord (Rotor)": "0.0 - 1000.0 mm",
            "Rotor Diameter": "0.0 - 1000.0 mm",
            "Root Chord (Rotor)": "0.0 - 1000.0 mm",
            "Blade Thickness (Rotor)": "0.0 - 1000.0 mm",
            "Hub Diameter": "0.0 - 10,000.0 mm",
            "Hub Length": "0.0 - 1000.0 mm",
            "Blade Clearance": "0.0 - 10.0 mm",
            "Num of Blade (Rotor)": "1 - 1000",
            "Duct ID": "0.0 - 1000.0 mm",
            "Duct Length": "0.0 - 1000.0 mm",
            "Duct Thickness": "0.0 - 100.0 mm",
            "Num of Blade (Stator)": "1 - 1000",
            "Mount Can Length": "0.0 - 1000.0 mm",
            "Mount Can Dia": "0.0 - 1000.0 mm",
            "Mount Can Loc": "0.0 - 1000.0 mm",
            "Blade Thickness (Stator)": "0.0 - 100.0 mm",
            "Root Chord (Stator)": "0.0 - 1000.0 mm",
            "Tip Chord (Stator)": "0.0 - 1000.0 mm",
            "X Twist (Stator)": "0.0 - 1000.0 degrees",
            "Y Twist (Stator)": "0.0 - 1000.0 degrees"
        }
        
        self.exportObj = None
        self.clicked = None
        self.fileOpen = False
        self.failed = []
        self.darkMode = True
        self._load_theme_preference()
        
        # Initialize undo/redo manager
        self.undo_manager = UndoRedoManager()
        
        # Track current values for undo
        self.field_previous_values = {}
        
        # Initialize recent files manager
        self.recent_files_manager = RecentFilesManager()
        
        # Initialize error logger
        logger.info("CompPy started")
        logger.debug(f"Window size: {MainWindow.width()}x{MainWindow.height()}")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName("gridLayout")
        

        self.Rotor_Frame = QFrame(self.centralwidget)
        self.Rotor_Frame.setMaximumSize(QSize(375, 16777215))
        self.Rotor_Frame.setFrameShape(QFrame.StyledPanel)
        self.Rotor_Frame.setFrameShadow(QFrame.Raised)
        self.Rotor_Frame.setObjectName("Rotor_Frame")
        
        self.gridLayout_2 = QGridLayout(self.Rotor_Frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        
        self.YT_Label = QLabel(self.Rotor_Frame)
        self.YT_Label.setStyleSheet("font: bold")
        self.YT_Label.setObjectName("YT_Label")
        
        self.gridLayout_2.addWidget(self.YT_Label, 11, 2, 1, 1)
        
        self.YT_Line = QLineEdit(self.Rotor_Frame)
        self.YT_Line.setAlignment(Qt.AlignCenter)
        self.YT_Line.setObjectName("Y Twist (Rotor)")
        self.YT_Line.setValidator(QDoubleValidator(0.0, 100.0, 3, self.YT_Line))
        self.YT_Line.setToolTip(get_tooltip("Y Twist (Rotor)"))
        self.YT_Line.textChanged.connect(self.CheckState)
        self.YT_Line.editingFinished.connect(self.TrackUndo)
        self.YT_Line.textChanged.emit(self.YT_Line.text())
        
        self.gridLayout_2.addWidget(self.YT_Line, 11, 3, 1, 1)
        
        self.wallCheck = QCheckBox(self.Rotor_Frame)
        self.wallCheck.setStyleSheet("font: bold;")
        self.wallCheck.setObjectName("wallCheck")
        
        self.gridLayout_2.addWidget(self.wallCheck, 12, 0, 1, 1)
        
        self.RDia_Label = QLabel(self.Rotor_Frame)
        self.RDia_Label.setStyleSheet("font: bold")
        self.RDia_Label.setObjectName("RDia_Label")
        
        self.gridLayout_2.addWidget(self.RDia_Label, 2, 0, 1, 1)
        
        self.BT_Label = QLabel(self.Rotor_Frame)
        self.BT_Label.setStyleSheet("font: bold")
        self.BT_Label.setObjectName("BT_Label")
        
        self.gridLayout_2.addWidget(self.BT_Label, 9, 0, 1, 1)
        
        self.R_Title = QLabel(self.Rotor_Frame)
        self.R_Title.setStyleSheet("font-size: 16px; font: bold;")
        self.R_Title.setObjectName("R_Title")
        
        self.gridLayout_2.addWidget(self.R_Title, 0, 0, 1, 2)
        
        self.NB_Label = QLabel(self.Rotor_Frame)
        self.NB_Label.setStyleSheet("font: bold")
        self.NB_Label.setObjectName("NB_Label")
        
        self.gridLayout_2.addWidget(self.NB_Label, 4, 2, 1, 1)
        
        self.RC_Label = QLabel(self.Rotor_Frame)
        self.RC_Label.setStyleSheet("font: bold")
        self.RC_Label.setObjectName("RC_Label")
        
        self.gridLayout_2.addWidget(self.RC_Label, 7, 0, 1, 1)
        
        self.HDia_Label = QLabel(self.Rotor_Frame)
        self.HDia_Label.setStyleSheet("font: bold")
        self.HDia_Label.setObjectName("HDia_Label")
        
        self.gridLayout_2.addWidget(self.HDia_Label, 2, 2, 1, 1)
        
        self.TC_Label = QLabel(self.Rotor_Frame)
        self.TC_Label.setStyleSheet("font: bold")
        self.TC_Label.setObjectName("TC_Label")
        
        self.gridLayout_2.addWidget(self.TC_Label, 7, 2, 1, 1)
        
        self.XT_Line = QLineEdit(self.Rotor_Frame)
        self.XT_Line.setAlignment(Qt.AlignCenter)
        self.XT_Line.setObjectName("X Twist (Rotor)")
        self.XT_Line.setValidator(QDoubleValidator(0.0, 100.0, 3, self.XT_Line))
        self.XT_Line.textChanged.connect(self.CheckState)
        self.XT_Line.textChanged.emit(self.XT_Line.text())
        
        self.gridLayout_2.addWidget(self.XT_Line, 11, 1, 1, 1)
        
        self.TC_Line = QLineEdit(self.Rotor_Frame)
        self.TC_Line.setAlignment(Qt.AlignCenter)
        self.TC_Line.setObjectName("Tip Chord (Rotor)")
        self.TC_Line.setValidator(QDoubleValidator(0.0, 1000.0, 3, self.TC_Line))
        self.TC_Line.textChanged.connect(self.CheckState)
        self.TC_Line.textChanged.emit(self.TC_Line.text())
        
        self.gridLayout_2.addWidget(self.TC_Line, 7, 3, 1, 1)
        
        self.RD_Line = QLineEdit(self.Rotor_Frame)
        self.RD_Line.setAlignment(Qt.AlignCenter)
        self.RD_Line.setObjectName("Rotor Diameter")
        self.RD_Line.setValidator(QDoubleValidator(0.0, 1000.0, 3, self.RD_Line))
        self.RD_Line.textChanged.connect(self.CheckState)
        self.RD_Line.textChanged.emit(self.RD_Line.text())
        
        self.gridLayout_2.addWidget(self.RD_Line, 2, 1, 1, 1)
        
        self.HL_Label = QLabel(self.Rotor_Frame)
        self.HL_Label.setStyleSheet("font: bold")
        self.HL_Label.setObjectName("HL_Label")
        
        self.gridLayout_2.addWidget(self.HL_Label, 4, 0, 1, 1)
        
        self.RC_Line = QLineEdit(self.Rotor_Frame)
        self.RC_Line.setAlignment(Qt.AlignCenter)
        self.RC_Line.setObjectName("Root Chord (Rotor)")
        self.RC_Line.setValidator(QDoubleValidator(0.0, 1000.0, 3, self.RC_Line))
        self.RC_Line.textChanged.connect(self.CheckState)
        self.RC_Line.textChanged.emit(self.RC_Line.text())
        
        self.gridLayout_2.addWidget(self.RC_Line, 7, 1, 1, 1)
        
        self.BT_Line = QLineEdit(self.Rotor_Frame)
        self.BT_Line.setAlignment(Qt.AlignCenter)
        self.BT_Line.setObjectName("Blade Thickness (Rotor)")
        self.BT_Line.setValidator(QDoubleValidator(0.0, 1000.0, 3, self.BT_Line))
        self.BT_Line.textChanged.connect(self.CheckState)
        self.BT_Line.textChanged.emit(self.BT_Line.text())
        
        self.gridLayout_2.addWidget(self.BT_Line, 9, 1, 1, 1)
        
        self.BC_Label = QLabel(self.Rotor_Frame)
        self.BC_Label.setStyleSheet("font: bold")
        self.BC_Label.setObjectName("BC_Label")
        
        self.gridLayout_2.addWidget(self.BC_Label, 9, 2, 1, 1)
        
        self.HD_Line = QLineEdit(self.Rotor_Frame)
        self.HD_Line.setAlignment(Qt.AlignCenter)
        self.HD_Line.setObjectName("Hub Diameter")
        self.HD_Line.setValidator(QDoubleValidator(0.0, 10000.0, 3, self.HD_Line))
        self.HD_Line.textChanged.connect(self.CheckState)
        self.HD_Line.textChanged.emit(self.HD_Line.text())
        
        self.gridLayout_2.addWidget(self.HD_Line, 2, 3, 1, 1)
        
        self.HL_Line = QLineEdit(self.Rotor_Frame)
        self.HL_Line.setAlignment(Qt.AlignCenter)
        self.HL_Line.setObjectName("Hub Length")
        self.HL_Line.setValidator(QDoubleValidator(0.0, 1000.0, 3, self.HL_Line))
        self.HL_Line.textChanged.connect(self.CheckState)
        self.HL_Line.textChanged.emit(self.HL_Line.text())
        
        self.gridLayout_2.addWidget(self.HL_Line, 4, 1, 1, 1)
        
        self.BC_Line = QLineEdit(self.Rotor_Frame)
        self.BC_Line.setAlignment(Qt.AlignCenter)
        self.BC_Line.setObjectName("Blade Clearance")
        self.BC_Line.setValidator(QDoubleValidator(0.0, 10.0, 3, self.BC_Line))
        self.BC_Line.textChanged.connect(self.CheckState)
        self.BC_Line.textChanged.emit(self.BC_Line.text())
        
        self.gridLayout_2.addWidget(self.BC_Line, 9, 3, 1, 1)
        
        self.XT_Label = QLabel(self.Rotor_Frame)
        self.XT_Label.setStyleSheet("font: bold")
        self.XT_Label.setObjectName("XT_Label")
        
        self.gridLayout_2.addWidget(self.XT_Label, 11, 0, 1, 1)
        
        self.NB_Line = QLineEdit(self.Rotor_Frame)
        self.NB_Line.setAlignment(Qt.AlignCenter)
        self.NB_Line.setObjectName("Num of Blade (Rotor)")
        self.NB_Line.setValidator(QIntValidator(1, 1000,  self.NB_Line))
        self.NB_Line.textChanged.connect(self.CheckState)
        self.NB_Line.textChanged.emit(self.NB_Line.text())
        
        self.gridLayout_2.addWidget(self.NB_Line, 4, 3, 1, 1)
        
        self.line_2 = QFrame(self.Rotor_Frame)
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        
        self.gridLayout_2.addWidget(self.line_2, 1, 0, 1, 4)
        
        self.gridLayout.addWidget(self.Rotor_Frame, 1, 0, 1, 1)
        
        self.Up_Frame = QFrame(self.centralwidget)
        self.Up_Frame.setMaximumSize(QSize(16777215, 400))
        self.Up_Frame.setFrameShape(QFrame.StyledPanel)
        self.Up_Frame.setFrameShadow(QFrame.Raised)
        self.Up_Frame.setObjectName("Up_Frame")
        
        self.horizontalLayout = QHBoxLayout(self.Up_Frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        self.L_Frame = QFrame(self.Up_Frame)
        self.L_Frame.setMaximumSize(QSize(410, 16777215))
        self.L_Frame.setFrameShape(QFrame.StyledPanel)
        self.L_Frame.setFrameShadow(QFrame.Raised)
        self.L_Frame.setObjectName("L_Frame")
        
        self.gridLayout_4 = QGridLayout(self.L_Frame)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setHorizontalSpacing(5)
        self.gridLayout_4.setObjectName("gridLayout_4")
                 
        self.U_Frame = QFrame(self.L_Frame)
        self.U_Frame.setMinimumSize(QSize(200, 0))
        self.U_Frame.setMaximumSize(QSize(200, 200))
        self.U_Frame.setFrameShape(QFrame.StyledPanel)
        self.U_Frame.setFrameShadow(QFrame.Raised)
        self.U_Frame.setObjectName("U_Frame")
        
        self.formLayout = QFormLayout(self.U_Frame)
        self.formLayout.setLabelAlignment(Qt.AlignCenter)
        self.formLayout.setFormAlignment(Qt.AlignHCenter|Qt.AlignTop)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        
        self.R_Label = QLabel(self.U_Frame)
        self.R_Label.setStyleSheet("font: bold;")
        self.R_Label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.R_Label.setObjectName("R_Label")
        
        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.R_Label)
        
        self.R_Line = QLineEdit(self.U_Frame)
        self.R_Line.setAlignment(Qt.AlignCenter)
        self.R_Line.setObjectName("Reaction (R)")
        self.R_Line.setValidator(QDoubleValidator(0.0, 1.0, 3, self.R_Line))
        self.R_Line.textChanged.connect(self.CheckState)
        self.R_Line.textChanged.emit(self.R_Line.text())
        
        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.R_Line)
        
        self.PSI_Label = QLabel(self.U_Frame)
        self.PSI_Label.setStyleSheet("font: bold;")
        self.PSI_Label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.PSI_Label.setObjectName("PSI_Label")
        
        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.PSI_Label)
        
        self.PSI_Line = QLineEdit(self.U_Frame)
        self.PSI_Line.setAlignment(Qt.AlignCenter)
        self.PSI_Line.setObjectName("Loading (Psi)")
        self.PSI_Line.setValidator(QDoubleValidator(0.0, 1.0, 3, self.PSI_Line))
        self.PSI_Line.textChanged.connect(self.CheckState)
        self.PSI_Line.textChanged.emit(self.PSI_Line.text())
        
        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.PSI_Line)
        
        self.PHI_Label = QLabel(self.U_Frame)
        self.PHI_Label.setStyleSheet("font: bold;")
        self.PHI_Label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.PHI_Label.setObjectName("PHI_Label")
        
        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.PHI_Label)
        
        self.PHI_Line = QLineEdit(self.U_Frame)
        self.PHI_Line.setAlignment(Qt.AlignCenter)
        self.PHI_Line.setObjectName("Flow (Phi)")
        self.PHI_Line.setValidator(QDoubleValidator(0.0, 1.0, 3, self.PHI_Line))
        self.PHI_Line.textChanged.connect(self.CheckState)
        self.PHI_Line.textChanged.emit(self.PHI_Line.text())
        
        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.PHI_Line)
        
        self.Title = QLabel(self.U_Frame)
        self.Title.setStyleSheet("font-size: 16px; font: bold;")
        self.Title.setAlignment(Qt.AlignCenter)
        self.Title.setObjectName("Title")
        
        self.formLayout.setWidget(0, QFormLayout.SpanningRole, self.Title)
        
        self.MLR_Label = QLabel(self.U_Frame)
        self.MLR_Label.setStyleSheet("font: bold;")
        self.MLR_Label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.MLR_Label.setObjectName("MLR_Label")
        
        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.MLR_Label)
        
        self.MLR_Line = QLineEdit(self.U_Frame)
        self.MLR_Line.setAlignment(Qt.AlignCenter)
        self.MLR_Line.setObjectName("Mean Line Radius")
        self.MLR_Line.setValidator(QDoubleValidator(0.0, 1000.0, 3, self.MLR_Line))
        self.MLR_Line.textChanged.connect(self.CheckState)
        self.MLR_Line.textChanged.emit(self.MLR_Line.text())
        
        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.MLR_Line)
        
        self.RPM_Label = QLabel(self.U_Frame)
        self.RPM_Label.setStyleSheet("font: bold;")
        self.RPM_Label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.RPM_Label.setObjectName("RPM_Label")
        
        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.RPM_Label)
        
        self.RPM_Line = QLineEdit(self.U_Frame)
        self.RPM_Line.setAlignment(Qt.AlignCenter)
        self.RPM_Line.setObjectName("RPM")
        self.RPM_Line.setValidator(QIntValidator(1, 100000,  self.RPM_Line))
        self.RPM_Line.textChanged.connect(self.CheckState)
        self.RPM_Line.textChanged.emit(self.RPM_Line.text())
        
        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.RPM_Line)
        
        self.line = QFrame(self.U_Frame)
        self.line.setMinimumSize(QSize(200, 0))
        self.line.setMaximumSize(QSize(16777215, 16777215))
        self.line.setLineWidth(1)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setObjectName("line")
        
        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.line)
        
        self.gridLayout_4.addWidget(self.U_Frame, 0, 1, 1, 1)
        
        self.listWidget = QListWidget(self.L_Frame)
        self.listWidget.setMinimumSize(QSize(200, 200))
        self.listWidget.setMaximumSize(QSize(200, 200))
        self.listWidget.setTextElideMode(Qt.ElideMiddle)
        self.listWidget.setObjectName("listWidget")
        
        
        self.listWidget.itemClicked.connect(self.ListClicked)
        
        self.gridLayout_4.addWidget(self.listWidget, 0, 0, 1, 1)
        
        self.renderExport = QPushButton(self.L_Frame)
        self.renderExport.setObjectName("renderExport")
        self.renderExport.clicked.connect(self.Export)
        
        self.gridLayout_4.addWidget(self.renderExport, 3, 1, 1, 1)
        
        self.frame = QFrame(self.L_Frame)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setObjectName("frame")
        
        self.gridLayout_5 = QGridLayout(self.frame)
        self.gridLayout_5.setObjectName("gridLayout_5")
        
        self.removeButton = QPushButton(self.frame)
        self.removeButton.setObjectName("removeButton")
        self.removeButton.clicked.connect(self.RemoveStage)
        self.gridLayout_5.addWidget(self.removeButton, 0, 1, 1, 1)
        
        self.addButton = QPushButton(self.frame)
        self.addButton.setObjectName("addButton")
        self.addButton.clicked.connect(self.AddStage)
        self.gridLayout_5.addWidget(self.addButton, 0, 0, 1, 1)
        
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        
        self.gridLayout_5.addItem(spacerItem, 1, 0, 1, 1)
        self.gridLayout_4.addWidget(self.frame, 1, 0, 2, 1)
        
        self.profileButton = QPushButton(self.L_Frame)
        self.profileButton.setObjectName("profileButton")
        self.profileButton.clicked.connect(self.PlotProfile)
        
        self.renderButton = QPushButton(self.L_Frame)
        self.renderButton.setObjectName("renderButton")
        self.renderButton.clicked.connect(self.Render)
        
       
        self.gridLayout_4.addWidget(self.profileButton, 1, 1, 1, 1)
        self.gridLayout_4.addWidget(self.renderButton, 2, 1, 1, 1)
        self.horizontalLayout.addWidget(self.L_Frame)
        
        self.R_Frame = QFrame()
        self.R_FrameLayout = QGridLayout(self.R_Frame)
        self.R_Frame.setMinimumSize(QSize(375, 0))
        self.R_Frame.setMaximumSize(QSize(400, 400))
        self.R_Frame.setObjectName("R_Frame")
        
        self.L_Frame.raise_()
        self.L_Frame.raise_()
        
        self.horizontalLayout.addWidget(self.R_Frame)
        
        self.gridLayout.addWidget(self.Up_Frame, 0, 0, 1, 3)
        
        self.Stator_Frame = QFrame(self.centralwidget)
        self.Stator_Frame.setMaximumSize(QSize(375, 200))
        self.Stator_Frame.setFrameShape(QFrame.StyledPanel)
        self.Stator_Frame.setFrameShadow(QFrame.Raised)
        self.Stator_Frame.setObjectName("Stator_Frame")
        
        self.gridLayout_3 = QGridLayout(self.Stator_Frame)
        self.gridLayout_3.setObjectName("gridLayout_3")
        
        self.DI_Label = QLabel(self.Stator_Frame)
        self.DI_Label.setStyleSheet("font: bold;")
        self.DI_Label.setObjectName("DI_Label")
        
        self.gridLayout_3.addWidget(self.DI_Label, 2, 2, 1, 1)
        
        self.S_Title = QLabel(self.Stator_Frame)
        self.S_Title.setStyleSheet("font-size: 16px; font: bold;")
        self.S_Title.setObjectName("S_Title")
        
        self.gridLayout_3.addWidget(self.S_Title, 0, 0, 1, 4)
        
        self.DI_Line = QLineEdit(self.Stator_Frame)
        self.DI_Line.setAlignment(Qt.AlignCenter)
        self.DI_Line.setObjectName("Duct ID")
        self.DI_Line.setValidator(QDoubleValidator(0.0, 1000.0, 3, self.DI_Line))
        self.DI_Line.textChanged.connect(self.CheckState)
        self.DI_Line.textChanged.emit(self.DI_Line.text())
        
        self.gridLayout_3.addWidget(self.DI_Line, 2, 3, 1, 1)
        
        self.DT_Label = QLabel(self.Stator_Frame)
        self.DT_Label.setStyleSheet("font: bold;")
        self.DT_Label.setObjectName("DT_Label")
        
        self.gridLayout_3.addWidget(self.DT_Label, 3, 0, 1, 1)
        
        self.DL_Label = QLabel(self.Stator_Frame)
        self.DL_Label.setStyleSheet("font: bold;")
        self.DL_Label.setObjectName("DL_Label")
        
        self.gridLayout_3.addWidget(self.DL_Label, 2, 0, 1, 1)
        
        self.DL_Line = QLineEdit(self.Stator_Frame)
        self.DL_Line.setAlignment(Qt.AlignCenter)
        self.DL_Line.setObjectName("Duct Length")
        self.DL_Line.setValidator(QDoubleValidator(0.0, 1000.0, 3, self.DL_Line))
        self.DL_Line.textChanged.connect(self.CheckState)
        self.DL_Line.textChanged.emit(self.DL_Line.text())
        
        self.gridLayout_3.addWidget(self.DL_Line, 2, 1, 1, 1)
        
        self.DT_Line = QLineEdit(self.Stator_Frame)
        self.DT_Line.setAlignment(Qt.AlignCenter)
        self.DT_Line.setObjectName("Duct Thickness")
        self.DT_Line.setValidator(QDoubleValidator(0.0, 100.0, 3, self.DT_Line))
        self.DT_Line.textChanged.connect(self.CheckState)
        self.DT_Line.textChanged.emit(self.DT_Line.text())
        
        self.gridLayout_3.addWidget(self.DT_Line, 3, 1, 1, 1)
        
        self.NB_Label_2 = QLabel(self.Stator_Frame)
        self.NB_Label_2.setStyleSheet("font: bold;")
        self.NB_Label_2.setObjectName("NB_Label_2")
        
        self.gridLayout_3.addWidget(self.NB_Label_2, 3, 2, 1, 1)
        
        self.NB_Line_2 = QLineEdit(self.Stator_Frame)
        self.NB_Line_2.setAlignment(Qt.AlignCenter)
        self.NB_Line_2.setObjectName("Num of Blade (Stator)")
        self.NB_Line_2.setValidator(QIntValidator(1, 1000,  self.NB_Line_2))
        self.NB_Line_2.textChanged.connect(self.CheckState)
        self.NB_Line_2.textChanged.emit(self.NB_Line_2.text())
        
        self.gridLayout_3.addWidget(self.NB_Line_2, 3, 3, 1, 1)
        
        self.CL_Label = QLabel(self.Stator_Frame)
        self.CL_Label.setStyleSheet("font: bold;")
        self.CL_Label.setObjectName("CL_Label")
        
        self.gridLayout_3.addWidget(self.CL_Label, 4, 0, 1, 1)
        
        self.CL_Line = QLineEdit(self.Stator_Frame)
        self.CL_Line.setAlignment(Qt.AlignCenter)
        self.CL_Line.setObjectName("Mount Can Length")
        self.CL_Line.setValidator(QDoubleValidator(0.0, 1000.0, 3, self.CL_Line))
        self.CL_Line.textChanged.connect(self.CheckState)
        self.CL_Line.textChanged.emit(self.CL_Line.text())
        
        self.gridLayout_3.addWidget(self.CL_Line, 4, 1, 1, 1)
        
        self.CID_Label = QLabel(self.Stator_Frame)
        self.CID_Label.setStyleSheet("font: bold;")
        self.CID_Label.setObjectName("CID_Label")
        
        self.gridLayout_3.addWidget(self.CID_Label, 4, 2, 1, 1)
        
        self.CID_Line = QLineEdit(self.Stator_Frame)
        self.CID_Line.setAlignment(Qt.AlignCenter)
        self.CID_Line.setObjectName("Mount Can Dia")
        self.CID_Line.setValidator(QDoubleValidator(0.0, 1000.0, 3, self.CID_Line))
        self.CID_Line.textChanged.connect(self.CheckState)
        self.CID_Line.textChanged.emit(self.CID_Line.text())
        
        self.gridLayout_3.addWidget(self.CID_Line, 4, 3, 1, 1)
        
        self.XL_Label = QLabel(self.Stator_Frame)
        self.XL_Label.setStyleSheet("font: bold;")
        self.XL_Label.setObjectName("XL_Label")
        
        self.gridLayout_3.addWidget(self.XL_Label, 5, 0, 1, 1)
        
        self.XL_Line = QLineEdit(self.Stator_Frame)
        self.XL_Line.setAlignment(Qt.AlignCenter)
        self.XL_Line.setObjectName("Mount Can Loc")
        self.XL_Line.setValidator(QDoubleValidator(0.0, 1000.0, 3, self.XL_Line))
        self.XL_Line.textChanged.connect(self.CheckState)
        self.XL_Line.textChanged.emit(self.XL_Line.text())
        
        self.gridLayout_3.addWidget(self.XL_Line, 5, 1, 1, 1)
        
        self.BT_Label_2 = QLabel(self.Stator_Frame)
        self.BT_Label_2.setStyleSheet("font: bold;")
        self.BT_Label_2.setObjectName("BT_Label_2")
        
        self.gridLayout_3.addWidget(self.BT_Label_2, 5, 2, 1, 1)
        
        self.BT_Line_2 = QLineEdit(self.Stator_Frame)
        self.BT_Line_2.setAlignment(Qt.AlignCenter)
        self.BT_Line_2.setObjectName("Blade Thickness (Stator)")
        self.BT_Line_2.setValidator(QDoubleValidator(0.0, 100.0, 3, self.BT_Line_2))
        self.BT_Line_2.textChanged.connect(self.CheckState)
        self.BT_Line_2.textChanged.emit(self.BT_Line_2.text())
        
        self.gridLayout_3.addWidget(self.BT_Line_2, 5, 3, 1, 1)
        
        self.RC_Label_2 = QLabel(self.Stator_Frame)
        self.RC_Label_2.setStyleSheet("font: bold;")
        self.RC_Label_2.setObjectName("RC_Label_2")
        
        self.gridLayout_3.addWidget(self.RC_Label_2, 6, 0, 1, 1)
        
        self.RC_Line_2 = QLineEdit(self.Stator_Frame)
        self.RC_Line_2.setAlignment(Qt.AlignCenter)
        self.RC_Line_2.setObjectName("Root Chord (Stator)")
        self.RC_Line_2.setValidator(QDoubleValidator(0.0, 1000.0, 3, self.RC_Line_2))
        self.RC_Line_2.textChanged.connect(self.CheckState)
        self.RC_Line_2.textChanged.emit(self.RC_Line_2.text())
        
        self.gridLayout_3.addWidget(self.RC_Line_2, 6, 1, 1, 1)
        
        self.TC_Label_2 = QLabel(self.Stator_Frame)
        self.TC_Label_2.setStyleSheet("font: bold;")
        self.TC_Label_2.setObjectName("TC_Label_2")
        
        self.gridLayout_3.addWidget(self.TC_Label_2, 6, 2, 1, 1)
        
        self.TC_Line_2 = QLineEdit(self.Stator_Frame)
        self.TC_Line_2.setAlignment(Qt.AlignCenter)
        self.TC_Line_2.setObjectName("Tip Chord (Stator)")
        self.TC_Line_2.setValidator(QDoubleValidator(0.0, 1000.0, 3, self.TC_Line_2))
        self.TC_Line_2.textChanged.connect(self.CheckState)
        self.TC_Line_2.textChanged.emit(self.TC_Line_2.text())
        
        self.gridLayout_3.addWidget(self.TC_Line_2, 6, 3, 1, 1)
        
        self.XT_Label_2 = QLabel(self.Stator_Frame)
        self.XT_Label_2.setStyleSheet("font: bold;")
        self.XT_Label_2.setObjectName("XT_Label_2")
        
        self.gridLayout_3.addWidget(self.XT_Label_2, 7, 0, 1, 1)
        
        self.XT_Line_2 = QLineEdit(self.Stator_Frame)
        self.XT_Line_2.setAlignment(Qt.AlignCenter)
        self.XT_Line_2.setObjectName("X Twist (Stator)")
        self.XT_Line_2.setValidator(QDoubleValidator(0.0, 1000.0, 3, self.XT_Line_2))
        self.XT_Line_2.textChanged.connect(self.CheckState)
        self.XT_Line_2.textChanged.emit(self.XT_Line_2.text())
        
        self.gridLayout_3.addWidget(self.XT_Line_2, 7, 1, 1, 1)
        
        self.YT_Label_2 = QLabel(self.Stator_Frame)
        self.YT_Label_2.setStyleSheet("font: bold;")
        self.YT_Label_2.setObjectName("YT_Label_2")
        
        self.gridLayout_3.addWidget(self.YT_Label_2, 7, 2, 1, 1)
        
        self.YT_Line_2 = QLineEdit(self.Stator_Frame)
        self.YT_Line_2.setAlignment(Qt.AlignCenter)
        self.YT_Line_2.setObjectName("Y Twist (Stator)")
        self.YT_Line_2.setValidator(QDoubleValidator(0.0, 1000.0, 3, self.YT_Line_2))
        self.YT_Line_2.textChanged.connect(self.CheckState)
        self.YT_Line_2.textChanged.emit(self.YT_Line_2.text())
        
        self.gridLayout_3.addWidget(self.YT_Line_2, 7, 3, 1, 1)
        
        self.line_3 = QFrame(self.Stator_Frame)
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        
        self.gridLayout_3.addWidget(self.line_3, 1, 0, 1, 4)
        
        self.gridLayout.addWidget(self.Stator_Frame, 1, 2, 1, 1)
        
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        self.gridLayout.addItem(spacerItem1, 1, 1, 1, 1)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 805, 21))
        self.menubar.setObjectName("menubar")
        
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        
        MainWindow.setMenuBar(self.menubar)
        
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionOpen.setShortcut("Ctrl+O")
        self.actionOpen.setStatusTip("Open File")
        self.actionOpen.triggered.connect(self.OpenFile)
        
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave.setShortcut("Ctrl+S")
        self.actionSave.setStatusTip("Save File")
        self.actionSave.triggered.connect(self.SaveFile)
        
        # Recent files menu
        self.menuRecentFiles = QMenu(self.menuFile)
        self.menuRecentFiles.setObjectName("menuRecentFiles")
        
        # Clear recent files action (create before UpdateRecentFilesMenu)
        self.actionClearRecent = QAction(MainWindow)
        self.actionClearRecent.setObjectName("actionClearRecent")
        self.actionClearRecent.setStatusTip("Clear Recent Files")
        self.actionClearRecent.triggered.connect(self.ClearRecentFiles)
        
        # Now update the menu
        self.UpdateRecentFilesMenu()
        
        # Undo/Redo actions
        self.actionUndo = QAction(MainWindow)
        self.actionUndo.setObjectName("actionUndo")
        self.actionUndo.setShortcut("Ctrl+Z")
        self.actionUndo.setStatusTip("Undo")
        self.actionUndo.triggered.connect(self.Undo)
        self.actionUndo.setEnabled(False)
        
        self.actionRedo = QAction(MainWindow)
        self.actionRedo.setObjectName("actionRedo")
        self.actionRedo.setShortcut("Ctrl+Y")
        self.actionRedo.setStatusTip("Redo")
        self.actionRedo.triggered.connect(self.Redo)
        self.actionRedo.setEnabled(False)
        
        # Presets menu
        self.menuPresets = QMenu(self.menubar)
        self.menuPresets.setObjectName("menuPresets")
        
        # Tools menu
        self.menuTools = QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        
        # Assembly viewer action
        self.actionAssemblyView = QAction(MainWindow)
        self.actionAssemblyView.setObjectName("actionAssemblyView")
        self.actionAssemblyView.setStatusTip("View All Stages Together")
        self.actionAssemblyView.triggered.connect(self.ShowAssemblyView)
        
        self.actionToggleDarkMode = QAction(MainWindow)
        self.actionToggleDarkMode.setObjectName("actionToggleDarkMode")
        self.actionToggleDarkMode.setCheckable(True)
        self.actionToggleDarkMode.setChecked(True)
        self.actionToggleDarkMode.setStatusTip("Toggle Dark Mode")
        self.actionToggleDarkMode.triggered.connect(self.ToggleDarkMode)
        
        # View log file action
        self.actionViewLog = QAction(MainWindow)
        self.actionViewLog.setObjectName("actionViewLog")
        self.actionViewLog.setStatusTip("View Error Log File")
        self.actionViewLog.triggered.connect(self.ViewLogFile)

        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addSeparator()
        self.menuFile.addMenu(self.menuRecentFiles)
        self.menuRecentFiles.addAction(self.actionClearRecent)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionUndo)
        self.menuFile.addAction(self.actionRedo)
        
        # Add preset actions dynamically
        for preset_name in get_preset_names():
            action = QAction(preset_name, MainWindow)
            action.setStatusTip(get_preset_description(preset_name))
            action.triggered.connect(lambda checked, name=preset_name: self.LoadPreset(name))
            self.menuPresets.addAction(action)
        
        self.menuTools.addAction(self.actionAssemblyView)
        self.menuTools.addSeparator()
        self.menuTools.addAction(self.actionViewLog)
        self.menuView.addAction(self.actionToggleDarkMode)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuPresets.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuView.menuAction())

        #Set Tab Order
        MainWindow.setTabOrder(self.R_Line, self.PSI_Line)
        MainWindow.setTabOrder(self.PSI_Line, self.PHI_Line)
        MainWindow.setTabOrder(self.PHI_Line, self.MLR_Line)
        MainWindow.setTabOrder(self.MLR_Line, self.RPM_Line)
        MainWindow.setTabOrder(self.RPM_Line, self.RD_Line)
        MainWindow.setTabOrder(self.RD_Line, self.HD_Line)
        MainWindow.setTabOrder(self.HD_Line, self.HL_Line)
        MainWindow.setTabOrder(self.HL_Line, self.NB_Line)
        MainWindow.setTabOrder(self.NB_Line, self.RC_Line)
        MainWindow.setTabOrder(self.RC_Line, self.TC_Line)
        MainWindow.setTabOrder(self.TC_Line, self.BT_Line)
        MainWindow.setTabOrder(self.BT_Line, self.BC_Line)
        MainWindow.setTabOrder(self.BC_Line, self.XT_Line)
        MainWindow.setTabOrder(self.XT_Line, self.YT_Line)
        MainWindow.setTabOrder(self.YT_Line, self.DL_Line)
        MainWindow.setTabOrder(self.DL_Line, self.DI_Line)
        MainWindow.setTabOrder(self.DI_Line, self.DT_Line)
        MainWindow.setTabOrder(self.DT_Line, self.NB_Line_2)
        MainWindow.setTabOrder(self.NB_Line_2, self.CL_Line)
        MainWindow.setTabOrder(self.CL_Line, self.CID_Line)
        MainWindow.setTabOrder(self.CID_Line, self.XL_Line)
        MainWindow.setTabOrder(self.XL_Line, self.BT_Line_2)
        MainWindow.setTabOrder(self.BT_Line_2, self.RC_Line_2)
        MainWindow.setTabOrder(self.RC_Line_2, self.TC_Line_2)
        MainWindow.setTabOrder(self.TC_Line_2, self.XT_Line_2)
        MainWindow.setTabOrder(self.XT_Line_2, self.YT_Line_2)
        
        self.retranslateUi(MainWindow)
        
        # Add tooltips to all input fields
        self.AddTooltips()
        
        # Enable drag and drop for stage list
        self.listWidget.setDragDropMode(QAbstractItemView.InternalMove)
        self.listWidget.model().rowsMoved.connect(self.OnStagesReordered)
        
        QMetaObject.connectSlotsByName(MainWindow)


    ################################
    ##Function: retranslateUi
    #Sets the text of all the labels
    ##Inputs: 
    #self: Ui_MainWindow
    #MainWindow: MainWindow
    ##Returns:
    #none
    ################################   
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("CompPy - Compressor Design")
        self.YT_Label.setText("Center of Y Twist")
        self.wallCheck.setText("Support Wall")
        self.RDia_Label.setText("Rotor Diameter")
        self.BT_Label.setText("Blade Thickness")
        self.R_Title.setText("Rotor Specifications")
        self.NB_Label.setText("Num of Blades")
        self.RC_Label.setText("Root Chord")
        self.HDia_Label.setText("Hub Diameter")
        self.TC_Label.setText("Tip Chord")
        self.HL_Label.setText("Hub Length")
        self.BC_Label.setText("Blade Clearance")
        self.XT_Label.setText("Center of X Twist")
        self.R_Label.setText("Reaction (R)")
        self.PSI_Label.setText("Loading (PSI)")
        self.PHI_Label.setText("Flow (PHI)")
        self.Title.setText("Universal Coefficients")
        self.MLR_Label.setText("Mean Line Radius")
        self.RPM_Label.setText("RPM")
        self.renderExport.setText("Export STL")
        self.removeButton.setText("Remove Stage")
        self.addButton.setText("Add Stage")
        self.profileButton.setText("Draw Blade Profile")
        self.renderButton.setText("Render STL")
        self.DI_Label.setText("Duct ID")
        self.S_Title.setText("Stator Specifications")
        self.DT_Label.setText("Duct Thickness")
        self.DL_Label.setText("Duct Length")
        self.NB_Label_2.setText("Num of Blades")
        self.CL_Label.setText("Mount Can Length")
        self.CID_Label.setText("Mount Can Dia")
        self.XL_Label.setText("Mount Can Loc")
        self.BT_Label_2.setText("Blade Thickness")
        self.RC_Label_2.setText("Root Chord")
        self.TC_Label_2.setText("Tip Chord")
        self.XT_Label_2.setText("Center of X Twist")
        self.YT_Label_2.setText("Center of Y Twist")
        self.menuFile.setTitle("File")
        self.menuRecentFiles.setTitle("Recent Files")
        self.menuPresets.setTitle("Presets")
        self.menuTools.setTitle("Tools")
        self.menuView.setTitle("View")
        self.actionOpen.setText("Open")
        self.actionSave.setText("Save")
        self.actionClearRecent.setText("Clear Recent Files")
        self.actionUndo.setText("Undo")
        self.actionRedo.setText("Redo")
        self.actionAssemblyView.setText("Assembly Viewer")
        self.actionViewLog.setText("View Error Log")
        self.actionToggleDarkMode.setText("Dark Mode")
        
        # Apply dark mode theme on startup
        self.ApplyTheme()
        
    ################################
    ##Function: OpenFile
    #Opens compressor profile from .json file
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################   
    def OpenFile(self):
        #Open open file dialog window
        name = QFileDialog.getOpenFileName(self.MainWindow, "Open File",  None, 'Json files (*.json)')
        
        logger.info("Opening file dialog")
        
        # Check if user cancelled
        if not name[0]:
            logger.debug("User cancelled file open")
            return
        filename = name[0]
        
        logger.info(f"Opening file: {filename}")
        
        #Clear the list of anything
        self.listWidget.clear()
        try:
            #Set dictionaries with incoming vars
            self.commonVars, self.rotorVars, self.statorVars = map(list, zip(*list(StageOpen(filename))))
            
            #Add the stages
            for i in range(1, len(self.commonVars) + 1):
                self.listWidget.addItem("Stage {}".format(i))
            
            # Mark file as open and select first stage
            self.fileOpen = True
            self.clicked = 0
            
            # Populate UI fields with first stage data
            if self.commonVars and self.rotorVars and self.statorVars:
                for dict in [self.commonVars[0], self.rotorVars[0], self.statorVars[0]]:
                    for obj in dict:
                        widget = self.MainWindow.findChild(QLineEdit, obj)
                        if widget:
                            widget.setText(str(dict[obj]))
                        else:
                            logger.debug("OpenFile: QLineEdit '%s' not found, skipping", obj)
                
                # Select first item in list
                self.listWidget.setCurrentRow(0)
                
                # Add to recent files
                self.recent_files_manager.add_file(filename)
                self.UpdateRecentFilesMenu()
                logger.info(f"Successfully opened file: {filename}")
                
                # Show success message
                box = QMessageBox(self.MainWindow)
                box.setText("File Loaded Successfully")
                box.setInformativeText(f"Loaded {len(self.commonVars)} stage(s) from file.")
                box.setWindowTitle("Load Success")
                box.setIcon(QMessageBox.Information)
                box.exec_()
            
        except EOFError: 
            logger.error("Invalid file format (EOFError)")
            box = QMessageBox(self.MainWindow)
            box.setText("Invalid File Format")
            box.setInformativeText("Confirm file is a valid CompPy JSON file.")
            box.setWindowTitle("Load Error")
            box.setIcon(QMessageBox.Critical)
            box.exec_()
        except Exception as e:
            logger.error(f"Error loading file: {e}", exc_info=True)
            box = QMessageBox(self.MainWindow)
            box.setText("Error Loading File")
            box.setInformativeText(f"An error occurred: {str(e)}")
            box.setWindowTitle("Load Error")
            box.setIcon(QMessageBox.Critical)
            box.exec_()
            
            
    ################################
    ##Function: SaveFile
    #Saves compressor profile to .json file
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################       
    def SaveFile(self):
        # Check if we have any stages to save
        if not self.commonVars or not self.rotorVars or not self.statorVars:
            box = QMessageBox(self.MainWindow)
            box.setText("No Stages to Save")
            box.setInformativeText("Please add a stage first using 'Add Stage' button.")
            box.setWindowTitle("Save Error")
            box.exec_()
            return
        
        # Ensure we have a valid clicked index
        if self.clicked is None or self.clicked >= len(self.commonVars):
            self.clicked = 0
        
        #Open save file dialog window
        name = QFileDialog.getSaveFileName(self.MainWindow, "Save File", None, 'Json files (*.json)')
        
        # Check if user cancelled
        if not name[0]:
            return
        name = name[0]
        
        #Make sure the current stage is saved to the dictionaries
        for dict in [self.commonVars[self.clicked], self.rotorVars[self.clicked], self.statorVars[self.clicked]]:
            for item in dict:
                widget = self.MainWindow.findChild(QLineEdit, item)
                if widget:
                    text = widget.text()
                    if text:
                        dict[item] = text
        
        #Save dictionaries to .json file
        if not name.lower().endswith('.json'):
            name += '.json'
        
        try:
            StageSave(name, self.commonVars, self.rotorVars, self.statorVars)
            
            # Add to recent files
            self.recent_files_manager.add_file(name)
            self.UpdateRecentFilesMenu()
            logger.info(f"Successfully saved file: {name}")
            
            # Show success message
            box = QMessageBox(self.MainWindow)
            box.setText("File Saved Successfully")
            box.setInformativeText(f"Saved {len(self.commonVars)} stage(s) to:\n{name}")
            box.setWindowTitle("Save Success")
            box.setIcon(QMessageBox.Information)
            box.exec_()
            
        except Exception as e:
            logger.error(f"Error saving file: {e}", exc_info=True)
            box = QMessageBox(self.MainWindow)
            box.setText("Error Saving File")
            box.setInformativeText(f"An error occurred: {str(e)}")
            box.setWindowTitle("Save Error")
            box.setIcon(QMessageBox.Critical)
            box.exec_()
    
    
    ################################
    ##Function: OnStagesReordered
    #Handle drag-and-drop reordering of stages
    ################################   
    def OnStagesReordered(self, parent, start, end, destination, row):
        # Qt has already reordered the list widget items
        # We need to reorder our data structures to match
        if not self.commonVars or len(self.commonVars) <= 1:
            return
        try:
            # The moved items are from start to end
            # Reorder all three lists
            moved_common = self.commonVars[start:end + 1]
            moved_rotor = self.rotorVars[start:end + 1]
            moved_stator = self.statorVars[start:end + 1]
            
            # Remove from old positions
            del self.commonVars[start:end + 1]
            del self.rotorVars[start:end + 1]
            del self.statorVars[start:end + 1]
            
            # Adjust destination index if moving down
            dest = row if row < start else row - len(moved_common)
            if dest < 0:
                dest = 0
            if dest > len(self.commonVars):
                dest = len(self.commonVars)
            
            # Insert at new position
            for i, item in enumerate(moved_common):
                self.commonVars.insert(dest + i, item)
            for i, item in enumerate(moved_rotor):
                self.rotorVars.insert(dest + i, item)
            for i, item in enumerate(moved_stator):
                self.statorVars.insert(dest + i, item)
            
            # Renumber items
            for i in range(self.listWidget.count()):
                self.listWidget.item(i).setText("Stage {}".format(i + 1))
        except Exception:
            pass

    ################################
    ##Function: RemoveStage
    #Removes selected stage from list and profiles
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################   
    def RemoveStage(self):
        # Use row position as the stage index (robust to renames/reordering).
        row = self.listWidget.currentRow()
        if row < 0 or row >= len(self.rotorVars):
            return

        del self.rotorVars[row]
        del self.commonVars[row]
        del self.statorVars[row]

        self.listWidget.takeItem(row)

        # Renumber so list labels always match data positions.
        for i in range(self.listWidget.count()):
            self.listWidget.item(i).setText("Stage {}".format(i + 1))

        # Keep selection valid.
        if self.listWidget.count():
            self.clicked = min(row, self.listWidget.count() - 1)
            self.listWidget.setCurrentRow(self.clicked)
        else:
            self.clicked = None
                     
                     
    ################################
    ##Function: AddStage
    #Adds next stage to list and profiles
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################   
    def AddStage(self):
        try:
            logger.debug("Adding new stage")
            # Get default parameters
            defaults = get_default_parameters()
            
            #Add stage list item
            self.listWidget.addItem("Stage {}".format(self.listWidget.count() + 1))

            #Add new stage vars with defaults
            self.rotorVars.append(defaults['Rotor'].copy())
            self.statorVars.append(defaults['Stator'].copy())
            self.commonVars.append(defaults['Stage'].copy())
            
            logger.info(f"Added stage {len(self.commonVars)} with default parameters")
            
        except Exception as e:
            logger.error(f"Error adding stage: {e}", exc_info=True)
        
        
    ################################
    ##Function: ListClicked
    #Loads currently selected stage profile
    #while saving the previously selected profile
    ##Inputs: 
    #self: Ui_MainWindow
    #clicked: currently selected stage
    ##Returns:
    #none
    ################################   
    def ListClicked(self, clicked):
        #Check if we have any stages
        if not self.commonVars or not self.rotorVars or not self.statorVars:
            return

        #Making sure there's no overlap (clicked==0 is valid; do not use truthiness)
        if not (self.clicked is not None and 0 <= self.clicked < self.listWidget.count()):
            self.clicked = 0
        
        #Ensure clicked index is valid
        if self.clicked >= len(self.commonVars):
            self.clicked = 0
        
        #Set current value of qLineEdit to corresponding dict value,
        #of previously selected stage, if there is a value to change
        for dict in [self.commonVars[self.clicked], self.rotorVars[self.clicked], self.statorVars[self.clicked]]:
            for item in dict:
                widget = self.MainWindow.findChild(QLineEdit, item)
                if widget:
                    text = widget.text()
                    if text:
                        dict[item] = text
                else:
                    logger.debug("ListClicked: QLineEdit '%s' not found, skipping save", item)

        #Set currently selected stage
        try:
            self.clicked = int(clicked.text().split()[-1]) - 1
        except (ValueError, IndexError):
            self.clicked = 0
        
        #Ensure new clicked index is valid
        if self.clicked >= len(self.commonVars):
            self.clicked = 0
        
        #Set each value in list of current stage to their corresponding qLineEdit
        for dict in [self.commonVars, self.rotorVars, self.statorVars]:
            for obj in dict[self.clicked]:
                widget = self.MainWindow.findChild(QLineEdit, obj)
                if widget:
                    widget.setText(str(dict[self.clicked][obj]))
                else:
                    logger.debug("ListClicked: QLineEdit '%s' not found, skipping load", obj)


    ################################
    ##Function: Export
    #If object rendered, exports to .stl file
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################   
    def Export(self):       
        #If object was previously generated
        if self.exportObj:
            name = QFileDialog.getSaveFileName(self.MainWindow, 'Save File', None, 'STL files (*.stl)')
            
            # Check if user cancelled
            if version == 5:
                if not name[0]:
                    return
                filename = name[0]
            else:
                if not name:
                    return
                filename = name
            
            # Add .stl extension if not present
            if not filename.lower().endswith('.stl'):
                filename += '.stl'
            
            try:
                self.exportObj.save(filename)
                
                # Show success message
                box = QMessageBox(self.MainWindow)
                box.setText("STL Exported Successfully")
                box.setInformativeText(f"Saved to:\n{filename}")
                box.setWindowTitle("Export Success")
                box.setIcon(QMessageBox.Information)
                box.exec_()
                
            except Exception as e:
                box = QMessageBox(self.MainWindow)
                box.setText("Error Exporting STL")
                box.setInformativeText(f"An error occurred: {str(e)}")
                box.setWindowTitle("Export Error")
                box.setIcon(QMessageBox.Critical)
                box.exec_()
                
        #If there was no rendered object, display error window
        else:
            box = QMessageBox(self.MainWindow)
            box.setText("Nothing to Export")
            box.setInformativeText("Please render an STL object first using 'Render STL' button.")
            box.setWindowTitle("Export Error")
            box.setIcon(QMessageBox.Warning)
            box.exec_()
                                
    
    ################################
    ##Function: CheckState
    #Determines validity of currently editing qLineEdit
    #Green for acceptable
    #Yellow / Red are unacceptable
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################       
    def CheckState(self):
        sender = self.MainWindow.sender()
        if sender is None or not isinstance(sender, QLineEdit):
            return
        validator = sender.validator()
        if validator is None:
            return
        state = validator.validate(sender.text(), 0)[0]
        
        #Check every line
        for dict in [self.commonValidators, self.rotorValidators, self.statorValidators]:
            if sender.objectName() in dict:
                dict[sender.objectName()] = state
            else: continue
        
        field_name = sender.objectName()
        base_tooltip = get_tooltip(field_name)
        
        #Set color of qLineEdit box (theme-aware) and tooltip with validation feedback
        if state == QValidator.Acceptable:
            bgcolor = "#00cc44" if self.darkMode else "#009933" # green
            sender.setToolTip(base_tooltip)  # Show normal tooltip
        elif state == QValidator.Intermediate:
            bgcolor = "#cccc00" if self.darkMode else "#ffff00" # yellow
            valid_range = self.validRanges.get(field_name, "see documentation")
            hint = f"{base_tooltip}\n\n⚠ Value incomplete or out of range\nValid: {valid_range}"
            sender.setToolTip(hint)
        else:
            bgcolor = "#ff3333" if self.darkMode else "#ff0000" # red
            valid_range = self.validRanges.get(field_name, "see documentation")
            error_msg = f"{base_tooltip}\n\n❌ Invalid value!\nValid: {valid_range}"
            sender.setToolTip(error_msg)
            
        sender.setStyleSheet("QLineEdit { background-color: %s; color: #000000; }" % bgcolor)
        
    ################################
    ##Function: CheckAllStates
    #If object to be rendered or plotted each
    #qLineEdit object needs to be acceptably valid
    ##Inputs: 
    #self: Ui_MainWindow
    #obj: "R" or "S"
    ##Returns:
    #none
    ################################   
    def CheckAllStates(self, obj):

        if obj == "R": to_check = [self.commonValidators, self.rotorValidators]
        else: to_check = [self.commonValidators, self.statorValidators]

        #Check all values in validators dict
        #If one was not acceptable, append it to failure list with valid range suggestion
        for dict in to_check:
            if all(val == QValidator.Acceptable for val in dict.values()):
                continue
            for item in dict:
                if dict[item] != QValidator.Acceptable:
                    # Add tuple with field name and valid range
                    valid_range = self.validRanges.get(item, "see documentation")
                    self.failed.append((item, valid_range))

        
    ################################
    ##Function: PlotProfile
    #Plots blade profile for selected object if all valid
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################   
    def PlotProfile(self):
        from RClickWin import RenderSel, ErrorWindow
        
        # Check if we have any stages
        if not self.commonVars or not self.rotorVars or not self.statorVars:
            box = QMessageBox(self.MainWindow)
            box.setText("No Stages Available")
            box.setInformativeText("Please add a stage first using 'Add Stage' button.")
            box.setWindowTitle("Plot Profile Error")
            box.exec_()
            return
        
        # Ensure we have a valid clicked index
        if self.clicked is None or self.clicked >= len(self.commonVars):
            self.clicked = 0
        
        #Delete Currently Occupating Widget
        for i in reversed(range(self.R_FrameLayout.count())): 
            widget = self.R_FrameLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        #Make sure the current stage is saved to the dictionaries
        for dict in [self.commonVars[self.clicked], self.rotorVars[self.clicked], self.statorVars[self.clicked]]:
            for item in dict:
                widget = self.MainWindow.findChild(QLineEdit, item)
                if widget:
                    text = widget.text()
                    if text:
                        dict[item] = text
        
        wind = RenderSel(self.MainWindow)
        wind.show()
        
        if wind.exec_():
            if wind.sel == 1: 
                self.CheckAllStates("R")
                
                #If there was no failure
                if not self.failed: 
                    prof = BladePlot.NACA4Profile(self.MainWindow, self.commonVars[self.clicked], self.rotorVars[self.clicked], "R")
                    self.R_FrameLayout.addWidget(prof)
                    prof.plotter()
                    self.R_Frame.setLayout(self.R_FrameLayout)
                    prof.close()
                    
                #If there was a failure, show the failures
                else: ErrorWindow(self.MainWindow, self.failed).show()
                    
            #If stator was picked
            elif wind.sel == 2: 
                self.CheckAllStates("S")
                
                #If there was no failure
                if not self.failed: 
                    prof = BladePlot.NACA4Profile(self.MainWindow, self.commonVars[self.clicked], self.statorVars[self.clicked], "S")
                    self.R_FrameLayout.addWidget(prof)
                    prof.plotter()
                    self.R_Frame.setLayout(self.R_FrameLayout)
                    prof.close()
                
                #If there was a failure, show the failures
                else: ErrorWindow(self.MainWindow, self.failed).show()
            
            else: pass
            
        #Reset failed list
        self.failed = []
        

    ################################
    ##Function: Render
    #3D renders selected object if all valid
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################   
    def Render(self):
        from RClickWin import RenderSel, ErrorWindow
        
        # Check if we have any stages
        if not self.commonVars or not self.rotorVars or not self.statorVars:
            box = QMessageBox(self.MainWindow)
            box.setText("No Stages Available")
            box.setInformativeText("Please add a stage first using 'Add Stage' button.")
            box.setWindowTitle("Render Error")
            box.exec_()
            return
        
        # Ensure we have a valid clicked index
        if self.clicked is None or self.clicked >= len(self.commonVars):
            self.clicked = 0
        
        #Delete Currently Occupating Widget
        for i in reversed(range(self.R_FrameLayout.count())): 
            widget = self.R_FrameLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        #Make sure the current stage is saved to the dictionaries
        for dict in [self.commonVars[self.clicked], self.rotorVars[self.clicked], self.statorVars[self.clicked]]:
            for item in dict:
                widget = self.MainWindow.findChild(QLineEdit, item)
                if widget:
                    text = widget.text()
                    if text:
                        dict[item] = text
                     
        #Display selection window
        wind = RenderSel(self.MainWindow)
        wind.show()
        
        #Once window is closed
        if wind.exec_():
            #If rotor was picked
            if wind.sel == 1: 
                self.CheckAllStates("R")
                
                #If there was no failure
                if not self.failed:
                    # Clear existing widgets to prevent memory leaks
                    if hasattr(self, 'R_FrameLayout'):
                        for i in reversed(range(self.R_FrameLayout.count())):
                            widget = self.R_FrameLayout.itemAt(i).widget()
                            if widget:
                                widget.setParent(None)
                                widget.deleteLater()
                    # Create progress dialog
                    progress = QProgressDialog("Generating rotor mesh...", None, 0, 0, self.MainWindow)
                    progress.setWindowTitle("Rendering Rotor")
                    progress.setWindowModality(Qt.WindowModal)
                    progress.show()
                    QApplication.processEvents()
                    
                    logger.info("Rendering rotor")
                    rend = RenderWindow.RenderWindow(self.MainWindow, self.commonVars[self.clicked], self.rotorVars[self.clicked], "R", self.wallCheck.isChecked())
                    self.R_FrameLayout.addWidget(rend)
                    self.R_Frame.setLayout(self.R_FrameLayout)
                    self.exportObj = rend.returnObject()
                    
                    progress.close()
                    logger.info("Rotor rendered successfully")
                    
                #If there was a failure, show the failures
                else: ErrorWindow(self.MainWindow, self.failed).show()
            
            #If stator was picked
            elif wind.sel == 2: 
                self.CheckAllStates("S")
                
                #If there was no failure
                if not self.failed: 
                    # Clear existing widgets to prevent memory leaks
                    if hasattr(self, 'R_FrameLayout'):
                        for i in reversed(range(self.R_FrameLayout.count())):
                            widget = self.R_FrameLayout.itemAt(i).widget()
                            if widget:
                                widget.setParent(None)
                                widget.deleteLater()
                    rend = RenderWindow.RenderWindow(self.MainWindow, self.commonVars[self.clicked], self.statorVars[self.clicked], "S")
                    self.R_FrameLayout.addWidget(rend)
                    self.R_Frame.setLayout(self.R_FrameLayout)
                    self.exportObj = rend.returnObject()
                
                #If there was a failure, show the failures
                else: ErrorWindow(self.MainWindow, self.failed).show()
            
            else: pass
  
        #Reset failed list
        self.failed = []
                                
    
    ################################
    ##Function: ToggleDarkMode
    #Toggles between light and dark mode
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################   
    def ToggleDarkMode(self):
        self.darkMode = not self.darkMode
        self._save_theme_preference()
        self.ApplyTheme()
    
    def _get_settings_path(self):
        settings_dir = os.path.expanduser('~/.config/comppy')
        try:
            os.makedirs(settings_dir, exist_ok=True)
        except Exception:
            pass
        return os.path.join(settings_dir, 'settings.json')
    
    def _load_theme_preference(self):
        try:
            path = self._get_settings_path()
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                if isinstance(settings, dict) and 'darkMode' in settings:
                    self.darkMode = bool(settings['darkMode'])
        except Exception:
            self.darkMode = True
    
    def _save_theme_preference(self):
        try:
            path = self._get_settings_path()
            settings = {'darkMode': bool(self.darkMode)}
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(settings, f)
        except Exception:
            pass
    
    
    ################################
    ##Function: ApplyTheme
    #Applies the current theme (light or dark)
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################   
    def ApplyTheme(self):
        if self.darkMode:
            # Dark mode palette
            darkPalette = """
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                }
                QFrame {
                    background-color: #323232;
                    border: 1px solid #3f3f3f;
                }
                QLabel {
                    color: #e0e0e0;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #555555;
                    padding: 2px;
                }
                QLineEdit:focus {
                    border: 1px solid #0078d4;
                }
                QPushButton {
                    background-color: #404040;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                    padding: 5px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                    border: 1px solid #666666;
                }
                QPushButton:pressed {
                    background-color: #353535;
                }
                QListWidget {
                    background-color: #404040;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                }
                QListWidget::item:selected {
                    background-color: #0078d4;
                }
                QListWidget::item:hover {
                    background-color: #4a4a4a;
                }
                QMenuBar {
                    background-color: #323232;
                    color: #e0e0e0;
                }
                QMenuBar::item:selected {
                    background-color: #404040;
                }
                QMenu {
                    background-color: #323232;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                }
                QMenu::item:selected {
                    background-color: #0078d4;
                }
                QCheckBox {
                    color: #e0e0e0;
                }
            """
            self.MainWindow.setStyleSheet(darkPalette)
        else:
            # Light mode (default Qt style)
            self.MainWindow.setStyleSheet("")
        
        # Reapply validation colors for line edits
        for dict in [self.commonValidators, self.rotorValidators, self.statorValidators]:
            for name, state in dict.items():
                if state is not None:
                    widget = self.MainWindow.findChild(QLineEdit, name)
                    if widget:
                        if state == QValidator.Acceptable:
                            bgcolor = "#009933" if not self.darkMode else "#00cc44"
                        elif state == QValidator.Intermediate:
                            bgcolor = "#ffff00" if not self.darkMode else "#cccc00"
                        else:
                            bgcolor = "#ff0000" if not self.darkMode else "#ff3333"
                        widget.setStyleSheet("QLineEdit { background-color: %s; color: #000000; }" % bgcolor)
    
    ################################
    ##Function: AddTooltips
    #Add tooltips to all input fields
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################
    def AddTooltips(self):
        """Add tooltips to all input fields and connect undo tracking.

        Undo is tracked on editingFinished (one entry per field commit),
        not textChanged (which would flood the stack per keystroke).
        """
        all_fields = list(self.commonValidators.keys()) + \
                     list(self.rotorValidators.keys()) + \
                     list(self.statorValidators.keys())

        for field_name in all_fields:
            widget = self.MainWindow.findChild(QLineEdit, field_name)
            if widget:
                # Add tooltip
                tooltip = get_tooltip(field_name)
                if tooltip:
                    # Don't clobber live validation tooltips set by CheckState.
                    if not widget.toolTip():
                        widget.setToolTip(tooltip)

                # Connect undo tracking once.
                try:
                    widget.editingFinished.disconnect(self.TrackUndo)
                except (TypeError, RuntimeError):
                    pass
                widget.editingFinished.connect(self.TrackUndo)

                # Initialize field previous values
                self.field_previous_values[field_name] = widget.text()
    
    ################################
    ##Function: TrackUndo
    #Track changes for undo/redo functionality
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################
    def TrackUndo(self):
        """Track field changes for undo (called on editingFinished)."""
        sender = self.MainWindow.sender()
        if sender is None or not isinstance(sender, QLineEdit):
            return

        field_name = sender.objectName()
        if not field_name:
            return

        new_value = sender.text()

        # Get previous value
        old_value = self.field_previous_values.get(field_name, "")

        # Only track committed changes (skip initial population).
        if field_name in self.field_previous_values and old_value != new_value:
            state = {
                'stage_idx': self.clicked if self.clicked is not None else 0,
                'field_name': field_name,
                'old_value': old_value,
                'new_value': new_value
            }
            self.undo_manager.push_state(state)

            # Update undo/redo button states
            self.actionUndo.setEnabled(self.undo_manager.can_undo())
            self.actionRedo.setEnabled(self.undo_manager.can_redo())

        # Store current value as previous
        self.field_previous_values[field_name] = new_value
    
    ################################
    ##Function: Undo
    #Undo last change
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################
    def Undo(self):
        """Undo last parameter change"""
        state = self.undo_manager.undo()
        if state:
            # Restore old value
            widget = self.MainWindow.findChild(QLineEdit, state['field_name'])
            if widget:
                # Block signals to avoid creating new undo state
                widget.blockSignals(True)
                try:
                    widget.setText(state['old_value'])
                finally:
                    widget.blockSignals(False)
                self.field_previous_values[state['field_name']] = state['old_value']

            # Update button states
            self.actionUndo.setEnabled(self.undo_manager.can_undo())
            self.actionRedo.setEnabled(self.undo_manager.can_redo())
    
    ################################
    ##Function: Redo
    #Redo last undone change
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################
    def Redo(self):
        """Redo last undone change"""
        state = self.undo_manager.redo()
        if state:
            # Restore new value
            widget = self.MainWindow.findChild(QLineEdit, state['field_name'])
            if widget:
                # Block signals to avoid creating new undo state
                widget.blockSignals(True)
                try:
                    widget.setText(state['new_value'])
                finally:
                    widget.blockSignals(False)
                self.field_previous_values[state['field_name']] = state['new_value']

            # Update button states
            self.actionUndo.setEnabled(self.undo_manager.can_undo())
            self.actionRedo.setEnabled(self.undo_manager.can_redo())
    
    ################################
    ##Function: LoadPreset
    #Load a preset configuration
    ##Inputs: 
    #self: Ui_MainWindow
    #preset_name: name of preset to load
    ##Returns:
    #none
    ################################
    def LoadPreset(self, preset_name):
        """Load a preset configuration"""
        preset = get_preset(preset_name)
        if not preset:
            return
        
        # Ask user for confirmation
        reply = QMessageBox.question(
            self.MainWindow,
            'Load Preset',
            f'Load preset "{preset_name}"?\n\n{get_preset_description(preset_name)}\n\nThis will replace current stage values.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Ensure we have at least one stage
        if not self.commonVars:
            self.AddStage()
        
        # Get current stage index
        stage_idx = self.clicked if self.clicked is not None else 0
        
        # Load preset values into current stage
        if 'Stage' in preset:
            for field_name, value in preset['Stage'].items():
                self.commonVars[stage_idx][field_name] = value
                widget = self.MainWindow.findChild(QLineEdit, field_name)
                if widget:
                    widget.setText(value)
        
        if 'Rotor' in preset:
            for field_name, value in preset['Rotor'].items():
                self.rotorVars[stage_idx][field_name] = value
                widget = self.MainWindow.findChild(QLineEdit, field_name)
                if widget:
                    widget.setText(value)
        
        if 'Stator' in preset:
            for field_name, value in preset['Stator'].items():
                self.statorVars[stage_idx][field_name] = value
                widget = self.MainWindow.findChild(QLineEdit, field_name)
                if widget:
                    widget.setText(value)
        
        # Clear undo history after loading preset
        self.undo_manager.clear()
        self.actionUndo.setEnabled(False)
        self.actionRedo.setEnabled(False)
    
    ################################
    ##Function: ShowAssemblyView
    #Show 3D assembly viewer with all stages
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################
    def ShowAssemblyView(self):
        """Show assembly viewer with all stages"""
        if not self.commonVars or len(self.commonVars) == 0:
            QMessageBox.warning(
                self.MainWindow,
                "No Stages",
                "Please add at least one stage before viewing assembly."
            )
            return
        
        # Prepare stages data
        stages_data = []
        for i in range(len(self.commonVars)):
            stages_data.append({
                'common': self.commonVars[i],
                'rotor': self.rotorVars[i],
                'stator': self.statorVars[i],
                'stage_num': i + 1
            })
        
        # Create and show assembly viewer window
        try:
            self.assembly_window = QDialog(self.MainWindow)
            self.assembly_window.setWindowTitle("Assembly Viewer")
            self.assembly_window.resize(1000, 800)
            
            layout = QVBoxLayout()
            viewer = AssemblyViewer(self.assembly_window, stages_data)
            layout.addWidget(viewer)
            
            self.assembly_window.setLayout(layout)
            self.assembly_window.show()
        except Exception as e:
            QMessageBox.critical(
                self.MainWindow,
                "Assembly Viewer Error",
                f"Could not create assembly viewer:\n{str(e)}"
            )
    
    ################################
    ##Function: UpdateRecentFilesMenu
    #Update recent files menu with current list
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################
    def UpdateRecentFilesMenu(self):
        """Update recent files menu"""
        # Clear existing actions (except Clear Recent Files)
        self.menuRecentFiles.clear()
        
        # Get recent files
        recent_files = self.recent_files_manager.get_recent_files()
        
        # Add recent files
        for filepath in recent_files:
            # Create action with just filename
            filename = os.path.basename(filepath)
            action = QAction(filename, self.MainWindow)
            action.setStatusTip(filepath)
            action.setData(filepath)
            action.triggered.connect(lambda checked, path=filepath: self.OpenRecentFile(path))
            self.menuRecentFiles.addAction(action)
        
        # Add separator if we have recent files
        if recent_files:
            self.menuRecentFiles.addSeparator()
        
        # Add clear action
        self.menuRecentFiles.addAction(self.actionClearRecent)
        
        # Disable menu if no recent files
        self.menuRecentFiles.setEnabled(len(recent_files) > 0 or True)  # Always enable for Clear option
    
    ################################
    ##Function: OpenRecentFile
    #Open a recent file
    ##Inputs: 
    #self: Ui_MainWindow
    #filepath: path to file
    ##Returns:
    #none
    ################################
    def OpenRecentFile(self, filepath):
        """Open a recent file"""
        try:
            logger.info(f"Opening recent file: {filepath}")
            
            # Check if file exists
            if not os.path.exists(filepath):
                QMessageBox.warning(
                    self.MainWindow,
                    "File Not Found",
                    f"File no longer exists:\n{filepath}"
                )
                # Remove from recent files
                self.recent_files_manager.remove_file(filepath)
                self.UpdateRecentFilesMenu()
                return
            
            # Clear the list
            self.listWidget.clear()
            
            # Load the file
            self.commonVars, self.rotorVars, self.statorVars = map(list, zip(*list(StageOpen(filepath))))
            
            # Add stages to list
            for i in range(1, len(self.commonVars) + 1):
                self.listWidget.addItem(f"Stage {i}")
            
            # Mark file as open
            self.fileOpen = True
            self.clicked = 0
            
            # Populate UI with first stage
            if self.commonVars and self.rotorVars and self.statorVars:
                for dict in [self.commonVars[0], self.rotorVars[0], self.statorVars[0]]:
                    for obj in dict:
                        widget = self.MainWindow.findChild(QLineEdit, obj)
                        if widget:
                            widget.setText(str(dict[obj]))
                
                self.listWidget.setCurrentRow(0)
            
            logger.info(f"Successfully opened recent file: {filepath}")
            
        except Exception as e:
            logger.error(f"Error opening recent file: {e}", exc_info=True)
            QMessageBox.critical(
                self.MainWindow,
                "Error Opening File",
                f"Could not open file:\n{str(e)}"
            )
    
    ################################
    ##Function: ClearRecentFiles
    #Clear recent files list
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################
    def ClearRecentFiles(self):
        """Clear recent files list"""
        reply = QMessageBox.question(
            self.MainWindow,
            'Clear Recent Files',
            'Clear all recent files from the menu?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.recent_files_manager.clear()
            self.UpdateRecentFilesMenu()
            logger.info("Cleared recent files list")
    
    ################################
    ##Function: ViewLogFile
    #Open log file in default editor
    ##Inputs: 
    #self: Ui_MainWindow
    ##Returns:
    #none
    ################################
    def ViewLogFile(self):
        """Open log file"""
        try:
            logger.open_log_file()
        except Exception as e:
            QMessageBox.information(
                self.MainWindow,
                "Log File Location",
                f"Log file location:\n{logger.get_log_file_path()}"
            )
    
    
    ################################
    ##Function: closeEvent
    #Handles closing of program
    ##Inputs: 
    #self: Ui_MainWindow
    #event: closing event
    ##Returns:
    #none
    ################################   
    def closeEvent(self, event):
        event.accept()
        QApplication.quit()
        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

