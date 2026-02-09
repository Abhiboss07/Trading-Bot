# 🌌 QuantumTrade: Binance Futures Trading Bot

A professional, institutional-grade trading platform for Binance USDT-M Futures. Featuring a **production-ready CLI** and a **stunning Glassmorphism Web UI**, QuantumTrade supports advanced order types, algorithmic strategies, and comprehensive risk management.

## 🚀 Key Highlights

- 💎 **Modern Web UI**: A beautiful, glass-morphism landing page with real-time trading simulations.
- ⚡ **Institutional Execution**: Optimized for low-latency market and limit order execution.
- 🤖 **Advanced Algorithmic Strategies**: TWAP execution and automated Grid Trading.
- 🛡️ **Fail-Safe Risk Management**: Built-in position limits, daily loss thresholds, and balance verification.
- 📊 **Structured Observability**: Color-coded CLI output and rotating audit logs.

## ✨ Features

### 🌐 Modern Web Interface
- ✅ **Glassmorphism Design**: Premium visual aesthetic with backdrop-blur effects.
- ✅ **Interactive Terminal**: Real-time trade log simulations.
- ✅ **Performance Visualization**: Simulated equity curves and performance metrics.
- ✅ **Fully Responsive**: Optimized for desktop and mobile viewing.

### ⚙️ Core Order Types
- ✅ **Market Orders**: Instant execution with reduce-only support.
- ✅ **Limit Orders**: Precision pricing with Post-only (maker) and TIF (GTC, IOC, FOK) options.
- ✅ **Advanced Validation**: Formatting for price precision and lot size according to Binance rules.

### 📈 Advanced Orders & Strategies
- ✅ **Stop-Limit Orders**: Smart trigger logic for exits.
- ✅ **OCO (One-Cancels-the-Other)**: Simultaneous TP/SL management.
- ✅ **TWAP**: Time-Weighted Average Price execution for large orders.
- ✅ **Grid Trading**: Automated range-bound profit capture (Neutral, Long, Short).

### 🔒 Security & Validation
- ✅ **Strict Input Validation**: Pre-flight checks on symbols, quantities, and prices.
- ✅ **Risk Limit Enforcement**: Prevents over-leveraging and account-blowing trades.
- ✅ **Secrets Management**: Secure API credential handling via `.env`.

## 📁 Project Structure

```
Trading Bot/
├── index.html                 # QuantumTrade Landing Page
├── style.css                  # Premium Design System
├── script.js                   # Interactive UI Logic
├── src/
│   ├── __init__.py
│   ├── config_loader.py       # Configuration management
│   ├── logger.py               # Structured logging system
│   ├── validator.py            # 400+ lines of validation logic
│   ├── market_orders.py        # Market & basic limit orders
│   ├── limit_orders.py         # Advanced limit orders
│   ├── bot.py                  # Main bot orchestrator
│   └── advanced/
│       ├── oco.py              # OCO order implementation
│       ├── twap.py             # TWAP execution strategy
│       └── grid_strategy.py    # Grid trading automation
├── main.py                     # Professional CLI entry point
├── config.yaml                 # User-defined trading parameters
├── requirements.txt            # Python dependencies
└── .env.example               # Environment variables template
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Binance Futures account (Testnet recommended for testing)
- API Key and Secret from Binance

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd "c:/Users/abhic/OneDrive/Desktop/Interships/Trading Bot"
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example file
   copy .env.example .env
   
   # Edit .env with your credentials
   # For Testnet (recommended):
   BINANCE_API_KEY=your_testnet_api_key
   BINANCE_API_SECRET=your_testnet_api_secret
   USE_TESTNET=true
   ```

5. **Get Testnet API Keys** (Recommended for testing)
   - Visit: https://testnet.binancefuture.com/
   - Register and generate API keys
   - Use these keys in your `.env` file

## 📖 Usage Guide

### Basic Commands

#### 1. Check Account Balance
```bash
python main.py balance
```

#### 2. Market Orders
```bash
# Buy 0.001 BTC at market price
python main.py market --symbol BTCUSDT --side BUY --quantity 0.001

# Sell 0.001 BTC at market price
python main.py market --symbol BTCUSDT --side SELL --quantity 0.001
```

#### 3. Limit Orders
```bash
# Buy 0.001 BTC at $50,000
python main.py limit --symbol BTCUSDT --side BUY --quantity 0.001 --price 50000

# Sell with post-only (maker) order
python main.py limit --symbol BTCUSDT --side SELL --quantity 0.001 --price 52000 --post-only
```

#### 4. Stop-Limit Orders
```bash
# Stop-loss: Sell if price drops to $49,500, execute at $49,000
python main.py stop-limit --symbol BTCUSDT --side SELL --quantity 0.001 --stop-price 49500 --price 49000
```

### Advanced Strategies

#### 5. OCO Orders (One-Cancels-the-Other)
```bash
# Place take-profit at $52,000 and stop-loss at $48,000
python main.py oco --symbol BTCUSDT --side SELL --quantity 0.001 --tp-price 52000 --sl-price 48000
```

#### 6. TWAP (Time-Weighted Average Price)
```bash
# Buy 0.01 BTC split into 5 chunks, 60 seconds apart
python main.py twap --symbol BTCUSDT --side BUY --quantity 0.01 --chunks 5 --interval 60

# Custom TWAP with 10 chunks, 30 seconds apart
python main.py twap --symbol BTCUSDT --side BUY --quantity 0.05 --chunks 10 --interval 30
```

#### 7. Grid Trading
```bash
# Create neutral grid between $45,000 and $55,000 with 10 levels
python main.py grid --symbol BTCUSDT --lower-price 45000 --upper-price 55000 --quantity 0.01 --levels 10

# Long grid (buy orders only)
python main.py grid --symbol BTCUSDT --lower-price 45000 --upper-price 50000 --quantity 0.01 --levels 5 --mode long

# Short grid (sell orders only)
python main.py grid --symbol BTCUSDT --lower-price 50000 --upper-price 55000 --quantity 0.01 --levels 5 --mode short
```

### Position Management

#### 8. View Position
```bash
python main.py position --symbol BTCUSDT
```

#### 9. Close Position
```bash
# Close 100% of position
python main.py close --symbol BTCUSDT

# Close 50% of position
python main.py close --symbol BTCUSDT --percentage 50
```

#### 10. Set Leverage
```bash
# Set 10x leverage
python main.py leverage --symbol BTCUSDT --leverage 10
```

#### 11. Cancel All Orders
```bash
python main.py cancel --symbol BTCUSDT
```

## ⚙️ Configuration

### config.yaml
Customize trading parameters, risk management, and execution settings:

```yaml
trading:
  default_symbol: "BTCUSDT"
  default_leverage: 10
  max_leverage: 20

risk_management:
  max_position_size_usdt: 1000
  max_loss_per_trade_usdt: 100
  daily_loss_limit_usdt: 500
  max_open_orders: 10

execution:
  twap:
    default_chunks: 5
    default_interval_seconds: 60
  grid:
    default_grid_levels: 10
    min_grid_spacing_percent: 0.5
```

### Environment Variables (.env)
```bash
# API Configuration
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
USE_TESTNET=true  # Set to false for production

# Trading Configuration
DEFAULT_SYMBOL=BTCUSDT
DEFAULT_LEVERAGE=10
```

## 📊 Logging

All trading activity is logged to `bot.log` with:
- Timestamps for every action
- Order placement and execution details
- API call tracking
- Error traces with full stack traces
- Risk metrics and position updates

Example log output:
```
2024-10-24 12:30:45 | INFO     | [PLACING] MARKET | BTCUSDT | Qty: 0.001 @ MARKET | side=BUY
2024-10-24 12:30:46 | INFO     | [PLACED] MARKET | BTCUSDT | Qty: 0.001 @ MARKET | order_id=12345 | status=FILLED
2024-10-24 12:30:46 | INFO     | [EXECUTION] BUY 0.001 BTCUSDT @ 50000.00
```

## 🔒 Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore` by default
2. **Use Testnet first** - Always test with testnet before production
3. **API Key Permissions** - Only enable Futures trading permissions
4. **IP Whitelist** - Restrict API keys to specific IP addresses
5. **Withdraw Restrictions** - Disable withdrawal permissions for trading bots
6. **Regular Monitoring** - Check logs and positions regularly

## 🧪 Testing

### Testnet Testing
```bash
# 1. Ensure USE_TESTNET=true in .env
# 2. Use testnet API keys
# 3. Run commands normally

# Test market order
python main.py market --symbol BTCUSDT --side BUY --quantity 0.001

# Test balance
python main.py balance

# Test TWAP
python main.py twap --symbol BTCUSDT --side BUY --quantity 0.01 --chunks 3 --interval 10
```

### Production Checklist
- [ ] Tested all order types on testnet
- [ ] Verified risk limits are appropriate
- [ ] Reviewed and understood all configuration
- [ ] Set up monitoring and alerts
- [ ] Started with small position sizes
- [ ] Have stop-loss strategy in place

## 📈 Performance Optimization

- **Async TWAP**: Use async execution for better performance
- **Batch Operations**: Grid orders placed efficiently
- **Connection Pooling**: Reuses HTTP connections
- **Logging Optimization**: Rotating logs prevent disk space issues
- **Validation Caching**: Reduces redundant checks

## 🐛 Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Solution: Create `.env` file from `.env.example` and add your API keys

2. **"Invalid symbol"**
   - Solution: Ensure symbol ends with USDT (e.g., BTCUSDT, ETHUSDT)

3. **"Insufficient balance"**
   - Solution: Check balance with `python main.py balance`

4. **"Leverage not set"**
   - Solution: Set leverage first: `python main.py leverage --symbol BTCUSDT --leverage 10`

5. **API Connection Errors**
   - Solution: Check internet connection and API key permissions

### Debug Mode
Enable detailed logging by editing `config.yaml`:
```yaml
logging:
  level: "DEBUG"  # Change from INFO to DEBUG
```

## 📝 API Documentation

- **Binance Futures API**: https://binance-docs.github.io/apidocs/futures/en/
- **Python Binance Library**: https://python-binance.readthedocs.io/

## ⚠️ Disclaimer

**This trading bot is for educational purposes. Trading cryptocurrencies involves substantial risk of loss. Never invest more than you can afford to lose.**

- Past performance does not guarantee future results
- Always test thoroughly on testnet before using real funds
- Monitor your positions and risk exposure regularly
- Use appropriate stop-losses and risk management
- The developers are not responsible for any financial losses

## 🤝 Contributing

This is a professional assignment project. For improvements:
1. Test thoroughly on testnet
2. Follow existing code style
3. Add appropriate logging
4. Update documentation

## 📄 License

This project is created for educational purposes as part of a trading bot assignment.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review log files in `bot.log`
3. Verify configuration in `config.yaml` and `.env`
4. Test on Binance Testnet first

---

**Built with ❤️ for professional futures trading**
