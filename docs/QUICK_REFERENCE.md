# Quick Reference Guide

## Project Overview
**Stock Predictor** - Intelligent stock analysis system with AI-powered trading assistant

## Live Application
🌐 **URL**: https://stock-predictor-three.vercel.app/

## Key Features
- 📊 Real-time stock analysis
- 🤖 AI chatbot assistant
- 📈 Technical indicators (RSI, MA, MACD, ATR)
- 🎯 5-level trading signals
- ⚠️ Risk management system
- 📰 Market intelligence

## Emergency Contacts & Fixes

### Critical Issues & Solutions
| Issue | Solution | Status |
|-------|----------|--------|
| "news.forEach is not a function" | Enhanced data structure handling | ✅ Fixed |
| Trading prediction shows "N/A" | Complete frontend-backend mapping | ✅ Fixed |
| 500 Internal Server Error | Syntax errors in app.py | ✅ Fixed |

### Quick Fix Commands
```bash
# Check Python syntax
python -m py_compile app.py

# Fix indentation issues
powershell -Command "(Get-Content app.py) -replace '        else:', '            else:' | Set-Content app.py"

# Deploy to Vercel
git add .
git commit -m "Fix description"
git push origin main
```

## File Structure
```
stock_predictor/
├── app.py                    # Main Flask application
├── templates/
│   ├── index.html            # Main dashboard
│   └── chatbot_interface.html
├── static/js/
│   └── script_working.js     # Frontend JavaScript
├── chatbot_intelligence.py   # Chatbot logic
├── market_data.py           # Market data
├── multi_source_data.py     # Data sources
├── requirements.txt         # Dependencies
└── docs/                   # Documentation
```

## API Endpoints
```
GET  /                           # Main dashboard
GET  /get_stock_data/<ticker>/<risk> # Stock analysis
GET  /chatbot                    # Chatbot interface
POST /chatbot_query              # Chatbot API
GET  /get_signals                # Signal analysis
GET  /health                     # Health check
```

## Signal System
- **STRONG_BUY**: High confidence buy signal
- **BUY**: Moderate buy signal
- **HOLD**: Neutral/wait signal
- **SELL**: Moderate sell signal
- **STRONG_SELL**: High confidence sell signal

## Technical Indicators
- **RSI (14)**: Momentum oscillator (0-100)
- **MA20/50/200**: Simple moving averages
- **MACD**: Trend following indicator
- **ATR (14)**: Volatility measure
- **Volume Ratio**: Current vs average volume

## Risk Management
- **Stop-Loss**: ATR-based (2x ATR below recent low)
- **Exit Target**: 3:1 risk-reward ratio
- **Support Level**: Recent 20-day low
- **Resistance Level**: Recent 20-day high

## Data Sources
1. **Primary**: Yahoo Finance
2. **Fallback**: Google Finance, Alpha Vantage, FMP
3. **Emergency**: Direct Yahoo Finance with enhanced logic

## Error Handling
- Multi-source fallback chain
- Emergency fallback with complete analysis
- Comprehensive error logging
- Graceful degradation

## Performance
- 5-minute cache for stock data
- Request deduplication
- Optimized API responses
- Edge caching via Vercel

## Deployment
- **Platform**: Vercel
- **Runtime**: Python 3.9.16
- **Server**: Gunicorn
- **CI/CD**: Automatic on git push

## Monitoring
- Health check endpoint: `/health`
- Error logging in console
- Performance tracking
- Uptime monitoring

## Common Issues

### Frontend Issues
1. **N/A Display**: Check backend response structure
2. **Signal Colors**: Verify signal mapping in JavaScript
3. **Chart Errors**: Check Chart.js configuration

### Backend Issues
1. **Data Source Failures**: Check multi-source fallback
2. **Syntax Errors**: Run `python -m py_compile app.py`
3. **API Timeouts**: Check timeout settings

### Deployment Issues
1. **Build Failures**: Check requirements.txt
2. **Runtime Errors**: Check Vercel logs
3. **Performance**: Check response times

## Development Commands
```bash
# Local development
flask run

# Install dependencies
pip install -r requirements.txt

# Test syntax
python -m py_compile app.py

# Git operations
git status
git add .
git commit -m "Message"
git push origin main
```

## Key Files to Edit
- **app.py**: Main application logic
- **script_working.js**: Frontend JavaScript
- **index.html**: Main dashboard
- **chatbot_intelligence.py**: Chatbot logic

## Documentation
- **PROJECT_DOCUMENTATION.md**: Complete project docs
- **ERROR_ANALYSIS.md**: Detailed error analysis
- **REQUIREMENTS_ANALYSIS.md**: Requirements and implementation
- **README.md**: Basic project information

## Support
- Check error logs in console
- Review HAR files for API issues
- Test with different stocks
- Verify data source status

## Recent Changes
- ✅ Fixed "news.forEach" error
- ✅ Resolved "N/A" display issue
- ✅ Fixed 500 server errors
- ✅ Enhanced emergency fallback
- ✅ Improved error handling

## Next Steps
1. UI/UX enhancements
2. Mobile responsiveness
3. Performance optimization
4. Advanced features
5. User feedback collection

---
*Last Updated: November 26, 2025*
*Version: 2.0*
