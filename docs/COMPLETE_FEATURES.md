# 🚀 Stock Predictor - Complete Feature Documentation

## 1. 🔐 Tiered Access System

### Free Access (No Login)
*   **Top 20 Nifty 200 Stocks**: Real-time ranking based on market cap.
*   **Trading Predictions**: Buy/Sell/Hold signals for top stocks.
*   **Basic Technical Indicators**: RSI, SMA, ATR values.
*   **Stock Search**: Search for any NIFTY stock.
*   **Educational Tooltips**: Learn trading terms on hover.

### Enhanced Access (Login Required)
*   **Quick Stock Analysis**: Detailed analysis for any specific stock.
*   **Market Insights**: News, Analyst Recommendations, and Sentiment.
*   **Analysis Summary**: AI-powered summary of the stock's potential.
*   **Investment Style Selection**: Choose between Conservative, Balanced, and Aggressive risk profiles.
*   **AI Trading Assistant**: Interactive chatbot for trading queries.
*   **Export Functionality**: Download analysis data as CSV.

---

## 2. 🤖 AI Trading Chatbot (New!)

### Intelligent Features
*   **Intent Detection**: Automatically understands if you want:
    *   **Price Check**: "Price of Reliance"
    *   **Full Analysis**: "Analyze TCS", "Should I buy INFY?"
    *   **Stop-Loss Advice**: "Stop loss for SBIN"
    *   **Definitions**: "What is RSI?", "Explain MACD"
*   **Real-Time Data Integration**: Fetches live market data to answer your queries.
*   **Smart Symbol Mapping**: Recognizes company names (e.g., "Maruti") and maps them to NSE symbols (`MARUTI.NS`).
*   **Rich UI**: Displays stock cards and analysis summaries directly in the chat.
*   **Voice Support**: Voice-to-text input for hands-free querying.

---

## 3. 🔍 Smart Filtering & Sorting

### Advanced Filters
*   **Signal Type**: Filter stocks by BUY, SELL, or HOLD signals.
*   **Sector**: Auto-populated filter based on the sectors of available stocks.
*   **Market Cap**: Filter by Large Cap (>₹20k Cr), Mid Cap (₹5k-20k Cr), and Small Cap (<₹5k Cr).
*   **Sort By**:
    *   **Name**: Alphabetical order.
    *   **Signal**: Buy -> Hold -> Sell.
    *   **Confidence**: Highest confidence first.
    *   **Entry/Exit/Stop-Loss**: Sort by price levels.

---

## 4. 📊 Technical Analysis Engine

### Indicators Used
*   **SMA (Simple Moving Average)**: 50-day and 200-day averages for trend detection.
*   **RSI (Relative Strength Index)**: Momentum indicator (Overbought > 70, Oversold < 30).
*   **ATR (Average True Range)**: Volatility measure for dynamic stop-loss calculation.
*   **MACD**: Trend-following momentum indicator.

### Signal Logic
*   **BUY**: Price > SMA200 AND RSI < 30 (Oversold) AND Golden Cross (SMA50 > SMA200).
*   **SELL**: Price < SMA200 AND RSI > 70 (Overbought) AND Death Cross (SMA50 < SMA200).
*   **HOLD**: Mixed signals or neutral RSI (30-70).

---

## 5. 🎨 UI/UX Enhancements

*   **Consistent Premium Badging**: Gold "Premium" badges on all locked features.
*   **Dynamic Login CTA**: Footer CTA that disappears when logged in.
*   **Responsive Design**: Fully optimized for mobile and desktop.
*   **Clean Layout**: Removed clutter (testimonials, duplicate filters) for a professional look.
*   **Interactive Charts**: Chart.js integration for visualizing price trends.

---

## 6. 🛠️ Technical Stack

*   **Backend**: Flask (Python)
*   **Data**: Yahoo Finance API (`yfinance`), NSE Data
*   **Frontend**: Bootstrap 5, Vanilla JS, Chart.js
*   **Analysis**: Pandas, NumPy, TA-Lib (optional/custom implementation)
*   **Deployment**: Ready for Vercel/Render

---

## 7. 🔮 Future Roadmap

*   **User Accounts**: Real database for user registration (currently demo admin/password).
*   **Portfolio Tracking**: Save analyzed stocks to a personal portfolio.
*   **Alerts**: Email/SMS alerts for price targets.
*   **More Indicators**: Bollinger Bands, Stochastic Oscillator.
