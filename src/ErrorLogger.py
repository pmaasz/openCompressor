"""
Error Logger for CompPy
Logs errors and exceptions to file for debugging
"""
import logging
import os
import tempfile
from pathlib import Path
from datetime import datetime


class ErrorLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ErrorLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.log_dir = self._get_log_dir()
        self.log_file = self.log_dir / f'comppy_{datetime.now().strftime("%Y%m%d")}.log'
        self._setup_logger()
    
    def _get_log_dir(self):
        """Get writable log directory; fall back to temp on permission errors (gh #21)."""
        candidates = []
        try:
            candidates.append(Path.home() / '.comppy' / 'logs')
        except (RuntimeError, OSError):
            pass
        candidates.append(Path(tempfile.gettempdir()) / 'comppy' / 'logs')
        for log_dir in candidates:
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                probe = log_dir / '.write_probe'
                probe.write_text('', encoding='utf-8')
                try:
                    probe.unlink()
                except OSError:
                    pass
                return log_dir
            except OSError:
                continue
        # Last resort: temp dir itself (should exist).
        return Path(tempfile.gettempdir())
    
    def _setup_logger(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger('CompPy')
        self.logger.setLevel(logging.DEBUG)
        # Avoid duplicate handlers on re-init (e.g. tests, fork).
        if self.logger.handlers:
            return

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Rotating file handler (was unbounded FileHandler). Falls back to console-only.
        try:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                self.log_file, maxBytes=5 * 1024 * 1024, backupCount=3,
                encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except OSError as e:
            print(f"Warning: could not open log file {self.log_file}: {e}")
        
        # Console handler (only errors and above)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Best-effort cleanup of logs older than 30 days.
        try:
            self.clear_old_logs()
        except OSError:
            pass
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message, exc_info=False):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message, exc_info=False):
        """Log critical message"""
        self.logger.critical(message, exc_info=exc_info)
    
    def exception(self, message):
        """Log exception with traceback"""
        self.logger.exception(message)
    
    def get_log_file_path(self):
        """Get path to current log file"""
        return str(self.log_file)
    
    def open_log_file(self):
        """Open log file in default text editor"""
        import subprocess
        import platform
        
        system = platform.system()
        try:
            if system == 'Windows':
                os.startfile(self.log_file)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', self.log_file])
            else:  # Linux
                subprocess.run(['xdg-open', self.log_file])
        except OSError as e:
            print(f"Could not open log file: {e}")
    
    def clear_old_logs(self, days=30):
        """Delete log files older than specified days"""
        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (days * 86400)
            
            for log_file in self.log_dir.glob('comppy_*.log'):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    self.info(f"Deleted old log file: {log_file.name}")
        except OSError as e:
            self.error(f"Error clearing old logs: {e}")


# Singleton instance
logger = ErrorLogger()
