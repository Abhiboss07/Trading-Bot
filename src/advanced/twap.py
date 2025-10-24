"""
TWAP (Time-Weighted Average Price) Module
Splits large orders into smaller chunks over time
"""

import time
import asyncio
from typing import Optional, Dict, Any, List
from binance.client import Client
from src.logger import get_logger
from src.validator import OrderValidator
from src.market_orders import MarketOrderExecutor


class TWAPExecutor:
    """Executes TWAP (Time-Weighted Average Price) orders"""
    
    def __init__(self, client: Client, validator: OrderValidator, config: Dict[str, Any]):
        """
        Initialize TWAP executor
        
        Args:
            client: Binance client instance
            validator: Order validator instance
            config: TWAP configuration
        """
        self.client = client
        self.validator = validator
        self.logger = get_logger()
        self.market_executor = MarketOrderExecutor(client, validator)
        
        # TWAP configuration
        self.default_chunks = config.get('default_chunks', 5)
        self.default_interval = config.get('default_interval_seconds', 60)
        self.min_chunk_size = config.get('min_chunk_size_usdt', 10)
    
    def execute_twap_order(self, symbol: str, side: str, total_quantity: float,
                          chunks: Optional[int] = None, 
                          interval_seconds: Optional[int] = None,
                          use_limit: bool = False,
                          limit_offset_percent: float = 0.1) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a TWAP order by splitting into chunks
        
        Args:
            symbol: Trading symbol
            side: Order side (BUY or SELL)
            total_quantity: Total quantity to execute
            chunks: Number of chunks (default from config)
            interval_seconds: Time between chunks (default from config)
            use_limit: Use limit orders instead of market
            limit_offset_percent: Price offset for limit orders
            
        Returns:
            List of executed orders or None if failed
        """
        # Use defaults if not provided
        chunks = chunks or self.default_chunks
        interval_seconds = interval_seconds or self.default_interval
        
        # Validate TWAP parameters
        is_valid, error = self.validator.validate_twap_parameters(
            total_quantity, chunks, interval_seconds
        )
        if not is_valid:
            self.logger.error(f"Invalid TWAP parameters: {error}")
            return None
        
        # Validate symbol and side
        is_valid, error = self.validator.validate_symbol(symbol)
        if not is_valid:
            self.logger.error(f"Invalid symbol: {error}")
            return None
        
        is_valid, error = self.validator.validate_side(side)
        if not is_valid:
            self.logger.error(f"Invalid side: {error}")
            return None
        
        # Calculate chunk size
        chunk_size = total_quantity / chunks
        chunk_size = self.validator.format_quantity(chunk_size)
        
        self.logger.info(
            f"Starting TWAP execution: {symbol} {side} "
            f"Total: {total_quantity}, Chunks: {chunks}, "
            f"Chunk Size: {chunk_size}, Interval: {interval_seconds}s"
        )
        
        executed_orders = []
        
        try:
            for i in range(chunks):
                # Adjust last chunk to account for rounding
                if i == chunks - 1:
                    executed_qty = sum(order.get('executedQty', 0) for order in executed_orders)
                    chunk_size = total_quantity - executed_qty
                    chunk_size = self.validator.format_quantity(chunk_size)
                
                self.logger.info(f"Executing TWAP chunk {i+1}/{chunks}: {chunk_size} {symbol}")
                
                # Place order
                if use_limit:
                    # Get current price
                    ticker = self.client.futures_symbol_ticker(symbol=symbol)
                    current_price = float(ticker['price'])
                    
                    # Calculate limit price with offset
                    if side.upper() == 'BUY':
                        limit_price = current_price * (1 - limit_offset_percent / 100)
                    else:
                        limit_price = current_price * (1 + limit_offset_percent / 100)
                    
                    limit_price = self.validator.format_price(limit_price)
                    
                    order = self.market_executor.place_limit_order(
                        symbol=symbol,
                        side=side,
                        quantity=chunk_size,
                        price=limit_price,
                        time_in_force='IOC'  # Immediate or Cancel
                    )
                else:
                    order = self.market_executor.place_market_order(
                        symbol=symbol,
                        side=side,
                        quantity=chunk_size
                    )
                
                if order:
                    executed_orders.append(order)
                    self.logger.info(
                        f"TWAP chunk {i+1}/{chunks} executed: "
                        f"Order ID: {order['orderId']}, "
                        f"Status: {order['status']}"
                    )
                else:
                    self.logger.error(f"Failed to execute TWAP chunk {i+1}/{chunks}")
                
                # Wait before next chunk (except for last chunk)
                if i < chunks - 1:
                    self.logger.debug(f"Waiting {interval_seconds}s before next chunk")
                    time.sleep(interval_seconds)
            
            # Summary
            total_executed = sum(float(order.get('executedQty', 0)) for order in executed_orders)
            avg_price = self._calculate_average_price(executed_orders)
            
            self.logger.info(
                f"TWAP execution completed: "
                f"Executed {total_executed}/{total_quantity}, "
                f"Average Price: {avg_price:.2f}, "
                f"Orders: {len(executed_orders)}/{chunks}"
            )
            
            return executed_orders
            
        except Exception as e:
            self.logger.log_error_trace(e, "execute_twap_order")
            return executed_orders if executed_orders else None
    
    async def execute_twap_order_async(self, symbol: str, side: str, total_quantity: float,
                                      chunks: Optional[int] = None,
                                      interval_seconds: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Execute TWAP order asynchronously
        
        Args:
            symbol: Trading symbol
            side: Order side
            total_quantity: Total quantity
            chunks: Number of chunks
            interval_seconds: Interval between chunks
            
        Returns:
            List of executed orders
        """
        chunks = chunks or self.default_chunks
        interval_seconds = interval_seconds or self.default_interval
        
        # Validate parameters
        is_valid, error = self.validator.validate_twap_parameters(
            total_quantity, chunks, interval_seconds
        )
        if not is_valid:
            self.logger.error(f"Invalid TWAP parameters: {error}")
            return None
        
        chunk_size = total_quantity / chunks
        chunk_size = self.validator.format_quantity(chunk_size)
        
        self.logger.info(f"Starting async TWAP: {chunks} chunks of {chunk_size} every {interval_seconds}s")
        
        executed_orders = []
        
        try:
            for i in range(chunks):
                if i == chunks - 1:
                    executed_qty = sum(float(order.get('executedQty', 0)) for order in executed_orders)
                    chunk_size = total_quantity - executed_qty
                    chunk_size = self.validator.format_quantity(chunk_size)
                
                order = self.market_executor.place_market_order(
                    symbol=symbol,
                    side=side,
                    quantity=chunk_size
                )
                
                if order:
                    executed_orders.append(order)
                
                if i < chunks - 1:
                    await asyncio.sleep(interval_seconds)
            
            return executed_orders
            
        except Exception as e:
            self.logger.log_error_trace(e, "execute_twap_order_async")
            return executed_orders if executed_orders else None
    
    def _calculate_average_price(self, orders: List[Dict[str, Any]]) -> float:
        """
        Calculate average execution price from orders
        
        Args:
            orders: List of order responses
            
        Returns:
            Average execution price
        """
        total_qty = 0.0
        total_value = 0.0
        
        for order in orders:
            qty = float(order.get('executedQty', 0))
            price = float(order.get('avgPrice', 0))
            
            total_qty += qty
            total_value += qty * price
        
        if total_qty > 0:
            return total_value / total_qty
        return 0.0
    
    def get_twap_summary(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary statistics for TWAP execution
        
        Args:
            orders: List of executed orders
            
        Returns:
            Summary dictionary
        """
        if not orders:
            return {}
        
        total_qty = sum(float(order.get('executedQty', 0)) for order in orders)
        avg_price = self._calculate_average_price(orders)
        
        prices = [float(order.get('avgPrice', 0)) for order in orders if order.get('avgPrice')]
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        
        return {
            'total_orders': len(orders),
            'total_quantity': total_qty,
            'average_price': avg_price,
            'min_price': min_price,
            'max_price': max_price,
            'price_range': max_price - min_price,
            'total_value': total_qty * avg_price
        }
