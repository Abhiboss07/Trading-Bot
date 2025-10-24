"""
Example Usage Scripts for Binance Futures Trading Bot
Demonstrates all major features with practical examples
"""

from src.bot import BinanceFuturesBot
from src.logger import get_logger
import time


def example_1_basic_market_order():
    """Example 1: Place a basic market order"""
    print("\n" + "="*60)
    print("Example 1: Basic Market Order")
    print("="*60 + "\n")
    
    bot = BinanceFuturesBot()
    
    # Set leverage
    bot.set_leverage("BTCUSDT", 1)
    
    # Place market buy order
    order = bot.market_executor.place_market_order(
        symbol="BTCUSDT",
        side="BUY",
        quantity=0.001
    )
    
    if order:
        print(f"✓ Order placed: {order['orderId']}")
        print(f"  Status: {order['status']}")
    
    bot.shutdown()


def example_2_limit_order_with_monitoring():
    """Example 2: Place limit order and monitor until filled"""
    print("\n" + "="*60)
    print("Example 2: Limit Order with Monitoring")
    print("="*60 + "\n")
    
    bot = BinanceFuturesBot()
    
    # Get current price
    current_price = bot.get_current_price("BTCUSDT")
    print(f"Current price: ${current_price:,.2f}")
    
    # Place limit order 1% below current price
    limit_price = current_price * 0.99
    
    order = bot.limit_executor.place_limit_order(
        symbol="BTCUSDT",
        side="BUY",
        quantity=0.001,
        price=limit_price,
        time_in_force="GTC"
    )
    
    if order:
        print(f"✓ Limit order placed at ${limit_price:,.2f}")
        print(f"  Order ID: {order['orderId']}")
        
        # Monitor order status (for demo, check a few times)
        for i in range(3):
            time.sleep(2)
            status = bot.market_executor.get_order_status("BTCUSDT", order['orderId'])
            if status:
                print(f"  Status check {i+1}: {status['status']}")
                if status['status'] == 'FILLED':
                    print("  ✓ Order filled!")
                    break
    
    bot.shutdown()


def example_3_oco_order():
    """Example 3: OCO order (take-profit and stop-loss)"""
    print("\n" + "="*60)
    print("Example 3: OCO Order (Take-Profit + Stop-Loss)")
    print("="*60 + "\n")
    
    bot = BinanceFuturesBot()
    
    # First, open a position
    print("Step 1: Opening position...")
    entry_order = bot.market_executor.place_market_order(
        symbol="BTCUSDT",
        side="BUY",
        quantity=0.001
    )
    
    if not entry_order:
        print("Failed to open position")
        bot.shutdown()
        return
    
    print(f"✓ Position opened: {entry_order['orderId']}")
    
    # Get entry price
    time.sleep(1)
    position = bot.get_position("BTCUSDT")
    if not position:
        print("Could not get position info")
        bot.shutdown()
        return
    
    entry_price = position['entry_price']
    print(f"  Entry price: ${entry_price:,.2f}")
    
    # Set OCO orders (2% profit, 1% loss)
    tp_price = entry_price * 1.02
    sl_price = entry_price * 0.99
    
    print("\nStep 2: Setting OCO orders...")
    oco_result = bot.oco_executor.place_oco_order(
        symbol="BTCUSDT",
        side="SELL",
        quantity=0.001,
        take_profit_price=tp_price,
        stop_loss_price=sl_price
    )
    
    if oco_result:
        tp_order, sl_order = oco_result
        print(f"✓ OCO orders placed:")
        print(f"  Take Profit: ${tp_price:,.2f} (Order: {tp_order['orderId']})")
        print(f"  Stop Loss: ${sl_price:,.2f} (Order: {sl_order['orderId']})")
    
    bot.shutdown()


def example_4_twap_execution():
    """Example 4: TWAP order execution"""
    print("\n" + "="*60)
    print("Example 4: TWAP Order Execution")
    print("="*60 + "\n")
    
    bot = BinanceFuturesBot()
    
    print("Executing TWAP order: 0.003 BTC in 3 chunks, 5 seconds apart")
    
    orders = bot.twap_executor.execute_twap_order(
        symbol="BTCUSDT",
        side="BUY",
        total_quantity=0.003,
        chunks=3,
        interval_seconds=5
    )
    
    if orders:
        summary = bot.twap_executor.get_twap_summary(orders)
        print(f"\n✓ TWAP execution completed:")
        print(f"  Total Orders: {summary['total_orders']}")
        print(f"  Total Quantity: {summary['total_quantity']}")
        print(f"  Average Price: ${summary['average_price']:,.2f}")
        print(f"  Price Range: ${summary['min_price']:,.2f} - ${summary['max_price']:,.2f}")
        print(f"  Total Value: ${summary['total_value']:,.2f}")
    
    bot.shutdown()


def example_5_grid_trading():
    """Example 5: Grid trading strategy"""
    print("\n" + "="*60)
    print("Example 5: Grid Trading Strategy")
    print("="*60 + "\n")
    
    bot = BinanceFuturesBot()
    
    # Get current price
    current_price = bot.get_current_price("BTCUSDT")
    print(f"Current price: ${current_price:,.2f}")
    
    # Create grid 5% below to 5% above current price
    lower_price = current_price * 0.95
    upper_price = current_price * 1.05
    
    print(f"\nCreating grid:")
    print(f"  Lower: ${lower_price:,.2f}")
    print(f"  Upper: ${upper_price:,.2f}")
    print(f"  Levels: 5")
    
    grid_result = bot.grid_executor.create_grid_orders(
        symbol="BTCUSDT",
        lower_price=lower_price,
        upper_price=upper_price,
        total_quantity=0.005,
        grid_levels=5,
        mode='neutral'
    )
    
    if grid_result:
        print(f"\n✓ Grid created successfully:")
        print(f"  Buy Orders: {len(grid_result['buy_orders'])}")
        print(f"  Sell Orders: {len(grid_result['sell_orders'])}")
        print(f"  Total Orders: {grid_result['total_orders']}")
        
        print(f"\n  Grid Prices:")
        for i, price in enumerate(grid_result['grid_prices'], 1):
            print(f"    Level {i}: ${price:,.2f}")
    
    bot.shutdown()


def example_6_risk_management():
    """Example 6: Risk management and position monitoring"""
    print("\n" + "="*60)
    print("Example 6: Risk Management & Position Monitoring")
    print("="*60 + "\n")
    
    bot = BinanceFuturesBot()
    
    # Check account balance
    print("Step 1: Account Overview")
    balance = bot.get_account_balance()
    if balance:
        print(f"  Available Balance: ${balance['available_balance']:,.2f}")
        print(f"  Total Wallet: ${balance['total_wallet_balance']:,.2f}")
        print(f"  Unrealized PnL: ${balance['total_unrealized_profit']:,.2f}")
    
    # Check position
    print("\nStep 2: Position Analysis")
    position = bot.get_position("BTCUSDT")
    if position:
        print(f"  Position Size: {position['position_amount']} BTC")
        print(f"  Entry Price: ${position['entry_price']:,.2f}")
        print(f"  Unrealized PnL: ${position['unrealized_profit']:,.2f}")
        print(f"  Leverage: {position['leverage']}x")
        
        # Get risk metrics
        print("\nStep 3: Risk Metrics")
        metrics = bot.get_risk_metrics("BTCUSDT")
        if metrics:
            print(f"  Position Value: ${metrics['position_value_usdt']:,.2f}")
            print(f"  Position %: {metrics['position_percentage']:.2f}%")
            print(f"  PnL %: {metrics['unrealized_pnl_percentage']:.2f}%")
            print(f"  Effective Exposure: ${metrics['effective_exposure']:,.2f}")
    else:
        print("  No open position")
    
    # Check risk limits before placing order
    print("\nStep 4: Risk Limit Check")
    current_price = bot.get_current_price("BTCUSDT")
    is_safe, error = bot.check_risk_limits("BTCUSDT", 0.01, current_price)
    
    if is_safe:
        print("  ✓ Order would be within risk limits")
    else:
        print(f"  ✗ Risk limit exceeded: {error}")
    
    bot.shutdown()


def example_7_complete_trading_workflow():
    """Example 7: Complete trading workflow"""
    print("\n" + "="*60)
    print("Example 7: Complete Trading Workflow")
    print("="*60 + "\n")
    
    bot = BinanceFuturesBot()
    logger = get_logger()
    
    symbol = "BTCUSDT"
    
    # Step 1: Setup
    print("Step 1: Account Setup")
    bot.set_leverage(symbol, 2)
    bot.set_margin_type(symbol, "CROSSED")
    
    # Step 2: Market Analysis
    print("\nStep 2: Market Analysis")
    current_price = bot.get_current_price(symbol)
    print(f"  Current {symbol} Price: ${current_price:,.2f}")
    
    # Step 3: Entry
    print("\nStep 3: Entry Order")
    entry_qty = 0.001
    entry_order = bot.market_executor.place_market_order(
        symbol=symbol,
        side="BUY",
        quantity=entry_qty
    )
    
    if not entry_order:
        print("  Failed to enter position")
        bot.shutdown()
        return
    
    print(f"  ✓ Entered position: {entry_order['orderId']}")
    
    # Step 4: Get position info
    time.sleep(1)
    position = bot.get_position(symbol)
    if not position:
        print("  Could not get position")
        bot.shutdown()
        return
    
    entry_price = position['entry_price']
    print(f"  Entry Price: ${entry_price:,.2f}")
    
    # Step 5: Set protective orders
    print("\nStep 4: Setting Protective Orders")
    tp_price = entry_price * 1.03  # 3% profit target
    sl_price = entry_price * 0.98  # 2% stop loss
    
    oco_result = bot.oco_executor.place_oco_order(
        symbol=symbol,
        side="SELL",
        quantity=entry_qty,
        take_profit_price=tp_price,
        stop_loss_price=sl_price
    )
    
    if oco_result:
        print(f"  ✓ Take Profit: ${tp_price:,.2f}")
        print(f"  ✓ Stop Loss: ${sl_price:,.2f}")
    
    # Step 6: Monitor
    print("\nStep 5: Position Monitoring")
    metrics = bot.get_risk_metrics(symbol)
    if metrics:
        print(f"  Position Value: ${metrics['position_value_usdt']:,.2f}")
        print(f"  Current PnL: ${metrics['unrealized_pnl_usdt']:,.2f}")
        print(f"  Risk/Reward Ratio: 1:{(tp_price - entry_price) / (entry_price - sl_price):.2f}")
    
    print("\n✓ Complete workflow executed successfully!")
    print("  Check bot.log for detailed execution logs")
    
    bot.shutdown()


def run_all_examples():
    """Run all examples (for demonstration)"""
    print("\n" + "="*70)
    print("  BINANCE FUTURES TRADING BOT - EXAMPLE USAGE")
    print("="*70)
    print("\n⚠️  WARNING: These examples will place REAL orders on your account!")
    print("   Make sure you're using TESTNET (USE_TESTNET=true in .env)")
    print("   Press Ctrl+C to cancel\n")
    
    try:
        input("Press Enter to continue or Ctrl+C to cancel...")
    except KeyboardInterrupt:
        print("\nCancelled by user")
        return
    
    examples = [
        ("Basic Market Order", example_1_basic_market_order),
        ("Limit Order with Monitoring", example_2_limit_order_with_monitoring),
        ("OCO Order", example_3_oco_order),
        ("TWAP Execution", example_4_twap_execution),
        ("Grid Trading", example_5_grid_trading),
        ("Risk Management", example_6_risk_management),
        ("Complete Workflow", example_7_complete_trading_workflow)
    ]
    
    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\n  0. Run all examples")
    print("  q. Quit")
    
    choice = input("\nSelect example (0-7, q): ").strip()
    
    if choice.lower() == 'q':
        print("Exiting...")
        return
    
    try:
        choice_num = int(choice)
        if choice_num == 0:
            # Run all
            for name, func in examples:
                print(f"\n\nRunning: {name}")
                try:
                    func()
                    time.sleep(2)
                except Exception as e:
                    print(f"Error in {name}: {e}")
        elif 1 <= choice_num <= len(examples):
            # Run selected
            name, func = examples[choice_num - 1]
            print(f"\n\nRunning: {name}")
            func()
        else:
            print("Invalid choice")
    except ValueError:
        print("Invalid input")
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_examples()
