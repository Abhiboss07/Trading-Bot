"""
Test Script for Binance Futures Trading Bot
Run this to verify all components are working correctly
"""

import sys
from src.bot import BinanceFuturesBot
from src.logger import get_logger


def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_initialization():
    """Test bot initialization"""
    print_section("1. Testing Bot Initialization")
    
    try:
        bot = BinanceFuturesBot()
        logger = get_logger()
        logger.info("Bot initialized successfully")
        print("✓ Bot initialization: PASSED")
        return bot
    except Exception as e:
        print(f"✗ Bot initialization: FAILED")
        print(f"  Error: {e}")
        print("\nPlease ensure:")
        print("  1. You have created a .env file with your API credentials")
        print("  2. Your API keys are valid")
        print("  3. All dependencies are installed (pip install -r requirements.txt)")
        return None


def test_configuration(bot: BinanceFuturesBot):
    """Test configuration loading"""
    print_section("2. Testing Configuration")
    
    try:
        # Test config access
        trading_config = bot.config.get_trading_config()
        risk_config = bot.config.get_risk_config()
        
        print(f"✓ Trading config loaded:")
        print(f"  Default Symbol: {trading_config.get('default_symbol')}")
        print(f"  Default Leverage: {trading_config.get('default_leverage')}")
        print(f"  Max Leverage: {trading_config.get('max_leverage')}")
        
        print(f"\n✓ Risk config loaded:")
        print(f"  Max Position Size: {risk_config.get('max_position_size_usdt')} USDT")
        print(f"  Max Open Orders: {risk_config.get('max_open_orders')}")
        
        print(f"\n✓ Testnet Mode: {bot.config.is_testnet()}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test: FAILED")
        print(f"  Error: {e}")
        return False


def test_validation(bot: BinanceFuturesBot):
    """Test validation system"""
    print_section("3. Testing Validation System")
    
    tests_passed = 0
    tests_total = 0
    
    # Test symbol validation
    tests_total += 1
    is_valid, error = bot.validator.validate_symbol("BTCUSDT")
    if is_valid:
        print("✓ Valid symbol (BTCUSDT): PASSED")
        tests_passed += 1
    else:
        print(f"✗ Valid symbol test: FAILED - {error}")
    
    tests_total += 1
    is_valid, error = bot.validator.validate_symbol("INVALID")
    if not is_valid:
        print("✓ Invalid symbol detection: PASSED")
        tests_passed += 1
    else:
        print("✗ Invalid symbol detection: FAILED")
    
    # Test quantity validation
    tests_total += 1
    is_valid, error = bot.validator.validate_quantity(0.001, 50000)
    if is_valid:
        print("✓ Valid quantity: PASSED")
        tests_passed += 1
    else:
        print(f"✗ Valid quantity test: FAILED - {error}")
    
    tests_total += 1
    is_valid, error = bot.validator.validate_quantity(-1)
    if not is_valid:
        print("✓ Invalid quantity detection: PASSED")
        tests_passed += 1
    else:
        print("✗ Invalid quantity detection: FAILED")
    
    # Test price validation
    tests_total += 1
    is_valid, error = bot.validator.validate_price(50000)
    if is_valid:
        print("✓ Valid price: PASSED")
        tests_passed += 1
    else:
        print(f"✗ Valid price test: FAILED - {error}")
    
    tests_total += 1
    is_valid, error = bot.validator.validate_price(-100)
    if not is_valid:
        print("✓ Invalid price detection: PASSED")
        tests_passed += 1
    else:
        print("✗ Invalid price detection: FAILED")
    
    # Test side validation
    tests_total += 1
    is_valid, error = bot.validator.validate_side("BUY")
    if is_valid:
        print("✓ Valid side (BUY): PASSED")
        tests_passed += 1
    else:
        print(f"✗ Valid side test: FAILED - {error}")
    
    tests_total += 1
    is_valid, error = bot.validator.validate_side("INVALID")
    if not is_valid:
        print("✓ Invalid side detection: PASSED")
        tests_passed += 1
    else:
        print("✗ Invalid side detection: FAILED")
    
    # Test TWAP validation
    tests_total += 1
    is_valid, error = bot.validator.validate_twap_parameters(0.01, 5, 60)
    if is_valid:
        print("✓ Valid TWAP parameters: PASSED")
        tests_passed += 1
    else:
        print(f"✗ Valid TWAP test: FAILED - {error}")
    
    # Test Grid validation
    tests_total += 1
    is_valid, error = bot.validator.validate_grid_parameters(45000, 55000, 10)
    if is_valid:
        print("✓ Valid Grid parameters: PASSED")
        tests_passed += 1
    else:
        print(f"✗ Valid Grid test: FAILED - {error}")
    
    print(f"\n📊 Validation Tests: {tests_passed}/{tests_total} passed")
    return tests_passed == tests_total


def test_api_connection(bot: BinanceFuturesBot):
    """Test API connection"""
    print_section("4. Testing API Connection")
    
    try:
        # Test getting account balance
        balance = bot.get_account_balance()
        if balance:
            print("✓ API Connection: SUCCESSFUL")
            print(f"  Available Balance: {balance['available_balance']:.2f} USDT")
            print(f"  Total Wallet: {balance['total_wallet_balance']:.2f} USDT")
            return True
        else:
            print("✗ API Connection: FAILED")
            print("  Could not retrieve account balance")
            return False
    except Exception as e:
        print(f"✗ API Connection: FAILED")
        print(f"  Error: {e}")
        print("\nPlease check:")
        print("  1. Your API keys are correct")
        print("  2. API keys have Futures trading permissions")
        print("  3. You're using testnet keys if USE_TESTNET=true")
        return False


def test_market_data(bot: BinanceFuturesBot):
    """Test market data retrieval"""
    print_section("5. Testing Market Data Retrieval")
    
    try:
        # Test getting current price
        symbol = "BTCUSDT"
        price = bot.get_current_price(symbol)
        
        if price:
            print(f"✓ Market Data: SUCCESSFUL")
            print(f"  Current {symbol} Price: ${price:,.2f}")
            return True
        else:
            print("✗ Market Data: FAILED")
            return False
    except Exception as e:
        print(f"✗ Market Data: FAILED")
        print(f"  Error: {e}")
        return False


def test_logging(bot: BinanceFuturesBot):
    """Test logging system"""
    print_section("6. Testing Logging System")
    
    try:
        logger = get_logger()
        
        # Test different log levels
        logger.debug("Debug message test")
        logger.info("Info message test")
        logger.warning("Warning message test")
        
        # Test structured logging
        logger.log_order(
            action="TEST",
            order_type="MARKET",
            symbol="BTCUSDT",
            quantity=0.001,
            price=50000
        )
        
        logger.log_api_call(
            endpoint="/test",
            method="GET",
            status="SUCCESS"
        )
        
        print("✓ Logging System: WORKING")
        print("  Check bot.log file for detailed logs")
        return True
    except Exception as e:
        print(f"✗ Logging System: FAILED")
        print(f"  Error: {e}")
        return False


def test_position_info(bot: BinanceFuturesBot):
    """Test position information retrieval"""
    print_section("7. Testing Position Information")
    
    try:
        symbol = "BTCUSDT"
        position = bot.get_position(symbol)
        
        if position:
            print(f"✓ Position Info Retrieved:")
            print(f"  Symbol: {position['symbol']}")
            print(f"  Amount: {position['position_amount']}")
            print(f"  Entry Price: {position['entry_price']:.2f}")
            print(f"  Unrealized PnL: {position['unrealized_profit']:.2f} USDT")
        else:
            print(f"✓ Position Info: No open position for {symbol}")
        
        return True
    except Exception as e:
        print(f"✗ Position Info: FAILED")
        print(f"  Error: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  BINANCE FUTURES TRADING BOT - TEST SUITE")
    print("="*60)
    print("\n⚠️  NOTE: This test suite will NOT place any real orders")
    print("   It only tests configuration, validation, and data retrieval\n")
    
    # Initialize bot
    bot = test_initialization()
    if not bot:
        print("\n❌ CRITICAL: Bot initialization failed. Cannot continue tests.")
        return
    
    # Run tests
    results = {
        "Configuration": test_configuration(bot),
        "Validation": test_validation(bot),
        "API Connection": test_api_connection(bot),
        "Market Data": test_market_data(bot),
        "Logging": test_logging(bot),
        "Position Info": test_position_info(bot)
    }
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {test_name:.<40} {status}")
    
    print(f"\n{'='*60}")
    print(f"  Overall: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 All tests passed! Your bot is ready to use.")
        print("\nNext steps:")
        print("  1. Review the README.md for usage examples")
        print("  2. Start with small test orders on testnet")
        print("  3. Monitor bot.log for detailed execution logs")
        print("  4. Try: python main.py balance")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        print("   Check your configuration and API credentials.")
    
    # Cleanup
    bot.shutdown()


if __name__ == '__main__':
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
