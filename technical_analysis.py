import pandas as pd
import numpy as np
import yfinance as yf
import math
from datetime import datetime, timedelta

def calculate_normal_cdf(x, mu, sigma):
    """Calculate Cumulative Distribution Function (CDF) for Normal Distribution"""
    return 0.5 * (1 + math.erf((x - mu) / (sigma * math.sqrt(2))))

def fetch_historical_data(ticker, period="1y"):
    """Fetch historical data for technical analysis"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if hist.empty:
            return None
        return hist
    except Exception as e:
        print(f"Error fetching history for {ticker}: {e}")
        return None

def calculate_rsi(data, period=14):
    """Calculate Relative Strength Index (RSI)"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, fast=12, slow=26, signal=9):
    """Calculate MACD, Signal line, and Histogram"""
    exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def calculate_smas(data):
    """Calculate Simple Moving Averages (20, 50, 200)"""
    sma20 = data['Close'].rolling(window=20).mean()
    sma50 = data['Close'].rolling(window=50).mean()
    sma200 = data['Close'].rolling(window=200).mean()
    return sma20, sma50, sma200

def calculate_atr(data, period=14):
    """Calculate Average True Range (ATR)"""
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr

def calculate_enhanced_metrics(data, current_price, risk_profile='Medium'):
    """
    Calculate Enhanced Logic metrics (formerly KL) based on probability distribution
    """
    try:
        # Calculate daily returns
        data['Daily_Return'] = data['Close'].pct_change()
        
        # Calculate mu (average daily return) and sigma (volatility)
        # Using last 30 days as per requirement
        recent_data = data.tail(30)
        mu = recent_data['Daily_Return'].mean()
        sigma = recent_data['Daily_Return'].std()
        
        if pd.isna(mu) or pd.isna(sigma) or sigma == 0:
            return None
            
        # Define targets to evaluate
        targets = [0.02, 0.03, 0.04, 0.05] # 2%, 3%, 4%, 5%
        
        # Define allowed loss based on risk profile
        # Low: 1%, Medium: 2%, High: 3% (Adjusted from spreadsheet's fixed 1%)
        allowed_loss_map = {'Low': 0.01, 'Medium': 0.02, 'High': 0.03, 'Custom': 0.02}
        allowed_loss = allowed_loss_map.get(risk_profile, 0.02)
        
        best_target = 0.03
        max_expected_return = -float('inf')
        
        for target in targets:
            # P(Target) = 1 - CDF(target) => Probability of reaching target
            p_target = 1 - calculate_normal_cdf(target, mu, sigma)
            
            # P(Loss) = CDF(-allowed_loss) => Probability of falling below loss limit
            p_loss = calculate_normal_cdf(-allowed_loss, mu, sigma)
            
            # Expected Return formula
            expected_return = (p_target * target) - (p_loss * allowed_loss)
            
            if expected_return > max_expected_return:
                max_expected_return = expected_return
                best_target = target
                
        # Recommendation
        recommendation = "BUY" if max_expected_return > 0 else "HOLD"
        
        # Suggested Entry: current * (1 - entryZ * sigma)
        entry_z = 0.5
        suggested_entry = current_price * (1 - (entry_z * sigma))
        
        # Stop Loss: 1% below suggested entry (or allowed_loss below?)
        stop_loss = suggested_entry * (1 - allowed_loss)
        
        # Exit Price: Entry * (1 + best_target)
        exit_price = suggested_entry * (1 + best_target)
        
        return {
            'mu': mu,
            'sigma': sigma,
            'best_target_pct': best_target,
            'expected_return': max_expected_return,
            'recommendation': recommendation,
            'suggested_entry': suggested_entry,
            'stop_loss': stop_loss,
            'exit_price': exit_price,
            'risk_profile': risk_profile
        }
        
    except Exception as e:
        print(f"Error calculating Enhanced metrics: {e}")
        return None

def analyze_stock(ticker, current_data=None, risk_profile='Medium'):
    """
    Perform comprehensive technical analysis on a stock.
    Returns a dictionary with indicators and signals.
    """
    try:
        # Fetch historical data
        hist = fetch_historical_data(ticker)
        if hist is None or len(hist) < 50: # Need at least 50 days for SMA50
            return None
            
        # Calculate indicators
        rsi_series = calculate_rsi(hist)
        macd, macd_signal, macd_hist = calculate_macd(hist)
        sma20, sma50, sma200 = calculate_smas(hist)
        atr_series = calculate_atr(hist)
        
        # Get latest values
        current_price = hist['Close'].iloc[-1]
        rsi = rsi_series.iloc[-1]
        macd_val = macd.iloc[-1]
        macd_sig = macd_signal.iloc[-1]
        macd_h = macd_hist.iloc[-1]
        ma20 = sma20.iloc[-1]
        ma50 = sma50.iloc[-1]
        ma200 = sma200.iloc[-1] if len(hist) >= 200 else None
        atr = atr_series.iloc[-1]
        
        # Volume analysis
        current_volume = hist['Volume'].iloc[-1]
        avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Support/Resistance (Simple 20-day high/low)
        recent_high = hist['High'].tail(20).max()
        recent_low = hist['Low'].tail(20).min()
        
        # --- Signal Generation Logic (Enhanced) ---
        signal_score = 0
        factors = []
        
        # 1. RSI Analysis (40% weight)
        if rsi < 30:
            signal_score += 40
            factors.append(f"RSI ({rsi:.1f}) oversold")
        elif rsi > 70:
            signal_score -= 40
            factors.append(f"RSI ({rsi:.1f}) overbought")
        else:
            factors.append(f"RSI ({rsi:.1f}) neutral")
            
        # 2. Moving Average Analysis (25% weight)
        if ma20 > ma50:
            signal_score += 25
            factors.append("Price above MAs (bullish trend)")
        elif ma20 < ma50:
            signal_score -= 25
            factors.append("Price below MAs (bearish trend)")
            
        # 3. MACD Analysis (20% weight)
        if macd_val > macd_sig:
            signal_score += 20
            factors.append("MACD bullish crossover")
        else:
            signal_score -= 20
            factors.append("MACD bearish crossover")
            
        # 4. Volume Analysis (10% weight)
        if volume_ratio > 1.5:
            if signal_score > 0:
                signal_score += 10
                factors.append(f"High volume ({volume_ratio:.1f}x) confirms buy")
            else:
                signal_score -= 10
                factors.append(f"High volume ({volume_ratio:.1f}x) confirms sell")
                
        # 5. ATR/Volatility (5% weight)
        if atr > 0 and (atr / current_price) < 0.02: # Low volatility
            signal_score += 5
            factors.append("Low volatility (stable)")
            
        # Determine Final Signal
        if signal_score >= 60:
            signal = "STRONG_BUY"
        elif signal_score >= 20:
            signal = "BUY"
        elif signal_score <= -60:
            signal = "STRONG_SELL"
        elif signal_score <= -20:
            signal = "SELL"
        else:
            signal = "HOLD"
            
        # Calculate Confidence
        confidence = min(95, 50 + abs(signal_score) / 2)
        
        # --- Enhanced Logic Integration ---
        enhanced_metrics = calculate_enhanced_metrics(hist, current_price, risk_profile)
        
        # Merge Enhanced logic if available
        enhanced_recommendation = "HOLD"
        enhanced_entry = current_price
        enhanced_stop = current_price * 0.95
        enhanced_exit = current_price * 1.05
        
        if enhanced_metrics:
            enhanced_recommendation = enhanced_metrics['recommendation']
            enhanced_entry = enhanced_metrics['suggested_entry']
            enhanced_stop = enhanced_metrics['stop_loss']
            enhanced_exit = enhanced_metrics['exit_price']
            
        return {
            'symbol': ticker,
            'current_price': round(current_price, 2),
            'price_change': 0, # Placeholder, updated by app.py
            'price_change_percent': 0, # Placeholder
            'rsi': round(rsi, 2),
            'macd': round(macd_val, 2),
            'macd_signal': round(macd_sig, 2),
            'sma_20': round(ma20, 2),
            'sma_50': round(ma50, 2),
            'atr': round(atr, 2),
            'volatility': round(atr/current_price, 4),
            'volume_ratio': round(volume_ratio, 2),
            'signal': signal,
            'signal_score': signal_score,
            'signal_factors': factors,
            'confidence': round(confidence, 1),
            # Enhanced Metrics
            'enhanced_recommendation': enhanced_recommendation,
            'enhanced_entry': round(enhanced_entry, 2),
            'enhanced_stop': round(enhanced_stop, 2),
            'enhanced_exit': round(enhanced_exit, 2),
            'historical_data': {
                'dates': hist.index.strftime('%Y-%m-%d').tolist(),
                'prices': hist['Close'].tolist(),
                'volumes': hist['Volume'].tolist()
            }
        }
        
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return None
