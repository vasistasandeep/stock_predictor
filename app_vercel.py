from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import yfinance as yf
import pandas as pd
import numpy as np
import talib
import time
import requests
from datetime import datetime, timedelta
from market_data import get_market_news, get_analyst_recommendations, get_market_sentiment
from vercel_compatible import get_vercel_compatible_stocks, get_vercel_stock_data, clear_vercel_cache
import os

app = Flask(__name__)

# Vercel-compatible: No global state, use request-scoped data
data_update_interval = 300  # 5 minutes cache for Vercel

def get_nifty_200_list():
    """Vercel-compatible stock list fetching (no background threads)"""
    try:
        print("🚀 Vercel-compatible stock data fetch...")
        
        # Use Vercel-compatible method
        stocks = get_vercel_compatible_stocks()
        
        if stocks:
            print(f"✅ Vercel: Successfully fetched {len(stocks)} stocks")
            return stocks
        else:
            print("⚠️ Vercel: Using emergency fallback")
            return get_vercel_emergency_stock_list()
            
    except Exception as e:
        print(f"❌ Vercel: Error fetching stocks - {e}")
        return get_vercel_emergency_stock_list()

def get_vercel_emergency_stock_list():
    """Emergency fallback for Vercel"""
    return [
        {'symbol': 'RELIANCE.NS', 'market_cap': 177399, 'name': 'RELIANCE INDUSTRIES LTD', 'sector': 'Energy', 'current_price': 1569.90, 'price_change': 1.96, 'data_source': 'vercel-emergency'},
        {'symbol': 'TCS.NS', 'market_cap': 95554, 'name': 'TATA CONSULTANCY SERVICES', 'sector': 'Technology', 'current_price': 3162.90, 'price_change': 0.5, 'data_source': 'vercel-emergency'},
        {'symbol': 'HDFCBANK.NS', 'market_cap': 12892, 'name': 'HDFC BANK LTD', 'sector': 'Banking', 'current_price': 1003.90, 'price_change': -0.2, 'data_source': 'vercel-emergency'},
        {'symbol': 'ICICIBANK.NS', 'market_cap': 82067, 'name': 'ICICI BANK LTD', 'sector': 'Banking', 'current_price': 1375.00, 'price_change': 0.8, 'data_source': 'vercel-emergency'},
        {'symbol': 'HINDUNILVR.NS', 'market_cap': 47581, 'name': 'HINDUSTAN UNILEVER LTD', 'sector': 'FMCG', 'current_price': 2425.20, 'price_change': -0.3, 'data_source': 'vercel-emergency'}
    ]

@app.route('/')
def index():
    """Main dashboard - Vercel compatible"""
    try:
        # Get stocks synchronously for Vercel
        stocks = get_nifty_200_list()
        
        # Render template with stock data
        return render_template('index.html', stocks=stocks)
    except Exception as e:
        print(f"❌ Vercel index error: {e}")
        # Emergency fallback
        return render_template('index.html', stocks=get_vercel_emergency_stock_list())

@app.route('/get_top_20_stocks')
def get_top_20_stocks():
    """Return top 20 stocks - Vercel compatible"""
    try:
        print("🔄 Vercel: Fetching top 20 stocks...")
        
        stocks = get_nifty_200_list()
        
        if stocks:
            response_data = {
                'is_fresh': True,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'next_update_in_minutes': 5,
                'stock_details': stocks[:20],  # Limit to 20 for Vercel
                'data_source': 'vercel-real-time',
                'cache_status': 'fresh'
            }
            
            print(f"✅ Vercel: Returning {len(stocks)} stocks")
            return jsonify(response_data)
        else:
            # Emergency fallback response
            fallback_stocks = get_vercel_emergency_stock_list()
            return jsonify({
                'is_fresh': False,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'next_update_in_minutes': 1,
                'stock_details': fallback_stocks,
                'data_source': 'vercel-emergency-fallback',
                'cache_status': 'emergency'
            })
            
    except Exception as e:
        print(f"❌ Vercel get_top_20_stocks error: {e}")
        # Emergency fallback
        fallback_stocks = get_vercel_emergency_stock_list()
        return jsonify({
            'is_fresh': False,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'next_update_in_minutes': 1,
            'stock_details': fallback_stocks,
            'data_source': 'vercel-error-fallback',
            'error': str(e)
        })

@app.route('/get_stock_data/<ticker>/<risk>')
def get_stock_data(ticker, risk):
    """Get stock analysis - Vercel compatible"""
    try:
        print(f"🔄 Vercel: Analyzing {ticker} with {risk} risk...")
        
        # Use Vercel-compatible stock data fetching
        stock_data = get_vercel_stock_data(ticker, risk)
        
        if not stock_data:
            return jsonify({'error': 'Stock data not available', 'ticker': ticker})
        
        # Get market data (with timeout protection)
        try:
            news = get_market_news(ticker, limit=3)  # Reduced for Vercel
            recommendations = get_analyst_recommendations(ticker)
            sentiment = get_market_sentiment(ticker)
        except Exception as e:
            print(f"⚠️ Vercel: Market data error for {ticker} - {e}")
            # Fallback data
            news = {'news': [{'title': 'Market data temporarily unavailable', 'summary': 'Please try again later'}]}
            recommendations = {'recommendation': 'HOLD', 'total_analysts': 0}
            sentiment = {'score': 0.5, 'sentiment': 'NEUTRAL'}
        
        # Generate analysis summary
        current_price = stock_data.get('current_price', 0)
        rsi = stock_data.get('rsi', 50)
        
        analysis_summary = generate_vercel_analysis_summary(current_price, rsi, risk)
        
        response_data = {
            'ticker': ticker,
            'current_price': current_price,
            'rsi': rsi,
            'ma20': stock_data.get('ma20'),
            'ma50': stock_data.get('ma50'),
            'risk_level': risk,
            'analysis_summary': analysis_summary,
            'market_news': news,
            'analyst_recommendations': recommendations,
            'market_sentiment': sentiment,
            'data_source': 'vercel-real-time',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"✅ Vercel: Analysis complete for {ticker}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Vercel stock analysis error for {ticker}: {e}")
        return jsonify({
            'error': 'Analysis failed',
            'ticker': ticker,
            'message': 'Stock analysis temporarily unavailable',
            'data_source': 'vercel-error-fallback'
        })

def generate_vercel_analysis_summary(current_price, rsi, risk):
    """Generate analysis summary - Vercel compatible"""
    try:
        if rsi > 70:
            signal = "SELL"
            reason = f"RSI ({rsi:.1f}) indicates overbought conditions"
        elif rsi < 30:
            signal = "BUY"
            reason = f"RSI ({rsi:.1f}) indicates oversold conditions"
        else:
            signal = "HOLD"
            reason = f"RSI ({rsi:.1f}) is in neutral zone"
        
        risk_multipliers = {'low': 0.02, 'moderate': 0.05, 'high': 0.10}
        stop_loss = current_price * (1 - risk_multipliers.get(risk, 0.05))
        
        return f"Technical indicators suggest {signal}. {reason}. Consider stop-loss at ₹{stop_loss:.2f} for {risk} risk."
        
    except Exception as e:
        return "Technical analysis temporarily unavailable. Please consult financial advisor."

@app.route('/refresh_data')
def refresh_data():
    """Refresh data - Vercel compatible"""
    try:
        clear_vercel_cache()
        return jsonify({
            'message': 'Vercel cache cleared successfully',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'next_refresh': 'Data will be refreshed on next request'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Keep existing routes
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blogs')
def blogs():
    return render_template('blogs.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Vercel health check
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'platform': 'vercel',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'cache_status': 'active'
    })

if __name__ == '__main__':
    print("🚀 Starting Vercel-compatible Stock Predictor...")
    app.run(debug=True, host='0.0.0.0', port=5000)
