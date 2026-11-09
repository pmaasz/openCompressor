"""
Recent Files Manager for CompPy
Tracks and provides quick access to recently opened files
"""
import json
import os
from pathlib import Path


class RecentFilesManager:
    def __init__(self, max_files=10):
        self.max_files = max_files
        self.recent_files = []
        self.config_file = self._get_config_path()
        self.load()
    
    def _get_config_path(self):
        """Get path to config file in user's home directory"""
        home = Path.home()
        config_dir = home / '.comppy'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'recent_files.json'

    def remove_file(self, filepath):
        """Remove a file from the list and persist."""
        try:
            resolved = str(Path(filepath).resolve())
        except OSError:
            resolved = os.path.abspath(filepath)
        if resolved in self.recent_files:
            self.recent_files.remove(resolved)
            self.save()

    def add_file(self, filepath):
        """Add a file to recent files list"""
        # Convert to absolute, resolved path
        try:
            filepath = str(Path(filepath).resolve())
        except OSError:
            filepath = os.path.abspath(filepath)
        
        # Remove if already exists
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        
        # Add to front
        self.recent_files.insert(0, filepath)
        
        # Trim to max size
        self.recent_files = self.recent_files[:self.max_files]
        
        # Remove files that no longer exist
        self.recent_files = [f for f in self.recent_files if os.path.exists(f)]
        
        # Save
        self.save()
    
    def get_recent_files(self):
        """Get list of recent files (only those that still exist)"""
        # Filter out non-existent files
        self.recent_files = [f for f in self.recent_files if os.path.exists(f)]
        return self.recent_files
    
    def clear(self):
        """Clear recent files list"""
        self.recent_files = []
        self.save()
    
    def save(self):
        """Save recent files to config file (atomic write)."""
        try:
            tmp = self.config_file.with_suffix('.json.tmp')
            with open(tmp, 'w') as f:
                json.dump(self.recent_files, f, indent=2)
                f.flush()
                try:
                    os.fsync(f.fileno())
                except OSError:
                    pass
            os.replace(tmp, self.config_file)
        except OSError as e:
            print(f"Error saving recent files: {e}")

    def load(self):
        """Load recent files from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                if not isinstance(loaded, list):
                    raise ValueError("recent files config must be a list")
                self.recent_files = [str(f) for f in loaded]
                # Filter out non-existent files
                self.recent_files = [f for f in self.recent_files if os.path.exists(f)]
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error loading recent files (resetting): {e}")
            self.recent_files = []
        except OSError as e:
            print(f"Error loading recent files: {e}")
            self.recent_files = []
