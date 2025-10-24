"""
Configuration Loader Module
Handles loading and validation of configuration from .env and config.yaml
"""

import os
import yaml
from typing import Dict, Any
from dotenv import load_dotenv
from pathlib import Path


class ConfigLoader:
    """Loads and manages configuration from environment and YAML files"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration loader
        
        Args:
            config_path: Path to YAML configuration file
        """
        # Load environment variables
        load_dotenv()
        
        # Load YAML configuration
        self.config_path = Path(config_path)
        self.config = self._load_yaml_config()
        
        # Validate required environment variables
        self._validate_env_vars()
    
    def _load_yaml_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    def _validate_env_vars(self):
        """Validate required environment variables are set"""
        required_vars = ['BINANCE_API_KEY', 'BINANCE_API_SECRET']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                "Please create a .env file based on .env.example"
            )
    
    def get_api_credentials(self) -> tuple:
        """Get Binance API credentials"""
        return (
            os.getenv('BINANCE_API_KEY'),
            os.getenv('BINANCE_API_SECRET')
        )
    
    def is_testnet(self) -> bool:
        """Check if testnet mode is enabled"""
        return os.getenv('USE_TESTNET', 'true').lower() == 'true'
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key_path: Configuration key path (e.g., 'trading.default_symbol')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_trading_config(self) -> Dict[str, Any]:
        """Get trading configuration"""
        return self.config.get('trading', {})
    
    def get_risk_config(self) -> Dict[str, Any]:
        """Get risk management configuration"""
        return self.config.get('risk_management', {})
    
    def get_execution_config(self) -> Dict[str, Any]:
        """Get execution configuration"""
        return self.config.get('execution', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.config.get('logging', {})
    
    def get_validation_config(self) -> Dict[str, Any]:
        """Get validation configuration"""
        return self.config.get('validation', {})
