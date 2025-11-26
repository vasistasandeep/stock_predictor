import re
import random
from technical_analysis import analyze_stock

# Common trading terms and definitions
TRADING_TERMS = {
    "rsi": "RSI (Relative Strength Index) measures the speed and change of price movements. RSI > 70 is considered overbought (sell signal), and RSI < 30 is oversold (buy signal).",
    "macd": "MACD (Moving Average Convergence Divergence) is a trend-following momentum indicator that shows the relationship between two moving averages of a security's price.",
    "stop loss": "A stop-loss order is an order placed with a broker to buy or sell a specific stock once the stock reaches a certain price. It is designed to limit an investor's loss on a position in a security.",
    "support": "Support is a price level where a stock has difficulty falling below. It suggests that buyers are entering the market.",
    "resistance": "Resistance is a price level where a stock has difficulty rising above. It suggests that sellers are entering the market.",
    "bullish": "Bullish means expecting the price of a stock or the market to rise.",
    "bearish": "Bearish means expecting the price of a stock or the market to fall.",
    "volatility": "Volatility is a statistical measure of the dispersion of returns for a given security or market index. High volatility means the price can change dramatically over a short time period.",
    "dividend": "A dividend is the distribution of some of a company's earnings to a class of its shareholders, as determined by the company's board of directors.",
    "pe ratio": "The P/E ratio (Price-to-Earnings ratio) measures a company's current share price relative to its per-share earnings. It helps determine if a stock is overvalued or undervalued."
}

# Common NIFTY 50/200 stocks mapping (Name -> Symbol)
STOCK_MAPPING = {
    "reliance": "RELIANCE.NS",
    "tcs": "TCS.NS",
    "hdfc": "HDFCBANK.NS",
    "hdfc bank": "HDFCBANK.NS",
    "infosys": "INFY.NS",
    "infy": "INFY.NS",
    "icici": "ICICIBANK.NS",
    "icici bank": "ICICIBANK.NS",
    "sbi": "SBIN.NS",
    "sbin": "SBIN.NS",
    "state bank": "SBIN.NS",
    "bharti": "BHARTIARTL.NS",
    "airtel": "BHARTIARTL.NS",
    "itc": "ITC.NS",
    "kotak": "KOTAKBANK.NS",
    "l&t": "LT.NS",
    "larsent": "LT.NS",
    "axis": "AXISBANK.NS",
    "hul": "HINDUNILVR.NS",
    "maruti": "MARUTI.NS",
    "tata motors": "TATAMOTORS.NS",
    "sun pharma": "SUNPHARMA.NS",
    "wipro": "WIPRO.NS",
    "hcl": "HCLTECH.NS",
    "asian paints": "ASIANPAINT.NS",
    "bajaj finance": "BAJFINANCE.NS",
    "bajaj finserv": "BAJAJFINSV.NS",
    "titan": "TITAN.NS",
    "ultra tech": "ULTRACEMCO.NS",
    "ntpc": "NTPC.NS",
    "power grid": "POWERGRID.NS",
    "nestle": "NESTLEIND.NS",
    "tech mahindra": "TECHM.NS",
    "mahindra": "M&M.NS",
    "m&m": "M&M.NS",
    "coal india": "COALINDIA.NS",
    "adani ent": "ADANIENT.NS",
    "adani ports": "ADANIPORTS.NS",
    "jsw steel": "JSWSTEEL.NS",
    "tata steel": "TATASTEEL.NS",
    "hindalco": "HINDALCO.NS",
    "grasim": "GRASIM.NS",
    "cipla": "CIPLA.NS",
    "dr reddy": "DRREDDY.NS",
    "eicher": "EICHERMOT.NS",
    "hero": "HEROMOTOCO.NS",
    "divis": "DIVISLAB.NS",
    "apollo": "APOLLOHOSP.NS",
    "britannia": "BRITANNIA.NS",
    "bpcl": "BPCL.NS",
    "onngc": "ONGC.NS"
}

def extract_stock_symbol(message):
    """Try to identify a stock symbol from the message."""
    message_lower = message.lower()
    
    # Check mapping first
    for name, symbol in STOCK_MAPPING.items():
        if name in message_lower:
            return symbol
            
    # Check for explicit symbols (uppercase words, 3-5 chars)
    # This is a simple heuristic
    words = message.split()
    for word in words:
        clean_word = re.sub(r'[^a-zA-Z]', '', word)
        if clean_word.upper() == clean_word and 3 <= len(clean_word) <= 10:
            # Assume it might be a symbol, append .NS if not present
            if not clean_word.endswith('.NS'):
                return f"{clean_word}.NS"
            return clean_word
            
    return None

def process_chatbot_query(message):
    """Process the user message and return a response."""
    message = message.lower().strip()
    response_data = {"response": "", "data": None}
    
    # 1. Check for greetings
    if message in ['hi', 'hello', 'hey', 'start', 'help']:
        response_data["response"] = "Hello! I'm your AI Trading Assistant. You can ask me about stock prices, get buy/sell recommendations, or learn about trading terms. For example, try asking 'Analyze Reliance' or 'What is RSI?'"
        return response_data

    # 2. Check for definitions
    for term, definition in TRADING_TERMS.items():
        if term in message:
            response_data["response"] = f"💡 **{term.upper()}**: {definition}"
            return response_data

    # 3. Check for stock analysis/price queries
    symbol = extract_stock_symbol(message)
    
    if symbol:
        try:
            # Determine intent
            intent = "analysis"
            if "price" in message:
                intent = "price"
            elif "stop loss" in message:
                intent = "stop_loss"
            elif "buy" in message or "sell" in message:
                intent = "signal"
                
            # Fetch real data
            # Use 'medium' risk as default for general queries
            analysis = analyze_stock(symbol, risk_profile='medium')
            
            if not analysis:
                response_data["response"] = f"I couldn't fetch data for {symbol}. Please check the symbol and try again."
                return response_data
                
            # Format response based on intent
            if intent == "price":
                response_data["response"] = f"The current price of **{analysis['symbol']}** is **₹{analysis['current_price']}**."
                response_data["data"] = {"stock_recommendations": [{
                    "symbol": analysis['symbol'],
                    "name": analysis['symbol'], # We might not have full name here easily without extra call
                    "price": analysis['current_price'],
                    "change": 0, # We'd need historical data for change, placeholder
                    "risk": "Medium",
                    "signal": analysis['recommendation']
                }]}
                
            elif intent == "stop_loss":
                response_data["response"] = f"For **{analysis['symbol']}**, the recommended stop-loss is **₹{analysis['stop_loss']}**. This is based on a medium risk profile."
                
            else: # Full analysis/signal
                signal_emoji = "🟢" if analysis['recommendation'] == "BUY" else "🔴" if analysis['recommendation'] == "SELL" else "🟡"
                
                response_data["response"] = (
                    f"{signal_emoji} **Analysis for {analysis['symbol']}**:\n\n"
                    f"**Signal:** {analysis['recommendation']}\n"
                    f"**Entry:** ₹{analysis['entry_price']}\n"
                    f"**Target:** ₹{analysis['exit_price']}\n"
                    f"**Stop-Loss:** ₹{analysis['stop_loss']}\n\n"
                    f"_{analysis['reason']}_"
                )
                
                # Add rich data for UI
                response_data["data"] = {
                    "analysis": {
                        "symbol": analysis['symbol'],
                        "current_price": analysis['current_price'],
                        "stop_loss": analysis['stop_loss'],
                        "exit_target": analysis['exit_price'],
                        "risk_reward_ratio": "1:2" # Approximate
                    }
                }
                
            return response_data
            
        except Exception as e:
            print(f"Error analyzing stock {symbol}: {e}")
            response_data["response"] = f"I encountered an error analyzing {symbol}. It might be delisted or the data source is unavailable."
            return response_data

    # 4. Fallback
    response_data["response"] = "I'm not sure I understand. Try asking about a specific stock (e.g., 'Analyze TCS') or a trading term (e.g., 'What is MACD')."
    return response_data
