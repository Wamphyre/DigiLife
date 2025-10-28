"""
Sistema de logging
"""

import logging
from datetime import datetime
import config


class Logger:
    """Logger personalizado para DigiLife"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.logger = logging.getLogger('DigiLife')
        self.logger.setLevel(logging.DEBUG if any(config.DEBUG.values()) else logging.INFO)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        self._initialized = True
    
    def info(self, message: str):
        """Log info"""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log debug"""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log warning"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error"""
        self.logger.error(message)
