"""
Main CLI Entry Point for Binance Futures Trading Bot
"""

import sys
import argparse
from typing import Optional
from src.bot import BinanceFuturesBot
from src.logger import get_logger


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description='Binance Futures Trading Bot - Professional CLI Trading Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Market Orders
  python main.py market --symbol BTCUSDT --side BUY --quantity 0.001
  
  # Limit Orders
  python main.py limit --symbol BTCUSDT --side BUY --quantity 0.001 --price 50000
  
  # Stop-Limit Orders
  python main.py stop-limit --symbol BTCUSDT --side SELL --quantity 0.001 --price 49000 --stop-price 49500
  
  # OCO Orders (One-Cancels-Other)
  python main.py oco --symbol BTCUSDT --side SELL --quantity 0.001 --tp-price 52000 --sl-price 48000
  
  # TWAP Orders (Time-Weighted Average Price)
  python main.py twap --symbol BTCUSDT --side BUY --quantity 0.01 --chunks 5 --interval 60
  
  # Grid Trading
  python main.py grid --symbol BTCUSDT --lower-price 45000 --upper-price 55000 --quantity 0.01 --levels 10
  
  # Account Info
  python main.py balance
  python main.py position --symbol BTCUSDT
  python main.py close --symbol BTCUSDT
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Market order
    market_parser = subparsers.add_parser('market', help='Place market order')
    market_parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTCUSDT)')
    market_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    market_parser.add_argument('--quantity', type=float, required=True, help='Order quantity')
    market_parser.add_argument('--reduce-only', action='store_true', help='Reduce only mode')
    
    # Limit order
    limit_parser = subparsers.add_parser('limit', help='Place limit order')
    limit_parser.add_argument('--symbol', required=True, help='Trading symbol')
    limit_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    limit_parser.add_argument('--quantity', type=float, required=True, help='Order quantity')
    limit_parser.add_argument('--price', type=float, required=True, help='Limit price')
    limit_parser.add_argument('--tif', default='GTC', choices=['GTC', 'IOC', 'FOK'], help='Time in force')
    limit_parser.add_argument('--post-only', action='store_true', help='Post-only (maker) order')
    
    # Stop-limit order
    stop_parser = subparsers.add_parser('stop-limit', help='Place stop-limit order')
    stop_parser.add_argument('--symbol', required=True, help='Trading symbol')
    stop_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    stop_parser.add_argument('--quantity', type=float, required=True, help='Order quantity')
    stop_parser.add_argument('--price', type=float, required=True, help='Limit price')
    stop_parser.add_argument('--stop-price', type=float, required=True, help='Stop trigger price')
    
    # OCO order
    oco_parser = subparsers.add_parser('oco', help='Place OCO order (take-profit + stop-loss)')
    oco_parser.add_argument('--symbol', required=True, help='Trading symbol')
    oco_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Exit order side')
    oco_parser.add_argument('--quantity', type=float, required=True, help='Order quantity')
    oco_parser.add_argument('--tp-price', type=float, required=True, help='Take profit price')
    oco_parser.add_argument('--sl-price', type=float, required=True, help='Stop loss price')
    
    # TWAP order
    twap_parser = subparsers.add_parser('twap', help='Execute TWAP order')
    twap_parser.add_argument('--symbol', required=True, help='Trading symbol')
    twap_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    twap_parser.add_argument('--quantity', type=float, required=True, help='Total quantity')
    twap_parser.add_argument('--chunks', type=int, help='Number of chunks (default: 5)')
    twap_parser.add_argument('--interval', type=int, help='Interval in seconds (default: 60)')
    
    # Grid trading
    grid_parser = subparsers.add_parser('grid', help='Create grid trading orders')
    grid_parser.add_argument('--symbol', required=True, help='Trading symbol')
    grid_parser.add_argument('--lower-price', type=float, required=True, help='Lower price bound')
    grid_parser.add_argument('--upper-price', type=float, required=True, help='Upper price bound')
    grid_parser.add_argument('--quantity', type=float, required=True, help='Total quantity')
    grid_parser.add_argument('--levels', type=int, help='Number of grid levels (default: 10)')
    grid_parser.add_argument('--mode', choices=['neutral', 'long', 'short'], default='neutral', help='Grid mode')
    
    # Account commands
    subparsers.add_parser('balance', help='Get account balance')
    
    position_parser = subparsers.add_parser('position', help='Get position info')
    position_parser.add_argument('--symbol', required=True, help='Trading symbol')
    
    close_parser = subparsers.add_parser('close', help='Close position')
    close_parser.add_argument('--symbol', required=True, help='Trading symbol')
    close_parser.add_argument('--percentage', type=float, default=100.0, help='Percentage to close (default: 100)')
    
    # Leverage
    leverage_parser = subparsers.add_parser('leverage', help='Set leverage')
    leverage_parser.add_argument('--symbol', required=True, help='Trading symbol')
    leverage_parser.add_argument('--leverage', type=int, required=True, help='Leverage value')
    
    # Cancel orders
    cancel_parser = subparsers.add_parser('cancel', help='Cancel all orders')
    cancel_parser.add_argument('--symbol', required=True, help='Trading symbol')
    
    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize bot
    try:
        bot = BinanceFuturesBot()
        logger = get_logger()
    except Exception as e:
        print(f"Error initializing bot: {e}")
        print("Make sure you have created a .env file with your API credentials.")
        print("See .env.example for reference.")
        return
    
    try:
        # Execute command
        if args.command == 'market':
            logger.info(f"Executing market order: {args.side} {args.quantity} {args.symbol}")
            order = bot.market_executor.place_market_order(
                symbol=args.symbol,
                side=args.side,
                quantity=args.quantity,
                reduce_only=args.reduce_only
            )
            if order:
                print(f"✓ Market order placed successfully")
                print(f"  Order ID: {order['orderId']}")
                print(f"  Status: {order['status']}")
            else:
                print("✗ Failed to place market order")
        
        elif args.command == 'limit':
            logger.info(f"Executing limit order: {args.side} {args.quantity} {args.symbol} @ {args.price}")
            order = bot.limit_executor.place_limit_order(
                symbol=args.symbol,
                side=args.side,
                quantity=args.quantity,
                price=args.price,
                time_in_force=args.tif,
                post_only=args.post_only
            )
            if order:
                print(f"✓ Limit order placed successfully")
                print(f"  Order ID: {order['orderId']}")
                print(f"  Price: {args.price}")
                print(f"  Status: {order['status']}")
            else:
                print("✗ Failed to place limit order")
        
        elif args.command == 'stop-limit':
            logger.info(f"Executing stop-limit order: {args.side} {args.quantity} {args.symbol}")
            order = bot.limit_executor.place_stop_limit_order(
                symbol=args.symbol,
                side=args.side,
                quantity=args.quantity,
                price=args.price,
                stop_price=args.stop_price
            )
            if order:
                print(f"✓ Stop-limit order placed successfully")
                print(f"  Order ID: {order['orderId']}")
                print(f"  Stop Price: {args.stop_price}")
                print(f"  Limit Price: {args.price}")
            else:
                print("✗ Failed to place stop-limit order")
        
        elif args.command == 'oco':
            logger.info(f"Executing OCO order: {args.symbol}")
            result = bot.oco_executor.place_oco_order(
                symbol=args.symbol,
                side=args.side,
                quantity=args.quantity,
                take_profit_price=args.tp_price,
                stop_loss_price=args.sl_price
            )
            if result:
                tp_order, sl_order = result
                print(f"✓ OCO orders placed successfully")
                print(f"  Take Profit Order ID: {tp_order['orderId']} @ {args.tp_price}")
                print(f"  Stop Loss Order ID: {sl_order['orderId']} @ {args.sl_price}")
            else:
                print("✗ Failed to place OCO orders")
        
        elif args.command == 'twap':
            logger.info(f"Executing TWAP order: {args.side} {args.quantity} {args.symbol}")
            orders = bot.twap_executor.execute_twap_order(
                symbol=args.symbol,
                side=args.side,
                total_quantity=args.quantity,
                chunks=args.chunks,
                interval_seconds=args.interval
            )
            if orders:
                summary = bot.twap_executor.get_twap_summary(orders)
                print(f"✓ TWAP execution completed")
                print(f"  Total Orders: {summary['total_orders']}")
                print(f"  Total Quantity: {summary['total_quantity']}")
                print(f"  Average Price: {summary['average_price']:.2f}")
                print(f"  Price Range: {summary['min_price']:.2f} - {summary['max_price']:.2f}")
            else:
                print("✗ TWAP execution failed")
        
        elif args.command == 'grid':
            logger.info(f"Creating grid for {args.symbol}")
            result = bot.grid_executor.create_grid_orders(
                symbol=args.symbol,
                lower_price=args.lower_price,
                upper_price=args.upper_price,
                total_quantity=args.quantity,
                grid_levels=args.levels,
                mode=args.mode
            )
            if result:
                print(f"✓ Grid created successfully")
                print(f"  Mode: {result['mode']}")
                print(f"  Grid Levels: {result['grid_levels']}")
                print(f"  Price Range: {result['lower_price']} - {result['upper_price']}")
                print(f"  Buy Orders: {len(result['buy_orders'])}")
                print(f"  Sell Orders: {len(result['sell_orders'])}")
                print(f"  Total Orders: {result['total_orders']}")
            else:
                print("✗ Failed to create grid")
        
        elif args.command == 'balance':
            balance = bot.get_account_balance()
            if balance:
                print(f"\n📊 Account Balance:")
                print(f"  Available: {balance['available_balance']:.2f} USDT")
                print(f"  Total Wallet: {balance['total_wallet_balance']:.2f} USDT")
                print(f"  Unrealized PnL: {balance['total_unrealized_profit']:.2f} USDT")
                print(f"  Margin Balance: {balance['total_margin_balance']:.2f} USDT")
            else:
                print("✗ Failed to get balance")
        
        elif args.command == 'position':
            position = bot.get_position(args.symbol)
            if position:
                print(f"\n📈 Position for {args.symbol}:")
                print(f"  Amount: {position['position_amount']}")
                print(f"  Entry Price: {position['entry_price']:.2f}")
                print(f"  Unrealized PnL: {position['unrealized_profit']:.2f} USDT")
                print(f"  Leverage: {position['leverage']}x")
                print(f"  Margin Type: {position['margin_type']}")
                
                # Show risk metrics
                metrics = bot.get_risk_metrics(args.symbol)
                if metrics:
                    print(f"\n⚠️  Risk Metrics:")
                    print(f"  Position Value: {metrics['position_value_usdt']:.2f} USDT")
                    print(f"  Position %: {metrics['position_percentage']:.2f}%")
                    print(f"  PnL %: {metrics['unrealized_pnl_percentage']:.2f}%")
            else:
                print(f"No open position for {args.symbol}")
        
        elif args.command == 'close':
            success = bot.close_position(args.symbol, args.percentage)
            if success:
                print(f"✓ Position closed successfully ({args.percentage}%)")
            else:
                print("✗ Failed to close position")
        
        elif args.command == 'leverage':
            success = bot.set_leverage(args.symbol, args.leverage)
            if success:
                print(f"✓ Leverage set to {args.leverage}x for {args.symbol}")
            else:
                print("✗ Failed to set leverage")
        
        elif args.command == 'cancel':
            success = bot.market_executor.cancel_all_orders(args.symbol)
            if success:
                print(f"✓ All orders cancelled for {args.symbol}")
            else:
                print("✗ Failed to cancel orders")
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        print("\n\nInterrupted by user")
    except Exception as e:
        logger.log_error_trace(e, "main")
        print(f"\n✗ Error: {e}")
    finally:
        bot.shutdown()


if __name__ == '__main__':
    main()
