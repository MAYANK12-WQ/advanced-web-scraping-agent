import logging
import colorlog
import os
from datetime import datetime

def setup_logger(log_level=logging.INFO):
    """
    Setup and configure the logging system with color formatting
    
    Args:
        log_level: Logging level (default: INFO)
        
    Returns:
        Logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"logs/scraping_agent_{timestamp}.log"
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create console handler with color formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Define color scheme
    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    console_handler.setFormatter(color_formatter)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    
    # Define file formatter
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging system initialized. Log file: {log_file}")
    return logger

class LogCapture:
    """
    Utility class to capture log messages for display in the UI
    """
    
    def __init__(self, max_entries=100):
        self.max_entries = max_entries
        self.log_entries = []
        self.setup_handler()
    
    def setup_handler(self):
        """Setup a handler to capture log messages"""
        self.handler = logging.Handler()
        self.handler.setLevel(logging.INFO)
        
        # Set formatter
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
        self.handler.setFormatter(formatter)
        
        # Set emit function
        self.handler.emit = self.capture_log
        
        # Add handler to root logger
        logging.getLogger().addHandler(self.handler)
    
    def capture_log(self, record):
        """Capture log record and store it"""
        log_entry = self.handler.format(record)
        self.log_entries.append(log_entry)
        
        # Limit the number of entries
        if len(self.log_entries) > self.max_entries:
            self.log_entries.pop(0)
    
    def get_logs(self):
        """Get all captured log entries as a string"""
        return "\n".join(self.log_entries)
    
    def clear(self):
        """Clear all captured log entries"""
        self.log_entries = []

# Create a global log capture instance
log_capture = LogCapture()

def get_captured_logs():
    """Get captured logs for display in UI"""
    return log_capture.get_logs()

def clear_captured_logs():
    """Clear captured logs"""
    log_capture.clear()
