# CompPy Quick Start Guide

## For Ubuntu/Debian Users

### 1. Install System Dependencies
```bash
sudo apt install python3-pyqt5
```

### 2. Setup Project
```bash
cd /home/philip/Workspace/CompPy
python3 -m venv venv --system-site-packages
source venv/bin/activate
pip install matplotlib numpy numpy-stl
```

### 3. Run
```bash
python comppy.py
```

That's it! The application should now launch successfully.

## Troubleshooting

### "Could not load Qt platform plugin xcb"
Use the system PyQt5 as shown above (Quick Start method).

### "QSocketNotifier: Can only be used with threads started with QThread"
This is a harmless Qt warning that can be safely ignored. It doesn't affect functionality.

To suppress it, you can run with:
```bash
python comppy.py 2>&1 | grep -v "QSocketNotifier"
```

Or set this environment variable:
```bash
export QT_LOGGING_RULES="*.debug=false;qt.qpa.*=false"
python comppy.py
```

### "NameError: name 'MainWindow' is not defined"
This has been fixed in the latest version. Make sure you've pulled the latest changes.

### Tests Not Running
Make sure you're in the virtual environment:
```bash
source venv/bin/activate
python -m unittest discover -s tests -v
```

## What's Included

- **12 functional tests** covering aerodynamics, 3D mesh generation, and file I/O
- **Organized source code** in `src/` directory
- **Requirements file** for easy dependency management
- **Comprehensive documentation** in README.md and INSTALL.md

## Next Steps

- Read `README.md` for full usage instructions
- Check `INSTALL.md` for detailed troubleshooting
- Run tests with `python -m unittest discover -s tests -v`
