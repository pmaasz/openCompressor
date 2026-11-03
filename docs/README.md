# Documentation Directory

This directory contains documentation for CompPy.

## Files

### User Documentation
- **[DEMO_SCRIPT.md](DEMO_SCRIPT.md)** - Step-by-step demo walkthrough
  - Perfect for presentations
  - Shows features in action
  - Includes talking points

### Developer Documentation
- See the main [README.md](../README.md) for project overview, installation, and usage

## Quick Start

### For Users
1. Read the main [README.md](../README.md) for installation and usage
2. Follow [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for a hands-on tutorial
3. Use tooltips in the application for parameter help

### For Developers
1. Check the source code in `src/`
2. Run tests with `python -m unittest discover -s tests -v`
3. See GitHub issues for planned features

## Features

### Core Features
- **Tooltips & Help** - Hover over input fields for parameter descriptions and valid ranges
- **Undo/Redo** - Full history tracking with Ctrl+Z / Ctrl+Y shortcuts
- **Parameter Presets** - Ready-to-use configurations for common compressor types
- **3D Assembly Viewer** - View all stages together with animation
- **Drag-and-Drop** - Reorder stages easily
- **Enhanced Validation** - Real-time feedback with color-coded status
- **Recent Files** - Quick access to recently opened designs
- **Error Logging** - Automatic logging to `~/.comppy/logs/`
- **Dark Mode** - Theme preference saved to `~/.config/comppy/settings.json`

## Testing

All features are tested:
```bash
python -m unittest discover -s tests -v
```

## Support

For questions or issues:
1. Review tooltips in the application
2. Check the main [README.md](../README.md)
3. Open an issue on the project repository

## Contributing

To add new features:
1. Follow existing code structure
2. Add unit tests
3. Update documentation
4. Test with existing features
