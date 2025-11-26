from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from chatbot_intelligence import (
    get_stock_recommendations, get_stop_loss_analysis, get_market_sentiment_analysis,
    get_top_movers, get_beginner_recommendations, extract_stock_symbol,
    get_stock_analysis, get_help_response, handle_portfolio_queries, get_default_response
)
from market_data import get_market_news, get_analyst_recommendations, get_market_sentiment
from multi_source_data import get_stock_data_multi_source, get_multiple_stocks_multi_source, get_data_source_status
import os

app = Flask(__name__)

# Vercel-compatible: Request-scoped caching
_vercel_cache = {}
_cache_timestamps = {}
CACHE_DURATION = timedelta(minutes=5)  # 5-minute cache for Vercel

# Multi-source data configuration
DEFAULT_DATA_SOURCE = 'yahoo'
AVAILABLE_SOURCES = ['yahoo', 'google', 'alpha_vantage', 'fmp']

def get_nifty_200_constituents():
    """Fetch REAL NIFTY 200 index constituents from Yahoo Finance"""
    try:
        print("🌐 Attempting to fetch NIFTY 200 constituents...")
        
        # Method 1: Try to get from NIFTY 200 index
        nifty_200_ticker = yf.Ticker("^NSEI")
        
        # Try to get index components (this might not work directly)
        # Alternative approach: Use known NIFTY 200 constituents from NSE
        nifty_200_symbols = get_nse_nifty_200_stocks()
        
        if nifty_200_symbols:
            print(f"✅ Successfully fetched {len(nifty_200_symbols)} NIFTY 200 constituents")
            return nifty_200_symbols
        else:
            print("⚠️ Could not fetch NIFTY 200 constituents, using fallback")
            return []
            
    except Exception as e:
        print(f"❌ Error fetching NIFTY 200 constituents: {e}")
        return []

def get_nse_nifty_200_stocks():
    """Get NIFTY 200 stocks from NSE website (real-time)"""
    try:
        # Method 1: Try to fetch from NSE API
        nse_url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20200"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(nse_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            stocks = []
            
            if 'data' in data and 'symbols' in data['data']:
                for stock in data['data']['symbols']:
                    symbol = stock.get('symbol', '')
                    if symbol:
                        # Convert NSE format to Yahoo Finance format
                        yahoo_symbol = f"{symbol}.NS"
                        stocks.append(yahoo_symbol)
            
            print(f"✅ Fetched {len(stocks)} stocks from NSE API")
            return stocks[:200]  # Limit to 200 stocks
        
        # Method 2: Fallback to predefined list (but still real-time data)
        return get_major_nifty_stocks()
        
    except Exception as e:
        print(f"❌ Error fetching NSE data: {e}")
        return get_major_nifty_stocks()

def get_major_nifty_stocks():
    """Get COMPREHENSIVE list of major NIFTY stocks for real-time analysis"""
    try:
        # Much larger comprehensive list of NIFTY stocks (still real-time data fetching)
        major_stocks = [
            # TOP 20 LARGE CAP (always included)
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS',
            'INFY.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS',
            'AXISBANK.NS', 'DMART.NS', 'MARUTI.NS', 'ASIANPAINT.NS', 'HCLTECH.NS',
            'ULTRACEMCO.NS', 'BAJFINANCE.NS', 'WIPRO.NS', 'NESTLEIND.NS', 'DRREDDY.NS',
            
            # LARGE CAP BANKS & FINANCIALS
            'LT.NS', 'SUNPHARMA.NS', 'TITAN.NS', 'M&M.NS', 'POWERGRID.NS',
            'NTPC.NS', 'COALINDIA.NS', 'BPCL.NS', 'GAIL.NS', 'ONGC.NS',
            'HDFCLIFE.NS', 'SBILIFE.NS', 'GRASIM.NS', 'ADANIPORTS.NS', 'TECHM.NS',
            
            # LARGE CAP CONSUMER & RETAIL
            'DIVISLAB.NS', 'BRITANNIA.NS', 'DLF.NS', 'BAJAJFINSV.NS', 'DABUR.NS',
            'PIDILITEIND.NS', 'HEROMOTOCO.NS', 'TATASTEEL.NS', 'EICHERMOT.NS', 'BALKRISIND.NS',
            'APOLLOHOSP.NS', 'SHREECEM.NS', 'TATACONSUM.NS', 'GODREJCP.NS', 'UBL.NS',
            
            # LARGE CAP SERVICES & TECHNOLOGY
            'ICICIGI.NS', 'TATAMOTORS.NS', 'JIOFINANCIAL.NS', 'CHOLAHLDNG.NS', 'INDUSINDBK.NS',
            'HDFCAMC.NS', 'SBICARD.NS', 'PNB.NS', 'BANKBARODA.NS', 'CANBK.NS',
            'INDIGO.NS', 'MUTHOOTFIN.NS', 'NAUKRI.NS', 'PAGEIND.NS', 'AMBUJACEM.NS',
            
            # MID CAP & LARGE CAP MIX
            'ACC.NS', 'GMRINFRA.NS', 'TATACOMM.NS', 'SIEMENS.NS', 'L&TFH.NS',
            'COFORGE.NS', 'MRF.NS', 'CEATLTD.NS', 'AUBANK.NS', 'FEDERALBNK.NS',
            'IDFC.NS', 'PFC.NS', 'REC.NS', 'IRCTC.NS', 'IRFC.NS',
            
            # INFRASTRUCTURE & INDUSTRIALS
            'RVNL.NS', 'RVINFRA.NS', 'IRCON.NS', 'NBCC.NS', 'NCC.NS',
            'TATAPOWER.NS', 'JSWSTEEL.NS', 'JINDALSTEL.NS', 'HINDALCO.NS', 'VEDL.NS',
            'COALINDIA.NS', 'NMDC.NS', 'NALCO.NS', 'HINDZINC.NS', 'MOIL.NS',
            
            # PHARMA & HEALTHCARE
            'LUPIN.NS', 'CADILAHC.NS', 'BIOCON.NS', 'AUROPHARMA.NS', 'GLAXO.NS',
            'SANOFI.NS', 'PFIZER.NS', 'CROMPTON.NS', 'LAURUSLABS.NS', 'TORNTPHARM.NS',
            
            # CONSUMER DURABLES & FMCG
            'WHIRLPOOL.NS', 'VOLTAS.NS', 'CUMMINSIND.NS', 'THERMAX.NS', 'ABB.NS',
            'GODREJIND.NS', 'TITAN.NS', 'KAJARIACER.NS', 'CERA.NS', 'JYOTHYLAB.NS',
            
            # IT & SERVICES
            'MINDTREE.NS', 'MPHASIS.NS', 'PERSISTENT.NS', 'LTI.NS', 'COGNIZANT.NS',
            'WIPRO.NS', 'TECHM.NS', 'OFSS.NS', 'SONATSOFTW.NS', 'TRIGYN.NS',
            
            # AUTOMOBILE & ANCILLARIES
            'M&M.NS', 'TATAMOTORS.NS', 'HEROMOTOCO.NS', 'BAJAJ-AUTO.NS', 'TVSMOTOR.NS',
            'EICHERMOT.NS', 'ASHOKLEY.NS', 'MRF.NS', 'CEATLTD.NS', 'APOLLOTYRE.NS',
            
            # REAL ESTATE & CONSTRUCTION
            'DLF.NS', 'GODREJPROP.NS', 'OBEROIREALTY.NS', 'BRIGADE.NS', 'PHOENIXLTD.NS',
            'PRESTIGE.NS', 'ANANTRAJ.NS', 'ASHIANA.NS', 'MAHINDRALIFE.NS', 'PNCINFRA.NS',
            
            # TELECOM & MEDIA
            'BHARTIARTL.NS', 'JIOFINANCIAL.NS', 'TATATELE.NS', 'DISHTV.NS', 'DEN.NS',
            'ZEEL.NS', 'SUNTV.NS', 'BALAJITELE.NS', 'HATHWAY.NS', 'DISH.NS',
            
            # CHEMICALS & FERTILIZERS
            'UPL.NS', 'PIIND.NS', 'SUMICHEM.NS', 'AARTIIND.NS', 'SOLARINDS.NS',
            'COROMANDEL.NS', 'CHAMBLFERT.NS', 'URVARAK.NS', 'DEEPAKFERT.NS', 'GNFC.NS',
            
            # TEXTILES & APPAREL
            'ARVIND.NS', 'PAGEIND.NS', 'KPRMILL.NS', 'TRIDENT.NS', 'WELSPUNLIV.NS',
            'VARDHMAN.NS', 'RAYMOND.NS', 'BOMBAYDYEING.NS', 'SUTLEJTEX.NS', 'CENTURYTEX.NS'
        ]
        
        print(f"📊 Using COMPREHENSIVE NIFTY stocks list ({len(major_stocks)} stocks)")
        print("🔄 All stocks will fetch REAL-TIME data from Yahoo Finance")
        return major_stocks
        
    except Exception as e:
        print(f"Error getting major NIFTY stocks: {e}")
        return []

def get_nifty_200_list(source=None):
    """Multi-source: Fetch REAL-TIME data with caching and fallback handling."""
    global _vercel_cache, _cache_timestamps, CACHE_DURATION
    
    cache_key = f"top_20_stocks_{source or 'default'}"
    current_time = datetime.now()
    
    # Check if we have fresh cached data
    if (cache_key in _cache_timestamps and 
        cache_key in _vercel_cache and
        current_time - _cache_timestamps[cache_key] < CACHE_DURATION):
        
        print(f"✅ Multi-source: Using cached stock data from {source or 'default'}")
        return _vercel_cache[cache_key]
    
    print(f"🔄 Multi-source: Fetching fresh stock data from {source or 'auto'}...")
    
    try:
        # Get stock list
        nifty_200_stocks = get_major_nifty_stocks()
        
        if not nifty_200_stocks:
            print("⚠️ Multi-source: Using fallback stock list")
            nifty_200_stocks = [
                'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS',
                'INFY.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS',
                'AXISBANK.NS', 'DMART.NS', 'MARUTI.NS', 'ASIANPAINT.NS', 'HCLTECH.NS',
                'ULTRACEMCO.NS', 'BAJFINANCE.NS', 'WIPRO.NS', 'NESTLEIND.NS', 'DRREDDY.NS'
            ]
        
        print(f"📊 Multi-source: Processing {len(nifty_200_stocks)} stocks...")
        
        # Use multi-source data fetching
        stock_data = get_multiple_stocks_multi_source(
            nifty_200_stocks[:50],  # Limit to 50 for performance
            source=source,
            timeout=5  # 5 second timeout per stock
        )
        
        print(f"🔄 Multi-source: Successfully fetched {len(stock_data)} stocks")
        
        if stock_data:
            # Convert market cap to INR crores
            usd_to_inr = 83.5
            for stock in stock_data:
                if stock.get('market_cap', 0) > 0:
                    stock['market_cap'] = (stock['market_cap'] * usd_to_inr) / 10000000
                stock['data_source'] = f"multi-source-{stock.get('data_source', 'unknown')}"
            
            # Sort by market cap and get top 20
            sorted_stocks = sorted(stock_data, key=lambda x: x['market_cap'], reverse=True)
            top_20_stocks = sorted_stocks[:20]
            
            # Cache the results
            _vercel_cache[cache_key] = top_20_stocks
            _cache_timestamps[cache_key] = current_time
            
            print(f"✅ Multi-source: Successfully fetched {len(top_20_stocks)} stocks")
            return top_20_stocks
        else:
            print("❌ Multi-source: No stock data fetched, using emergency fallback")
            return get_vercel_emergency_fallback()
            
    except Exception as e:
        print(f"❌ Multi-source: Error fetching stocks - {e}")
        return get_vercel_emergency_fallback()

def get_vercel_emergency_fallback():
    """Emergency fallback for Vercel when everything else fails"""
    return [
        {'symbol': 'RELIANCE.NS', 'market_cap': 177399, 'name': 'RELIANCE INDUSTRIES LTD', 'sector': 'Energy', 'current_price': 1569.90, 'price_change': 1.96, 'volume': 14052178, 'pe_ratio': 25.56, 'dividend_yield': 0.36, 'price_to_book': 2.42, 'data_source': 'vercel-emergency'},
        {'symbol': 'TCS.NS', 'market_cap': 95554, 'name': 'TATA CONSULTANCY SERVICES', 'sector': 'Technology', 'current_price': 3162.90, 'price_change': 0.5, 'volume': 2000000, 'pe_ratio': 28.5, 'dividend_yield': 1.2, 'price_to_book': 12.3, 'data_source': 'vercel-emergency'},
        {'symbol': 'HDFCBANK.NS', 'market_cap': 12892, 'name': 'HDFC BANK LTD', 'sector': 'Banking', 'current_price': 1003.90, 'price_change': -0.2, 'volume': 5000000, 'pe_ratio': 18.5, 'dividend_yield': 1.5, 'price_to_book': 2.1, 'data_source': 'vercel-emergency'},
        {'symbol': 'ICICIBANK.NS', 'market_cap': 82067, 'name': 'ICICI BANK LTD', 'sector': 'Banking', 'current_price': 1375.00, 'price_change': 0.8, 'volume': 4500000, 'pe_ratio': 22.1, 'dividend_yield': 1.8, 'price_to_book': 2.8, 'data_source': 'vercel-emergency'},
        {'symbol': 'HINDUNILVR.NS', 'market_cap': 47581, 'name': 'HINDUSTAN UNILEVER LTD', 'sector': 'FMCG', 'current_price': 2425.20, 'price_change': -0.3, 'volume': 1500000, 'pe_ratio': 55.2, 'dividend_yield': 1.9, 'price_to_book': 8.5, 'data_source': 'vercel-emergency'}
    ]

# Vercel-compatible: No background threading
# All data fetching is now request-scoped with caching

@app.route('/get_top_20_stocks')
def get_top_20_stocks():
    """Multi-source: Return REAL-TIME top 20 stocks with source selection."""
    
    try:
        # Get data source from query parameter
        source = request.args.get('source', DEFAULT_DATA_SOURCE)
        
        print(f"🔄 Multi-source: Fetching top 20 stocks from {source}...")
        
        # Use multi-source stock fetching
        stocks = get_nifty_200_list(source=source)
        
        if stocks:
            response_data = {
                'is_fresh': True,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'next_update_in_minutes': 5,
                'stocks': [stock['symbol'] for stock in stocks[:20]],  # Extract symbols
                'stock_details': stocks[:20],  # Limit to 20
                'data_source': source,
                'cache_status': 'fresh',
                'available_sources': AVAILABLE_SOURCES
            }
            
            print(f"✅ Multi-source: Returning {len(stocks)} stocks from {source}")
            return jsonify(response_data)
        else:
            # Emergency fallback response
            fallback_stocks = get_vercel_emergency_fallback()
            return jsonify({
                'is_fresh': False,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'next_update_in_minutes': 1,
                'stocks': [stock['symbol'] for stock in fallback_stocks],
                'stock_details': fallback_stocks,
                'data_source': 'emergency-fallback',
                'cache_status': 'emergency',
                'available_sources': AVAILABLE_SOURCES,
                'error': 'All data sources failed'
            })
            
    except Exception as e:
        print(f"❌ Multi-source get_top_20_stocks error: {e}")
        # Emergency fallback
        fallback_stocks = get_vercel_emergency_fallback()
        return jsonify({
            'is_fresh': False,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'next_update_in_minutes': 1,
            'stocks': [stock['symbol'] for stock in fallback_stocks],
            'stock_details': fallback_stocks,
            'data_source': 'error-fallback',
            'cache_status': 'error',
            'available_sources': AVAILABLE_SOURCES,
            'error': str(e)
        })

@app.route('/get_data_sources')
def get_data_sources():
    """Get available data sources and their status"""
    try:
        source_status = get_data_source_status()
        
        return jsonify({
            'status': 'success',
            'sources': source_status,
            'default_source': DEFAULT_DATA_SOURCE,
            'available_sources': AVAILABLE_SOURCES,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        print(f"❌ Error getting data sources: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'sources': {},
            'default_source': DEFAULT_DATA_SOURCE,
            'available_sources': AVAILABLE_SOURCES
        }), 500

def get_multi_source_fallback(ticker, risk_appetite, source):
    """Multi-source fallback for stock analysis"""
    try:
        print(f"🔄 Multi-source: Using fallback analysis for {ticker} from {source}")
        
        # Emergency fallback data
        fallback_data = {
            'RELIANCE.NS': {'current_price': 1569.90, 'name': 'RELIANCE INDUSTRIES LTD'},
            'TCS.NS': {'current_price': 3162.90, 'name': 'TATA CONSULTANCY SERVICES'},
            'HDFCBANK.NS': {'current_price': 1003.90, 'name': 'HDFC BANK LTD'},
            'ICICIBANK.NS': {'current_price': 1375.00, 'name': 'ICICI BANK LTD'},
            'HINDUNILVR.NS': {'current_price': 2425.20, 'name': 'HINDUSTAN UNILEVER LTD'}
        }
        
        data = fallback_data.get(ticker, {
            'current_price': 1000.0,
            'name': ticker
        })
        
        current_price = data['current_price']
        rsi = 50.0  # Default neutral
        
        # Generate analysis summary
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
        stop_loss = current_price * (1 - risk_multipliers.get(risk_appetite, 0.05))
        
        analysis_summary = f"All data sources failed for {source}. Using fallback analysis. {reason}. Consider stop-loss at ₹{stop_loss:.2f} for {risk_appetite} risk."
        
        response_data = {
            'ticker': ticker,
            'current_price': current_price,
            'rsi': rsi,
            'ma20': None,
            'ma50': None,
            'risk_level': risk_appetite,
            'analysis_summary': analysis_summary,
            'market_news': {'news': [{'title': 'All data sources unavailable', 'summary': 'Please try again later or contact support'}]},
            'analyst_recommendations': {'recommendation': 'HOLD', 'total_analysts': 0},
            'market_sentiment': {'score': 0.5, 'sentiment': 'NEUTRAL'},
            'data_source': 'multi-source-emergency-fallback',
            'requested_source': source,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': f'All data sources failed for {source}'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Multi-source: Even fallback failed for {ticker} - {e}")
        return jsonify({
            'ticker': ticker,
            'current_price': 1000.0,
            'rsi': 50.0,
            'ma20': None,
            'ma50': None,
            'risk_level': risk_appetite,
            'analysis_summary': 'Analysis temporarily unavailable. Please try again later.',
            'market_news': {'news': [{'title': 'Analysis unavailable', 'summary': 'Please try again later'}]},
            'analyst_recommendations': {'recommendation': 'HOLD', 'total_analysts': 0},
            'market_sentiment': {'score': 0.5, 'sentiment': 'NEUTRAL'},
            'data_source': 'multi-source-emergency-fallback',
            'requested_source': source,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(e)
        })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/old_trading_logic')
def old_trading_logic():
    """Documentation page for original trading logic"""
    return render_template('old_trading_logic.html')

@app.route('/new_trading_logic')
def new_trading_logic():
    """Documentation page for enhanced trading logic"""
    return render_template('new_trading_logic.html')

@app.route('/chatbot')
def chatbot():
    """AI Trading Assistant interface"""
    return render_template('chatbot_interface.html')

@app.route('/chatbot_query', methods=['POST'])
def chatbot_query():
    """Handle chatbot queries with real-time market intelligence"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower().strip()
        
        print(f"🤖 Chatbot Query: {user_message}")
        
        # Initialize response
        response_text = ""
        additional_data = {}
        
        # Stock recommendation queries
        if any(keyword in user_message for keyword in ['best stocks', 'recommend', 'buy today', 'top stocks', 'which stock']):
            response_text, additional_data = get_stock_recommendations(user_message)
        
        # Stop-loss queries
        elif any(keyword in user_message for keyword in ['stop loss', 'stoploss', 'risk', 'exit target']):
            response_text, additional_data = get_stop_loss_analysis(user_message)
        
        # Market sentiment queries
        elif any(keyword in user_message for keyword in ['market sentiment', 'market mood', 'how is market', 'market condition']):
            response_text, additional_data = get_market_sentiment_analysis()
        
        # Top gainers/losers
        elif any(keyword in user_message for keyword in ['top gainers', 'gainers', 'top losers', 'losers', 'movers']):
            response_text, additional_data = get_top_movers(user_message)
        
        # Beginner recommendations
        elif any(keyword in user_message for keyword in ['beginner', 'new investor', 'noob', 'start investing', 'first time']):
            response_text, additional_data = get_beginner_recommendations()
        
        # Specific stock queries
        elif any(ticker in user_message.upper() for ticker in ['RELIANCE', 'TCS', 'HDFC', 'INFY', 'SBIN']):
            stock_symbol = extract_stock_symbol(user_message)
            if stock_symbol:
                response_text, additional_data = get_stock_analysis(stock_symbol)
        
        # General help and explanations
        elif any(keyword in user_message for keyword in ['help', 'explain', 'what is', 'how to', 'tutorial']):
            response_text, additional_data = get_help_response(user_message)
        
        # Watchlist and portfolio queries
        elif any(keyword in user_message for keyword in ['watchlist', 'portfolio', 'add to', 'my stocks']):
            response_text, additional_data = handle_portfolio_queries(user_message)
        
        # Default response
        else:
            response_text = get_default_response(user_message)
        
        return jsonify({
            'response': response_text,
            'data': additional_data
        })
        
    except Exception as e:
        print(f"❌ Chatbot error: {e}")
        return jsonify({
            'response': "I'm having trouble understanding. Could you please rephrase your question? I can help with stock recommendations, stop-loss calculations, market analysis, and investment guidance.",
            'data': {}
        })

# Vercel-specific static file handling
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files with proper headers for Vercel"""
    try:
        response = send_from_directory('static', filename)
        # Add caching headers for better performance
        response.headers['Cache-Control'] = 'public, max-age=31536000'
        return response
    except Exception as e:
        print(f"Error serving static file {filename}: {e}")
        return f"File not found: {filename}", 404

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blogs')
def blogs():
    return render_template('blogs.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/test_functionality')
def test_functionality():
    return render_template('test_functionality.html')

@app.route('/test_quick_analysis')
def test_quick_analysis():
    return render_template('test_quick_analysis.html')

@app.route('/enhanced_demo')
def enhanced_demo():
    return render_template('enhanced_demo.html')

@app.route('/get_market_news/<string:symbol>')
def get_market_news_endpoint(symbol):
    """Get latest market news for a stock"""
    try:
        news = get_market_news(symbol, limit=5)
        return jsonify({
            'status': 'success',
            'news': news,
            'total': len(news)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch market news: {str(e)}'
        }), 500

@app.route('/get_analyst_recommendations/<string:symbol>')
def get_analyst_recommendations_endpoint(symbol):
    """Get analyst recommendations for a stock"""
    try:
        recommendations = get_analyst_recommendations(symbol)
        sentiment = get_market_sentiment(symbol)
        
        return jsonify({
            'status': 'success',
            'recommendations': recommendations,
            'sentiment': sentiment
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch analyst recommendations: {str(e)}'
        }), 500


@app.route('/refresh_data')
def refresh_data():
    """Manual endpoint to trigger data refresh."""
    try:
        get_nifty_200_list()
        return jsonify({
            'status': 'success',
            'message': 'Data refreshed successfully',
            'last_updated': last_data_update.strftime('%Y-%m-%d %H:%M:%S') if last_data_update else None,
            'stocks_count': len(get_nifty_200_list())
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to refresh data: {str(e)}'
        }), 500

@app.route('/get_all_signals')
def get_all_signals():
    """Get buy/sell/hold signals for all top stocks using multi-source data."""
    try:
        print("🔄 Starting multi-source bulk signal analysis...")
        
        # Get stock data from multi-source system
        stocks = get_nifty_200_list()
        signals = []
        
        if not stocks:
            print("❌ No stocks available for analysis")
            return jsonify({
                'status': 'error',
                'message': 'No stock data available'
            }), 500
        
        # Analyze top 20 stocks
        for stock_data in stocks[:20]:
            symbol = stock_data['symbol']
            
            try:
                # Create simple signal based on current price and change
                current_price = stock_data.get('current_price', 1000.0)
                price_change = stock_data.get('price_change', 0.0)
                
                # Simple signal logic
                if price_change > 2:
                    signal = "BUY"
                    signal_color = "success"
                    confidence = min(85, 60 + abs(price_change) * 5)
                elif price_change < -2:
                    signal = "SELL"
                    signal_color = "danger"
                    confidence = min(85, 60 + abs(price_change) * 5)
                else:
                    signal = "HOLD"
                    signal_color = "warning"
                    confidence = 50
                
                signal_data = {
                    'success': True,
                    'symbol': symbol,
                    'signal': signal,
                    'signal_color': signal_color,
                    'confidence': confidence,
                    'current_price': current_price,
                    'price_change': price_change,
                    'name': stock_data.get('name', symbol),
                    'sector': stock_data.get('sector', 'Unknown'),
                    'data_source': stock_data.get('data_source', 'unknown')
                }
                
                signals.append(signal_data)
                
            except Exception as e:
                print(f"⚠️ Failed to analyze {symbol}: {e}")
                # Add fallback signal
                signals.append({
                    'success': False,
                    'symbol': symbol,
                    'signal': 'HOLD',
                    'signal_color': 'warning',
                    'confidence': 50,
                    'current_price': 1000.0,
                    'price_change': 0.0,
                    'name': symbol,
                    'sector': 'Unknown',
                    'data_source': 'fallback',
                    'error': str(e)
                })
        
        print(f"✅ Multi-source bulk analysis complete: {len(signals)} signals")
        
        return jsonify({
            'status': 'success',
            'signals': signals,
            'total_analyzed': len(signals)
        })
        
    except Exception as e:
        print(f"❌ Error in bulk signal analysis: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to analyze signals: {str(e)}'
        }), 500

@app.route('/get_stock_data/<string:ticker>/<string:risk_appetite>')
def get_stock_data(ticker, risk_appetite):
    """Multi-source: Get stock analysis with source selection and fallback handling"""
    try:
        # Get data source from query parameter
        source = request.args.get('source', DEFAULT_DATA_SOURCE)
        
        # Get custom parameters if risk_appetite is Custom
        custom_stop_loss = request.args.get('customStopLoss', type=float)
        custom_exit_target = request.args.get('customExitTarget', type=float)
        
        print(f"🔄 Multi-source: Analyzing {ticker} with {risk_appetite} risk from {source}...")
        if risk_appetite == 'Custom' and custom_stop_loss and custom_exit_target:
            print(f"🎯 Custom parameters: Stop-Loss={custom_stop_loss}%, Exit Target={custom_exit_target}%")
        
        # Check cache first
        cache_key = f"stock_{ticker}_{risk_appetite}_{source}"
        current_time = datetime.now()
        
        if (cache_key in _cache_timestamps and 
            cache_key in _vercel_cache and
            current_time - _cache_timestamps[cache_key] < timedelta(minutes=1)):
            
            print(f"✅ Multi-source: Using cached analysis for {ticker} from {source}")
            return jsonify(_vercel_cache[cache_key])
        
        # Add .NS suffix if not present for Indian stocks
        if not ticker.endswith('.NS'):
            ticker = ticker + '.NS'
        
        # Use multi-source data fetching
        stock_data = get_stock_data_multi_source(ticker, source=source, timeout=10)
        
        # Always try to run enhanced trading logic, even if data sources fail
        current_price = 0
        actual_source = "multi-source-emergency-fallback"
        
        if stock_data:
            data = stock_data['data']
            actual_source = stock_data['source']
            current_price = data.get('current_price', 0)
        
        # Calculate comprehensive technical indicators using direct Yahoo Finance
        try:
            # Get historical data for technical indicators
            stock = yf.Ticker(ticker)
            hist = stock.history(period="60d", interval="1d")
            
            if not hist.empty and len(hist) >= 50:
                # Use current price from historical data if data source failed
                if current_price == 0:
                    current_price = hist['Close'].iloc[-1]
                
                # Calculate moving averages
                hist['MA20'] = hist['Close'].rolling(window=20).mean()
                hist['MA50'] = hist['Close'].rolling(window=50).mean()
                hist['MA200'] = hist['Close'].rolling(window=200).mean()
                
                # RSI calculation
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss.replace(0, 1)
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1]
                
                # ATR calculation
                high_low = hist['High'] - hist['Low']
                high_close = abs(hist['High'] - hist['Close'].shift())
                low_close = abs(hist['Low'] - hist['Close'].shift())
                true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                atr = true_range.rolling(window=14).mean().iloc[-1]
                
                # Volume analysis
                avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
                current_volume = hist['Volume'].iloc[-1]
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                
                # Enhanced signal generation
                signal_score = 0
                signal_factors = []
                
                # RSI scoring (40% weight)
                if current_rsi < 30:
                    signal_score += 40
                    signal_factors.append("RSI oversold")
                elif current_rsi > 70:
                    signal_score -= 40
                    signal_factors.append("RSI overbought")
                elif 30 <= current_rsi <= 50:
                    signal_score += 10
                    signal_factors.append("RSI bullish")
                elif 50 < current_rsi <= 70:
                    signal_score -= 10
                    signal_factors.append("RSI bearish")
                
                # Moving averages scoring (25% weight)
                if current_price > hist['MA20'].iloc[-1] > hist['MA50'].iloc[-1]:
                    signal_score += 25
                    signal_factors.append("Uptrend (MA20 > MA50)")
                elif current_price < hist['MA20'].iloc[-1] < hist['MA50'].iloc[-1]:
                    signal_score -= 25
                    signal_factors.append("Downtrend (MA20 < MA50)")
                
                # Volume confirmation (10% weight)
                if volume_ratio > 1.5:
                    signal_score += 10
                    signal_factors.append("High volume confirmation")
                elif volume_ratio < 0.5:
                    signal_score -= 10
                    signal_factors.append("Low volume warning")
                
                # ATR volatility adjustment (5% weight)
                if atr > 0:
                    price_atr_ratio = (atr / current_price) * 100
                    if price_atr_ratio < 2:
                        signal_score += 5
                        signal_factors.append("Low volatility")
                    elif price_atr_ratio > 5:
                        signal_score -= 5
                        signal_factors.append("High volatility")
                
                # MACD scoring (20% weight)
                try:
                    exp1 = hist['Close'].ewm(span=12).mean()
                    exp2 = hist['Close'].ewm(span=26).mean()
                    macd = exp1 - exp2
                    signal_line = macd.ewm(span=9).mean()
                    macd_histogram = macd - signal_line
                    
                    if macd.iloc[-1] > signal_line.iloc[-1] and macd_histogram.iloc[-1] > 0:
                        signal_score += 20
                        signal_factors.append("MACD bullish")
                    elif macd.iloc[-1] < signal_line.iloc[-1] and macd_histogram.iloc[-1] < 0:
                        signal_score -= 20
                        signal_factors.append("MACD bearish")
                except:
                    signal_factors.append("MACD unavailable")
                
                # Generate signal based on score
                if signal_score >= 60:
                    signal = "STRONG_BUY"
                    signal_color = "success"
                    confidence = min(95, 70 + (signal_score - 60) // 4)
                elif signal_score >= 20:
                    signal = "BUY"
                    signal_color = "success"
                    confidence = min(85, 60 + (signal_score - 20) // 2)
                elif signal_score <= -60:
                    signal = "STRONG_SELL"
                    signal_color = "danger"
                    confidence = min(95, 70 + (-signal_score - 60) // 4)
                elif signal_score <= -20:
                    signal = "SELL"
                    signal_color = "danger"
                    confidence = min(85, 60 + (-signal_score - 20) // 2)
                else:
                    signal = "HOLD"
                    signal_color = "warning"
                    confidence = 70
                
                # Enhanced risk management
                recent_low = hist['Low'][-20:].min()
                recent_high = hist['High'][-20:].max()
                
                # ATR-based stop loss
                signal = "SELL"
                signal_color = "danger"
                confidence = min(85, 60 + abs(signal_score) // 10)
                reason = f"Bearish signal: {', '.join(signal_factors[:2])}"
            else:
                signal = "HOLD"
                signal_color = "warning"
                confidence = 50
                reason = f"Neutral signal: {', '.join(signal_factors[:2])}"
            
            print(f"🎯 Enhanced Signal Generated: {signal} (Score: {signal_score}, Confidence: {confidence}%)")
            print(f"📋 Signal Factors: {', '.join(signal_factors)}")
            
            # Calculate risk multipliers - handle custom parameters
            if risk_appetite == 'Custom' and custom_stop_loss and custom_exit_target:
                stop_loss_multiplier = custom_stop_loss / 100
                exit_multiplier = custom_exit_target / 100
                print(f"🎯 Using custom multipliers: Stop-Loss={stop_loss_multiplier:.3f}, Exit={exit_multiplier:.3f}")
            else:
                risk_multipliers = {'low': 0.02, 'moderate': 0.05, 'high': 0.10, 'medium': 0.05}
                stop_loss_multiplier = risk_multipliers.get(risk_appetite.lower(), 0.05)
                exit_multiplier = stop_loss_multiplier * 3  # 3:1 risk-reward ratio for non-custom
            
            # Enhanced risk management with ATR-based stop-loss
            if risk_appetite == 'Custom' and custom_stop_loss and custom_exit_target:
                # Custom parameters
                stop_loss = current_price * (1 - stop_loss_multiplier)
                exit_price = current_price * (1 + exit_multiplier)
                target_profit = exit_price - current_price
            else:
                # ATR-based stop-loss (2x ATR below recent low for better risk management)
                atr_stop_loss = recent_low - (2 * atr)
                percentage_stop_loss = current_price * (1 - stop_loss_multiplier)
                
                # Use the more conservative (higher) stop-loss
                stop_loss = max(atr_stop_loss, percentage_stop_loss)
                
                # Exit target based on 3:1 risk-reward ratio
                risk_amount = current_price - stop_loss
                exit_price = current_price + (3 * risk_amount)
                target_profit = 3 * risk_amount
            
            # Support/Resistance levels
            support_level = recent_low
            resistance_level = recent_high
            
            print(f"💰 Enhanced Risk Management:")
            print(f"   Current Price: ₹{current_price:.2f}")
            print(f"   Stop-Loss: ₹{stop_loss:.2f} (ATR-based: ₹{atr_stop_loss:.2f if atr_stop_loss else 'N/A'})")
            print(f"   Exit Target: ₹{exit_price:.2f}")
            print(f"   Target Profit: ₹{target_profit:.2f}")
            print(f"   Support Level: ₹{support_level:.2f}")
            print(f"   Resistance Level: ₹{resistance_level:.2f}")
            print(f"   Risk Multipliers: StopLoss={stop_loss_multiplier:.3f}, Exit={exit_multiplier:.3f}")
            
            # Enhanced analysis summary
            analysis_summary = f"Enhanced technical analysis: {signal}. {reason}. "
            analysis_summary += f"ATR-based stop-loss at ₹{stop_loss:.2f}, exit target ₹{exit_price:.2f}. "
            analysis_summary += f"Support at ₹{support_level:.2f}, resistance at ₹{resistance_level:.2f}."
            
            # Get market data with timeout protection
            try:
                news = get_market_news(ticker, limit=3)
                recommendations = get_analyst_recommendations(ticker)
                sentiment = get_market_sentiment(ticker)
            except Exception as e:
                print(f"⚠️ Multi-source: Market data error for {ticker} - {e}")
                news = {'news': [{'title': 'Market data temporarily unavailable', 'summary': 'Please try again later'}]}
                recommendations = {'recommendation': 'HOLD', 'total_analysts': 0}
                sentiment = {'score': 0.5, 'sentiment': 'NEUTRAL'}
            
            response_data = {
                'ticker': ticker,
                'current_price': round(current_price, 2),
                # Enhanced technical indicators
                'rsi': round(rsi, 2) if rsi else 50.0,
                'ma20': round(ma20, 2) if ma20 else None,
                'ma50': round(ma50, 2) if ma50 else None,
                'ma200': round(ma200, 2) if ma200 else None,
                'atr': round(atr, 2) if atr else 0.0,
                'macd': round(macd_current, 4) if macd_current else 0.0,
                'macd_signal': round(macd_signal, 4) if macd_signal else 0.0,
                'macd_histogram': round(macd_hist, 4) if macd_hist else 0.0,
                'volume_ratio': round(volume_ratio, 2) if volume_ratio else 1.0,
                # Support and resistance levels
                'support_level': round(support_level, 2) if support_level else None,
                'resistance_level': round(resistance_level, 2) if resistance_level else None,
                # Signal analysis
                'signal_score': signal_score,
                'signal_factors': signal_factors,
                'risk_level': risk_appetite,
                'analysis_summary': analysis_summary,
                'market_news': news,
                'analyst_recommendations': recommendations,
                'market_sentiment': sentiment,
                'data_source': f"multi-source-{actual_source}",
                'requested_source': source,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                # Enhanced trading prediction fields
                'signal': signal,
                'signal_color': signal_color,
                'entry_price': round(current_price, 2),
                'exit_price': round(exit_price, 2),
                'stop_loss': round(stop_loss, 2),
                'confidence': confidence,
                'target_profit': round(target_profit, 2),
                'risk_reward_ratio': round(target_profit / (current_price - stop_loss), 2) if current_price > stop_loss else 2.0,
                'time_horizon': '1-2 weeks',
                'atr_stop_loss': round(atr_stop_loss, 2) if 'atr_stop_loss' in locals() else None,
                'chart_data': {
                    'dates': [],
                    'prices': [],
                    'volumes': []
                }
            }
            
            # Cache the result
            _vercel_cache[cache_key] = response_data
            _cache_timestamps[cache_key] = current_time
            
            print(f"✅ Multi-source: Analysis complete for {ticker} from {actual_source}")
            return jsonify(response_data)
        
        else:
            print(f"❌ Multi-source: All sources failed for {ticker}, using fallback")
            return get_multi_source_fallback(ticker, risk_appetite, source)
            
    except Exception as e:
        print(f"❌ Multi-source: Stock analysis error for {ticker}: {e}")
        return get_multi_source_fallback(ticker, risk_appetite, source)

def get_multi_source_fallback(ticker, risk_appetite, source):
    """Multi-source fallback for stock analysis"""
    try:
        print(f"🔄 Multi-source: Using fallback analysis for {ticker} from {source}")
        
        # Emergency fallback data
        fallback_data = {
            'RELIANCE.NS': {'current_price': 1569.90, 'name': 'RELIANCE INDUSTRIES LTD'},
            'TCS.NS': {'current_price': 3162.90, 'name': 'TATA CONSULTANCY SERVICES'},
            'HDFCBANK.NS': {'current_price': 1003.90, 'name': 'HDFC BANK LTD'},
            'ICICIBANK.NS': {'current_price': 1375.00, 'name': 'ICICI BANK LTD'},
            'HINDUNILVR.NS': {'current_price': 2425.20, 'name': 'HINDUSTAN UNILEVER LTD'}
        }
        
        data = fallback_data.get(ticker, {
            'current_price': 1000.0,
            'name': ticker
        })
        
        current_price = data['current_price']
        rsi = 50.0  # Default neutral
        
        # Generate analysis summary
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
        stop_loss = current_price * (1 - risk_multipliers.get(risk_appetite, 0.05))
        
        analysis_summary = f"All data sources failed for {source}. Using fallback analysis. {reason}. Consider stop-loss at ₹{stop_loss:.2f} for {risk_appetite} risk."
        
        response_data = {
            'ticker': ticker,
            'current_price': current_price,
            'rsi': rsi,
            'ma20': None,
            'ma50': None,
            'risk_level': risk_appetite,
            'analysis_summary': analysis_summary,
            'market_news': {'news': [{'title': 'All data sources unavailable', 'summary': 'Please try again later or contact support'}]},
            'analyst_recommendations': {'recommendation': 'HOLD', 'total_analysts': 0},
            'market_sentiment': {'score': 0.5, 'sentiment': 'NEUTRAL'},
            'data_source': 'multi-source-emergency-fallback',
            'requested_source': source,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': f'All data sources failed for {source}'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Multi-source: Even fallback failed for {ticker} - {e}")
        return jsonify({
            'ticker': ticker,
            'current_price': 1000.0,
            'rsi': 50.0,
            'ma20': None,
            'ma50': None,
            'risk_level': risk_appetite,
            'analysis_summary': 'Analysis temporarily unavailable. Please try again later.',
            'market_news': {'news': [{'title': 'Analysis unavailable', 'summary': 'Please try again later'}]},
            'analyst_recommendations': {'recommendation': 'HOLD', 'total_analysts': 0},
            'market_sentiment': {'score': 0.5, 'sentiment': 'NEUTRAL'},
            'data_source': 'multi-source-emergency-fallback',
            'requested_source': source,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(e)
        })
        
        # RSI calculation (same as bulk analysis)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
        
        hist['ATR'] = talib.ATR(hist['High'], hist['Low'], hist['Close'], timeperiod=14)
        
        print(f"📈 Calculated indicators, data length after calculations: {len(hist)}")
        
        # Remove rows with NaN values (only after all calculations)
        hist_clean = hist.dropna()
        print(f"🧹 Data length after dropping NaN: {len(hist_clean)}")
        
        if hist_clean.empty:
            print("❌ No valid data after dropping NaN values")
            return create_fallback_response()

        hist = hist_clean

        # Generate Signal based on multiple conditions
        # Condition 1: SMA Crossover
        sma_cross_signal = np.where(hist['SMA50'] > hist['SMA200'], 1, -1)
        
        # Condition 2: RSI levels (oversold/overbought)
        rsi_signal = np.where(hist['RSI'] < 30, 1, np.where(hist['RSI'] > 70, -1, 0))
        
        # Combined signal (weighted approach)
        hist['Signal'] = np.where(sma_cross_signal == 1, 1, 
                                np.where(sma_cross_signal == -1, -1, rsi_signal))
        
        # Generate trading signals (buy/sell/hold)
        hist['Position'] = hist['Signal'].diff()

        # Get signal using UNIFIED function for 100% consistency
        unified_signal = calculate_unified_signal(ticker, period=period, interval=interval)
        
        if not hist.empty and unified_signal['success']:
            signal_text = unified_signal['signal']
            current_price = unified_signal['current_price']
            current_sma_50 = unified_signal['sma_50']
            current_sma_200 = unified_signal['sma_200']
            current_rsi = unified_signal['rsi']
            
            print(f"✅ UNIFIED signal for {ticker}: {signal_text}")

            # Suggest Entry, Exit, and Stop-Loss
            recent_low = hist['Low'][-14:].min()
            recent_high = hist['High'][-14:].max()
            entry_price = f'{recent_low:.2f}'
            
            # Adjust exit price and stop-loss based on risk appetite
            if risk_appetite == 'Custom' and custom_stop_loss and custom_exit_target:
                # Custom risk - use user-defined percentages
                stop_loss = f'{(recent_low * (1 - custom_stop_loss/100)):.2f}'
                exit_price = f'{(recent_low * (1 + custom_exit_target/100)):.2f}'
            elif risk_appetite == 'Low':
                stop_loss = f'{(recent_low * 0.98):.2f}' # 2% below the 14-day low
                exit_price = f'{(recent_low * 1.06):.2f}'  # 6% above entry (3:1 risk-reward)
            elif risk_appetite == 'Medium':
                stop_loss = f'{(recent_low * 0.95):.2f}' # 5% below the 14-day low
                exit_price = f'{(recent_low * 1.15):.2f}'  # 15% above entry (3:1 risk-reward)
            else: # High
                stop_loss = f'{(recent_low * 0.90):.2f}' # 10% below the 14-day low
                exit_price = f'{(recent_low * 1.30):.2f}'  # 30% above entry (3:1 risk-reward)

            attributes = {
                'SMA50': f'{hist["SMA50"].iloc[-1]:.2f}',
                'SMA200': f'{hist["SMA200"].iloc[-1]:.2f}',
                'RSI': f'{hist["RSI"].iloc[-1]:.2f}',
                'ATR': f'{hist["ATR"].iloc[-1]:.2f}'
            }
            data = hist.to_json()
            
            print(f"✅ Successfully analyzed {ticker}: {signal_text}")
            
            # Get additional market data
            try:
                print(f"📰 Fetching market news for {ticker}...")
                market_news = get_market_news(ticker, limit=3)
                print(f"📊 Getting analyst recommendations for {ticker}...")
                analyst_data = get_analyst_recommendations(ticker)
                market_sentiment = get_market_sentiment(ticker)
            except Exception as e:
                print(f"⚠️ Error fetching additional market data: {e}")
                market_news = []
                analyst_data = get_default_recommendations()
                market_sentiment = {'sentiment': 'UNKNOWN', 'score': 0.5, 'summary': 'Unable to determine sentiment'}

            response = {
                'signal': signal_text,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'stop_loss': stop_loss,
                'attributes': attributes,
                'data': data,
                # New fields
                'market_news': market_news,
                'analyst_recommendations': analyst_data,
                'market_sentiment': market_sentiment,
                'analysis_summary': generate_analysis_summary(signal_text, analyst_data, market_sentiment)
            }

            return jsonify(response)
        else:
            print("❌ Empty dataframe after processing")
            return create_fallback_response()
            
    except Exception as e:
        print(f"❌ Error in get_stock_data: {str(e)}")
        return create_fallback_response()

def calculate_unified_signal(symbol, period="2y", interval="1d"):
    """
    UNIFIED signal calculation function used by ALL endpoints
    Ensures 100% consistency across the application
    Returns: dict with all signal data
    """
    try:
        print(f"🔍 UNIFIED analysis for {symbol} (period: {period}, interval: {interval})")
        
        # Get stock data
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period, interval=interval)
        
        if hist.empty:
            print(f"❌ No data for {symbol}")
            return create_fallback_signal_dict(symbol)
        
        # Calculate ALL indicators using EXACT same method
        close = hist['Close']
        sma_50 = close.rolling(window=50).mean()
        sma_200 = close.rolling(window=200).mean()
        
        # RSI calculation (manual method for consistency)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Get latest values
        current_price = close.iloc[-1]
        current_sma_50 = sma_50.iloc[-1]
        current_sma_200 = sma_200.iloc[-1] if not pd.isna(sma_200.iloc[-1]) else current_sma_50
        current_rsi = rsi.iloc[-1]
        
        print(f"📊 {symbol} - Price: {current_price:.2f}, SMA50: {current_sma_50:.2f}, SMA200: {current_sma_200:.2f}, RSI: {current_rsi:.2f}")
        
        # Generate signal using unified logic
        signal, signal_color = generate_unified_signal_logic(current_price, current_sma_50, current_sma_200, current_rsi)
        
        # Return unified signal data
        return {
            'symbol': symbol,
            'signal': signal,
            'signal_color': signal_color,
            'current_price': round(current_price, 2),
            'sma_50': round(current_sma_50, 2) if not pd.isna(current_sma_50) else None,
            'sma_200': round(current_sma_200, 2) if not pd.isna(current_sma_200) else None,
            'rsi': round(current_rsi, 2) if not pd.isna(current_rsi) else None,
            'success': True
        }
        
    except Exception as e:
        print(f"❌ Error in unified signal calculation for {symbol}: {e}")
        return create_fallback_signal_dict(symbol)

def generate_unified_signal_logic(current_price, sma_50, sma_200, rsi):
    """
    UNIFIED signal logic - single source of truth
    """
    try:
        # Handle NaN values
        sma_200_valid = not pd.isna(sma_200)
        rsi_valid = not pd.isna(rsi)
        
        # More balanced BUY conditions
        buy_conditions = (
            current_price > sma_50 and
            (not sma_200_valid or current_price > sma_200) and
            rsi_valid and 25 <= rsi <= 75
        )
        
        # More balanced SELL conditions  
        sell_conditions = (
            current_price < sma_50 and
            (not sma_200_valid or current_price < sma_200) and
            rsi_valid and 25 <= rsi <= 75
        )
        
        if buy_conditions:
            return "BUY", "success"
        elif sell_conditions:
            return "SELL", "danger"
        else:
            return "HOLD", "warning"
            
    except Exception as e:
        print(f"Error in signal logic: {e}")
        return "HOLD", "warning"

def create_fallback_signal_dict(symbol):
    """Create fallback signal data"""
    return {
        'symbol': symbol,
        'signal': 'HOLD',
        'signal_color': 'warning',
        'current_price': None,
        'sma_50': None,
        'sma_200': None,
        'rsi': None,
        'success': False
    }

def generate_analysis_summary(signal, analyst_data, sentiment):
    """Generate a comprehensive analysis summary"""
    try:
        summary_parts = []
        
        # Signal-based summary
        if signal == 'BUY':
            summary_parts.append("Technical indicators suggest a BUY signal")
        elif signal == 'SELL':
            summary_parts.append("Technical indicators suggest a SELL signal")
        else:
            summary_parts.append("Technical indicators suggest HOLDING")
        
        # Analyst summary
        if analyst_data.get('total_analysts', 0) > 0:
            total = analyst_data['total_analysts']
            strong_buy = analyst_data.get('strong_buy', 0)
            buy = analyst_data.get('buy', 0)
            hold = analyst_data.get('hold', 0)
            
            if strong_buy + buy > hold:
                summary_parts.append(f"Analysts are generally bullish ({strong_buy + buy} out of {total} recommend buying)")
            elif hold > strong_buy + buy:
                summary_parts.append(f"Analysts recommend holding ({hold} out of {total} analysts)")
            else:
                summary_parts.append(f"Analyst opinions are mixed ({total} analysts covering)")
        else:
            summary_parts.append("Analyst recommendations not available")
        
        # Sentiment summary
        sentiment_score = sentiment.get('score', 0.5)
        if sentiment_score > 0.6:
            summary_parts.append("Market sentiment appears positive")
        elif sentiment_score < 0.4:
            summary_parts.append("Market sentiment appears negative")
        else:
            summary_parts.append("Market sentiment appears neutral")
        
        return ". ".join(summary_parts) + "."
        
    except Exception as e:
        print(f"Error generating analysis summary: {e}")
        return "Analysis summary unavailable."

def get_default_recommendations():
    """Default recommendations when data is not available"""
    return {
        'strong_buy': 0,
        'buy': 0,
        'hold': 0,
        'sell': 0,
        'strong_sell': 0,
        'total_analysts': 0,
        'target_price': None,
        'source': 'Not Available',
        'summary': 'Analyst recommendations not available at this time.'
    }

def create_emergency_fallback_response(ticker, risk_appetite, current_price=0):
    """Create emergency fallback response with enhanced trading logic when all sources fail"""
    try:
        # Try to get at least basic price data from Yahoo Finance
        if current_price == 0:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d", interval="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
        
        # Generate basic signal with minimal data
        if current_price > 0:
            # Simple fallback signal logic
            signal = "HOLD"
            signal_color = "warning"
            confidence = 50
            signal_factors = ["Limited data available"]
            
            # Basic risk management
            stop_loss = current_price * 0.95  # 5% stop loss
            exit_target = current_price * 1.10  # 10% target
            
            return jsonify({
                'signal': signal,
                'signal_color': signal_color,
                'confidence': confidence,
                'signal_score': 0,
                'signal_factors': signal_factors,
                'current_price': round(current_price, 2),
                'entry_price': round(current_price, 2),
                'exit_price': round(exit_target, 2),
                'stop_loss': round(stop_loss, 2),
                'target_profit': round(exit_target - current_price, 2),
                'risk_reward_ratio': '2:1',
                'time_horizon': '1 week',
                # Technical indicators (limited)
                'rsi': 50.0,
                'ma20': None,
                'ma50': None,
                'ma200': None,
                'atr': None,
                'volume_ratio': None,
                'macd': None,
                'macd_signal': None,
                'macd_histogram': None,
                'support_level': None,
                'resistance_level': None,
                # Market data
                'market_news': {'news': [{'title': 'All data sources unavailable', 'summary': 'Please try again later or contact support'}]},
                'analyst_recommendations': {'recommendation': 'HOLD', 'total_analysts': 0},
                'market_sentiment': {'sentiment': 'NEUTRAL', 'score': 0.5},
                'analysis_summary': f"All data sources failed. Using basic analysis. RSI (50.0) is in neutral zone. Consider stop-loss at ₹{stop_loss:.2f} for {risk_appetite} risk.",
                'data_source': 'multi-source-emergency-fallback',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ticker': ticker,
                'risk_level': risk_appetite,
                'error': 'All data sources failed'
            })
        else:
            # Complete fallback when no price data available
            return jsonify({
                'signal': 'HOLD',
                'signal_color': 'warning',
                'confidence': 50,
                'signal_score': 0,
                'signal_factors': ['No data available'],
                'current_price': 0,
                'entry_price': 0,
                'exit_price': 0,
                'stop_loss': 0,
                'target_profit': 0,
                'risk_reward_ratio': 'N/A',
                'time_horizon': 'N/A',
                # Technical indicators
                'rsi': None,
                'ma20': None,
                'ma50': None,
                'ma200': None,
                'atr': None,
                'volume_ratio': None,
                'macd': None,
                'macd_signal': None,
                'macd_histogram': None,
                'support_level': None,
                'resistance_level': None,
                # Market data
                'market_news': {'news': [{'title': 'All data sources unavailable', 'summary': 'Please try again later or contact support'}]},
                'analyst_recommendations': {'recommendation': 'HOLD', 'total_analysts': 0},
                'market_sentiment': {'sentiment': 'NEUTRAL', 'score': 0.5},
                'analysis_summary': 'All data sources failed. No price data available.',
                'data_source': 'multi-source-emergency-fallback',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ticker': ticker,
                'risk_level': risk_appetite,
                'error': 'All data sources failed'
            })
            
    except Exception as e:
        print(f"❌ Error in emergency fallback: {e}")
        return jsonify({
            'signal': 'HOLD',
            'signal_color': 'warning',
            'confidence': 50,
            'current_price': 0,
            'entry_price': 0,
            'exit_price': 0,
            'stop_loss': 0,
            'rsi': 50.0,
            'ma20': None,
            'ma50': None,
            'ma200': None,
            'atr': None,
            'market_news': {'news': [{'title': 'All data sources unavailable', 'summary': 'Please try again later or contact support'}]},
            'analyst_recommendations': {'recommendation': 'HOLD', 'total_analysts': 0},
            'market_sentiment': {'sentiment': 'NEUTRAL', 'score': 0.5},
            'analysis_summary': 'All data sources failed. Please try again later.',
            'data_source': 'multi-source-emergency-fallback',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ticker': ticker,
            'risk_level': risk_appetite,
            'error': 'All data sources failed'
        })

def create_fallback_response():
    """Create a fallback response when stock data is not available"""
    return jsonify({
        'signal': 'Not Available',
        'entry_price': 'Not Available',
        'exit_price': 'Not Available',
        'stop_loss': 'Not Available',
        'attributes': {
            'SMA50': 'Not Available',
            'SMA200': 'Not Available',
            'RSI': 'Not Available',
            'ATR': 'Not Available'
        },
        'data': pd.DataFrame().to_json(),
        'market_news': [],
        'analyst_recommendations': get_default_recommendations(),
        'market_sentiment': {'sentiment': 'UNKNOWN', 'score': 0.5, 'summary': 'Unable to determine sentiment'},
        'analysis_summary': 'Analysis unavailable due to data issues.'
    })

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Stock Predictor API',
        'version': '2.0',
        'static_files': 'ok'
    })

@app.route('/api/health')
def api_health():
    """API health check for Vercel"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'static': '/static/*',
            'api': '/api/*',
            'main': '/'
        }
    })

# Production deployment
if __name__ == '__main__':
    # Fetch the list on startup
    print("Initializing Stock Predictor Application...")
    # Multi-source: Initialize with data fetch
    get_nifty_200_list()
    
    print("Starting Flask server with multi-source data support...")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
