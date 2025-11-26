# Stock Predictor - Technical Documentation

**Version:** 2.0  
**Date:** November 26, 2025  
**Technical Lead:** Vasista Sandeep  
**Company:** Stock Predictor Technologies Pvt. Ltd.

---

## 📋 Overview

Stock Predictor is a Flask-based web application that provides real-time stock analysis and prediction capabilities for Indian retail investors. The system integrates multiple data sources, implements technical analysis algorithms, and delivers insights through a responsive web interface.

### 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Data Sources  │
│                 │    │                 │    │                 │
│ • Bootstrap UI  │◄──►│ • Flask App     │◄──►│ • NSE API       │
│ • Chart.js      │    │ • Python Logic  │    │ • Yahoo Finance │
│ • JavaScript    │    │ • TA-Lib        │    │ • Moneycontrol  │
│ • Responsive    │    │ • Pandas        │    │ • Static Fallback│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Side   │    │   Server Side   │    │   External APIs │
│                 │    │                 │    │                 │
│ • Browser Cache │    │ • Session Mgmt  │    │ • REST APIs     │
│ • Local Storage │    │ • Data Processing│    │ • Data Streams  │
│ • Tooltips      │    │ • Request-Scoped│    │ • Rate Limits   │
│ • Charts        │    │   Caching       │    │ • Authentication│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🗂️ Project Structure

```
stock_predictor/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── docs/                          # Documentation folder
│   ├── Product_Requirements_Document.md
│   └── Technical_Documentation.md
├── static/                        # Static assets
│   ├── css/
│   │   └── style.css              # Custom styles and responsive design
│   └── js/
│       └── script.js              # Frontend JavaScript and chart logic
├── templates/                      # HTML templates
│   ├── index.html                 # Main application interface
│   ├── pricing.html               # Pricing and subscription page
│   ├── privacy.html               # Privacy policy page
│   └── terms.html                 # Terms of service page
└── .gitignore                     # Git ignore rules
```

---

## 🔧 Technology Stack

### Backend Technologies
- **Python 3.9+**: Primary programming language
- **Flask**: Web framework for API and routing
- **Pandas**: Data manipulation and technical analysis (SMA, RSI, ATR)
- **NumPy**: Numerical computations
- **Requests**: HTTP client for API calls
- **Vercel**: Serverless deployment platform

### Frontend Technologies
- **HTML5**: Semantic markup structure
- **Bootstrap 5**: Responsive UI framework
- **Chart.js**: Interactive charting library
- **Font Awesome**: Icon library
- **JavaScript ES6+**: Client-side logic
- **CSS3**: Styling and animations

### Data Sources
- **Yahoo Finance**: Primary data source (via yfinance)
- **Google Finance**: Secondary data source
- **Alpha Vantage**: Fallback data source
- **Financial Modeling Prep**: Fallback data source
- **Static Data**: Emergency fallback list

### Development Tools
- **Git**: Version control
- **VS Code**: Primary IDE
- **Chrome DevTools**: Debugging and profiling
- **Postman**: API testing

---

## 📊 Database Schema

### Data Models (Currently In-Memory)

#### Stock Data Structure
```python
{
    "ticker": "RELIANCE.NS",
    "company_name": "Reliance Industries Ltd.",
    "price": 2500.50,
    "change": 25.30,
    "change_percent": 1.02,
    "volume": 1500000,
    "market_cap": 1600000000000,
    "sector": "Energy",
    "last_updated": "2025-11-26T11:30:00Z"
}
```

#### Technical Indicators Structure
```python
{
    "ticker": "RELIANCE.NS",
    "sma_50": 2450.75,
    "sma_200": 2300.25,
    "rsi": 65.5,
    "atr": 45.2,
    "signal": "Buy",
    "entry_price": 2480.00,
    "exit_price": 2600.00,
    "stop_loss": 2400.00,
    "risk_appetite": "medium"
}
```

#### Historical Data Structure
```python
{
    "dates": ["2025-11-01", "2025-11-02", ...],
    "open": [2480.0, 2490.0, ...],
    "high": [2520.0, 2515.0, ...],
    "low": [2470.0, 2485.0, ...],
    "close": [2500.0, 2495.0, ...],
    "volume": [1500000, 1450000, ...],
    "sma_50": [2450.0, 2452.0, ...],
    "sma_200": [2300.0, 2305.0, ...],
    "rsi": [60.0, 62.0, ...],
    "atr": [44.0, 44.5, ...]
}
```

---

## 🌐 API Documentation

### Core Endpoints

#### `GET /`
**Description**: Main application interface  
**Response**: HTML page with full application UI  
**Authentication**: None required  
**Rate Limit**: None

#### `GET /get_top_20_stocks`
**Description**: Fetch top 20 NIFTY 200 stocks by market cap  
**Response**: 
```json
{
    "stocks": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", ...],
    "last_updated": "2025-11-26 11:30:00",
    "is_fresh": true,
    "next_update_in_minutes": 45
}
```
**Authentication**: None required  
**Rate Limit**: 10 requests/minute

#### `GET /get_stock_data/<ticker>/<risk_appetite>`
**Description**: Get detailed stock analysis with technical indicators  
**Parameters**:
- `ticker`: Stock symbol (e.g., "RELIANCE.NS")
- `risk_appetite`: "low", "medium", or "high"
- `period` (optional): "1mo", "6mo", "2y" (default: "2y")
- `frequency` (optional): "daily", "weekly", "monthly" (default: "daily")

**Response**:
```json
{
    "signal": "Buy",
    "entry_price": "2480.00",
    "exit_price": "2600.00",
    "stop_loss": "2400.00",
    "attributes": {
        "SMA50": "2450.75",
        "SMA200": "2300.25",
        "RSI": "65.5",
        "ATR": "45.2"
    },
    "data": "{\"Close\":{\"1609459200000\":2500.0,...}}"
}
```
**Authentication**: None required  
**Rate Limit**: 30 requests/minute

#### `GET /refresh_data`
**Description**: Manual trigger for data refresh  
**Response**:
```json
{
    "status": "success",
    "message": "Data refreshed successfully",
    "last_updated": "2025-11-26 11:30:00",
    "stocks_count": 20
}
```
**Authentication**: None required  
**Rate Limit**: 5 requests/minute

### Static Pages
- `GET /privacy`: Privacy policy page
- `GET /terms`: Terms of service page  
- `GET /pricing`: Pricing and subscription page

---

## 🔄 Data Flow Architecture

### Data Refresh Process (Serverless)
```python
1. User Request (e.g., /get_top_20_stocks)
   ↓
2. Check Request-Scoped Cache (Vercel)
   ↓
3. If Cache Miss:
   a. get_nifty_200_list()
   b. Try Yahoo → Google → Alpha Vantage → FMP
   c. Store in Cache (5 min duration)
   ↓
4. Return Data
```

### Stock Analysis Process
```python
1. User Request (ticker + risk_appetite)
   ↓
2. Yahoo Finance API Call (historical data)
   ↓
3. Calculate Technical Indicators
   ├── SMA50 (50-day moving average)
   ├── SMA200 (200-day moving average)
   ├── RSI (14-period relative strength index)
   └── ATR (14-period average true range)
   ↓
4. Generate Trading Signal
   ├── SMA Crossover Analysis
   ├── RSI Overbought/Oversold
   └── Combined Signal Logic
   ↓
5. Calculate Price Targets
   ├── Entry Price (14-day low)
   ├── Exit Price (14-day high)
   └── Stop-Loss (risk-based percentage)
   ↓
6. Return JSON Response
```

### Frontend Data Flow
```javascript
1. Page Load
   ↓
2. Fetch Top 20 Stocks
   ↓
3. Display Stock List
   ↓
4. User Selects Stock + Risk Level
   ↓
5. Fetch Stock Analysis
   ↓
6. Update UI Components
   ├── Signal Badge
   ├── Price Cards
   ├── Technical Indicators
   └── Interactive Chart
```

---

## 📈 Technical Indicators Implementation

### Simple Moving Average (SMA)
```python
def calculate_sma(prices, period):
    return prices.rolling(window=period).mean()

# Usage
hist['SMA50'] = hist['Close'].rolling(window=50).mean()
hist['SMA200'] = hist['Close'].rolling(window=200).mean()
```

**Logic**: Average closing price over specified period  
**Signal**: Price above SMA = Bullish, below = Bearish

### Relative Strength Index (RSI)
```python
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Usage
# Custom Pandas Implementation
hist['RSI'] = calculate_rsi(hist['Close'], period=14)
```

**Logic**: Momentum oscillator (0-100 scale)  
**Signal**: <30 = Oversold (Buy), >70 = Overbought (Sell)

### Average True Range (ATR)
```python
def calculate_atr(high, low, close, period=14):
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

# Usage
# Custom Pandas Implementation
hist['ATR'] = calculate_atr(hist['High'], hist['Low'], hist['Close'], period=14)
```

**Logic**: Volatility measure based on price ranges  
**Signal**: Higher ATR = Higher volatility, affects stop-loss distance

### Signal Generation Algorithm
```python
def generate_signal(hist):
    # SMA Crossover Signal
    sma_cross_signal = np.where(hist['SMA50'] > hist['SMA200'], 1, -1)
    
    # RSI Signal
    rsi_signal = np.where(hist['RSI'] < 30, 1, 
                         np.where(hist['RSI'] > 70, -1, 0))
    
    # Combined Signal
    hist['Signal'] = np.where(sma_cross_signal == 1, 1, 
                             np.where(sma_cross_signal == -1, -1, rsi_signal))
    
    return hist['Signal'].iloc[-1]
```

---

## 🎨 Frontend Architecture

### Component Structure
```javascript
// Core Components
├── Stock List Component
├── Analysis Cards Component
├── Chart Component
├── Risk Selection Component
├── Filter Component
└── Onboarding Modal Component
```

### State Management
```javascript
// Global State
let allStocks = [];           // Master stock list
let filteredStocks = [];      // Filtered results
let currentStock = null;      // Selected stock data
let chartInstance = null;     // Chart.js instance
let userPreferences = {};     // User settings

// Local Storage
localStorage.setItem('stockPredictorOnboarding', 'true');
```

### Event Handling
```javascript
// Main Event Listeners
document.addEventListener('DOMContentLoaded', initializeApp);
document.getElementById('fetchBtn').addEventListener('click', analyzeStock);
document.getElementById('riskFilter').addEventListener('change', applyFilters);
document.getElementById('chartFrequency').addEventListener('change', updateChart);
```

### Chart Configuration
```javascript
const chartConfig = {
    type: 'line',
    data: {
        labels: dates,
        datasets: [
            {
                label: 'Stock Price',
                data: closePrices,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderWidth: 2,
                tension: 0.1
            },
            {
                label: '50-Day SMA',
                data: sma50,
                borderColor: '#ff9800',
                backgroundColor: 'rgba(255, 152, 0, 0.1)',
                borderWidth: 2,
                tension: 0.1
            },
            {
                label: '200-Day SMA',
                data: sma200,
                borderColor: '#f44336',
                backgroundColor: 'rgba(244, 67, 54, 0.1)',
                borderWidth: 2,
                tension: 0.1
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: true, position: 'top' },
            tooltip: { mode: 'index', intersect: false }
        },
        scales: {
            x: { display: true, title: { display: true, text: 'Date' } },
            y: { display: true, title: { display: true, text: 'Price (₹)' } }
        }
    }
};
```

---

## 🔒 Security Implementation

### Data Protection
```python
# Input Validation
def validate_ticker(ticker):
    pattern = r'^[A-Z]+\.NS$'
    return re.match(pattern, ticker) is not None

# Risk Appetite Validation
def validate_risk_appetite(risk):
    return risk in ['low', 'medium', 'high']

# URL Encoding
ticker = encodeURIComponent(ticker)
risk_appetite = encodeURIComponent(risk_appetite)
```

### Error Handling
```python
try:
    # API call
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logger.error(f"API call failed: {e}")
    return fallback_data
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return None
```

### Rate Limiting
```python
# Simple rate limiting (in production, use Redis)
request_counts = {}
RATE_LIMIT = {
    'get_top_20_stocks': 10,  # per minute
    'get_stock_data': 30,     # per minute
    'refresh_data': 5         # per minute
}

def check_rate_limit(endpoint, ip_address):
    key = f"{endpoint}:{ip_address}"
    current_time = time.time()
    
    if key not in request_counts:
        request_counts[key] = []
    
    # Remove old requests (older than 1 minute)
    request_counts[key] = [t for t in request_counts[key] 
                          if current_time - t < 60]
    
    if len(request_counts[key]) >= RATE_LIMIT[endpoint]:
        return False
    
    request_counts[key].append(current_time)
    return True
```

---

## 📊 Performance Optimization

### Caching Strategy
```python
# In-memory caching for stock data
stock_cache = {}
CACHE_DURATION = 300  # 5 minutes

def get_cached_stock_data(ticker):
    cache_key = f"stock_{ticker}"
    current_time = time.time()
    
    if cache_key in stock_cache:
        cached_data, timestamp = stock_cache[cache_key]
        if current_time - timestamp < CACHE_DURATION:
            return cached_data
    
    # Fetch fresh data
    fresh_data = fetch_stock_data(ticker)
    stock_cache[cache_key] = (fresh_data, current_time)
    return fresh_data
```

### Database Optimization (Future)
```sql
-- Indexes for performance
CREATE INDEX idx_stocks_ticker ON stocks(ticker);
CREATE INDEX idx_prices_date ON prices(date);
CREATE INDEX idx_prices_ticker ON prices(ticker);

-- Partitioning for large datasets
CREATE TABLE prices_2025 PARTITION OF prices
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

### Frontend Optimization
```javascript
// Lazy loading for charts
const chartObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            loadChart(entry.target);
            chartObserver.unobserve(entry.target);
        }
    });
});

// Debounce search functionality
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

const searchStock = debounce((query) => {
    performSearch(query);
}, 300);
```

---

## 🧪 Testing Strategy

### Unit Tests
```python
# test_technical_indicators.py
import unittest
import pandas as pd
from app import calculate_sma, calculate_rsi, generate_signal

class TestTechnicalIndicators(unittest.TestCase):
    
    def setUp(self):
        # Sample data
        self.prices = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109])
    
    def test_sma_calculation(self):
        sma = calculate_sma(self.prices, 5)
        self.assertEqual(len(sma), len(self.prices))
        self.assertTrue(pd.isna(sma.iloc[0:4]).all())
    
    def test_rsi_calculation(self):
        rsi = calculate_rsi(self.prices, 5)
        self.assertTrue(all(0 <= x <= 100 for x in rsi.dropna()))
    
    def test_signal_generation(self):
        hist = pd.DataFrame({
            'Close': self.prices,
            'SMA50': calculate_sma(self.prices, 5),
            'SMA200': calculate_sma(self.prices, 8),
            'RSI': calculate_rsi(self.prices, 5)
        })
        signal = generate_signal(hist)
        self.assertIn(signal, [-1, 0, 1])

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests
```python
# test_api_endpoints.py
import unittest
import json
from app import app

class TestAPIEndpoints(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_get_top_20_stocks(self):
        response = self.app.get('/get_top_20_stocks')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('stocks', data)
        self.assertIsInstance(data['stocks'], list)
    
    def test_get_stock_data(self):
        response = self.app.get('/get_stock_data/RELIANCE.NS/medium')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('signal', data)
        self.assertIn('entry_price', data)
    
    def test_invalid_ticker(self):
        response = self.app.get('/get_stock_data/INVALID/medium')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
```

### Frontend Tests
```javascript
// test_frontend.js
describe('Stock Predictor Frontend', () => {
    
    test('should initialize tooltips', () => {
        document.body.innerHTML = `
            <span data-bs-toggle="tooltip" title="Test">Test</span>
        `;
        initializeTooltips();
        expect(document.querySelector('.tooltip')).toBeTruthy();
    });
    
    test('should filter stocks by signal', () => {
        const mockStocks = [
            { ticker: 'RELIANCE.NS', signal: 'Buy' },
            { ticker: 'TCS.NS', signal: 'Sell' }
        ];
        const filtered = filterStocksBySignal(mockStocks, 'Buy');
        expect(filtered).toHaveLength(1);
        expect(filtered[0].ticker).toBe('RELIANCE.NS');
    });
    
    test('should update chart with new data', () => {
        const mockData = {
            data: '{"Close":{"1609459200000":2500}}'
        };
        updateChart(mockData, 'line');
        expect(window.myChart).toBeTruthy();
    });
});
```

---

## 🚀 Deployment Architecture

### Production Setup
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/stockpredictor
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=stockpredictor
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  postgres_data:
```

### Environment Configuration
```bash
# .env.production
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/stockpredictor
REDIS_URL=redis://localhost:6379/0
API_KEYS_NSE=your-nse-api-key
API_KEYS_YAHOO=your-yahoo-api-key
LOG_LEVEL=INFO
SENTRY_DSN=your-sentry-dsn
```

### Monitoring Setup
```python
# monitoring.py
import logging
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
STOCK_ANALYSIS_COUNT = Counter('stock_analysis_total', 'Total stock analyses')

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('/var/log/stockpredictor.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🔧 Development Workflow

### Git Workflow
```bash
# Feature branch workflow
git checkout -b feature/advanced-indicators
# Make changes
git add .
git commit -m "Add Bollinger Bands indicator"
git push origin feature/advanced-indicators
# Create Pull Request
# Code review
# Merge to main
```

### Code Quality
```python
# .pylintrc
[FORMAT]
max-line-length = 88

[MESSAGES CONTROL]
disable = C0330, C0326

[VARIABLES]
init-import = no

[BASIC]
good-names = i,j,k,ex,Run,_

[DESIGN]
max-args = 7
max-locals = 15
```

```json
// .eslintrc.json
{
    "env": {
        "browser": true,
        "es6": true
    },
    "extends": "eslint:recommended",
    "rules": {
        "indent": ["error", 4],
        "quotes": ["error", "single"],
        "semi": ["error", "always"]
    }
}
```

### Pre-commit Hooks
```bash
#!/bin/sh
# .git/hooks/pre-commit

# Run Python tests
python -m pytest tests/

# Run JavaScript tests
npm test

# Check code style
pylint app.py
eslint static/js/script.js

# Run security scan
bandit -r app.py
```

---

## 📊 Monitoring & Analytics

### Application Metrics
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Business metrics
STOCK_ANALYSIS_REQUESTS = Counter('stock_analysis_requests_total', 'Total stock analysis requests')
ACTIVE_USERS = Gauge('active_users_current', 'Current active users')
SUBSCRIPTION_REVENUE = Gauge('subscription_revenue_rupees', 'Monthly recurring revenue')

# Technical metrics
API_RESPONSE_TIME = Histogram('api_response_time_seconds', 'API response time')
DATABASE_CONNECTIONS = Gauge('database_connections_active', 'Active database connections')
CACHE_HIT_RATE = Gauge('cache_hit_rate', 'Cache hit rate percentage')
```

### Health Checks
```python
@app.route('/health')
def health_check():
    checks = {
        'database': check_database_connection(),
        'redis': check_redis_connection(),
        'external_apis': check_external_apis(),
        'memory_usage': check_memory_usage(),
        'disk_space': check_disk_space()
    }
    
    if all(checks.values()):
        return jsonify({'status': 'healthy', 'checks': checks}), 200
    else:
        return jsonify({'status': 'unhealthy', 'checks': checks}), 503
```

### Error Tracking
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn='your-sentry-dsn',
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    environment=os.getenv('FLASK_ENV', 'development')
)

@app.errorhandler(500)
def internal_error(error):
    sentry_sdk.capture_exception(error)
    return jsonify({'error': 'Internal server error'}), 500
```

---

## 🔮 Future Technical Enhancements

### Phase 2 Technical Roadmap
1. **Database Migration**
   - PostgreSQL for persistent storage
   - Redis for caching and sessions
   - Time-series database for historical data

2. **API Enhancement**
   - GraphQL for flexible data queries
   - WebSocket for real-time updates
   - Rate limiting with Redis

3. **Mobile Applications**
   - React Native iOS app
   - Flutter Android app
   - Shared API backend

4. **AI/ML Integration**
   - TensorFlow for prediction models
   - Scikit-learn for feature engineering
   - MLflow for model management

### Phase 3 Technical Roadmap
1. **Microservices Architecture**
   - Service discovery with Consul
   - API Gateway with Kong
   - Container orchestration with Kubernetes

2. **Advanced Analytics**
   - Apache Spark for big data processing
   - Elasticsearch for search and analytics
   - Kafka for real-time data streaming

3. **Security Enhancements**
   - OAuth 2.0 authentication
   - JWT token management
   - Zero-trust architecture

---

## 📞 Support & Maintenance

### Monitoring Dashboard
- Grafana for visualization
- Prometheus for metrics collection
- Alertmanager for notifications

### Backup Strategy
```bash
# Daily database backup
pg_dump stockpredictor > backup_$(date +%Y%m%d).sql

# Weekly full backup
tar -czf full_backup_$(date +%Y%m%d).tar.gz /var/lib/postgresql

# Offsite backup
aws s3 cp backup_$(date +%Y%m%d).sql s3://stockpredictor-backups/
```

### Incident Response
1. **Detection**: Automated alerts
2. **Assessment**: Impact analysis
3. **Resolution**: Fix implementation
4. **Communication**: User notifications
5. **Post-mortem**: Root cause analysis

---

## 📚 Additional Resources

### Documentation Links
- [Flask Documentation](https://flask.palletsprojects.com/)
- [TA-Lib Documentation](https://ta-lib.org/)
- [Chart.js Documentation](https://www.chartjs.org/)
- [Bootstrap Documentation](https://getbootstrap.com/)

### External APIs
- [NSE API Documentation](https://www.nseindia.com/)
- [Yahoo Finance API](https://finance.yahoo.com/)
- [Razorpay Payment Gateway](https://razorpay.com/)

### Development Tools
- [Python Testing with pytest](https://docs.pytest.org/)
- [JavaScript Testing with Jest](https://jestjs.io/)
- [Docker Documentation](https://docs.docker.com/)

---

**Document Status:** Active  
**Last Updated:** November 26, 2025  
**Next Review:** January 2026  
**Maintainer:** Vasista Sandeep
