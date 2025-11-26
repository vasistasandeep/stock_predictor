from flask import Flask, jsonify, render_template, request
import yfinance as yf
import pandas as pd
import numpy as np
import talib
import requests
from datetime import datetime, timedelta
import time
import threading

app = Flask(__name__)

top_20_stocks = []
last_data_update = None
data_update_interval = 3600  # Refresh data every hour (3600 seconds)

def get_nifty_200_list():
    """Fetches real-time NIFTY 200 list from NSE and stores the top 20 stocks."""
    global top_20_stocks, last_data_update
    try:
        # Method 1: Try NSE API first
        nse_url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20200"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        try:
            response = requests.get(nse_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    # Sort by market cap and get top 20
                    sorted_stocks = sorted(data['data'], key=lambda x: x.get('marketCap', 0), reverse=True)
                    top_20 = sorted_stocks[:20]
                    # Extract symbols and add .NS suffix for Yahoo Finance
                    top_20_stocks = [f"{stock['symbol']}.NS" for stock in top_20]
                    last_data_update = datetime.now()
                    print(f"Successfully fetched {len(top_20_stocks)} stocks from NSE API at {last_data_update.strftime('%Y-%m-%d %H:%M:%S')}")
                    return
        except Exception as nse_error:
            print(f"NSE API failed: {nse_error}")
        
        # Method 2: Fallback to NSE website scraping
        try:
            nse_csv_url = "https://www.nseindia.com/content/indices/ind_nifty200list.csv"
            response = requests.get(nse_csv_url, headers=headers, timeout=10)
            if response.status_code == 200:
                from io import StringIO
                df = pd.read_csv(StringIO(response.text))
                # Get first 20 symbols
                top_20 = df.head(20)
                top_20_stocks = [f"{symbol}.NS" for symbol in top_20['Symbol'].tolist()]
                last_data_update = datetime.now()
                print(f"Successfully fetched {len(top_20_stocks)} stocks from NSE CSV at {last_data_update.strftime('%Y-%m-%d %H:%M:%S')}")
                return
        except Exception as csv_error:
            print(f"NSE CSV failed: {csv_error}")
        
        # Method 3: Fallback to a reliable third-party source
        try:
            # Using Moneycontrol API for NIFTY 200
            moneycontrol_url = "https://www.moneycontrol.com/india/stockmarket/indices/nifty-200-200.html"
            response = requests.get(moneycontrol_url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Parse HTML to extract stock symbols (basic implementation)
                import re
                pattern = r'/stockpricequote/(.*?)/'
                symbols = list(set(re.findall(pattern, response.text)))
                # Clean and get first 20
                symbols = [s.strip() for s in symbols if s.strip() and len(s) > 1]
                top_20_stocks = [f"{symbol.upper()}.NS" for symbol in symbols[:20]]
                last_data_update = datetime.now()
                print(f"Successfully fetched {len(top_20_stocks)} stocks from Moneycontrol at {last_data_update.strftime('%Y-%m-%d %H:%M:%S')}")
                return
        except Exception as mc_error:
            print(f"Moneycontrol failed: {mc_error}")
        
        # Method 4: Final fallback to static list of major NIFTY 200 stocks
        print("Using fallback static list of major NIFTY 200 stocks")
        fallback_stocks = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS',
            'INFY.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS',
            'AXISBANK.NS', 'DMART.NS', 'MARUTI.NS', 'ASIANPAINT.NS', 'HCLTECH.NS',
            'ULTRACEMCO.NS', 'BAJFINANCE.NS', 'WIPRO.NS', 'NESTLEIND.NS', 'DRREDDY.NS'
        ]
        top_20_stocks = fallback_stocks
        last_data_update = datetime.now()
        
    except Exception as e:
        print(f"Error fetching NIFTY 200 list: {e}")
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
    """Return top 20 stocks with timestamp information."""
    response_data = {
        'stocks': top_20_stocks,
        'last_updated': last_data_update.strftime('%Y-%m-%d %H:%M:%S') if last_data_update else None,
        'is_fresh': is_data_fresh(),
        'next_update_in_minutes': max(0, data_update_interval - int((datetime.now() - last_data_update).total_seconds())) // 60 if last_data_update else 0
    }
    return jsonify(response_data)

@app.route('/')
def index():
    return render_template('index.html')

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
            'message': str(e)
        }), 500

@app.route('/get_stock_data/<string:ticker>/<string:risk_appetite>')
def get_stock_data(ticker, risk_appetite):
    # Get query parameters for chart filtering
    period = request.args.get('period', '2y')
    frequency = request.args.get('frequency', 'daily')
    
    # Get custom risk parameters if provided
    custom_stop_loss = request.args.get('customStopLoss', type=float)
    custom_exit_target = request.args.get('customExitTarget', type=float)
    
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

    # Calculate all indicators first
    hist['SMA50'] = hist['Close'].rolling(window=50).mean()
    hist['SMA200'] = hist['Close'].rolling(window=200).mean()
    hist['RSI'] = talib.RSI(hist['Close'], timeperiod=14)
    hist['ATR'] = talib.ATR(hist['High'], hist['Low'], hist['Close'], timeperiod=14)
    
    # Remove rows with NaN values (only after all calculations)
    hist.dropna(inplace=True)

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

    # Get the last signal and attributes
    if not hist.empty:
        last_signal = hist['Signal'].iloc[-1]  # Use Signal instead of Position for current state
        if last_signal == 1:
            signal_text = 'Buy'
        elif last_signal == -1:
            signal_text = 'Sell'
        else:
            signal_text = 'Hold'

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
    else:
        signal_text = 'Not Available'
        entry_price = 'Not Available'
        exit_price = 'Not Available'
        stop_loss = 'Not Available'
        attributes = {
            'SMA50': 'Not Available',
            'SMA200': 'Not Available',
            'RSI': 'Not Available',
            'ATR': 'Not Available'
        }
        data = pd.DataFrame().to_json()

    response = {
        'signal': signal_text,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'stop_loss': stop_loss,
        'attributes': attributes,
        'data': data
    }

    return jsonify(response)

if __name__ == '__main__':
    # Fetch the list on startup
    print("Initializing Stock Predictor Application...")
    get_nifty_200_list()
    
    # Start the background thread for periodic data refresh
    refresh_thread = threading.Thread(target=periodic_data_refresh, daemon=True)
    refresh_thread.start()
    print("Background data refresh thread started (refresh interval: 1 hour)")
    
    print("Starting Flask development server...")
    app.run(debug=True)
