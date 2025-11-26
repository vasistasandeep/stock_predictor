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
            
            if hist is not None and not hist.empty:
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
            
            if hist is not None and not hist.empty:
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
