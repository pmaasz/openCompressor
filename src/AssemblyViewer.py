"""
Enhanced 3D Assembly Viewer for CompPy
Shows all stages together with animation capabilities
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
    
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import numpy as np

from BladeRender import RenderRotor, RenderStator


class AssemblyViewer(QWidget):
    """
    3D viewer that displays all stages in an assembly
    Includes rotation animation and multiple view options
    """
    
    def __init__(self, parent, stages_data):
        """
        stages_data: list of dicts, each containing:
            {
                'common': common parameters dict,
                'rotor': rotor parameters dict,
                'stator': stator parameters dict,
                'stage_num': int
            }
        """
        super(AssemblyViewer, self).__init__(parent)
        
        self.stages_data = stages_data
        self.meshes = []
        self.animation_running = False
        self.rotation_angle = 0
        self.animation = None
        
        # Create layout
        self.layout = QVBoxLayout()
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111, projection='3d')
        
        # Control panel
        self.control_panel = self.create_control_panel()
        
        # Add widgets to layout
        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.control_panel)
        
        self.setLayout(self.layout)
        
        # Generate all meshes
        self.generate_assembly()
        
    def create_control_panel(self):
        """Create control panel with buttons"""
        panel = QWidget()
        layout = QHBoxLayout()
        
        # View buttons
        self.btn_front = QPushButton("Front View")
        self.btn_side = QPushButton("Side View")
        self.btn_top = QPushButton("Top View")
        self.btn_iso = QPushButton("Isometric")
        
        # Animation controls
        self.btn_animate = QPushButton("Start Animation")
        self.btn_animate.setCheckable(True)
        
        # Cross-section toggle
        self.btn_cross_section = QPushButton("Cross Section")
        self.btn_cross_section.setCheckable(True)
        
        # Connect signals
        self.btn_front.clicked.connect(lambda: self.set_view('front'))
        self.btn_side.clicked.connect(lambda: self.set_view('side'))
        self.btn_top.clicked.connect(lambda: self.set_view('top'))
        self.btn_iso.clicked.connect(lambda: self.set_view('iso'))
        self.btn_animate.clicked.connect(self.toggle_animation)
        self.btn_cross_section.clicked.connect(self.toggle_cross_section)
        
        # Add buttons to layout
        layout.addWidget(QLabel("View:"))
        layout.addWidget(self.btn_front)
        layout.addWidget(self.btn_side)
        layout.addWidget(self.btn_top)
        layout.addWidget(self.btn_iso)
        layout.addStretch()
        layout.addWidget(self.btn_animate)
        layout.addWidget(self.btn_cross_section)
        
        panel.setLayout(layout)
        return panel
        
    def generate_assembly(self):
        """Generate all stage meshes and display them"""
        self.ax.clear()
        self.meshes = []
        
        axial_offset = 0  # Track position along axis
        
        for stage_data in self.stages_data:
            common = stage_data['common']
            rotor_params = stage_data['rotor']
            stator_params = stage_data['stator']
            
            # Create temporary widget for rendering
            temp_widget = QWidget()
            
            # Generate rotor mesh
            try:
                rotor_renderer = RenderRotor(temp_widget, common, rotor_params, False)
                rotor_mesh = rotor_renderer.getObj()
                if rotor_mesh is not None:
                    self.meshes.append({
                        'vectors': rotor_mesh.vectors.copy(),
                        'type': 'rotor',
                        'offset': axial_offset,
                        'stage': stage_data['stage_num']
                    })
                    # Update offset based on rotor length
                    hub_length = float(rotor_params.get('Hub Length', 30))
                    axial_offset += hub_length * 1.2
                rotor_renderer.deleteLater()
            except (ValueError, TypeError, KeyError, RuntimeError, AttributeError, OSError) as e:
                from ErrorLogger import logger as _logger
                _logger.error(f"Error rendering rotor for stage {stage_data['stage_num']}: {e}",
                              exc_info=True)

            # Generate stator mesh
            try:
                stator_renderer = RenderStator(temp_widget, common, stator_params)
                stator_mesh = stator_renderer.getObj()
                if stator_mesh is not None:
                    self.meshes.append({
                        'vectors': stator_mesh.vectors.copy(),
                        'type': 'stator',
                        'offset': axial_offset,
                        'stage': stage_data['stage_num']
                    })
                    # Update offset based on stator length
                    duct_length = float(stator_params.get('Duct Length', 40))
                    axial_offset += duct_length * 1.2
                stator_renderer.deleteLater()
            except (ValueError, TypeError, KeyError, RuntimeError, AttributeError, OSError) as e:
                from ErrorLogger import logger as _logger
                _logger.error(f"Error rendering stator for stage {stage_data['stage_num']}: {e}",
                              exc_info=True)
        
        # Display all meshes
        self.display_assembly()
        
    def display_assembly(self, rotation=0):
        """Display all meshes in the assembly (non-destructive).

        Previously rotor mesh.vectors were rotated in place every frame,
        accumulating error. Now rotation is applied to a copy.
        """
        self.ax.clear()

        for mesh_data in self.meshes:
            base_vectors = mesh_data['vectors']
            offset = mesh_data['offset']
            mesh_type = mesh_data['type']

            vectors = base_vectors.copy()
            # Apply rotation to rotors only
            if mesh_type == 'rotor' and rotation != 0:
                # Rotate mesh around Z axis (vectorized, no in-place mutation)
                c, s = np.cos(rotation), np.sin(rotation)
                rotation_matrix = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
                vectors = vectors @ rotation_matrix.T

            # Offset mesh along Z axis and plot
            from mpl_toolkits.mplot3d.art3d import Poly3DCollection

            vectors[:, :, 2] += offset  # Add axial offset
            
            # Create collection
            collection = Poly3DCollection(vectors, alpha=0.7, linewidths=0.5, edgecolors='black')
            
            # Color based on type
            if mesh_type == 'rotor':
                collection.set_facecolor([0.3, 0.5, 0.8])  # Blue for rotors
            else:
                collection.set_facecolor([0.8, 0.5, 0.3])  # Orange for stators
            
            self.ax.add_collection3d(collection)
        
        # Set labels and limits
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z (Axial)')
        
        # Auto-scale
        self.ax.autoscale()
        
        # Set equal aspect ratio
        self.set_equal_aspect()
        
        self.canvas.draw()
        
    def set_equal_aspect(self):
        """Set equal aspect ratio for 3D plot"""
        extents = np.array([getattr(self.ax, f'get_{dim}lim')() for dim in 'xyz'])
        sz = extents[:, 1] - extents[:, 0]
        centers = np.mean(extents, axis=1)
        maxsize = max(abs(sz))
        r = maxsize / 2
        for ctr, dim in zip(centers, 'xyz'):
            getattr(self.ax, f'set_{dim}lim')(ctr - r, ctr + r)
            
    def set_view(self, view_type):
        """Set predefined camera view"""
        if view_type == 'front':
            self.ax.view_init(elev=0, azim=0)
        elif view_type == 'side':
            self.ax.view_init(elev=0, azim=90)
        elif view_type == 'top':
            self.ax.view_init(elev=90, azim=0)
        elif view_type == 'iso':
            self.ax.view_init(elev=30, azim=45)
        
        self.canvas.draw()
        
    def toggle_animation(self):
        """Start/stop rotation animation"""
        if self.btn_animate.isChecked():
            self.btn_animate.setText("Stop Animation")
            self.start_animation()
        else:
            self.btn_animate.setText("Start Animation")
            self.stop_animation()
            
    def start_animation(self):
        """Start rotation animation"""
        self.animation_running = True
        
        def update_frame(frame):
            if not self.animation_running:
                return
            self.rotation_angle = (frame * 5) % 360  # Rotate 5 degrees per frame
            self.display_assembly(rotation=np.radians(self.rotation_angle))
            return []
        
        # Create animation
        self.animation = FuncAnimation(
            self.figure, 
            update_frame, 
            frames=72,  # 360/5 = 72 frames for full rotation
            interval=50,  # 50ms between frames
            blit=False,
            repeat=True
        )
        
        self.canvas.draw()
        
    def stop_animation(self):
        """Stop rotation animation"""
        self.animation_running = False
        if self.animation:
            self.animation.event_source.stop()
            self.animation = None
            
    def toggle_cross_section(self):
        """Toggle cross-section view"""
        if self.btn_cross_section.isChecked():
            # Show only half of the assembly (cut along XZ plane)
            # This would require mesh slicing - simplified version shown
            self.ax.set_ylim([0, None])  # Show only positive Y
        else:
            self.ax.autoscale()  # Restore full view
            self.set_equal_aspect()
        
        self.canvas.draw()
