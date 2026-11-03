openCompressor (CompPy) - Compressor Design
==========================

This is a standalone axial compressor design program. I built this after the frustrating and monotonous task of using Python scripts in Blender to create and render axial compressor objects. Given user specified parameters, the program will render the object (rotor or stator) in the window and export the rendered object as a .STL file.

Ducted fans and axial compressors are designed using the same techniques. Given certain parameters, a blade shape can be constructed. Ducted fans work by increasing the velocity of the inflow, whereas an axial compressor attempts to maintain the velocity but increase the pressure. The difference is the use of stator vanes, which (on a very basic level) are reversed, static rotor blades. 

There are many ways to calculate how the rotor will be created and how it will perform, this program utilizes the Mean Line Radius technique.

Project Structure
"""""""""""""""""
::

    CompPy/
    ├── src/              # Source code modules
    │   ├── BladeCalc.py       # Aerodynamic calculations
    │   ├── BladePlot.py       # 2D blade profile plotting
    │   ├── BladeRender.py     # 3D blade rendering
    │   ├── StlUtils.py        # STL mesh generation utilities
    │   ├── FileOps.py         # JSON save/load operations
    │   ├── MainWindow.py      # Main GUI application
    │   ├── RenderWindow.py    # 3D render window widget
    │   └── RClickWin.py       # Dialog windows
    ├── tests/            # Functional tests
    ├── requirements.txt  # Python dependencies
    └── README.md        # This file

Dependencies
""""""""""""""""""
- Python 3.6+
- PyQt5 >= 5.15.0
- matplotlib >= 3.3.0
- numpy >= 1.19.0
- numpy-stl >= 2.16.0 (`Link <https://github.com/WoLpH/numpy-stl>`_)

Installation
""""""""""""
**Quick Start (Recommended for Ubuntu/Debian):**

1. Install system PyQt5::

    sudo apt install python3-pyqt5

2. Clone and setup::

    git clone <repository-url>
    cd CompPy
    python3 -m venv venv --system-site-packages
    source venv/bin/activate
    pip install matplotlib numpy numpy-stl

3. Run::

    python comppy.py

**Alternative (Install PyQt5 in venv):**

If you prefer to install everything in the virtual environment, you need system Qt libraries first::

    sudo apt update
    sudo apt install -y libxcb-xinerama0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
                        libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 \
                        libxkbcommon-x11-0 libgl1-mesa-glx libdbus-1-3

Then::

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python comppy.py

**Troubleshooting:**

- If you get "Could not load Qt platform plugin xcb" error, use the Quick Start method above
- For detailed platform-specific instructions, see ``INSTALL.md``

Testing
"""""""
The project includes comprehensive functional tests covering core calculations, 
3D mesh generation, and file operations.

Run all tests::

    python -m unittest discover -s tests -v

Run specific test module::

    python -m unittest tests.test_blade_calc -v

See ``tests/README.md`` for more information.

Usage
"""""
I've really tried to make this user-friendly but I'll still give a brief overview. 

- When the user opens the program, every box will be yellow and there will be no stages in the left-most list widget.

- To generate a rotor or stator object, the parameters need to be filled in. 

- To add a stage the **Add Stage** button must be clicked. This will generate the first stage object.

- Each stage has five common variables, **Reaction Coefficient**, **Loading Coefficient**, **Flow Coefficient**, **RPM**, and the **Mean Line Radius**. 
- As the user fills in the parameters, if the values are permissible, the box will turn green. Most items are simple floats, except for the obvious ones (**RPM**, **Num of Blades**)
- To generate just a rotor, you need to fill out the **Universal Coefficients** and the **Rotor Specifications** sections, you do not need to mess with the **Stator Sepcifications** section. And vise versa for generating a stator. 
- After entering all the parameters for the object, one can either click **Draw Blade Profile** to get drawings of the cross sections of the root and tip of blade. Or click **Render STL** to generate the 3D object. 
- Under **Rotor Specifications** there is a checkbox that says **Support Wall**, that is used to generate a wall around the rotor. This wall is primarily used for micro turbomachinery to prevent the rotor from destroying itself.
- Once one of those is picked, a window will pop up to choose which object to use. If all the parameters are valid in the subsection, the drawing or render will be generated. 
- If a 3D render is generated, it will appear in the top right-most corner. It has basic matplotlib functionality: Right Click to rotate, and Left Click to Zoom.
- If the user is happy with the 3D rendering, they can choose to export the STL file to a specified location with **Export STL**.
- You can continue this process for as many stages as you want.
- Once done, you can save your compressor under **File > Save** and it will generate a .json file that houses all the relevant information to be opened another time.

Assumptions
"""""""""""
**If there is any calculation done wrong, I apologize, it's a large program so overlooking something is very easy.**

- One assumption I did take was to make the Max Camber Pos to be 0.35. If you know what I'm talking about and have a problem with it, it's clearly labeled in the code and easily changed. If you don't or don't care, it's no issue at all. At the sizes I use this for, that parameter is almost insignificant. 

Known Issues 
""""""""""""
- For some reason, depending on the graphics card being used, the 3D render either appears perfectly, or without any contour lines. I'm still looking into the cause but if any of you experience it, give me a holler.
- There have been reports of freezing and/or extreme wait times for larger (~ 1 meter) scaled rotors and stators. I'm also looking into that, but at that size blade, you wouldn't want to use a single piece anyways as the rotor anyways...


New Features
""""""""""""
**UI/UX Enhancements:**

- **Tooltips & Help**: Hover over any input field to see detailed descriptions, usage guidance, and valid ranges
- **Undo/Redo**: Track parameter changes with full undo/redo support (Ctrl+Z / Ctrl+Y)
- **Parameter Presets**: Quick-load common compressor configurations from the Presets menu:
  
  - Micro Turbine - Single Stage
  - RC Ducted Fan - High Speed  
  - Industrial Compressor - Low Speed
  - High Pressure Ratio - Multi-Stage
  - Educational Example - Simple

- **Assembly Viewer**: View all stages together in 3D with rotation animation and multiple camera views
- **Drag-and-Drop Reordering**: Reorder stages by dragging them in the stage list
- **Real-time Validation**: Enhanced visual feedback with explanatory tooltips for invalid inputs

**Quick Wins (High Impact Features):**

- **Recent Files Menu**: Quick access to recently opened designs (File > Recent Files)
- **Progress Indicators**: Visual feedback during long STL mesh generation operations
- **Error Logging**: Automatic logging of all errors to `~/.comppy/logs/` for debugging
- **Default Parameters**: New stages automatically filled with sensible, validated defaults
- **Keyboard Shortcuts**: Ctrl+O (Open), Ctrl+S (Save), Ctrl+Z (Undo), Ctrl+Y (Redo)

See ``docs/UI_ENHANCEMENTS.md`` and ``docs/QUICK_WINS.md`` for detailed documentation.


What's To Come
""""""""""""""
- Rotor/stator performance statistics in the program.
- Generating all the parameters giving desired compressor performance (there's some serious Thermodynamics involved in this so it'll take a while)

Contact
"""""""
Want to yell at me? Or have a question, shoot me an email.



Dark Mode
"""""""""
The application includes a dark mode theme for reduced eye strain.

To toggle dark mode:

1. Click **View** in the menu bar
2. Check **Dark Mode**

Or simply press the menu item to toggle between light and dark themes.

The dark mode includes:

- Dark background (#2b2b2b) with light text
- Styled buttons, input fields, and list widgets
- Theme-aware validation colors (green/yellow/red)
- Consistent styling across all UI elements



Dark Mode Settings
""""""""""""""""""

Dark mode preference is automatically saved to ``~/.config/comppy/settings.json`` and restored on next launch.
