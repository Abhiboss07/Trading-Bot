# 🚀 Quick Reference Card

## Installation (One-Time Setup)

```powershell
# Install dependencies
pip install python-binance requests python-dotenv aiohttp colorlog pyyaml

# Setup environment
copy .env.example .env
notepad .env  # Add your Binance Testnet API keys

# Test installation
python test_bot.py
```

## Essential Commands

### Account Management
```powershell
# Check balance
python main.py balance

# View position
python main.py position --symbol BTCUSDT

# Set leverage
python main.py leverage --symbol BTCUSDT --leverage 10

# Close position
python main.py close --symbol BTCUSDT
```

### Basic Orders
```powershell
# Market Buy
python main.py market --symbol BTCUSDT --side BUY --quantity 0.001

# Market Sell
python main.py market --symbol BTCUSDT --side SELL --quantity 0.001

# Limit Buy
python main.py limit --symbol BTCUSDT --side BUY --quantity 0.001 --price 50000

# Limit Sell
python main.py limit --symbol BTCUSDT --side SELL --quantity 0.001 --price 52000
```

### Advanced Orders
```powershell
# Stop-Limit
python main.py stop-limit --symbol BTCUSDT --side SELL --quantity 0.001 --stop-price 49500 --price 49000

# OCO (Take-Profit + Stop-Loss)
python main.py oco --symbol BTCUSDT --side SELL --quantity 0.001 --tp-price 52000 --sl-price 48000

# TWAP (5 chunks, 60s interval)
python main.py twap --symbol BTCUSDT --side BUY --quantity 0.01 --chunks 5 --interval 60

# Grid Trading
python main.py grid --symbol BTCUSDT --lower-price 45000 --upper-price 55000 --quantity 0.01 --levels 10
```

### Order Management
```powershell
# Cancel all orders
python main.py cancel --symbol BTCUSDT
```

## File Structure
```
Trading Bot/
├── main.py              # Main CLI
├── test_bot.py          # Test suite
├── examples.py          # Usage examples
├── config.yaml          # Configuration
├── .env                 # API keys (create from .env.example)
├── bot.log              # Execution logs
├── README.md            # Full documentation
├── SETUP_GUIDE.md       # Setup instructions
└── src/                 # Source code
    ├── bot.py
    ├── market_orders.py
    ├── limit_orders.py
    ├── validator.py
    ├── logger.py
    └── advanced/
        ├── oco.py
        ├── twap.py
        └── grid_strategy.py
```

## Configuration Files

### .env (API Keys)
```
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_secret
USE_TESTNET=true
```

### config.yaml (Trading Settings)
```yaml
trading:
  default_leverage: 10
  max_leverage: 20

risk_management:
  max_position_size_usdt: 1000
  max_open_orders: 10
```

## Common Workflows

### Open Position with Protection
```powershell
# 1. Set leverage
python main.py leverage --symbol BTCUSDT --leverage 1

# 2. Enter position
python main.py market --symbol BTCUSDT --side BUY --quantity 0.001

# 3. Set OCO protection (adjust prices)
python main.py oco --symbol BTCUSDT --side SELL --quantity 0.001 --tp-price 52000 --sl-price 48000
```

### TWAP Large Order
```powershell
# Buy 0.05 BTC over 10 minutes (10 chunks, 60s each)
python main.py twap --symbol BTCUSDT --side BUY --quantity 0.05 --chunks 10 --interval 60
```

### Grid Trading Setup
```powershell
# Create neutral grid
python main.py grid --symbol BTCUSDT --lower-price 45000 --upper-price 55000 --quantity 0.01 --levels 10 --mode neutral
```

## Troubleshooting

### "Missing required environment variables"
→ Create `.env` file from `.env.example` and add API keys

### "Invalid API key"
→ Use testnet keys from https://testnet.binancefuture.com/

### "Insufficient balance"
→ Check balance: `python main.py balance`

### "Module not found"
→ Install: `pip install python-binance requests python-dotenv aiohttp colorlog pyyaml`

## Important Notes

⚠️ **Always use TESTNET first** (USE_TESTNET=true)
⚠️ **Start with small quantities** (0.001 BTC ≈ $50)
⚠️ **Set leverage to 1x** when testing
⚠️ **Use stop-losses** for every position
⚠️ **Monitor bot.log** for detailed execution

## Getting Help

1. **README.md** - Complete documentation
2. **SETUP_GUIDE.md** - Step-by-step setup
3. **test_bot.py** - Validate your setup
4. **examples.py** - Interactive examples
5. **bot.log** - Detailed execution logs

## Testnet Setup

1. Visit: https://testnet.binancefuture.com/
2. Register account
3. Generate API keys
4. Add to `.env` file
5. Set `USE_TESTNET=true`
6. Run: `python test_bot.py`

## Production Checklist

Before using real money:
- [ ] Tested all features on testnet
- [ ] Understand leverage risks
- [ ] Configured risk limits
- [ ] Have trading strategy
- [ ] Start with minimum amounts
- [ ] Set up stop-losses

---

**Quick Help**: `python main.py --help`
