import yfinance as yf
import requests
from datetime import datetime, timedelta
import json
import time

# Vercel-compatible cache (in-memory for single request)
_vercel_cache = {}
_cache_timestamp = {}

def get_vercel_compatible_stocks():
    """Get stocks in Vercel-compatible way (no background threads)"""
    global _vercel_cache, _cache_timestamp
    
    current_time = datetime.now()
    cache_key = "top_stocks"
    
    # Check if we have fresh cached data (5 minutes)
    if (cache_key in _cache_timestamp and 
        cache_key in _vercel_cache and
        current_time - _cache_timestamp[cache_key] < timedelta(minutes=5)):
        
        print("✅ Using Vercel-compatible cached data")
        return _vercel_cache[cache_key]
    
    print("🔄 Fetching fresh data for Vercel...")
    
    # Use a smaller, optimized stock list for Vercel
    vercel_stocks = [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS',
        'INFY.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS',
        'AXISBANK.NS', 'DMART.NS', 'MARUTI.NS', 'ASIANPAINT.NS', 'HCLTECH.NS',
        'ULTRACEMCO.NS', 'BAJFINANCE.NS', 'WIPRO.NS', 'NESTLEIND.NS', 'DRREDDY.NS'
    ]
    
    stock_data = []
    
    for symbol in vercel_stocks:
        try:
            # Faster data fetching for Vercel
            ticker = yf.Ticker(symbol)
            
            # Use shorter history for faster loading
            hist = ticker.history(period="5d", interval="1d")
            
            if hist.empty:
                continue
            
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            price_change = (current_price - previous_close) / previous_close * 100
            
            # Get basic info (skip heavy operations)
            info = ticker.info
            market_cap = info.get('marketCap', 0)
            
            if market_cap and market_cap > 0:
                usd_to_inr = 83.5
                market_cap_inr_cr = (market_cap * usd_to_inr) / 10000000
                
                stock_data.append({
                    'symbol': symbol,
                    'market_cap': market_cap_inr_cr,
                    'name': info.get('shortName', symbol),
                    'sector': info.get('sector', 'Unknown'),
                    'current_price': round(current_price, 2),
                    'price_change': round(price_change, 2),
                    'volume': int(hist['Volume'].iloc[-1]),
                    'pe_ratio': info.get('trailingPE'),
                    'dividend_yield': info.get('dividendYield'),
                    'price_to_book': info.get('priceToBook'),
                    'data_source': 'vercel-real-time'
                })
                
        except Exception as e:
            print(f"⚠️ {symbol}: Error - {str(e)}")
            continue
    
    # Sort by market cap and get top 20
    if stock_data:
        sorted_stocks = sorted(stock_data, key=lambda x: x['market_cap'], reverse=True)
        top_stocks = sorted_stocks[:20]
        
        # Cache the results
        _vercel_cache[cache_key] = top_stocks
        _cache_timestamp[cache_key] = current_time
        
        print(f"✅ Vercel data ready: {len(top_stocks)} stocks")
        return top_stocks
    else:
        # Emergency fallback
        print("❌ Using emergency fallback for Vercel")
        return [{
            'symbol': 'RELIANCE.NS',
            'market_cap': 177399,
            'name': 'RELIANCE INDUSTRIES LTD',
            'sector': 'Energy',
            'current_price': 1569.90,
            'price_change': 1.96,
            'volume': 14052178,
            'pe_ratio': 25.56,
            'dividend_yield': 0.36,
            'price_to_book': 2.42,
            'data_source': 'vercel-fallback'
        }]

def get_vercel_stock_data(symbol, risk_level='moderate'):
    """Get stock data in Vercel-compatible way"""
    try:
        # Check cache first
        cache_key = f"stock_{symbol}"
        current_time = datetime.now()
        
        if (cache_key in _cache_timestamp and 
            cache_key in _vercel_cache and
            current_time - _cache_timestamp[cache_key] < timedelta(minutes=1)):
            
            print(f"✅ Using cached data for {symbol}")
            return _vercel_cache[cache_key]
        
        print(f"🔄 Fetching fresh data for {symbol} on Vercel...")
        
        yahoo_symbol = symbol.replace('.NS', '') + '.NS'
        ticker = yf.Ticker(yahoo_symbol)
        
        # Fast data fetching
        hist = ticker.history(period="2mo", interval="1d")
        info = ticker.info
        
        if hist.empty:
            return get_vercel_emergency_fallback(symbol)
        
        current_price = hist['Close'].iloc[-1]
        
        # Quick technical analysis
        rsi = calculate_vercel_rsi(hist['Close'])
        ma20 = hist['Close'].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else None
        ma50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else None
        
        # Handle NaN values for Vercel
        if ma20 is not None and (ma20 != ma20):  # NaN check
            ma20 = None
        if ma50 is not None and (ma50 != ma50):  # NaN check
            ma50 = None
        
        stock_data = {
            'symbol': symbol,
            'current_price': float(current_price),
            'rsi': float(rsi) if rsi == rsi else 50.0,  # NaN check
            'ma20': float(ma20) if ma20 is not None and ma20 == ma20 else None,
            'ma50': float(ma50) if ma50 is not None and ma50 == ma50 else None,
            'name': info.get('shortName', symbol),
            'sector': info.get('sector', 'Unknown'),
            'market_cap': info.get('marketCap', 0),
            'data_source': 'vercel-real-time'
        }
        
        # Cache the result
        _vercel_cache[cache_key] = stock_data
        _cache_timestamp[cache_key] = current_time
        
        return stock_data
        
    except Exception as e:
        print(f"❌ Vercel error for {symbol}: {e}")
        return get_vercel_emergency_fallback(symbol)

def calculate_vercel_rsi(prices, period=14):
    """Vercel-compatible RSI calculation with error handling"""
    try:
        if len(prices) < period + 1:
            return 50.0
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Handle division by zero
        rs = gain / loss.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        result = rsi.iloc[-1]
        return float(result) if result == result else 50.0  # NaN check
        
    except Exception as e:
        print(f"RSI calculation error: {e}")
        return 50.0

def get_vercel_emergency_fallback(symbol):
    """Emergency fallback for Vercel when everything else fails"""
    fallback_data = {
        'RELIANCE.NS': {'current_price': 1569.90, 'rsi': 55.0, 'name': 'RELIANCE INDUSTRIES LTD'},
        'TCS.NS': {'current_price': 3162.90, 'rsi': 60.0, 'name': 'TATA CONSULTANCY SERVICES'},
        'HDFCBANK.NS': {'current_price': 1003.90, 'rsi': 52.0, 'name': 'HDFC BANK LTD'},
        'ICICIBANK.NS': {'current_price': 1375.00, 'rsi': 58.0, 'name': 'ICICI BANK LTD'},
        'HINDUNILVR.NS': {'current_price': 2425.20, 'rsi': 48.0, 'name': 'HINDUSTAN UNILEVER LTD'}
    }
    
    data = fallback_data.get(symbol, {
        'current_price': 1000.0,
        'rsi': 50.0,
        'name': symbol
    })
    
    return {
        'symbol': symbol,
        'current_price': data['current_price'],
        'rsi': data['rsi'],
        'ma20': None,
        'ma50': None,
        'name': data['name'],
        'sector': 'Unknown',
        'market_cap': 0,
        'data_source': 'vercel-emergency-fallback'
    }

def clear_vercel_cache():
    """Clear Vercel cache (useful for testing)"""
    global _vercel_cache, _cache_timestamp
    _vercel_cache = {}
    _cache_timestamp = {}
    print("🗑️ Vercel cache cleared")
