# Stock Predictor Application

A web-based stock analysis and prediction tool that provides actionable insights for Indian stocks. The application fetches real-time stock data, performs technical analysis, and generates buy/sell/hold signals based on various technical indicators.

![Stock Predictor Screenshot](https://via.placeholder.com/800x500.png?text=Stock+Predictor+Screenshot)

## Features

- **Top 20 NIFTY Stocks**: View and analyze the top 20 stocks from NIFTY 200 index
- **Technical Analysis**: Utilizes multiple technical indicators including:
  - 50-day and 200-day Simple Moving Averages (SMA)
  - Relative Strength Index (RSI)
  - Average True Range (ATR)
- **Risk-Based Recommendations**: Adjusts stop-loss levels based on user's risk appetite (Low/Medium/High)
- **Interactive Charts**: Visual representation of stock price movements and indicators
- **Actionable Signals**: Clear buy/sell/hold recommendations with entry, exit, and stop-loss levels

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- TA-Lib (Technical Analysis Library)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vasistasandeep/stock_predictor.git
   cd stock_predictor
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install TA-Lib**
   - Windows: Download the appropriate wheel file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)
     ```
     pip install TA_Lib‑0.4.24‑cp38‑cp38‑win_amd64.whl
     ```
   - macOS: `brew install ta-lib`
   - Linux: `sudo apt-get install ta-lib`

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the Flask development server**
   ```bash
   python app.py
   ```

2. **Open your web browser** and navigate to:
   ```
   http://127.0.0.1:5000
   ```

3. **Using the application**:
   - Select a stock from the "Top 20 Stocks" list or enter a stock symbol (e.g., RELIANCE.NS)
   - Choose your risk appetite (Low/Medium/High)
   - View the generated signal and technical analysis
   - Analyze the interactive price chart with moving averages

## Technical Indicators

- **50-day SMA**: Short-term trend indicator
- **200-day SMA**: Long-term trend indicator
- **RSI (14-day)**: Momentum oscillator measuring price movement speed and change
- **ATR (14-day)**: Volatility indicator showing market volatility

## Risk Appetite Settings

- **Low Risk**: Tighter stop-loss (2% below 14-day low)
- **Medium Risk**: Moderate stop-loss (5% below 14-day low)
- **High Risk**: Wider stop-loss (10% below 14-day low)

## Project Structure

```
stock_predictor/
├── app.py                # Main Flask application
├── requirements.txt      # Python dependencies
├── static/               # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css    # Custom styles
│   └── js/
│       └── script.js    # Frontend JavaScript
├── templates/
│   └── index.html       # Main HTML template
└── README.md            # This file
```

## API Endpoints

- `GET /`: Main application interface
- `GET /get_top_20_stocks`: Returns list of top 20 NIFTY stocks
- `GET /get_stock_data/<ticker>/<risk_appetite>`: Fetches stock data and analysis

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Yahoo Finance](https://finance.yahoo.com/) for stock data
- [TA-Lib](https://www.ta-lib.org/) for technical analysis functions
- [Chart.js](https://www.chartjs.org/) for interactive charts
- [Bootstrap](https://getbootstrap.com/) for responsive design

## Disclaimer

This application is for educational purposes only. The information provided should not be considered as financial advice. Always do your own research and consult with a certified financial advisor before making any investment decisions.

---

Developed by [Vasista Sandeep](https://github.com/vasistasandeep)
