"""
OCO (One-Cancels-the-Other) Orders Module
Places take-profit and stop-loss simultaneously
"""

from typing import Optional, Dict, Any, Tuple
from binance.client import Client
from src.logger import get_logger
from src.validator import OrderValidator
from src.limit_orders import LimitOrderExecutor


class OCOOrderExecutor:
    """Executes OCO (One-Cancels-the-Other) orders"""
    
    def __init__(self, client: Client, validator: OrderValidator):
        """
        Initialize OCO order executor
        
        Args:
            client: Binance client instance
            validator: Order validator instance
        """
        self.client = client
        self.validator = validator
        self.logger = get_logger()
        self.limit_executor = LimitOrderExecutor(client, validator)
    
    def place_oco_order(self, symbol: str, side: str, quantity: float,
                       take_profit_price: float, stop_loss_price: float,
                       entry_price: Optional[float] = None) -> Optional[Tuple[Dict, Dict]]:
        """
        Place an OCO order (take-profit and stop-loss)
        
        Args:
            symbol: Trading symbol
            side: Order side for closing position (opposite of entry)
            quantity: Order quantity
            take_profit_price: Take profit trigger price
            stop_loss_price: Stop loss trigger price
            entry_price: Entry price for validation (optional)
            
        Returns:
            Tuple of (take_profit_order, stop_loss_order) or None if failed
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
        
        is_valid, error = self.validator.validate_price(take_profit_price)
        if not is_valid:
            self.logger.error(f"Invalid take profit price: {error}")
            return None
        
        is_valid, error = self.validator.validate_price(stop_loss_price)
        if not is_valid:
            self.logger.error(f"Invalid stop loss price: {error}")
            return None
        
        # Validate price relationship
        side_upper = side.upper()
        if side_upper == 'SELL':
            # For closing long position: TP > entry > SL
            if take_profit_price <= stop_loss_price:
                self.logger.error("For SELL orders: take profit must be above stop loss")
                return None
        else:
            # For closing short position: SL > entry > TP
            if stop_loss_price <= take_profit_price:
                self.logger.error("For BUY orders: stop loss must be above take profit")
                return None
        
        try:
            self.logger.info(f"Placing OCO order for {symbol}: TP={take_profit_price}, SL={stop_loss_price}")
            
            # Place take profit order
            tp_order = self.limit_executor.place_take_profit_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                stop_price=take_profit_price,
                reduce_only=True
            )
            
            if not tp_order:
                self.logger.error("Failed to place take profit order")
                return None
            
            # Place stop loss order
            sl_order = self.limit_executor.place_stop_market_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                stop_price=stop_loss_price,
                reduce_only=True
            )
            
            if not sl_order:
                self.logger.error("Failed to place stop loss order, cancelling take profit")
                # Cancel the take profit order
                self.limit_executor.cancel_order(symbol, tp_order['orderId'])
                return None
            
            self.logger.info(
                f"OCO order placed successfully: "
                f"TP Order ID: {tp_order['orderId']}, "
                f"SL Order ID: {sl_order['orderId']}"
            )
            
            return (tp_order, sl_order)
            
        except Exception as e:
            self.logger.log_error_trace(e, "place_oco_order")
            return None
    
    def place_oco_with_entry(self, symbol: str, entry_side: str, quantity: float,
                            entry_price: Optional[float], take_profit_price: float,
                            stop_loss_price: float) -> Optional[Dict[str, Any]]:
        """
        Place entry order with OCO exit orders
        
        Args:
            symbol: Trading symbol
            entry_side: Entry order side (BUY or SELL)
            quantity: Order quantity
            entry_price: Entry limit price (None for market)
            take_profit_price: Take profit price
            stop_loss_price: Stop loss price
            
        Returns:
            Dict with entry and exit orders or None if failed
        """
        try:
            # Determine exit side (opposite of entry)
            exit_side = 'SELL' if entry_side.upper() == 'BUY' else 'BUY'
            
            # Place entry order
            if entry_price is None:
                entry_order = self.limit_executor.place_market_order(
                    symbol=symbol,
                    side=entry_side,
                    quantity=quantity
                )
            else:
                entry_order = self.limit_executor.place_limit_order(
                    symbol=symbol,
                    side=entry_side,
                    quantity=quantity,
                    price=entry_price
                )
            
            if not entry_order:
                self.logger.error("Failed to place entry order")
                return None
            
            self.logger.info(f"Entry order placed: {entry_order['orderId']}")
            
            # Place OCO exit orders
            oco_orders = self.place_oco_order(
                symbol=symbol,
                side=exit_side,
                quantity=quantity,
                take_profit_price=take_profit_price,
                stop_loss_price=stop_loss_price,
                entry_price=entry_price
            )
            
            if not oco_orders:
                self.logger.warning("Failed to place OCO orders, but entry order is active")
                return {
                    'entry_order': entry_order,
                    'oco_orders': None
                }
            
            return {
                'entry_order': entry_order,
                'take_profit_order': oco_orders[0],
                'stop_loss_order': oco_orders[1]
            }
            
        except Exception as e:
            self.logger.log_error_trace(e, "place_oco_with_entry")
            return None
    
    def monitor_oco_orders(self, symbol: str, tp_order_id: int, 
                          sl_order_id: int) -> Optional[str]:
        """
        Monitor OCO orders and cancel the other when one is filled
        
        Args:
            symbol: Trading symbol
            tp_order_id: Take profit order ID
            sl_order_id: Stop loss order ID
            
        Returns:
            'TP' if take profit filled, 'SL' if stop loss filled, None if both active
        """
        try:
            # Check take profit order
            tp_status = self.limit_executor.get_order_status(symbol, tp_order_id)
            if tp_status and tp_status['status'] == 'FILLED':
                self.logger.info(f"Take profit order {tp_order_id} filled, cancelling stop loss")
                self.limit_executor.cancel_order(symbol, sl_order_id)
                return 'TP'
            
            # Check stop loss order
            sl_status = self.limit_executor.get_order_status(symbol, sl_order_id)
            if sl_status and sl_status['status'] == 'FILLED':
                self.logger.info(f"Stop loss order {sl_order_id} filled, cancelling take profit")
                self.limit_executor.cancel_order(symbol, tp_order_id)
                return 'SL'
            
            return None
            
        except Exception as e:
            self.logger.log_error_trace(e, "monitor_oco_orders")
            return None
