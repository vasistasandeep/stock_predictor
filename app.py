from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
import numpy as np
import talib

app = Flask(__name__)

# URL for the Nifty 200 list
NIFTY_200_URL = 'https://raw.githubusercontent.com/Ratnesh-bhosale/NIFTY500_dataset/main/MCAP_31032020_TOP500.xlsx'

top_20_stocks = []

def get_nifty_200_list():
    """Fetches the Nifty 200 list and stores the top 20 stocks."""
    global top_20_stocks
    try:
        df = pd.read_excel(NIFTY_200_URL)
        # Assuming the column with ticker symbols is named 'Symbol'
        # Append '.NS' to ticker symbols for Yahoo Finance
        top_20_stocks = [f"{symbol}.NS" for symbol in df['Symbol'].head(20).tolist()]
    except Exception as e:
        print(f"Error fetching Nifty 200 list: {e}")

@app.route('/get_top_20_stocks')
def get_top_20_stocks():
    return jsonify(top_20_stocks)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_stock_data/<string:ticker>/<string:risk_appetite>')
def get_stock_data(ticker, risk_appetite):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="2y")

    # Calculate Simple Moving Averages
    hist['SMA50'] = hist['Close'].rolling(window=50).mean()
    hist['SMA200'] = hist['Close'].rolling(window=200).mean()
    hist.dropna(inplace=True) # Remove rows with no SMA values

    # Generate Signal
    hist['Signal'] = np.where(hist['SMA50'] > hist['SMA200'], 1, 0)
    hist['Position'] = hist['Signal'].diff()

    # Get the last signal and attributes
    if not hist.empty:
        last_signal = hist['Position'].iloc[-1]
        if last_signal == 1:
            signal_text = 'Buy'
        elif last_signal == -1:
            signal_text = 'Sell'
        else:
            signal_text = 'Hold'

        # Calculate RSI and ATR
        hist['RSI'] = talib.RSI(hist['Close'], timeperiod=14)
        hist['ATR'] = talib.ATR(hist['High'], hist['Low'], hist['Close'], timeperiod=14)
        hist.dropna(inplace=True)

        # Suggest Entry, Exit, and Stop-Loss
        recent_low = hist['Low'][-14:].min()
        recent_high = hist['High'][-14:].max()
        entry_price = f'{recent_low:.2f}'
        exit_price = f'{recent_high:.2f}'

        # Adjust stop-loss based on risk appetite
        if risk_appetite == 'Low':
            stop_loss = f'{(recent_low * 0.98):.2f}' # 2% below the 14-day low
        elif risk_appetite == 'Medium':
            stop_loss = f'{(recent_low * 0.95):.2f}' # 5% below the 14-day low
        else: # High
            stop_loss = f'{(recent_low * 0.90):.2f}' # 10% below the 14-day low

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
    get_nifty_200_list() # Fetch the list on startup
    app.run(debug=True)
