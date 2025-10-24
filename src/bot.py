"""
Main Trading Bot Module
Orchestrates all trading functionality
"""

from typing import Optional, Dict, Any
from binance.client import Client
from src.config_loader import ConfigLoader
from src.logger import get_logger, BotLogger
from src.validator import OrderValidator
from src.market_orders import MarketOrderExecutor
from src.limit_orders import LimitOrderExecutor
from src.advanced.oco import OCOOrderExecutor
from src.advanced.twap import TWAPExecutor
from src.advanced.grid_strategy import GridTradingExecutor


class BinanceFuturesBot:
    """Main trading bot class"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the trading bot
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = ConfigLoader(config_path)
        
        # Initialize logger
        log_config = self.config.get_logging_config()
        self.logger = get_logger(
            name="BinanceFuturesBot",
            log_file=log_config.get('log_file', 'bot.log'),
            level=log_config.get('level', 'INFO'),
            max_bytes=log_config.get('max_log_size_mb', 50) * 1024 * 1024,
            backup_count=log_config.get('backup_count', 5)
        )
        
        # Initialize Binance client
        api_key, api_secret = self.config.get_api_credentials()
        
        if self.config.is_testnet():
            self.logger.info("Initializing bot in TESTNET mode")
            self.client = Client(api_key, api_secret, testnet=True)
            # Set testnet URL
            self.client.API_URL = 'https://testnet.binancefuture.com'
        else:
            self.logger.warning("Initializing bot in PRODUCTION mode")
            self.client = Client(api_key, api_secret)
        
        # Initialize validator
        validation_config = self.config.get_validation_config()
        self.validator = OrderValidator(validation_config)
        
        # Initialize executors
        self.market_executor = MarketOrderExecutor(self.client, self.validator)
        self.limit_executor = LimitOrderExecutor(self.client, self.validator)
        self.oco_executor = OCOOrderExecutor(self.client, self.validator)
        
        # Initialize advanced executors
        execution_config = self.config.get_execution_config()
        self.twap_executor = TWAPExecutor(
            self.client, 
            self.validator, 
            execution_config.get('twap', {})
        )
        self.grid_executor = GridTradingExecutor(
            self.client, 
            self.validator, 
            execution_config.get('grid', {})
        )
        
        # Trading configuration
        self.trading_config = self.config.get_trading_config()
        self.risk_config = self.config.get_risk_config()
        
        self.logger.info("Trading bot initialized successfully")
    
    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """
        Set leverage for a symbol
        
        Args:
            symbol: Trading symbol
            leverage: Leverage value
            
        Returns:
            True if successful, False otherwise
        """
        # Validate leverage
        max_leverage = self.trading_config.get('max_leverage', 20)
        is_valid, error = self.validator.validate_leverage(leverage, max_leverage)
        if not is_valid:
            self.logger.error(f"Invalid leverage: {error}")
            return False
        
        try:
            self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
            self.logger.info(f"Leverage set to {leverage}x for {symbol}")
            return True
        except Exception as e:
            self.logger.log_error_trace(e, "set_leverage")
            return False
    
    def set_margin_type(self, symbol: str, margin_type: str = 'CROSSED') -> bool:
        """
        Set margin type for a symbol
        
        Args:
            symbol: Trading symbol
            margin_type: ISOLATED or CROSSED
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.futures_change_margin_type(symbol=symbol, marginType=margin_type)
            self.logger.info(f"Margin type set to {margin_type} for {symbol}")
            return True
        except Exception as e:
            # Margin type might already be set
            if 'No need to change margin type' in str(e):
                self.logger.info(f"Margin type already set to {margin_type} for {symbol}")
                return True
            self.logger.log_error_trace(e, "set_margin_type")
            return False
    
    def get_account_balance(self) -> Optional[Dict[str, Any]]:
        """
        Get account balance
        
        Returns:
            Account balance dict or None if failed
        """
        try:
            account = self.client.futures_account()
            balance = {
                'total_wallet_balance': float(account['totalWalletBalance']),
                'total_unrealized_profit': float(account['totalUnrealizedProfit']),
                'total_margin_balance': float(account['totalMarginBalance']),
                'available_balance': float(account['availableBalance']),
                'max_withdraw_amount': float(account['maxWithdrawAmount'])
            }
            
            self.logger.info(
                f"Account Balance: {balance['available_balance']:.2f} USDT available, "
                f"Total: {balance['total_wallet_balance']:.2f} USDT"
            )
            
            return balance
        except Exception as e:
            self.logger.log_error_trace(e, "get_account_balance")
            return None
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current position for a symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Position dict or None if no position
        """
        try:
            positions = self.client.futures_position_information(symbol=symbol)
            
            for pos in positions:
                if float(pos['positionAmt']) != 0:
                    position = {
                        'symbol': pos['symbol'],
                        'position_amount': float(pos['positionAmt']),
                        'entry_price': float(pos['entryPrice']),
                        'unrealized_profit': float(pos['unRealizedProfit']),
                        'leverage': int(pos['leverage']),
                        'margin_type': pos['marginType']
                    }
                    
                    self.logger.info(
                        f"Position: {position['position_amount']} {symbol} @ {position['entry_price']}, "
                        f"PnL: {position['unrealized_profit']:.2f} USDT"
                    )
                    
                    return position
            
            self.logger.info(f"No open position for {symbol}")
            return None
            
        except Exception as e:
            self.logger.log_error_trace(e, "get_position")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current market price for a symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Current price or None if failed
        """
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            self.logger.debug(f"Current price for {symbol}: {price}")
            return price
        except Exception as e:
            self.logger.log_error_trace(e, "get_current_price")
            return None
    
    def close_position(self, symbol: str, percentage: float = 100.0) -> bool:
        """
        Close position for a symbol
        
        Args:
            symbol: Trading symbol
            percentage: Percentage of position to close (default 100%)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current position
            position = self.get_position(symbol)
            if not position:
                self.logger.warning(f"No position to close for {symbol}")
                return False
            
            position_amt = position['position_amount']
            
            # Calculate quantity to close
            close_qty = abs(position_amt) * (percentage / 100.0)
            close_qty = self.validator.format_quantity(close_qty)
            
            # Determine side (opposite of position)
            side = 'SELL' if position_amt > 0 else 'BUY'
            
            self.logger.info(f"Closing {percentage}% of position: {close_qty} {symbol}")
            
            # Place market order to close
            order = self.market_executor.place_market_order(
                symbol=symbol,
                side=side,
                quantity=close_qty,
                reduce_only=True
            )
            
            if order:
                self.logger.info(f"Position closed successfully: Order ID {order['orderId']}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.log_error_trace(e, "close_position")
            return False
    
    def get_risk_metrics(self, symbol: str) -> Dict[str, Any]:
        """
        Calculate risk metrics for current position
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Risk metrics dictionary
        """
        try:
            position = self.get_position(symbol)
            if not position:
                return {}
            
            balance = self.get_account_balance()
            if not balance:
                return {}
            
            current_price = self.get_current_price(symbol)
            if not current_price:
                return {}
            
            position_value = abs(position['position_amount']) * current_price
            account_value = balance['total_wallet_balance']
            
            risk_metrics = {
                'position_value_usdt': position_value,
                'account_value_usdt': account_value,
                'position_percentage': (position_value / account_value) * 100 if account_value > 0 else 0,
                'unrealized_pnl_usdt': position['unrealized_profit'],
                'unrealized_pnl_percentage': (position['unrealized_profit'] / account_value) * 100 if account_value > 0 else 0,
                'leverage': position['leverage'],
                'effective_exposure': position_value * position['leverage']
            }
            
            self.logger.info(
                f"Risk Metrics: Position {risk_metrics['position_percentage']:.2f}% of account, "
                f"PnL: {risk_metrics['unrealized_pnl_percentage']:.2f}%"
            )
            
            return risk_metrics
            
        except Exception as e:
            self.logger.log_error_trace(e, "get_risk_metrics")
            return {}
    
    def check_risk_limits(self, symbol: str, quantity: float, price: float) -> tuple[bool, Optional[str]]:
        """
        Check if order complies with risk limits
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            price: Order price
            
        Returns:
            Tuple of (is_within_limits, error_message)
        """
        try:
            # Calculate order value
            order_value = quantity * price
            
            # Check against max position size
            max_position = self.risk_config.get('max_position_size_usdt', 1000)
            if order_value > max_position:
                return False, f"Order value ({order_value:.2f} USDT) exceeds max position size ({max_position} USDT)"
            
            # Check account balance
            balance = self.get_account_balance()
            if balance:
                available = balance['available_balance']
                if order_value > available:
                    return False, f"Insufficient balance: {available:.2f} USDT available, {order_value:.2f} USDT required"
            
            # Check max open orders
            open_orders = self.market_executor.get_open_orders(symbol)
            max_orders = self.risk_config.get('max_open_orders', 10)
            if len(open_orders) >= max_orders:
                return False, f"Maximum open orders ({max_orders}) reached"
            
            return True, None
            
        except Exception as e:
            self.logger.log_error_trace(e, "check_risk_limits")
            return False, "Error checking risk limits"
    
    def shutdown(self):
        """Shutdown the bot gracefully"""
        self.logger.info("Shutting down trading bot...")
        self.logger.info("Bot shutdown complete")
