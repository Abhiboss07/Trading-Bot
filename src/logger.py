"""
Logging Module
Provides structured logging with timestamps and error traces
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import colorlog
from logging.handlers import RotatingFileHandler


class BotLogger:
    """Structured logger for the trading bot"""
    
    def __init__(self, name: str = "TradingBot", log_file: str = "bot.log", 
                 level: str = "INFO", max_bytes: int = 50*1024*1024, backup_count: int = 5):
        """
        Initialize the logger
        
        Args:
            name: Logger name
            log_file: Log file path
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Maximum log file size before rotation
            backup_count: Number of backup files to keep
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        
        # File handler with rotation
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=max_bytes, 
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error message with optional exception info"""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Log critical message with optional exception info"""
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)
    
    def log_order(self, action: str, order_type: str, symbol: str, 
                  quantity: float, price: Optional[float] = None, **kwargs):
        """
        Log order-related actions with structured format
        
        Args:
            action: Action type (PLACE, CANCEL, FILL, etc.)
            order_type: Order type (MARKET, LIMIT, etc.)
            symbol: Trading symbol
            quantity: Order quantity
            price: Order price (optional)
            **kwargs: Additional order details
        """
        price_str = f"@ {price}" if price else "@ MARKET"
        details = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        
        message = f"[{action}] {order_type} | {symbol} | Qty: {quantity} {price_str}"
        if details:
            message += f" | {details}"
        
        self.info(message)
    
    def log_error_trace(self, error: Exception, context: str = ""):
        """
        Log error with full trace
        
        Args:
            error: Exception object
            context: Additional context about where error occurred
        """
        error_msg = f"Error in {context}: {type(error).__name__}: {str(error)}" if context else str(error)
        self.error(error_msg, exc_info=True)
    
    def log_api_call(self, endpoint: str, method: str = "GET", status: str = "SUCCESS", **kwargs):
        """
        Log API calls
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            status: Call status
            **kwargs: Additional details
        """
        details = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        message = f"[API] {method} {endpoint} | Status: {status}"
        if details:
            message += f" | {details}"
        
        if status == "SUCCESS":
            self.debug(message)
        else:
            self.warning(message)
    
    def log_trade_execution(self, symbol: str, side: str, quantity: float, 
                           price: float, pnl: Optional[float] = None, **kwargs):
        """
        Log trade execution details
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Executed quantity
            price: Execution price
            pnl: Profit/Loss (optional)
            **kwargs: Additional details
        """
        pnl_str = f"| PnL: {pnl:+.2f} USDT" if pnl is not None else ""
        details = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        
        message = f"[EXECUTION] {side} {quantity} {symbol} @ {price} {pnl_str}"
        if details:
            message += f" | {details}"
        
        self.info(message)


# Global logger instance
_logger_instance: Optional[BotLogger] = None


def get_logger(name: str = "TradingBot", **kwargs) -> BotLogger:
    """
    Get or create logger instance
    
    Args:
        name: Logger name
        **kwargs: Additional logger configuration
        
    Returns:
        BotLogger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = BotLogger(name, **kwargs)
    return _logger_instance
