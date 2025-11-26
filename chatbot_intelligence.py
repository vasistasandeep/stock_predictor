"""
AI Trading Assistant Intelligence Module
Real-time market intelligence and stock analysis for chatbot
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

def get_stock_recommendations(user_message):
    """Get real-time stock recommendations based on market analysis"""
    
    try:
        # Get top NIFTY 200 stocks
        nifty_stocks = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
            'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS', 'ITC.NS', 'ASIANPAINT.NS',
            'DMART.NS', 'AXISBANK.NS', 'LT.NS', 'MARUTI.NS', 'SUNPHARMA.NS',
            'TITAN.NS', 'BAJFINANCE.NS', 'NESTLEIND.NS', 'ULTRACEMCO.NS', 'WIPRO.NS'
        ]
        
        recommendations = []
        
        for stock_symbol in nifty_stocks[:10]:  # Analyze top 10 for performance
            try:
                stock = yf.Ticker(stock_symbol)
                hist = stock.history(period="60d", interval="1d")
                info = stock.info
                
                if not hist.empty and len(hist) >= 20:
                    current_price = hist['Close'].iloc[-1]
                    
                    # Technical analysis
                    hist['MA20'] = hist['Close'].rolling(window=20).mean()
                    hist['MA50'] = hist['Close'].rolling(window=50).mean()
                    
                    # RSI calculation
                    delta = hist['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss.replace(0, 1)
                    rsi = 100 - (100 / (1 + rs))
                    current_rsi = rsi.iloc[-1]
                    
                    # Volume analysis
                    avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
                    current_volume = hist['Volume'].iloc[-1]
                    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                    
                    # Signal generation
                    signal_score = 0
                    if current_rsi < 30:
                        signal_score += 40
                    elif current_rsi > 70:
                        signal_score -= 40
                    elif 30 <= current_rsi <= 50:
                        signal_score += 10
                    
                    if current_price > hist['MA20'].iloc[-1] > hist['MA50'].iloc[-1]:
                        signal_score += 25
                    elif current_price < hist['MA20'].iloc[-1] < hist['MA50'].iloc[-1]:
                        signal_score -= 25
                    
                    if volume_ratio > 1.5:
                        signal_score += 10
                    
                    # Determine signal and risk
                    if signal_score >= 60:
                        signal = "STRONG BUY"
                        risk = "LOW"
                    elif signal_score >= 20:
                        signal = "BUY"
                        risk = "MEDIUM"
                    elif signal_score <= -60:
                        signal = "STRONG SELL"
                        risk = "HIGH"
                    elif signal_score <= -20:
                        signal = "SELL"
                        risk = "HIGH"
                    else:
                        signal = "HOLD"
                        risk = "MEDIUM"
                    
                    # Calculate daily change
                    daily_change = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                    
                    recommendations.append({
                        'symbol': stock_symbol.replace('.NS', ''),
                        'name': info.get('shortName', stock_symbol),
                        'price': round(current_price, 2),
                        'change': round(daily_change, 2),
                        'signal': signal,
                        'risk': risk,
                        'rsi': round(current_rsi, 2),
                        'volume_ratio': round(volume_ratio, 2)
                    })
                    
            except Exception as e:
                print(f"Error analyzing {stock_symbol}: {e}")
                continue
        
        # Sort by signal score
        recommendations.sort(key=lambda x: (
            1 if x['signal'] == 'STRONG BUY' else
            2 if x['signal'] == 'BUY' else
            3 if x['signal'] == 'HOLD' else
            4 if x['signal'] == 'SELL' else 5
        ))
        
        # Get top recommendations
        top_recommendations = recommendations[:5]
        
        response_text = "📈 **Today's Top Stock Recommendations:**\n\n"
        response_text += "Based on real-time technical analysis, here are the best opportunities:\n\n"
        
        for i, stock in enumerate(top_recommendations, 1):
            trend_emoji = "📈" if stock['change'] >= 0 else "📉"
            response_text += f"{i}. **{stock['symbol']}** - {stock['signal']}\n"
            response_text += f"   {trend_emoji} Price: ₹{stock['price']} ({stock['change']:+.2f}%)\n"
            response_text += f"   🎯 Risk Level: {stock['risk']}\n"
            response_text += f"   📊 RSI: {stock['rsi']} | Volume: {stock['volume_ratio']}x\n\n"
        
        response_text += "💡 **Investment Tip:** Consider your risk appetite and diversification. These stocks show strong technical patterns based on RSI, moving averages, and volume analysis."
        
        return response_text, {'stock_recommendations': top_recommendations}
        
    except Exception as e:
        print(f"Error in stock recommendations: {e}")
        return "I'm having trouble fetching real-time data. Please try again in a moment.", {}

def get_stop_loss_analysis(user_message):
    """Analyze stop-loss for specific stocks or general guidance"""
    
    # Extract stock symbol from message
    stock_symbol = extract_stock_symbol(user_message)
    
    if stock_symbol:
        try:
            stock = yf.Ticker(f"{stock_symbol}.NS")
            hist = stock.history(period="60d", interval="1d")
            
            if not hist.empty and len(hist) >= 20:
                current_price = hist['Close'].iloc[-1]
                
                # Calculate ATR
                high_low = hist['High'] - hist['Low']
                high_close = abs(hist['High'] - hist['Close'].shift())
                low_close = abs(hist['Low'] - hist['Close'].shift())
                true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                atr = true_range.rolling(window=14).mean().iloc[-1]
                
                # Recent low for support
                recent_low = hist['Low'][-20:].min()
                
                # Calculate stop-loss levels
                atr_stop_loss = recent_low - (2 * atr)
                percentage_stop_loss_2 = current_price * 0.98  # 2%
                percentage_stop_loss_5 = current_price * 0.95  # 5%
                percentage_stop_loss_10 = current_price * 0.90  # 10%
                
                # Exit targets (3:1 risk-reward)
                risk_amount_2 = current_price - percentage_stop_loss_2
                risk_amount_5 = current_price - percentage_stop_loss_5
                risk_amount_10 = current_price - percentage_stop_loss_10
                
                exit_target_2 = current_price + (3 * risk_amount_2)
                exit_target_5 = current_price + (3 * risk_amount_5)
                exit_target_10 = current_price + (3 * risk_amount_10)
                
                response_text = f"🛡️ **Stop-Loss Analysis for {stock_symbol}:**\n\n"
                response_text += f"💰 **Current Price:** ₹{current_price:.2f}\n"
                response_text += f"📊 **ATR (Volatility):** ₹{atr:.2f}\n"
                response_text += f"📍 **Recent Support:** ₹{recent_low:.2f}\n\n"
                
                response_text += "**Recommended Stop-Loss Levels:**\n"
                response_text += f"🟢 **Conservative (2%):** ₹{percentage_stop_loss_2:.2f}\n"
                response_text += f"🟡 **Moderate (5%):** ₹{percentage_stop_loss_5:.2f}\n"
                response_text += f"🔴 **Aggressive (10%):** ₹{percentage_stop_loss_10:.2f}\n\n"
                
                response_text += "**Exit Targets (3:1 Risk/Reward):**\n"
                response_text += f"🎯 Conservative Target: ₹{exit_target_2:.2f}\n"
                response_text += f"🎯 Moderate Target: ₹{exit_target_5:.2f}\n"
                response_text += f"🎯 Aggressive Target: ₹{exit_target_10:.2f}\n\n"
                
                response_text += "💡 **Recommendation:** Use ATR-based stop-loss (₹{:.2f}) for better risk management as it adapts to market volatility.".format(atr_stop_loss)
                
                analysis_data = {
                    'symbol': stock_symbol,
                    'current_price': round(current_price, 2),
                    'stop_loss': round(atr_stop_loss, 2),
                    'exit_target': round(exit_target_5, 2),
                    'risk_reward_ratio': '3:1'
                }
                
                return response_text, {'analysis': analysis_data}
                
        except Exception as e:
            print(f"Error analyzing stop-loss for {stock_symbol}: {e}")
    
    # General stop-loss guidance
    response_text = "🛡️ **Stop-Loss Trading Guide:**\n\n"
    response_text += "**What is Stop-Loss?**\n"
    response_text += "A stop-loss is an order to sell a stock when it reaches a certain price, limiting potential losses.\n\n"
    
    response_text += "**Types of Stop-Loss:**\n"
    response_text += "🟢 **Conservative (2-3%):** Best for beginners and capital preservation\n"
    response_text += "🟡 **Moderate (5-7%):** Balanced approach for regular traders\n"
    response_text += "🔴 **Aggressive (10-15%):** For experienced traders with higher risk tolerance\n\n"
    
    response_text += "**ATR-Based Stop-Loss:**\n"
    response_text += "• Uses Average True Range for dynamic positioning\n"
    response_text += "• Adapts to market volatility\n"
    response_text += "• Generally more reliable than fixed percentages\n\n"
    
    response_text += "💡 **Pro Tip:** Always use 3:1 risk-reward ratio. If your stop-loss is 5%, your target should be 15% gains."
    
    return response_text, {}

def get_market_sentiment_analysis():
    """Analyze overall market sentiment and conditions"""
    
    try:
        # Get NIFTY index data
        nifty = yf.Ticker("^NSEI")
        nifty_hist = nifty.history(period="30d", interval="1d")
        
        if not nifty_hist.empty:
            current_nifty = nifty_hist['Close'].iloc[-1]
            nifty_change = ((current_nifty - nifty_hist['Close'].iloc[-2]) / nifty_hist['Close'].iloc[-2]) * 100
            
            # Calculate market breadth
            nifty_stocks = [
                'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
                'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS', 'ITC.NS', 'ASIANPAINT.NS'
            ]
            
            gainers = 0
            losers = 0
            
            for stock in nifty_stocks:
                try:
                    stock_data = yf.Ticker(stock)
                    stock_hist = stock_data.history(period="2d", interval="1d")
                    if not stock_hist.empty:
                        change = ((stock_hist['Close'].iloc[-1] - stock_hist['Close'].iloc[-2]) / stock_hist['Close'].iloc[-2]) * 100
                        if change > 0:
                            gainers += 1
                        else:
                            losers += 1
                except:
                    continue
            
            # Market sentiment calculation
            total_stocks = gainers + losers
            advance_decline_ratio = (gainers / total_stocks * 100) if total_stocks > 0 else 50
            
            # Determine sentiment
            if nifty_change > 1 and advance_decline_ratio > 60:
                sentiment = "🟢 **BULLISH** - Strong Uptrend"
                sentiment_desc = "Market is in strong uptick with broad participation"
            elif nifty_change > 0.5 and advance_decline_ratio > 55:
                sentiment = "🟡 **MODERATELY BULLISH** - Positive Trend"
                sentiment_desc = "Market showing positive momentum"
            elif nifty_change < -1 and advance_decline_ratio < 40:
                sentiment = "🔴 **BEARISH** - Downtrend"
                sentiment_desc = "Market in decline with widespread selling"
            elif nifty_change < -0.5 and advance_decline_ratio < 45:
                sentiment = "🟡 **MODERATELY BEARISH** - Negative Trend"
                sentiment_desc = "Market showing weakness"
            else:
                sentiment = "⚪ **NEUTRAL** - Consolidation"
                sentiment_desc = "Market is range-bound or consolidating"
            
            response_text = f"📊 **Market Sentiment Analysis:**\n\n"
            response_text += f"**Overall Sentiment:** {sentiment}\n"
            response_text += f"**Description:** {sentiment_desc}\n\n"
            
            response_text += f"**NIFTY Performance:**\n"
            response_text += f"• Current Level: {current_nifty:.2f}\n"
            response_text += f"• Daily Change: {nifty_change:+.2f}%\n\n"
            
            response_text += f"**Market Breadth:**\n"
            response_text += f"• Gainers: {gainers}/{total_stocks} ({advance_decline_ratio:.1f}%)\n"
            response_text += f"• Losers: {losers}/{total_stocks} ({100-advance_decline_ratio:.1f}%)\n\n"
            
            response_text += "**Trading Strategy:**\n"
            if "BULLISH" in sentiment:
                response_text += "📈 Consider buying on dips, focus on momentum stocks"
            elif "BEARISH" in sentiment:
                response_text += "📉 Be cautious, preserve capital, wait for clear signals"
            else:
                response_text += "⚖️ Wait for clear breakout, stock selection is key"
            
            return response_text, {'market_data': {
                'nifty_level': current_nifty,
                'nifty_change': nifty_change,
                'gainers': gainers,
                'losers': losers,
                'sentiment': sentiment
            }}
            
    except Exception as e:
        print(f"Error in market sentiment analysis: {e}")
    
    # Fallback response
    response_text = "📊 **Market Analysis:**\n\n"
    response_text += "I'm having trouble fetching real-time market data. Please check your internet connection and try again."
    
    return response_text, {}

def get_top_movers(user_message):
    """Get top gainers and losers"""
    
    try:
        # Get major stocks for analysis
        major_stocks = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
            'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS', 'ITC.NS', 'ASIANPAINT.NS',
            'DMART.NS', 'AXISBANK.NS', 'LT.NS', 'MARUTI.NS', 'SUNPHARMA.NS'
        ]
        
        movers = []
        
        for stock_symbol in major_stocks:
            try:
                stock = yf.Ticker(stock_symbol)
                hist = stock.history(period="2d", interval="1d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    previous_price = hist['Close'].iloc[-2]
                    change_pct = ((current_price - previous_price) / previous_price) * 100
                    
                    movers.append({
                        'symbol': stock_symbol.replace('.NS', ''),
                        'price': round(current_price, 2),
                        'change': round(change_pct, 2)
                    })
                    
            except Exception as e:
                continue
        
        # Sort by change percentage
        movers.sort(key=lambda x: x['change'], reverse=True)
        
        # Get top gainers and losers
        top_gainers = movers[:5]
        top_losers = movers[-5:]
        top_losers.reverse()  # Show biggest losers first
        
        if 'gainers' in user_message or 'top' in user_message:
            response_text = "📈 **Top Gainers Today:**\n\n"
            for i, stock in enumerate(top_gainers, 1):
                response_text += f"{i}. **{stock['symbol']}** - ₹{stock['price']} (+{stock['change']:.2f}%)\n"
            
            return response_text, {'stock_recommendations': top_gainers}
        
        elif 'losers' in user_message:
            response_text = "📉 **Top Losers Today:**\n\n"
            for i, stock in enumerate(top_losers, 1):
                response_text += f"{i}. **{stock['symbol']}** - ₹{stock['price']} ({stock['change']:.2f}%)\n"
            
            return response_text, {'stock_recommendations': top_losers}
        
        else:
            response_text = "📊 **Market Movers:**\n\n"
            response_text += "**📈 Top Gainers:**\n"
            for i, stock in enumerate(top_gainers[:3], 1):
                response_text += f"{i}. {stock['symbol']}: +{stock['change']:.2f}%\n"
            
            response_text += "\n**📉 Top Losers:**\n"
            for i, stock in enumerate(top_losers[:3], 1):
                response_text += f"{i}. {stock['symbol']}: {stock['change']:.2f}%\n"
            
            return response_text, {'stock_recommendations': top_gainers + top_losers}
            
    except Exception as e:
        print(f"Error getting top movers: {e}")
        return "Unable to fetch market movers data. Please try again.", {}

def get_beginner_recommendations():
    """Get stock recommendations suitable for beginners"""
    
    beginner_stocks = [
        'HDFCBANK.NS', 'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HINDUNILVR.NS',
        'ITC.NS', 'SUNPHARMA.NS', 'NESTLEIND.NS', 'KOTAKBANK.NS', 'ASIANPAINT.NS'
    ]
    
    recommendations = []
    
    for stock_symbol in beginner_stocks:
        try:
            stock = yf.Ticker(stock_symbol)
            hist = stock.history(period="1y", interval="1d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                year_ago_price = hist['Close'].iloc[-252] if len(hist) >= 252 else hist['Close'].iloc[0]
                yearly_return = ((current_price - year_ago_price) / year_ago_price) * 100
                
                # Calculate volatility (standard deviation of daily returns)
                daily_returns = hist['Close'].pct_change().dropna()
                volatility = daily_returns.std() * np.sqrt(252) * 100  # Annualized volatility
                
                # Beginner-friendly criteria
                if volatility < 30 and yearly_return > 0:  # Low volatility and positive returns
                    recommendations.append({
                        'symbol': stock_symbol.replace('.NS', ''),
                        'price': round(current_price, 2),
                        'yearly_return': round(yearly_return, 2),
                        'volatility': round(volatility, 2),
                        'risk': 'LOW'
                    })
                    
        except Exception as e:
            continue
    
    # Sort by yearly return
    recommendations.sort(key=lambda x: x['yearly_return'], reverse=True)
    
    response_text = "🎓 **Beginner-Friendly Stock Recommendations:**\n\n"
    response_text += "These stocks are selected based on:\n"
    response_text += "✅ Low volatility (less than 30% annually)\n"
    response_text += "✅ Positive historical returns\n"
    response_text += "✅ Strong market position\n"
    response_text += "✅ Good liquidity\n\n"
    
    response_text += "**Top Picks for Beginners:**\n"
    for i, stock in enumerate(recommendations[:5], 1):
        response_text += f"{i}. **{stock['symbol']}** - ₹{stock['price']}\n"
        response_text += f"   📈 Yearly Return: {stock['yearly_return']:+.2f}%\n"
        response_text += f"   📊 Volatility: {stock['volatility']:.1f}% (Low)\n\n"
    
    response_text += "💡 **Beginner Tips:**\n"
    response_text += "• Start with small investments\n"
    response_text += "• Focus on large-cap, stable companies\n"
    response_text += "• Use systematic investment plans (SIP)\n"
    response_text += "• Never invest more than you can afford to lose"
    
    return response_text, {'stock_recommendations': recommendations[:5]}

def extract_stock_symbol(message):
    """Extract stock symbol from user message"""
    
    # Common stock symbols to look for
    stock_symbols = ['RELIANCE', 'TCS', 'HDFC', 'HDFCBANK', 'INFY', 'SBIN', 'ITC', 
                    'TITAN', 'KOTAK', 'KOTAKBANK', 'AXIS', 'AXISBANK', 'LT', 'MARUTI',
                    'SUNPHARMA', 'DMART', 'BHARTI', 'ASIANPAINT', 'NESTLE', 'ULTRACEMCO',
                    'WIPRO', 'HINDUNILVR', 'BAJFINANCE']
    
    message_upper = message.upper()
    
    for symbol in stock_symbols:
        if symbol in message_upper:
            return symbol
    
    return None

def get_stock_analysis(stock_symbol):
    """Get detailed analysis for a specific stock"""
    
    try:
        stock = yf.Ticker(f"{stock_symbol}.NS")
        hist = stock.history(period="60d", interval="1d")
        info = stock.info
        
        if not hist.empty and len(hist) >= 20:
            current_price = hist['Close'].iloc[-1]
            
            # Technical indicators
            hist['MA20'] = hist['Close'].rolling(window=20).mean()
            hist['MA50'] = hist['Close'].rolling(window=50).mean()
            
            # RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss.replace(0, 1)
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # ATR
            high_low = hist['High'] - hist['Low']
            high_close = abs(hist['High'] - hist['Close'].shift())
            low_close = abs(hist['Low'] - hist['Close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=14).mean().iloc[-1]
            
            # Recent performance
            daily_change = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
            weekly_change = ((current_price - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100 if len(hist) >= 5 else 0
            monthly_change = ((current_price - hist['Close'].iloc[-20]) / hist['Close'].iloc[-20]) * 100 if len(hist) >= 20 else 0
            
            response_text = f"📊 **{stock_symbol} Detailed Analysis:**\n\n"
            response_text += f"💰 **Current Price:** ₹{current_price:.2f}\n"
            response_text += f"📈 **Daily Change:** {daily_change:+.2f}%\n"
            response_text += f"📈 **Weekly Change:** {weekly_change:+.2f}%\n"
            response_text += f"📈 **Monthly Change:** {monthly_change:+.2f}%\n\n"
            
            response_text += f"**Technical Indicators:**\n"
            response_text += f"📊 RSI (14): {current_rsi:.2f}\n"
            response_text += f"📈 MA20: ₹{hist['MA20'].iloc[-1]:.2f}\n"
            response_text += f"📈 MA50: ₹{hist['MA50'].iloc[-1]:.2f}\n"
            response_text += f"📊 ATR: ₹{atr:.2f}\n\n"
            
            # Signal generation
            signal = "HOLD"
            if current_rsi < 30:
                signal = "BUY"
            elif current_rsi > 70:
                signal = "SELL"
            
            response_text += f"**Recommendation:** {signal}\n"
            
            if info.get('shortName'):
                response_text += f"\n**Company:** {info['shortName']}"
            if info.get('sector'):
                response_text += f"\n**Sector:** {info['sector']}"
            
            return response_text, {}
            
    except Exception as e:
        print(f"Error analyzing {stock_symbol}: {e}")
        return f"Sorry, I couldn't fetch data for {stock_symbol}. Please check the stock symbol and try again.", {}

def get_help_response(user_message):
    """Get help and tutorial responses"""
    
    if 'stop loss' in user_message:
        return get_stop_loss_analysis(user_message)
    
    elif 'risk' in user_message:
        response_text = "⚠️ **Understanding Investment Risk:**\n\n"
        response_text += "**Types of Risk:**\n"
        response_text += "🎯 **Market Risk:** Overall market movements\n"
        response_text += "🏢 **Company Risk:** Company-specific issues\n"
        response_text += "💱 **Currency Risk:** Exchange rate fluctuations\n"
        response_text += "📈 **Volatility Risk:** Price fluctuations\n\n"
        
        response_text += "**Risk Management:**\n"
        response_text += "• Diversify across sectors\n"
        response_text += "• Use stop-loss orders\n"
        response_text += "• Invest based on risk appetite\n"
        response_text += "• Regular portfolio review\n\n"
        
        response_text += "**Risk Levels:**\n"
        response_text += "🟢 **Low Risk:** 2-3% stop-loss, stable companies\n"
        response_text += "🟡 **Medium Risk:** 5-7% stop-loss, balanced portfolio\n"
        response_text += "🔴 **High Risk:** 10-15% stop-loss, growth stocks"
        
        return response_text, {}
    
    else:
        response_text = "🤖 **AI Trading Assistant Help:**\n\n"
        response_text += "**I can help you with:**\n"
        response_text += "📈 Stock recommendations and analysis\n"
        response_text += "🛡️ Stop-loss calculations and risk management\n"
        response_text += "📊 Market sentiment and trends\n"
        response_text += "🎯 Top gainers and losers\n"
        response_text += "🎓 Beginner-friendly stock picks\n"
        response_text += "💼 Portfolio and watchlist management\n\n"
        
        response_text += "**Example Questions:**\n"
        response_text += "• \"What are the best stocks to buy today?\"\n"
        response_text += "• \"What is the stop-loss for RELIANCE?\"\n"
        response_text += "• \"How is the market sentiment today?\"\n"
        response_text += "• \"Show me top gainers\"\n"
        response_text += "• \"Recommend stocks for beginners\"\n\n"
        
        response_text += "💡 **Tip:** Be specific with stock symbols and I'll provide detailed analysis!"
        
        return response_text, {}

def handle_portfolio_queries(user_message):
    """Handle portfolio and watchlist queries"""
    
    response_text = "📋 **Portfolio Management:**\n\n"
    response_text += "I can help you manage your portfolio, but I need to implement the watchlist feature first. For now, I can:\n\n"
    response_text += "✅ Analyze individual stocks\n"
    response_text += "✅ Provide stop-loss recommendations\n"
    response_text += "✅ Suggest portfolio diversification\n"
    response_text += "✅ Monitor market conditions\n\n"
    
    response_text += "**Coming Soon:**\n"
    response_text += "📊 Personal watchlist\n"
    response_text += "💼 Portfolio tracking\n"
    response_text += "📈 Performance analytics\n"
    response_text += "🔔 Price alerts\n\n"
    
    response_text += "For now, ask me about specific stocks you're interested in!"
    
    return response_text, {}

def get_default_response(user_message):
    """Default response when no specific intent is detected"""
    
    responses = [
        "I'm here to help with stock analysis and trading guidance. Try asking about specific stocks, market sentiment, or investment strategies!",
        "I can provide stock recommendations, stop-loss calculations, and market analysis. What would you like to know?",
        "Want to know about today's top gainers or need help with a specific stock? Just ask!",
        "I'm your AI trading assistant. Ask me about stocks, market trends, or investment strategies!",
        "Need stock recommendations or market analysis? I'm here to help!"
    ]
    
    import random
    return random.choice(responses)
