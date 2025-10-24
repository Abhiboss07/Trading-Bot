# 🚀 Quick Setup Guide

## Step-by-Step Installation

### 1. Install Python Dependencies

Open PowerShell/Command Prompt in the project directory and run:

```powershell
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Get Binance Testnet API Keys

**IMPORTANT: Start with Testnet for safe testing!**

1. Visit **Binance Futures Testnet**: https://testnet.binancefuture.com/
2. Click **"Register"** (top right)
3. Complete registration with email
4. After login, go to **API Management**
5. Click **"Generate HMAC_SHA256 Key"**
6. Save your API Key and Secret Key securely
7. **Enable "Futures" permissions** (should be enabled by default)

### 3. Configure Environment Variables

```powershell
# Copy the example file
copy .env.example .env

# Edit .env file with your favorite text editor
notepad .env
```

Add your testnet credentials:
```
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_secret_here
USE_TESTNET=true
```

**Save and close the file.**

### 4. Test Your Setup

```powershell
# Run the test suite
python test_bot.py
```

You should see all tests passing ✓

### 5. Try Your First Command

```powershell
# Check your testnet balance
python main.py balance
```

Expected output:
```
📊 Account Balance:
  Available: 10000.00 USDT
  Total Wallet: 10000.00 USDT
  ...
```

## 🎯 Quick Start Examples

### Example 1: Check Balance
```powershell
python main.py balance
```

### Example 2: Get Current Price
```powershell
python main.py position --symbol BTCUSDT
```

### Example 3: Place a Small Test Order

**IMPORTANT: This will place a real order on testnet!**

```powershell
# Set leverage first
python main.py leverage --symbol BTCUSDT --leverage 1

# Place a small market buy order (0.001 BTC)
python main.py market --symbol BTCUSDT --side BUY --quantity 0.001
```

### Example 4: Check Your Position
```powershell
python main.py position --symbol BTCUSDT
```

### Example 5: Close Position
```powershell
python main.py close --symbol BTCUSDT
```

## 📊 Testing Advanced Features

### Test TWAP Order
```powershell
# Buy 0.01 BTC split into 3 chunks, 10 seconds apart
python main.py twap --symbol BTCUSDT --side BUY --quantity 0.01 --chunks 3 --interval 10
```

### Test OCO Order
```powershell
# First, open a position
python main.py market --symbol BTCUSDT --side BUY --quantity 0.001

# Then set OCO (take-profit and stop-loss)
# Adjust prices based on current market price
python main.py oco --symbol BTCUSDT --side SELL --quantity 0.001 --tp-price 52000 --sl-price 48000
```

### Test Grid Trading
```powershell
# Create a grid (adjust prices to current market)
python main.py grid --symbol BTCUSDT --lower-price 45000 --upper-price 55000 --quantity 0.01 --levels 5
```

## 🔧 Troubleshooting

### Issue: "Missing required environment variables"
**Solution:** Make sure you created `.env` file and added your API keys

### Issue: "Invalid API key"
**Solution:** 
- Check if you're using testnet keys with `USE_TESTNET=true`
- Verify keys are copied correctly (no extra spaces)
- Make sure API key has Futures permissions

### Issue: "Module not found"
**Solution:** Install dependencies: `pip install -r requirements.txt`

### Issue: "Insufficient balance"
**Solution:** 
- On testnet, you get 10,000 USDT automatically
- Try refreshing your testnet account
- Use smaller quantities (e.g., 0.001 instead of 1.0)

### Issue: "Leverage not set"
**Solution:** Set leverage before trading:
```powershell
python main.py leverage --symbol BTCUSDT --leverage 1
```

## 📝 Important Notes

### Testnet vs Production

**Testnet (Recommended for learning):**
- Free virtual money (10,000 USDT)
- Safe to experiment
- Same features as production
- Use testnet API keys
- Set `USE_TESTNET=true`

**Production (Real money):**
- ⚠️ **ONLY use after thorough testing**
- Real money at risk
- Use production API keys from binance.com
- Set `USE_TESTNET=false`
- Start with SMALL amounts

### Risk Management

1. **Always set leverage to 1x when testing**
2. **Use small quantities** (0.001 BTC = ~$50)
3. **Set stop-losses** for every position
4. **Monitor positions** regularly
5. **Never invest more than you can afford to lose**

## 🎓 Learning Path

### Day 1: Basics
1. ✅ Install and setup
2. ✅ Run test suite
3. ✅ Check balance
4. ✅ Place market order
5. ✅ Close position

### Day 2: Limit Orders
1. ✅ Place limit orders
2. ✅ Cancel orders
3. ✅ Use stop-limit orders
4. ✅ Monitor positions

### Day 3: Advanced Features
1. ✅ Test OCO orders
2. ✅ Test TWAP execution
3. ✅ Try grid trading
4. ✅ Review logs

### Day 4: Risk Management
1. ✅ Test with different leverage
2. ✅ Practice position sizing
3. ✅ Use stop-losses
4. ✅ Monitor account metrics

## 📚 Additional Resources

- **README.md** - Complete documentation
- **bot.log** - Detailed execution logs
- **config.yaml** - Configuration reference
- **Binance API Docs** - https://binance-docs.github.io/apidocs/futures/en/

## 🆘 Getting Help

1. Check **bot.log** for detailed error messages
2. Review **README.md** troubleshooting section
3. Verify your configuration in `.env` and `config.yaml`
4. Make sure you're using testnet for learning

## ✅ Pre-Production Checklist

Before using real money:

- [ ] Tested all features on testnet
- [ ] Understand all order types
- [ ] Configured risk limits in config.yaml
- [ ] Set up monitoring and alerts
- [ ] Have a trading strategy
- [ ] Understand leverage risks
- [ ] Started with minimum amounts
- [ ] Have stop-loss strategy

---

**Happy Trading! 🚀**

Remember: This bot is a tool. Success depends on your strategy, risk management, and discipline.
