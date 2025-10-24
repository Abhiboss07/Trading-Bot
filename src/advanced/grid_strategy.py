"""
Grid Trading Strategy Module
Automated buy-low/sell-high within a price range
"""

from typing import Optional, Dict, Any, List
from binance.client import Client
from src.logger import get_logger
from src.validator import OrderValidator
from src.market_orders import MarketOrderExecutor


class GridTradingExecutor:
    """Executes grid trading strategy"""
    
    def __init__(self, client: Client, validator: OrderValidator, config: Dict[str, Any]):
        """
        Initialize grid trading executor
        
        Args:
            client: Binance client instance
            validator: Order validator instance
            config: Grid configuration
        """
        self.client = client
        self.validator = validator
        self.logger = get_logger()
        self.market_executor = MarketOrderExecutor(client, validator)
        
        # Grid configuration
        self.default_grid_levels = config.get('default_grid_levels', 10)
        self.min_spacing = config.get('min_grid_spacing_percent', 0.5)
        self.max_spacing = config.get('max_grid_spacing_percent', 5.0)
    
    def create_grid_orders(self, symbol: str, lower_price: float, upper_price: float,
                          total_quantity: float, grid_levels: Optional[int] = None,
                          mode: str = 'neutral') -> Optional[Dict[str, Any]]:
        """
        Create grid trading orders
        
        Args:
            symbol: Trading symbol
            lower_price: Lower price bound
            upper_price: Upper price bound
            total_quantity: Total quantity to distribute across grid
            grid_levels: Number of grid levels (default from config)
            mode: Grid mode ('neutral', 'long', 'short')
            
        Returns:
            Dict with grid orders or None if failed
        """
        grid_levels = grid_levels or self.default_grid_levels
        
        # Validate grid parameters
        is_valid, error = self.validator.validate_grid_parameters(
            lower_price, upper_price, grid_levels
        )
        if not is_valid:
            self.logger.error(f"Invalid grid parameters: {error}")
            return None
        
        # Validate symbol
        is_valid, error = self.validator.validate_symbol(symbol)
        if not is_valid:
            self.logger.error(f"Invalid symbol: {error}")
            return None
        
        # Calculate grid spacing
        price_range = upper_price - lower_price
        grid_spacing = price_range / (grid_levels - 1)
        spacing_percent = (grid_spacing / lower_price) * 100
        
        # Validate spacing
        if spacing_percent < self.min_spacing:
            self.logger.error(f"Grid spacing ({spacing_percent:.2f}%) below minimum ({self.min_spacing}%)")
            return None
        
        if spacing_percent > self.max_spacing:
            self.logger.warning(f"Grid spacing ({spacing_percent:.2f}%) above recommended maximum ({self.max_spacing}%)")
        
        # Calculate quantity per grid level
        qty_per_level = total_quantity / grid_levels
        qty_per_level = self.validator.format_quantity(qty_per_level)
        
        self.logger.info(
            f"Creating grid for {symbol}: "
            f"Range: {lower_price}-{upper_price}, "
            f"Levels: {grid_levels}, "
            f"Spacing: {grid_spacing:.2f} ({spacing_percent:.2f}%), "
            f"Qty/Level: {qty_per_level}"
        )
        
        # Generate grid levels
        grid_prices = []
        for i in range(grid_levels):
            price = lower_price + (i * grid_spacing)
            price = self.validator.format_price(price)
            grid_prices.append(price)
        
        # Get current price
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            self.logger.info(f"Current price: {current_price}")
        except Exception as e:
            self.logger.log_error_trace(e, "get_current_price")
            return None
        
        # Place grid orders based on mode
        buy_orders = []
        sell_orders = []
        
        try:
            if mode == 'neutral':
                # Place buy orders below current price, sell orders above
                for price in grid_prices:
                    if price < current_price:
                        order = self.market_executor.place_limit_order(
                            symbol=symbol,
                            side='BUY',
                            quantity=qty_per_level,
                            price=price,
                            time_in_force='GTC',
                            post_only=True
                        )
                        if order:
                            buy_orders.append(order)
                    elif price > current_price:
                        order = self.market_executor.place_limit_order(
                            symbol=symbol,
                            side='SELL',
                            quantity=qty_per_level,
                            price=price,
                            time_in_force='GTC',
                            post_only=True
                        )
                        if order:
                            sell_orders.append(order)
            
            elif mode == 'long':
                # Only buy orders (accumulate on dips)
                for price in grid_prices:
                    if price <= current_price:
                        order = self.market_executor.place_limit_order(
                            symbol=symbol,
                            side='BUY',
                            quantity=qty_per_level,
                            price=price,
                            time_in_force='GTC',
                            post_only=True
                        )
                        if order:
                            buy_orders.append(order)
            
            elif mode == 'short':
                # Only sell orders (distribute on rallies)
                for price in grid_prices:
                    if price >= current_price:
                        order = self.market_executor.place_limit_order(
                            symbol=symbol,
                            side='SELL',
                            quantity=qty_per_level,
                            price=price,
                            time_in_force='GTC',
                            post_only=True
                        )
                        if order:
                            sell_orders.append(order)
            
            self.logger.info(
                f"Grid created: {len(buy_orders)} buy orders, "
                f"{len(sell_orders)} sell orders"
            )
            
            return {
                'symbol': symbol,
                'mode': mode,
                'grid_levels': grid_levels,
                'lower_price': lower_price,
                'upper_price': upper_price,
                'current_price': current_price,
                'grid_prices': grid_prices,
                'buy_orders': buy_orders,
                'sell_orders': sell_orders,
                'total_orders': len(buy_orders) + len(sell_orders)
            }
            
        except Exception as e:
            self.logger.log_error_trace(e, "create_grid_orders")
            return None
    
    def monitor_and_refill_grid(self, symbol: str, grid_config: Dict[str, Any]) -> bool:
        """
        Monitor grid and refill filled orders
        
        Args:
            symbol: Trading symbol
            grid_config: Grid configuration from create_grid_orders
            
        Returns:
            True if successful, False otherwise
        """
        try:
            buy_orders = grid_config.get('buy_orders', [])
            sell_orders = grid_config.get('sell_orders', [])
            mode = grid_config.get('mode', 'neutral')
            
            # Check buy orders
            for order in buy_orders:
                order_id = order['orderId']
                status = self.market_executor.get_order_status(symbol, order_id)
                
                if status and status['status'] == 'FILLED':
                    self.logger.info(f"Buy order {order_id} filled at {order['price']}")
                    
                    # Place corresponding sell order (if neutral mode)
                    if mode == 'neutral':
                        # Calculate sell price (grid spacing above)
                        grid_spacing = (grid_config['upper_price'] - grid_config['lower_price']) / (grid_config['grid_levels'] - 1)
                        sell_price = float(order['price']) + grid_spacing
                        sell_price = self.validator.format_price(sell_price)
                        
                        new_sell_order = self.market_executor.place_limit_order(
                            symbol=symbol,
                            side='SELL',
                            quantity=float(order['origQty']),
                            price=sell_price,
                            time_in_force='GTC',
                            post_only=True
                        )
                        
                        if new_sell_order:
                            self.logger.info(f"Placed new sell order at {sell_price}")
            
            # Check sell orders
            for order in sell_orders:
                order_id = order['orderId']
                status = self.market_executor.get_order_status(symbol, order_id)
                
                if status and status['status'] == 'FILLED':
                    self.logger.info(f"Sell order {order_id} filled at {order['price']}")
                    
                    # Place corresponding buy order (if neutral mode)
                    if mode == 'neutral':
                        grid_spacing = (grid_config['upper_price'] - grid_config['lower_price']) / (grid_config['grid_levels'] - 1)
                        buy_price = float(order['price']) - grid_spacing
                        buy_price = self.validator.format_price(buy_price)
                        
                        new_buy_order = self.market_executor.place_limit_order(
                            symbol=symbol,
                            side='BUY',
                            quantity=float(order['origQty']),
                            price=buy_price,
                            time_in_force='GTC',
                            post_only=True
                        )
                        
                        if new_buy_order:
                            self.logger.info(f"Placed new buy order at {buy_price}")
            
            return True
            
        except Exception as e:
            self.logger.log_error_trace(e, "monitor_and_refill_grid")
            return False
    
    def cancel_grid(self, symbol: str, grid_config: Dict[str, Any]) -> bool:
        """
        Cancel all grid orders
        
        Args:
            symbol: Trading symbol
            grid_config: Grid configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Cancelling grid for {symbol}")
            
            # Cancel all orders for the symbol
            result = self.market_executor.cancel_all_orders(symbol)
            
            if result:
                self.logger.info(f"Grid cancelled for {symbol}")
            
            return result
            
        except Exception as e:
            self.logger.log_error_trace(e, "cancel_grid")
            return False
    
    def get_grid_statistics(self, symbol: str, grid_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get grid trading statistics
        
        Args:
            symbol: Trading symbol
            grid_config: Grid configuration
            
        Returns:
            Statistics dictionary
        """
        try:
            buy_orders = grid_config.get('buy_orders', [])
            sell_orders = grid_config.get('sell_orders', [])
            
            filled_buys = 0
            filled_sells = 0
            total_buy_value = 0.0
            total_sell_value = 0.0
            
            # Check buy orders
            for order in buy_orders:
                status = self.market_executor.get_order_status(symbol, order['orderId'])
                if status and status['status'] == 'FILLED':
                    filled_buys += 1
                    total_buy_value += float(status['executedQty']) * float(status['avgPrice'])
            
            # Check sell orders
            for order in sell_orders:
                status = self.market_executor.get_order_status(symbol, order['orderId'])
                if status and status['status'] == 'FILLED':
                    filled_sells += 1
                    total_sell_value += float(status['executedQty']) * float(status['avgPrice'])
            
            profit = total_sell_value - total_buy_value
            
            return {
                'total_buy_orders': len(buy_orders),
                'total_sell_orders': len(sell_orders),
                'filled_buys': filled_buys,
                'filled_sells': filled_sells,
                'total_buy_value': total_buy_value,
                'total_sell_value': total_sell_value,
                'realized_profit': profit
            }
            
        except Exception as e:
            self.logger.log_error_trace(e, "get_grid_statistics")
            return {}
