"""
Market Orders Module
Handles market and limit order execution with validation
"""

from typing import Optional, Dict, Any
from binance.client import Client
from binance.exceptions import BinanceAPIException
from src.logger import get_logger
from src.validator import OrderValidator


class MarketOrderExecutor:
    """Executes market and limit orders on Binance Futures"""
    
    def __init__(self, client: Client, validator: OrderValidator):
        """
        Initialize market order executor
        
        Args:
            client: Binance client instance
            validator: Order validator instance
        """
        self.client = client
        self.validator = validator
        self.logger = get_logger()
    
    def place_market_order(self, symbol: str, side: str, quantity: float, 
                          reduce_only: bool = False) -> Optional[Dict[str, Any]]:
        """
        Place a market order
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            side: Order side (BUY or SELL)
            quantity: Order quantity
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
        
        is_valid, error = self.validator.validate_quantity(quantity)
        if not is_valid:
            self.logger.error(f"Invalid quantity: {error}")
            return None
        
        # Format quantity
        quantity = self.validator.format_quantity(quantity)
        
        try:
            self.logger.log_order(
                action="PLACING",
                order_type="MARKET",
                symbol=symbol,
                quantity=quantity,
                side=side,
                reduce_only=reduce_only
            )
            
            # Place market order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type='MARKET',
                quantity=quantity,
                reduceOnly=reduce_only
            )
            
            self.logger.log_order(
                action="PLACED",
                order_type="MARKET",
                symbol=symbol,
                quantity=quantity,
                side=side,
                order_id=order.get('orderId'),
                status=order.get('status')
            )
            
            self.logger.log_api_call(
                endpoint="/fapi/v1/order",
                method="POST",
                status="SUCCESS",
                order_id=order.get('orderId')
            )
            
            return order
            
        except BinanceAPIException as e:
            self.logger.log_error_trace(e, "place_market_order")
            self.logger.log_api_call(
                endpoint="/fapi/v1/order",
                method="POST",
                status="FAILED",
                error_code=e.code,
                error_msg=e.message
            )
            return None
        except Exception as e:
            self.logger.log_error_trace(e, "place_market_order")
            return None
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, 
                         price: float, time_in_force: str = 'GTC',
                         reduce_only: bool = False, 
                         post_only: bool = False) -> Optional[Dict[str, Any]]:
        """
        Place a limit order
        
        Args:
            symbol: Trading symbol
            side: Order side (BUY or SELL)
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force (GTC, IOC, FOK)
            reduce_only: Whether order should only reduce position
            post_only: Whether order should be post-only (maker)
            
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
        
        is_valid, error = self.validator.validate_quantity(quantity, price)
        if not is_valid:
            self.logger.error(f"Invalid quantity: {error}")
            return None
        
        is_valid, error = self.validator.validate_time_in_force(time_in_force)
        if not is_valid:
            self.logger.error(f"Invalid time in force: {error}")
            return None
        
        # Format values
        price = self.validator.format_price(price)
        quantity = self.validator.format_quantity(quantity)
        
        try:
            self.logger.log_order(
                action="PLACING",
                order_type="LIMIT",
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side,
                time_in_force=time_in_force,
                reduce_only=reduce_only,
                post_only=post_only
            )
            
            # Place limit order
            order_params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': 'LIMIT',
                'quantity': quantity,
                'price': price,
                'timeInForce': time_in_force.upper(),
                'reduceOnly': reduce_only
            }
            
            if post_only:
                order_params['postOnly'] = True
            
            order = self.client.futures_create_order(**order_params)
            
            self.logger.log_order(
                action="PLACED",
                order_type="LIMIT",
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side,
                order_id=order.get('orderId'),
                status=order.get('status')
            )
            
            self.logger.log_api_call(
                endpoint="/fapi/v1/order",
                method="POST",
                status="SUCCESS",
                order_id=order.get('orderId')
            )
            
            return order
            
        except BinanceAPIException as e:
            self.logger.log_error_trace(e, "place_limit_order")
            self.logger.log_api_call(
                endpoint="/fapi/v1/order",
                method="POST",
                status="FAILED",
                error_code=e.code,
                error_msg=e.message
            )
            return None
        except Exception as e:
            self.logger.log_error_trace(e, "place_limit_order")
            return None
    
    def cancel_order(self, symbol: str, order_id: int) -> bool:
        """
        Cancel an open order
        
        Args:
            symbol: Trading symbol
            order_id: Order ID to cancel
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Cancelling order {order_id} for {symbol}")
            
            result = self.client.futures_cancel_order(
                symbol=symbol,
                orderId=order_id
            )
            
            self.logger.info(f"Order {order_id} cancelled successfully")
            self.logger.log_api_call(
                endpoint="/fapi/v1/order",
                method="DELETE",
                status="SUCCESS",
                order_id=order_id
            )
            
            return True
            
        except BinanceAPIException as e:
            self.logger.log_error_trace(e, "cancel_order")
            self.logger.log_api_call(
                endpoint="/fapi/v1/order",
                method="DELETE",
                status="FAILED",
                error_code=e.code,
                error_msg=e.message
            )
            return False
        except Exception as e:
            self.logger.log_error_trace(e, "cancel_order")
            return False
    
    def get_order_status(self, symbol: str, order_id: int) -> Optional[Dict[str, Any]]:
        """
        Get order status
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
            
        Returns:
            Order status dict or None if failed
        """
        try:
            order = self.client.futures_get_order(
                symbol=symbol,
                orderId=order_id
            )
            
            self.logger.log_api_call(
                endpoint="/fapi/v1/order",
                method="GET",
                status="SUCCESS",
                order_id=order_id
            )
            
            return order
            
        except BinanceAPIException as e:
            self.logger.log_error_trace(e, "get_order_status")
            return None
        except Exception as e:
            self.logger.log_error_trace(e, "get_order_status")
            return None
    
    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """
        Get all open orders
        
        Args:
            symbol: Trading symbol (optional, None for all symbols)
            
        Returns:
            List of open orders
        """
        try:
            if symbol:
                orders = self.client.futures_get_open_orders(symbol=symbol)
            else:
                orders = self.client.futures_get_open_orders()
            
            self.logger.log_api_call(
                endpoint="/fapi/v1/openOrders",
                method="GET",
                status="SUCCESS",
                count=len(orders)
            )
            
            return orders
            
        except BinanceAPIException as e:
            self.logger.log_error_trace(e, "get_open_orders")
            return []
        except Exception as e:
            self.logger.log_error_trace(e, "get_open_orders")
            return []
    
    def cancel_all_orders(self, symbol: str) -> bool:
        """
        Cancel all open orders for a symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Cancelling all orders for {symbol}")
            
            result = self.client.futures_cancel_all_open_orders(symbol=symbol)
            
            self.logger.info(f"All orders cancelled for {symbol}")
            self.logger.log_api_call(
                endpoint="/fapi/v1/allOpenOrders",
                method="DELETE",
                status="SUCCESS"
            )
            
            return True
            
        except BinanceAPIException as e:
            self.logger.log_error_trace(e, "cancel_all_orders")
            return False
        except Exception as e:
            self.logger.log_error_trace(e, "cancel_all_orders")
            return False
