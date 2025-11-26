# 📈 Stock Predictor Application

A comprehensive web-based stock analysis and prediction tool that provides actionable insights for Indian stocks with educational features for beginners. The application fetches real-time stock data, performs technical analysis, and generates buy/sell/hold signals based on various technical indicators.

![Stock Predictor Screenshot](https://via.placeholder.com/800x500.png?text=Stock+Predictor+Enhanced+UI)

## 🌟 Key Features

### 📊 **Advanced Stock Analysis**
- **Real-time NIFTY 200 Data**: Automatic hourly updates with fallback mechanisms
- **Top 20 Stocks**: View and analyze the top 20 stocks from NIFTY 200 index by market cap
- **Multi-source Data**: NSE API, NSE CSV, Moneycontrol with static fallback
- **Technical Analysis**: Comprehensive indicators including SMA, RSI, ATR
- **Risk-Based Recommendations**: Adjustable stop-loss levels (Low/Medium/High risk)

### 🎓 **Educational Interface**
- **25+ Interactive Tooltips**: Hover-to-learn explanations for all technical terms
- **Expanded Jargons**: Simple explanations for SMA, RSI, ATR, and market concepts
- **Beginner's Guide**: Built-in tutorial for understanding trading signals
- **Visual Learning**: Color-coded indicators and comprehensive chart legends
- **Layman-Friendly**: No prior trading knowledge required

### 📈 **Advanced Charting**
- **Flexible Frequency**: Daily, Weekly, Monthly chart views
- **Time Period Selection**: 1 month, 6 months, 2 years historical data
- **Interactive Charts**: Professional visualization with Chart.js
- **Multiple Indicators**: Price, 50-day SMA, 200-day SMA on same chart
- **Smart Tooltips**: Detailed price information on hover

### 🔍 **Smart Filtering System**
- **Signal Type Filter**: Buy/Sell/Hold only stocks
- **Risk Level Filter**: Filter by risk appetite
- **Sector Classification**: Technology, Banking, FMCG, Pharma, Auto
- **Market Cap Sorting**: Large/Mid/Small cap categorization
- **Bulk Analysis**: Analyze all stocks with one click

### 💡 **User Experience**
- **Professional UI**: Modern gradient design with responsive layout
- **Loading States**: Visual feedback during data analysis
- **Export Functionality**: Download analysis results as CSV
- **Search Feature**: Real-time stock search
- **Mobile Responsive**: Works on all devices

## 📊 Data Sources & Methodology

### 🇮🇳 **Primary Data Sources**
1. **NSE API** (`https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20200`)
   - Real-time NIFTY 200 stock data
   - Market capitalization ranking
   - Primary source for top 20 stocks

2. **NSE CSV** (`https://www.nseindia.com/content/indices/ind_nifty200list.csv`)
   - Official NIFTY 200 constituent list
   - Backup data source
   - Reliable static data

3. **Moneycontrol** (`https://www.moneycontrol.com/india/stockmarket/indices/nifty-200-200.html`)
   - Web scraping fallback
   - Market data verification
   - Additional stock information

### 🔄 **Data Refresh System**
- **Automatic Updates**: Background thread refreshes data every hour
- **Manual Refresh**: User-initiated data refresh capability
- **Fallback Mechanism**: Static list of 20 major NIFTY stocks
- **Timestamp Tracking**: Shows data freshness and next update time

### 📈 **Technical Indicators Explained**

#### 📊 **Simple Moving Average (SMA)**
- **50-Day SMA**: Short-term trend indicator (average of last 50 trading days)
- **200-Day SMA**: Long-term trend indicator (average of last 200 trading days ~9 months)
- **Signal Generation**: Golden Cross (50 > 200) = Buy, Death Cross (50 < 200) = Sell

#### ⚡ **Relative Strength Index (RSI)**
- **Momentum Oscillator**: Measures speed of price changes (0-100 scale)
- **Oversold Condition**: RSI < 30 (Good buying opportunity)
- **Overbought Condition**: RSI > 70 (Consider selling)
- **Neutral Zone**: RSI 30-70 (Wait for clearer signals)

#### 📉 **Average True Range (ATR)**
- **Volatility Measure**: Typical price movement range
- **High ATR**: Volatile stock (larger price swings)
- **Low ATR**: Stable stock (smaller price movements)
- **Stop-Loss Setting**: Used to determine appropriate risk levels

## 🎯 Trading Signals & Risk Management

### 🟢 **Buy Signal Conditions**
- 50-day SMA crosses above 200-day SMA (Golden Cross)
- RSI < 30 (Oversold condition)
- Price above both moving averages
- Positive momentum indicators

### 🔴 **Sell Signal Conditions**
- 50-day SMA crosses below 200-day SMA (Death Cross)
- RSI > 70 (Overbought condition)
- Price below both moving averages
- Negative momentum indicators

### 🟡 **Hold Signal Conditions**
- Mixed signals between indicators
- Price trading between moving averages
- RSI in neutral zone (30-70)
- Unclear market direction

### 💰 **Risk Appetite Settings**
- **🟢 Low Risk**: Conservative approach, 2% stop-loss below 14-day low
- **🟡 Medium Risk**: Balanced approach, 5% stop-loss below 14-day low
- **🔴 High Risk**: Aggressive approach, 10% stop-loss below 14-day low

## 🚀 Installation & Setup

### 📋 **Prerequisites**
- Python 3.8+
- pip (Python package manager)
- TA-Lib (Technical Analysis Library)
- Git (for version control)

### 🛠️ **Installation Steps**

1. **Clone the repository**
   ```bash
   git clone https://github.com/vasistasandeep/stock_predictor.git
   cd stock_predictor
   ```

2. **Create and activate virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install TA-Lib**
   - **Windows**: Download wheel file from [UCI TA-Lib](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)
     ```bash
     pip install TA_Lib‑0.4.24‑cp38‑cp38‑win_amd64.whl
     ```
   - **macOS**: `brew install ta-lib`
   - **Linux**: `sudo apt-get install ta-lib-dev`

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### 🏃‍♂️ **Running the Application**

1. **Start the Flask development server**
   ```bash
   python app.py
   ```

2. **Open your web browser** and navigate to:
   ```
   http://127.0.0.1:5000
   ```

3. **Application Features**:
   - 📊 View real-time NIFTY 200 top 20 stocks
   - 🎓 Learn technical analysis with interactive tooltips
   - 📈 Analyze stocks with customizable chart settings
   - 🔍 Filter stocks by signal, risk, sector, and market cap
   - 💾 Export analysis results to CSV
   - 🔄 Refresh data manually or wait for automatic updates

## 🏗️ Project Architecture

### 📁 **Project Structure**
```
stock_predictor/
├── app.py                    # Main Flask application & API endpoints
├── requirements.txt          # Python dependencies
├── README.md                 # This comprehensive documentation
├── static/                   # Static assets
│   ├── css/
│   │   └── style.css         # Custom styles & responsive design
│   └── js/
│       └── script.js         # Frontend JavaScript & chart logic
├── templates/
│   └── index.html            # Main HTML template with educational UI
└── .gitignore               # Git ignore rules
```

### 🔧 **Technical Stack**
- **Backend**: Flask (Python web framework)
- **Data Sources**: Yahoo Finance API, NSE API, Web Scraping
- **Technical Analysis**: TA-Lib, Pandas, NumPy
- **Frontend**: Bootstrap 5, Chart.js, Custom JavaScript
- **Real-time Updates**: Threading, Background data refresh

### 🌐 **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application interface |
| `/get_top_20_stocks` | GET | Returns top 20 NIFTY stocks with timestamps |
| `/get_stock_data/<ticker>/<risk>` | GET | Fetches stock analysis with technical indicators |
| `/refresh_data` | GET | Manual data refresh endpoint |

### 📊 **Data Flow Architecture**
```
NSE API → Stock List → Yahoo Finance → Technical Analysis → Trading Signals → UI Display
    ↓              ↓               ↓                ↓              ↓
Fallback CSV → Market Cap → SMA/RSI/ATR → Risk Adjustment → Educational Tooltips
```

## 🎓 Educational Features

### 📚 **Learning Resources**
- **Interactive Tooltips**: Hover over any term for detailed explanation
- **Visual Indicators**: Color-coded signals for easy understanding
- **Step-by-Step Guide**: Built-in tutorial for beginners
- **Risk Management**: Clear explanations of stop-loss and position sizing

### 🎯 **Understanding Indicators**
- **Moving Averages**: Learn trend following strategies
- **RSI**: Understand momentum and overbought/oversold conditions
- **ATR**: Master volatility and risk management
- **Signal Generation**: See how buy/sell decisions are made

### 💡 **Trading Concepts Explained**
- **Market Capitalization**: Company size and stability
- **Support & Resistance**: Key price levels for trading
- **Risk-Reward Ratio**: Balancing profit potential with loss risk
- **Position Sizing**: How much to invest in each trade

## 🔧 Advanced Features

### 📊 **Chart Filtering**
- **Frequency Options**: Daily (detailed), Weekly (smoother), Monthly (long-term)
- **Time Periods**: 1 month (recent), 6 months (medium), 2 years (long-term)
- **Chart Types**: Line charts (clean), Candlestick charts (detailed)
- **Interactive Legends**: Click to show/hide indicators

### 🔍 **Smart Filtering**
- **Signal Strength**: Filter by confidence level
- **Sector Analysis**: Industry-specific stock filtering
- **Market Cap Sorting**: By company size and stability
- **Bulk Operations**: Analyze multiple stocks simultaneously

### 💾 **Data Export**
- **CSV Export**: Download analysis results
- **Timestamp Tracking**: Data freshness indicators
- **Risk Parameters**: Export with risk settings
- **Historical Data**: Chart data export capability

## 🤝 Contributing Guidelines

### 🌟 **How to Contribute**
1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit changes** (`git commit -m 'Add amazing feature'`)
4. **Push to branch** (`git push origin feature/amazing-feature`)
5. **Open Pull Request**

### 📝 **Development Guidelines**
- Follow PEP 8 Python style guidelines
- Add comprehensive comments and documentation
- Include tooltips for new features
- Test with different stocks and timeframes
- Ensure mobile responsiveness

### 🐛 **Bug Reports**
- Use GitHub Issues for bug reports
- Include stock ticker and steps to reproduce
- Provide browser and environment details
- Add screenshots if applicable

## 📜 License & Disclaimer

### ⚖️ **License**
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### ⚠️ **Important Disclaimer**
- **Educational Purpose Only**: This tool is for learning and education
- **Not Financial Advice**: Information provided should not be considered investment advice
- **Market Risks**: Stock market investments are subject to market risks
- **Professional Consultation**: Always consult with certified financial advisors
- **Data Accuracy**: While we strive for accuracy, data may have delays or errors

### 🔒 **Data Privacy**
- No personal data collection
- No account registration required
- Local processing only
- No third-party analytics

## 🙏 Acknowledgments & Credits

### 📊 **Data Providers**
- [Yahoo Finance](https://finance.yahoo.com/) - Real-time stock data and historical prices
- [NSE India](https://www.nseindia.com/) - Official NIFTY indices data
- [Moneycontrol](https://www.moneycontrol.com/) - Additional market data and verification

### 🛠️ **Technical Libraries**
- [TA-Lib](https://www.ta-lib.org/) - Technical analysis functions and indicators
- [Chart.js](https://www.chartjs.org/) - Interactive charting library
- [Bootstrap](https://getbootstrap.com/) - Responsive UI framework
- [Pandas](https://pandas.pydata.org/) - Data manipulation and analysis
- [Flask](https://flask.palletsprojects.com/) - Web framework

### 🎨 **Design Inspiration**
- Modern trading platforms for UI/UX patterns
- Educational platforms for tooltip systems
- Financial applications for data visualization

## 📞 Support & Contact

### 🐛 **Getting Help**
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check this README for detailed information
- **Community**: Fork, modify, and improve the project

### 📧 **Developer Contact**
- **GitHub**: [Vasista Sandeep](https://github.com/vasistasandeep)
- **Project Repository**: https://github.com/vasistasandeep/stock_predictor

### 🔄 **Version History**
- **v2.0**: Educational UI, chart filtering, enhanced tooltips
- **v1.0**: Basic stock analysis and prediction features

---

## 🚀 Quick Start Summary

```bash
# Clone and setup
git clone https://github.com/vasistasandeep/stock_predictor.git
cd stock_predictor
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Run the application
python app.py

# Open browser to http://127.0.0.1:5000
# Start analyzing stocks with educational tooltips!
```

**Happy Trading! 📈🚀**

---

*Built with ❤️ for the Indian trading community*
