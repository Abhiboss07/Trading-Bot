"""
Limit Orders Module
Extended limit order functionality with advanced features
"""

from typing import Optional, Dict, Any
from binance.client import Client
from src.logger import get_logger
from src.validator import OrderValidator
from src.market_orders import MarketOrderExecutor


class LimitOrderExecutor(MarketOrderExecutor):
    """Extended limit order executor with additional features"""
    
    def __init__(self, client: Client, validator: OrderValidator):
        """
        Initialize limit order executor
        
        Args:
            client: Binance client instance
            validator: Order validator instance
        """
        super().__init__(client, validator)
    
    def place_stop_limit_order(self, symbol: str, side: str, quantity: float,
                              price: float, stop_price: float,
                              time_in_force: str = 'GTC',
                              reduce_only: bool = False) -> Optional[Dict[str, Any]]:
        """
        Place a stop-limit order
        
        Args:
            symbol: Trading symbol
            side: Order side (BUY or SELL)
            quantity: Order quantity
            price: Limit price
            stop_price: Stop trigger price
            time_in_force: Time in force
            reduce_only: Whether order should only reduce position
            
        Returns:
            Order response dict or None if failed
        """
        # Validate inputs
        is_valid, error = self.validator.validate_symbol(symbol)
        if not is_valid:
            self.logger.error(f"Invalid symbol: {error}")
            return None
        
        is_valid, error = self.validator.validate_side(side)
        if not is_valid:
            self.logger.error(f"Invalid side: {error}")
            return None
        
        is_valid, error = self.validator.validate_price(price)
        if not is_valid:
            self.logger.error(f"Invalid price: {error}")
            return None
        
        is_valid, error = self.validator.validate_price(stop_price)
        if not is_valid:
            self.logger.error(f"Invalid stop price: {error}")
            return None
        
        is_valid, error = self.validator.validate_quantity(quantity, price)
        if not is_valid:
            self.logger.error(f"Invalid quantity: {error}")
            return None
        
        # Format values
        price = self.validator.format_price(price)
        stop_price = self.validator.format_price(stop_price)
        quantity = self.validator.format_quantity(quantity)
        
        try:
            self.logger.log_order(
                action="PLACING",
                order_type="STOP_LIMIT",
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side,
                stop_price=stop_price,
                time_in_force=time_in_force
            )
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type='STOP',
                quantity=quantity,
                price=price,
                stopPrice=stop_price,
                timeInForce=time_in_force.upper(),
                reduceOnly=reduce_only
            )
            
            self.logger.log_order(
                action="PLACED",
                order_type="STOP_LIMIT",
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side,
                order_id=order.get('orderId'),
                status=order.get('status')
            )
            
            return order
            
        except Exception as e:
            self.logger.log_error_trace(e, "place_stop_limit_order")
            return None
    
    def place_stop_market_order(self, symbol: str, side: str, quantity: float,
                               stop_price: float,
                               reduce_only: bool = False) -> Optional[Dict[str, Any]]:
        """
        Place a stop-market order
        
        Args:
            symbol: Trading symbol
            side: Order side (BUY or SELL)
            quantity: Order quantity
            stop_price: Stop trigger price
            reduce_only: Whether order should only reduce position
            
        Returns:
            Order response dict or None if failed
        """
        # Validate inputs
        is_valid, error = self.validator.validate_symbol(symbol)
        if not is_valid:
            self.logger.error(f"Invalid symbol: {error}")
            return None
        
        is_valid, error = self.validator.validate_side(side)
        if not is_valid:
            self.logger.error(f"Invalid side: {error}")
            return None
        
        is_valid, error = self.validator.validate_price(stop_price)
        if not is_valid:
            self.logger.error(f"Invalid stop price: {error}")
            return None
        
        is_valid, error = self.validator.validate_quantity(quantity)
        if not is_valid:
            self.logger.error(f"Invalid quantity: {error}")
            return None
        
        # Format values
        stop_price = self.validator.format_price(stop_price)
        quantity = self.validator.format_quantity(quantity)
        
        try:
            self.logger.log_order(
                action="PLACING",
                order_type="STOP_MARKET",
                symbol=symbol,
                quantity=quantity,
                side=side,
                stop_price=stop_price
            )
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type='STOP_MARKET',
                quantity=quantity,
                stopPrice=stop_price,
                reduceOnly=reduce_only
            )
            
            self.logger.log_order(
                action="PLACED",
                order_type="STOP_MARKET",
                symbol=symbol,
                quantity=quantity,
                side=side,
                order_id=order.get('orderId'),
                status=order.get('status')
            )
            
            return order
            
        except Exception as e:
            self.logger.log_error_trace(e, "place_stop_market_order")
            return None
    
    def place_take_profit_order(self, symbol: str, side: str, quantity: float,
                               stop_price: float, price: Optional[float] = None,
                               reduce_only: bool = True) -> Optional[Dict[str, Any]]:
        """
        Place a take-profit order
        
        Args:
            symbol: Trading symbol
            side: Order side (BUY or SELL)
            quantity: Order quantity
            stop_price: Take profit trigger price
            price: Limit price (None for market)
            reduce_only: Whether order should only reduce position
            
        Returns:
            Order response dict or None if failed
        """
        # Validate inputs
        is_valid, error = self.validator.validate_symbol(symbol)
        if not is_valid:
            self.logger.error(f"Invalid symbol: {error}")
            return None
        
        is_valid, error = self.validator.validate_side(side)
        if not is_valid:
            self.logger.error(f"Invalid side: {error}")
            return None
        
        is_valid, error = self.validator.validate_price(stop_price)
        if not is_valid:
            self.logger.error(f"Invalid stop price: {error}")
            return None
        
        is_valid, error = self.validator.validate_quantity(quantity)
        if not is_valid:
            self.logger.error(f"Invalid quantity: {error}")
            return None
        
        # Format values
        stop_price = self.validator.format_price(stop_price)
        quantity = self.validator.format_quantity(quantity)
        
        try:
            order_type = 'TAKE_PROFIT_MARKET' if price is None else 'TAKE_PROFIT'
            
            self.logger.log_order(
                action="PLACING",
                order_type=order_type,
                symbol=symbol,
                quantity=quantity,
                side=side,
                stop_price=stop_price
            )
            
            order_params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': order_type,
                'quantity': quantity,
                'stopPrice': stop_price,
                'reduceOnly': reduce_only
            }
            
            if price is not None:
                price = self.validator.format_price(price)
                order_params['price'] = price
                order_params['timeInForce'] = 'GTC'
            
            order = self.client.futures_create_order(**order_params)
            
            self.logger.log_order(
                action="PLACED",
                order_type=order_type,
                symbol=symbol,
                quantity=quantity,
                side=side,
                order_id=order.get('orderId'),
                status=order.get('status')
            )
            
            return order
            
        except Exception as e:
            self.logger.log_error_trace(e, "place_take_profit_order")
            return None
