from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import yfinance as yf
import pandas as pd
import numpy as np
import talib
import threading
import time
import requests
from datetime import datetime, timedelta
from market_data import get_market_news, get_analyst_recommendations, get_market_sentiment
import os

app = Flask(__name__)

top_20_stocks = []
last_data_update = None
data_update_interval = 3600  # Refresh data every hour (3600 seconds)

def get_nifty_200_list():
    """Fetches top 20 NIFTY stocks by market cap using Yahoo Finance."""
    global top_20_stocks, last_data_update
    
    try:
        print("Fetching top NIFTY stocks from Yahoo Finance...")
        
        # Major NIFTY stocks to analyze (these are the largest companies)
        nifty_stocks = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS',
            'INFY.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS',
            'AXISBANK.NS', 'DMART.NS', 'MARUTI.NS', 'ASIANPAINT.NS', 'HCLTECH.NS',
            'ULTRACEMCO.NS', 'BAJFINANCE.NS', 'WIPRO.NS', 'NESTLEIND.NS', 'DRREDDY.NS',
            'LT.NS', 'SUNPHARMA.NS', 'TITAN.NS', 'M&M.NS', 'POWERGRID.NS',
            'NTPC.NS', 'COALINDIA.NS', 'BPCL.NS', 'GAIL.NS', 'ONGC.NS',
            'HDFCLIFE.NS', 'SBILIFE.NS', 'GRASIM.NS', 'ADANIPORTS.NS', 'TECHM.NS'
        ]
        
        # Fetch market cap data for all stocks
        stock_data = []
        for symbol in nifty_stocks:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Get market cap (in crores INR)
                market_cap = info.get('marketCap', 0)
                if market_cap and market_cap > 0:
                    # Convert to INR crores for better understanding
                    market_cap_inr_cr = (market_cap * 83) / 10000000  # Approx 1 USD = 83 INR
                    stock_data.append({
                        'symbol': symbol,
                        'market_cap': market_cap_inr_cr,
                        'name': info.get('shortName', symbol),
                        'sector': info.get('sector', 'Unknown')
                    })
                    print(f"✅ {symbol}: ₹{market_cap_inr_cr:.0f} cr market cap")
                else:
                    print(f"⚠️ {symbol}: No market cap data")
                    
            except Exception as e:
                print(f"❌ {symbol}: Error - {str(e)}")
                continue
        
        # Sort by market cap and get top 20
        if stock_data:
            sorted_stocks = sorted(stock_data, key=lambda x: x['market_cap'], reverse=True)
            top_20_stocks = [stock['symbol'] for stock in sorted_stocks[:20]]
            
            print(f"\n🏆 TOP 20 STOCKS BY MARKET CAP:")
            for i, stock in enumerate(sorted_stocks[:20], 1):
                print(f"{i:2d}. {stock['symbol']:12s} - ₹{stock['market_cap']:,.0f} cr ({stock['name']})")
            
            last_data_update = datetime.now()
            print(f"\n✅ Successfully fetched {len(top_20_stocks)} top stocks from Yahoo Finance at {last_data_update.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            # Fallback to static list if Yahoo Finance fails
            print("⚠️ Yahoo Finance failed, using fallback list")
            fallback_stocks = [
                'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS',
                'INFY.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS',
                'AXISBANK.NS', 'DMART.NS', 'MARUTI.NS', 'ASIANPAINT.NS', 'HCLTECH.NS',
                'ULTRACEMCO.NS', 'BAJFINANCE.NS', 'WIPRO.NS', 'NESTLEIND.NS', 'DRREDDY.NS'
            ]
            top_20_stocks = fallback_stocks
            last_data_update = datetime.now()
            print(f"Using fallback list of {len(top_20_stocks)} stocks")
            
    except Exception as e:
        print(f"❌ Error fetching from Yahoo Finance: {e}")
        # Final fallback
        top_20_stocks = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS']
        last_data_update = datetime.now()

def periodic_data_refresh():
    """Background thread to periodically refresh NIFTY 200 data."""
    while True:
        try:
            print(f"Starting periodic data refresh at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            get_nifty_200_list()
            print(f"Data refresh completed. Next refresh in {data_update_interval//60} minutes.")
        except Exception as e:
            print(f"Error in periodic refresh: {e}")
        time.sleep(data_update_interval)

def is_data_fresh():
    """Check if the current data is fresh (not older than the refresh interval)."""
    if last_data_update is None:
        return False
    return (datetime.now() - last_data_update).total_seconds() < data_update_interval

@app.route('/get_top_20_stocks')
def get_top_20_stocks():
    """Return top 20 stocks with detailed information including sector and market cap categories."""
    
    # Get detailed stock information with sectors and market caps
    stock_details = []
    for symbol in top_20_stocks:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            market_cap = info.get('marketCap', 0)
            market_cap_inr_cr = (market_cap * 83) / 10000000 if market_cap else 0
            
            # Categorize market cap
            if market_cap_inr_cr >= 100000:  # > 1 lakh crore
                market_cap_category = "Large Cap"
            elif market_cap_inr_cr >= 20000:  # > 20k crore
                market_cap_category = "Mid Cap"
            else:
                market_cap_category = "Small Cap"
            
            stock_details.append({
                'symbol': symbol,
                'name': info.get('shortName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'market_cap_inr_cr': round(market_cap_inr_cr, 0),
                'market_cap_category': market_cap_category,
                'current_price': info.get('currentPrice', 0),
                'day_change': info.get('regularMarketPrice', 0) - info.get('regularMarketPreviousClose', 0)
            })
        except Exception as e:
            print(f"Error getting details for {symbol}: {e}")
            stock_details.append({
                'symbol': symbol,
                'name': symbol,
                'sector': 'Unknown',
                'market_cap_inr_cr': 0,
                'market_cap_category': 'Unknown',
                'current_price': 0,
                'day_change': 0
            })
    
    response_data = {
        'stocks': top_20_stocks,
        'stock_details': stock_details,
        'last_updated': last_data_update.strftime('%Y-%m-%d %H:%M:%S') if last_data_update else None,
        'is_fresh': is_data_fresh(),
        'next_update_in_minutes': max(0, data_update_interval - int((datetime.now() - last_data_update).total_seconds())) // 60 if last_data_update else 0
    }
    return jsonify(response_data)

@app.route('/')
def index():
    return render_template('index.html')

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
            'stocks_count': len(top_20_stocks)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to refresh data: {str(e)}'
        }), 500

@app.route('/get_all_signals')
def get_all_signals():
    """Get buy/sell/hold signals for all top stocks using UNIFIED function."""
    try:
        print("🔄 Starting UNIFIED bulk signal analysis...")
        signals = []
        
        for symbol in top_20_stocks:
            # Use the UNIFIED signal function for 100% consistency
            signal_data = calculate_unified_signal(symbol, period="2y", interval="1d")
            
            if signal_data['success']:
                signals.append(signal_data)
            else:
                print(f"⚠️ Failed to get signal for {symbol}, using fallback")
                signals.append(signal_data)
        
        print(f"✅ UNIFIED bulk analysis complete: {len(signals)} signals")
        
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
    try:
        print(f"🔍 Analyzing stock: {ticker} with risk: {risk_appetite}")
        
        # Get query parameters for chart filtering
        period = request.args.get('period', '2y')
        frequency = request.args.get('frequency', 'daily')
        
        # Get custom risk parameters if provided
        custom_stop_loss = request.args.get('customStopLoss', type=float)
        custom_exit_target = request.args.get('customExitTarget', type=float)
        
        # Add .NS suffix if not present for Indian stocks
        if not ticker.endswith('.NS'):
            ticker = ticker + '.NS'
        
        print(f"📈 Fetching data for: {ticker}")
        stock = yf.Ticker(ticker)
        
        # Map frequency to yfinance interval
        interval_map = {
            'daily': '1d',
            'weekly': '1wk', 
            'monthly': '1mo'
        }
        interval = interval_map.get(frequency, '1d')
        
        # Use appropriate period and interval
        hist = stock.history(period=period, interval=interval)
        print(f"📊 Got {len(hist)} rows of data")

        if hist.empty:
            print("❌ No data received from yfinance")
            return create_fallback_response()

        # Calculate all indicators first (same as bulk analysis)
        hist['SMA50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA200'] = hist['Close'].rolling(window=200).mean()
        
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
    get_nifty_200_list()
    
    # Start the background thread for periodic data refresh
    refresh_thread = threading.Thread(target=periodic_data_refresh, daemon=True)
    refresh_thread.start()
    print("Background data refresh thread started (refresh interval: 1 hour)")
    
    print("Starting Flask server...")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
