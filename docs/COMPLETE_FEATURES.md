# Stock Predictor - Complete Feature Documentation
**Last Updated:** November 27, 2025

## 🎯 Overview
Stock Predictor is a tiered stock analysis platform providing comprehensive insights for Indian stocks with both free and premium features.

---

## 🔐 Access Control System

### Free Features (No Login Required)
- ✅ **Top 20 Nifty 200 Stocks** - Real-time market cap ranking
- ✅ **Trading Prediction** - Buy/Sell/Hold signals
- ✅ **Technical Indicators** - RSI, SMA, ATR, MACD, Volume Ratio
- ✅ **Stock Search** - Real-time search by name or symbol
- ✅ **Advanced Filtering** - Signal, Sector, Market Cap filters
- ✅ **Sorting Options** - Sort by Name, Signal, Confidence, Entry/Exit/Stop-Loss
- ✅ **Basic Chart Visualization** - Price history charts

### Premium Features (Login Required)
- 🔒 **Quick Stock Analysis** - Advanced analysis form with risk settings
- 🔒 **Market Insights & Analysis** - News, Sentiment, Analyst Recommendations
- 🔒 **Analysis Summary** - Comprehensive AI-powered summaries
- 🔒 **AI Trading Assistant** - Chatbot for trading guidance
- 🔒 **Export to CSV** - Download analysis results
- 🔒 **Advanced Charts** - Enhanced charting features

### Login Credentials (Demo)
```
Username: admin
Password: password
```

> **Security Note:** For production, implement proper authentication with secure password hashing, environment variables for secrets, and user management system.

---

## 🎨 User Interface Features

### Navigation Bar
- **Dashboard Link** - Home page access
- **Enhanced Analysis Link** - Visible only when logged in, jumps to Quick Stock Analysis
- **Login/Logout Buttons** - Dynamic display based on auth status
- **AI Assistant Link** - Login-protected, visible only for authenticated users
- **Help Button** - Opens onboarding modal

### Premium Indicators
All premium sections display consistent badges:
```html
<span class="badge bg-warning text-dark ms-2">
    <i class="fas fa-lock"></i> Premium
</span>
```

### Login CTA Footer
- **Visibility**: Shows only when user is NOT logged in
- **Content**: "Login to Enjoy Enhanced Analysis" with prominent button
- **Behavior**: Automatically hidden when user logs in
- **Action**: Opens login modal on button click

### Footer Quick Links
- Vertically aligned with icons
- Links: About Us, Blogs, Help Center, Contact Us
- Icons for better visual hierarchy
- No text decoration for clean look

---

## 🔍 Filtering & Sorting System

### Filter Options

#### 1. Search Bar
- **Type**: Text input
- **Functionality**: Real-time search by stock name or symbol
- **Behavior**: Filters as you type

#### 2. Signal Filter
- **Type**: Dropdown
- **Options**: Auto-populated from analysis results
  - All Signals
  - BUY
  - SELL
  - HOLD
- **Behavior**: Dynamically populated after data fetch

#### 3. Sector Filter
- **Type**: Dropdown
- **Options**: Auto-populated from actual stock data
  - All Sectors
  - Technology
  - Financial Services
  - Energy
  - Healthcare
  - Consumer Goods
  - (and more based on available stocks)
- **Behavior**: Extracted from `allStockDetails` via `populateFilterDropdowns()`

#### 4. Market Cap Filter
- **Type**: Dropdown
- **Options**:
  - All
  - Large Cap (₹20,000+ Cr)
  - Mid Cap (₹5,000-20,000 Cr)
  - Small Cap (<₹5,000 Cr)
- **Behavior**: Filters based on `market_cap_category` field

#### 5. Sort By
- **Type**: Dropdown
- **Options**:
  - Name (A-Z) - Alphabetical sorting
  - Signal - BUY → HOLD → SELL order
  - Confidence % - Highest confidence first (descending)
  - Entry Price - Lowest to highest
  - Exit Price - Lowest to highest
  - Stop-Loss - Lowest to highest
- **Behavior**: Sorts filtered results in real-time

### Filter Implementation
```javascript
// Filters are applied via applyFilters() function
// Called on: filter change, search input, sort change
// Process: Filter → Sort → Display
```

---

## 📊 Technical Indicators

### Available Indicators
1. **RSI (Relative Strength Index)**
   - Range: 0-100
   - Oversold: < 30 (Buy signal)
   - Overbought: > 70 (Sell signal)

2. **SMA (Simple Moving Average)**
   - SMA 20: Short-term trend
   - SMA 50: Medium-term trend
   - Golden Cross: SMA 50 > SMA 200 (Bullish)
   - Death Cross: SMA 50 < SMA 200 (Bearish)

3. **ATR (Average True Range)**
   - Measures volatility
   - Higher ATR = More volatile
   - Used for stop-loss calculations

4. **MACD (Moving Average Convergence Divergence)**
   - MACD Line
   - Signal Line
   - Crossovers indicate buy/sell signals

5. **Volume Ratio**
   - Current volume vs average
   - > 1.5 indicates high activity

---

## 🎯 Risk Management

### Risk Levels (Quick Stock Analysis Only)
- **Low Risk**: Conservative, 2% stop-loss
- **Medium Risk**: Balanced, 5% stop-loss
- **High Risk**: Aggressive, 10% stop-loss
- **Custom**: User-defined stop-loss and exit targets

> **Note:** Risk level is NOT a filter - it's a parameter for analysis calculations.

---

## 🔄 Data Flow

### Stock Data Loading
```
1. Page Load → fetchStockData()
2. GET /get_top_20_stocks
3. Receive stock data + details
4. Store in allStocks, allStockDetails
5. Populate filters via populateFilterDropdowns()
6. Display stocks via updateStockDisplay()
```

### Filter Application
```
1. User changes filter/sort
2. applyFilters() triggered
3. Filter allStocks based on criteria
4. Sort filteredStocks by selected option
5. updateFilteredDisplay() renders results
```

### Authentication Flow
```
1. User clicks Login
2. Modal opens with credentials hint
3. Submit form → POST /login
4. Server validates → creates session
5. Response → isLoggedIn = true
6. updateAuthUI() called
7. Show enhanced sections, hide login CTA
```

---

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Mobile Optimizations
- Stacked filter layout
- Touch-friendly buttons
- Collapsible sections
- Optimized font sizes

---

## 🚀 Performance Features

### Data Optimization
- Background data fetching
- Efficient caching
- Minimal re-renders
- Lazy loading for charts

### User Experience
- Loading states for all async operations
- Real-time notifications
- Smooth transitions
- Error handling with user-friendly messages

---

## 🔧 Technical Stack

### Backend
- **Framework**: Flask (Python)
- **Data Source**: Yahoo Finance API (yfinance)
- **Analysis**: TA-Lib, Pandas, NumPy
- **Session Management**: Flask sessions

### Frontend
- **Framework**: Bootstrap 5
- **Charts**: Chart.js
- **Icons**: Font Awesome
- **JavaScript**: Vanilla JS (ES6+)

---

## 📝 Key Files

### Backend
- `app.py` - Main Flask application
- `technical_analysis.py` - Analysis engine
- `multi_source_data.py` - Data fetching

### Frontend
- `templates/index.html` - Main dashboard
- `static/js/script_working.js` - Frontend logic
- `static/css/style.css` - Custom styles

### Documentation
- `README.md` - Main documentation
- `docs/LOGIN_GUIDE.md` - Login system guide
- `docs/Product_Requirements_Document.md` - PRD

---

## 🐛 Known Limitations

1. **Demo Authentication**: Hardcoded credentials (admin/password)
2. **Session Persistence**: Sessions expire on browser close
3. **Data Refresh**: Manual refresh required for latest data
4. **API Rate Limits**: Yahoo Finance may throttle requests

---

## 🔮 Future Enhancements

### Planned Features
- [ ] User registration and management
- [ ] Persistent user preferences
- [ ] Watchlist functionality
- [ ] Price alerts
- [ ] Portfolio tracking
- [ ] Historical performance analysis
- [ ] Multi-language support
- [ ] Dark mode
- [ ] PWA capabilities

### Security Improvements
- [ ] Environment variable for secret key
- [ ] Password hashing (bcrypt/argon2)
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Secure cookie flags
- [ ] Session timeout
- [ ] Email verification

---

## 📞 Support

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check README.md and this guide
- **Login Guide**: See docs/LOGIN_GUIDE.md

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

**Built with ❤️ for the Indian trading community**
