# 📈 Stock Predictor Application

A **free educational stock analysis platform** that provides comprehensive insights for Indian stocks with interactive learning features. The application fetches real-time stock data, performs technical analysis, and generates buy/sell/hold signals based on various technical indicators - all focused on financial literacy and investor education.

![Stock Predictor Screenshot](https://via.placeholder.com/800x500.png?text=Stock+Predictor+Enhanced+UI)

## 🌟 Key Features

### 📊 **Advanced Stock Analysis**
- **🔄 Real-Time Yahoo Finance Integration**: Live market data with 160+ NIFTY stocks
- **📈 Top 20 Stocks**: Dynamic ranking by real-time market capitalization
- **💰 Live Market Metrics**: Real-time prices, market cap, volume, P/E ratios, dividend yields
- **📊 Technical Analysis**: Comprehensive indicators including SMA, RSI, ATR with NaN handling
- **🎯 Risk-Based Recommendations**: Adjustable stop-loss levels (Low/Medium/High risk)
- **📰 Stock-Specific News**: Generated news based on real stock performance
- **🧠 Market Sentiment**: Multi-source sentiment analysis (technical, news, volume, breadth)
- **👨‍💼 Analyst Recommendations**: Real Yahoo Finance analyst data with fallbacks

### 🌐 **Complete Website Structure**
- **Professional Navigation**: Clean, modern navbar with responsive design
- **About Us Page**: Comprehensive company information and mission
- **Financial Blogs**: Internal blog section with market insights and analysis
- **Contact Us Page**: Professional contact form with FAQ section
- **Help Center**: Integrated onboarding modal for user guidance
- **Simplified Footer**: Clean footer with essential links only

### 🎨 **Enhanced UI/UX Design**
- **Clean Hyperlinks**: All links without underlines for modern appearance
- **Text Rendering Fixes**: Eliminated text artifacts and rendering issues
- **Responsive Design**: Mobile-friendly layout across all devices
- **Professional Styling**: Modern design with consistent branding
- **Accessibility**: Proper ARIA labels and keyboard navigation

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

### 🔄 **Primary Real-Time Data Sources**
1. **🚀 Yahoo Finance API** (`yfinance` library)
   - **Live Market Data**: Real-time prices, volume, market cap
   - **160+ NIFTY Stocks**: Comprehensive coverage across sectors
   - **Financial Metrics**: P/E ratios, dividend yields, P/B ratios
   - **Technical Indicators**: Historical data for SMA, RSI, ATR calculations
   - **Primary Source**: Main data provider for all analysis

2. **🇮🇳 NSE API** (`https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20200`)
   - **Index Constituents**: Official NIFTY 200 stock list
   - **Market Ranking**: Real-time market capitalization data
   - **Backup Source**: Fallback when Yahoo Finance is unavailable

3. **📰 News & Sentiment APIs**
   - **Yahoo Finance News**: Real-time financial news
   - **Generated News**: Stock-specific news based on performance
   - **Sentiment Analysis**: Multi-source market sentiment indicators

### ⚡ **Real-Time Data Architecture**
- **🚀 Fast Startup**: Server starts immediately with fallback data
- **🔄 Background Fetch**: Real-time data loads in background threads
- **📊 Live Updates**: Continuous data refresh with timestamps
- **🛡️ Robust Fallbacks**: Multiple layers of error handling
- **✅ JSON Validation**: No more NaN errors, browser-compatible
- **📈 Market Timing**: Real-time market hours data with proper timezone handling

### 🔧 **Technical Implementation**
- **Background Threading**: Non-blocking real-time data fetching
- **Error Handling**: Comprehensive exception handling and fallbacks
- **Data Validation**: NaN handling and JSON compatibility
- **Performance Optimization**: Efficient data caching and retrieval
- **Production Ready**: Scalable architecture for deployment

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
├── app.py                    # Main Flask application & real-time API endpoints
├── market_data.py            # Real-time data processing & analysis engine
├── requirements.txt          # Python dependencies (yfinance, pandas, etc.)
├── README.md                 # This comprehensive documentation
├── realtime_data_manager.py  # Background real-time data service
├── final_verification.py     # Complete system testing suite
├── test_enhanced_data.py     # End-to-end real-time data validation
├── test_realtime_yahoo.py    # Yahoo Finance API testing
├── test_server_realtime.py   # Server real-time integration testing
├── static/                   # Static assets
│   ├── css/
│   │   └── style.css         # Custom styles & responsive design
│   └── js/
│       └── script_working.js # Frontend JavaScript with real-time updates
├── templates/
│   ├── index.html            # Main dashboard with real-time data
│   ├── about.html            # About Us page with company info
│   ├── blogs.html            # Financial blogs page
│   ├── contact.html          # Contact Us page with form
│   ├── privacy.html          # Privacy policy page
│   └── terms.html            # Terms of service page
├── docs/                     # Documentation
│   └── Product_Requirements_Document.md  # PRD document
└── .gitignore               # Git ignore rules
```

### 🔧 **Technical Stack**
- **Backend**: Flask (Python web framework)
- **🚀 Real-Time Data**: Yahoo Finance API (yfinance), NSE API
- **Technical Analysis**: TA-Lib, Pandas, NumPy with NaN handling
- **Frontend**: Bootstrap 5, Chart.js, Custom JavaScript
- **Background Processing**: Threading, Async data fetching
- **Data Validation**: JSON compatibility, Error handling
- **Production Ready**: Scalable architecture for Vercel deployment

### 🌐 **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard interface |
| `/about` | GET | About Us page with company information |
| `/blogs` | GET | Financial blogs and market insights |
| `/contact` | GET | Contact Us page with form and FAQ |
| `/privacy` | GET | Privacy policy page |
| `/terms` | GET | Terms of service page |
| `/get_top_20_stocks` | GET | **Real-time** top 20 NIFTY stocks with live metrics |
| `/get_stock_data/<ticker>/<risk>` | GET | **Real-time** stock analysis with live indicators |
| `/get_market_news/<ticker>` | GET | **Stock-specific** news with sentiment analysis |
| `/get_analyst_recommendations/<ticker>` | GET | **Live analyst** recommendations from Yahoo Finance |
| `/get_market_sentiment/<ticker>` | GET | **Comprehensive** market sentiment analysis |
| `/refresh_data` | GET | Manual real-time data refresh |

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

## 🌐 Open Source Portal

This project is available as a **free, open-source portal** accessible on both mobile and web devices:

### 📱 Mobile Access
- **Progressive Web App (PWA)** ready
- **Responsive design** for all screen sizes
- **Touch-friendly** interface
- **Offline capabilities** with service workers

### 🖥️ Web Access
- **Desktop optimized** interface
- **Cross-browser compatible**
- **Keyboard accessible**
- **Screen reader friendly**

### 🔧 Deployment Options
1. **GitHub Pages** (Free static hosting)
2. **Vercel/Netlify** (Free hosting with serverless functions)
3. **Heroku** (Free tier for Flask apps)
4. **Railway/Render** (Modern hosting platforms)
5. **Self-hosted** (VPS/Dedicated server)

### 🌍 Global Accessibility
- **Multi-language support** ready
- **WCAG 2.1 AA compliant**
- **High contrast mode**
- **Reduced motion support**
- **Keyboard navigation**
- **Screen reader optimized**

## 🤝 Contributing

We welcome contributions from the community! This is a **free, open-source project** designed to be accessible to everyone.

### 🎯 How to Contribute
1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** on mobile and web
5. **Submit** a Pull Request

### 🌟 Contribution Areas
- **Accessibility improvements**
- **Mobile responsiveness**
- **New features**
- **Bug fixes**
- **Documentation**
- **Translations**

### 📧 Contact
- **Issues**: Use GitHub Issues
- **Discussions**: Use GitHub Discussions
- **Email**: [Your email for community support]

## 🎉 Free & Open Source

This project is **100% free** and **open source**:
- ✅ **No cost** to use or modify
- ✅ **No restrictions** on commercial use
- ✅ **Community driven** development
- ✅ **Accessible** to everyone
- ✅ **Mobile and web** compatible

---

**🚀 Let's make stock market predictions accessible to everyone, everywhere!**

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
- **🚀 v4.0 (Latest)**: **Real-Time Data Integration Complete**
  - ✅ Live Yahoo Finance API integration with 160+ NIFTY stocks
  - ✅ Real-time market cap, prices, volume, P/E ratios, dividend yields
  - ✅ Stock-specific news generation based on performance
  - ✅ Comprehensive market sentiment analysis
  - ✅ Fixed JSON NaN errors for browser compatibility
  - ✅ Background data fetching with instant UI startup
  - ✅ Production-ready for Vercel deployment
- **v3.0**: Complete website structure, new pages (About, Blogs, Contact), UI fixes, text rendering improvements
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
