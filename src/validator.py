"""
Validation Module
Validates inputs for symbol, quantity, price thresholds, and order parameters
"""

import re
from typing import Optional, Dict, Any
from decimal import Decimal, InvalidOperation


class OrderValidator:
    """Validates trading order parameters"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize validator with configuration
        
        Args:
            config: Validation configuration dictionary
        """
        self.config = config
        self.min_order_size = config.get('min_order_size_usdt', 5)
        self.max_order_size = config.get('max_order_size_usdt', 100000)
        self.min_price = config.get('min_price', 0.01)
        self.max_price = config.get('max_price', 1000000)
        self.price_precision = config.get('price_precision', 2)
        self.quantity_precision = config.get('quantity_precision', 3)
    
    def validate_symbol(self, symbol: str) -> tuple[bool, Optional[str]]:
        """
        Validate trading symbol format
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not symbol:
            return False, "Symbol cannot be empty"
        
        # Symbol should be uppercase alphanumeric
        if not re.match(r'^[A-Z0-9]+$', symbol):
            return False, "Symbol must contain only uppercase letters and numbers"
        
        # Must end with USDT for USDT-M futures
        if not symbol.endswith('USDT'):
            return False, "Symbol must end with USDT for USDT-M futures"
        
        # Minimum length check
        if len(symbol) < 6:
            return False, "Symbol too short"
        
        return True, None
    
    def validate_quantity(self, quantity: float, price: Optional[float] = None) -> tuple[bool, Optional[str]]:
        """
        Validate order quantity
        
        Args:
            quantity: Order quantity
            price: Order price (for notional value check)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        
        # Check notional value if price is provided
        if price is not None:
            notional_value = quantity * price
            
            if notional_value < self.min_order_size:
                return False, f"Order value ({notional_value:.2f} USDT) below minimum ({self.min_order_size} USDT)"
            
            if notional_value > self.max_order_size:
                return False, f"Order value ({notional_value:.2f} USDT) exceeds maximum ({self.max_order_size} USDT)"
        
        return True, None
    
    def validate_price(self, price: float) -> tuple[bool, Optional[str]]:
        """
        Validate order price
        
        Args:
            price: Order price
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if price <= 0:
            return False, "Price must be greater than 0"
        
        if price < self.min_price:
            return False, f"Price ({price}) below minimum ({self.min_price})"
        
        if price > self.max_price:
            return False, f"Price ({price}) exceeds maximum ({self.max_price})"
        
        return True, None
    
    def validate_side(self, side: str) -> tuple[bool, Optional[str]]:
        """
        Validate order side
        
        Args:
            side: Order side (BUY or SELL)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_sides = ['BUY', 'SELL']
        side_upper = side.upper()
        
        if side_upper not in valid_sides:
            return False, f"Side must be one of {valid_sides}"
        
        return True, None
    
    def validate_order_type(self, order_type: str) -> tuple[bool, Optional[str]]:
        """
        Validate order type
        
        Args:
            order_type: Order type
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_types = ['MARKET', 'LIMIT', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET']
        order_type_upper = order_type.upper()
        
        if order_type_upper not in valid_types:
            return False, f"Order type must be one of {valid_types}"
        
        return True, None
    
    def validate_time_in_force(self, time_in_force: str) -> tuple[bool, Optional[str]]:
        """
        Validate time in force parameter
        
        Args:
            time_in_force: Time in force (GTC, IOC, FOK)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_tif = ['GTC', 'IOC', 'FOK']
        tif_upper = time_in_force.upper()
        
        if tif_upper not in valid_tif:
            return False, f"Time in force must be one of {valid_tif}"
        
        return True, None
    
    def validate_leverage(self, leverage: int, max_leverage: int = 125) -> tuple[bool, Optional[str]]:
        """
        Validate leverage value
        
        Args:
            leverage: Leverage value
            max_leverage: Maximum allowed leverage
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if leverage < 1:
            return False, "Leverage must be at least 1"
        
        if leverage > max_leverage:
            return False, f"Leverage ({leverage}) exceeds maximum ({max_leverage})"
        
        return True, None
    
    def validate_stop_price(self, stop_price: float, current_price: float, 
                           side: str) -> tuple[bool, Optional[str]]:
        """
        Validate stop price relative to current price
        
        Args:
            stop_price: Stop trigger price
            current_price: Current market price
            side: Order side (BUY or SELL)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        is_valid, error = self.validate_price(stop_price)
        if not is_valid:
            return is_valid, error
        
        side_upper = side.upper()
        
        # For BUY stop orders, stop price should be above current price
        if side_upper == 'BUY' and stop_price <= current_price:
            return False, f"Stop price ({stop_price}) must be above current price ({current_price}) for BUY orders"
        
        # For SELL stop orders, stop price should be below current price
        if side_upper == 'SELL' and stop_price >= current_price:
            return False, f"Stop price ({stop_price}) must be below current price ({current_price}) for SELL orders"
        
        return True, None
    
    def validate_percentage(self, percentage: float, min_pct: float = 0.1, 
                           max_pct: float = 100.0) -> tuple[bool, Optional[str]]:
        """
        Validate percentage value
        
        Args:
            percentage: Percentage value
            min_pct: Minimum allowed percentage
            max_pct: Maximum allowed percentage
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if percentage < min_pct:
            return False, f"Percentage ({percentage}%) below minimum ({min_pct}%)"
        
        if percentage > max_pct:
            return False, f"Percentage ({percentage}%) exceeds maximum ({max_pct}%)"
        
        return True, None
    
    def validate_grid_parameters(self, lower_price: float, upper_price: float, 
                                grid_levels: int) -> tuple[bool, Optional[str]]:
        """
        Validate grid trading parameters
        
        Args:
            lower_price: Lower price bound
            upper_price: Upper price bound
            grid_levels: Number of grid levels
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate prices
        is_valid, error = self.validate_price(lower_price)
        if not is_valid:
            return False, f"Lower price invalid: {error}"
        
        is_valid, error = self.validate_price(upper_price)
        if not is_valid:
            return False, f"Upper price invalid: {error}"
        
        # Upper price must be greater than lower price
        if upper_price <= lower_price:
            return False, "Upper price must be greater than lower price"
        
        # Validate grid levels
        if grid_levels < 2:
            return False, "Grid levels must be at least 2"
        
        if grid_levels > 100:
            return False, "Grid levels cannot exceed 100"
        
        return True, None
    
    def validate_twap_parameters(self, total_quantity: float, chunks: int, 
                                interval_seconds: int) -> tuple[bool, Optional[str]]:
        """
        Validate TWAP order parameters
        
        Args:
            total_quantity: Total quantity to execute
            chunks: Number of chunks to split into
            interval_seconds: Time interval between chunks
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate quantity
        is_valid, error = self.validate_quantity(total_quantity)
        if not is_valid:
            return is_valid, error
        
        # Validate chunks
        if chunks < 2:
            return False, "TWAP must have at least 2 chunks"
        
        if chunks > 100:
            return False, "TWAP chunks cannot exceed 100"
        
        # Validate interval
        if interval_seconds < 1:
            return False, "Interval must be at least 1 second"
        
        if interval_seconds > 3600:
            return False, "Interval cannot exceed 1 hour (3600 seconds)"
        
        # Check chunk size
        chunk_size = total_quantity / chunks
        if chunk_size <= 0:
            return False, "Chunk size too small"
        
        return True, None
    
    def format_price(self, price: float) -> float:
        """Format price to configured precision"""
        try:
            return round(price, self.price_precision)
        except (ValueError, InvalidOperation):
            return price
    
    def format_quantity(self, quantity: float) -> float:
        """Format quantity to configured precision"""
        try:
            return round(quantity, self.quantity_precision)
        except (ValueError, InvalidOperation):
            return quantity
