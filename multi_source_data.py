import os
# Configure cache for Vercel (read-only filesystem fix)
if os.environ.get('VERCEL'):
    os.environ['XDG_CACHE_HOME'] = '/tmp/.cache'

import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import json
import re

class MultiSourceDataFetcher:
    """Multi-source stock data fetcher with fallback capabilities"""
    
    def __init__(self):
        self.sources = {
            'yahoo': YahooFinanceSource(),
            'google': GoogleFinanceSource(),
            'alpha_vantage': AlphaVantageSource(),
            'fmp': FinancialModelingPrepSource()
        }
        self.default_source = 'yahoo'
        self.fallback_order = ['yahoo', 'google', 'alpha_vantage', 'fmp']
        
    def fetch_stock_data(self, symbol, source=None, timeout=10):
        """Fetch stock data from specified source with fallback"""
        if source and source in self.sources:
            # Try specific source first
            data = self.sources[source].fetch_stock_data(symbol, timeout)
            if data:
                return {'data': data, 'source': source}
        
        # Try all sources in fallback order
        for source_name in self.fallback_order:
            try:
                print(f"🔄 Trying {source_name} for {symbol}...")
                data = self.sources[source_name].fetch_stock_data(symbol, timeout)
                if data:
                    print(f"✅ Success with {source_name}")
                    return {'data': data, 'source': source_name}
            except Exception as e:
                print(f"❌ {source_name} failed: {e}")
                continue
        
        print(f"❌ All sources failed for {symbol}")
        return None
    
    def fetch_multiple_stocks(self, symbols, source=None, timeout=10):
        """Fetch data for multiple stocks with source preference"""
        results = []
        
        for symbol in symbols:
            try:
                result = self.fetch_stock_data(symbol, source, timeout)
                if result:
                    results.append({
                        'symbol': symbol,
                        **result['data'],
                        'data_source': result['source']
                    })
            except Exception as e:
                print(f"❌ Error fetching {symbol}: {e}")
                continue
        
        return results
    
    def get_available_sources(self):
        """Get list of available data sources with status"""
        status = {}
        for name, source in self.sources.items():
            try:
                # Quick test with a known stock
                test_data = source.fetch_stock_data('RELIANCE.NS', 5)
                status[name] = {
                    'available': test_data is not None,
                    'name': source.get_display_name(),
                    'description': source.get_description()
                }
            except Exception as e:
                status[name] = {
                    'available': False,
                    'name': source.get_display_name(),
                    'description': source.get_description(),
                    'error': str(e)
                }
        
        return status

class GoogleFinanceSource:
    """Google Finance data source"""
    
    def fetch_stock_data(self, symbol, timeout=10):
        """Fetch stock data from Google Finance"""
        try:
            # Convert symbol for Google Finance URL
            if symbol.endswith('.NS'):
                google_symbol = symbol.replace('.NS', 'NSE')
            elif symbol.endswith('.BO'):
                google_symbol = symbol.replace('.BO', 'BOM')
            else:
                google_symbol = symbol
            
            # Google Finance search URL
            search_url = f"https://www.google.com/finance/quote/{google_symbol}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=timeout)
            
            if response.status_code != 200:
                return None
            
            # Parse the HTML response
            content = response.text
            
            # Extract current price using regex
            price_pattern = r'data-last-price="([^"]+)"'
            price_match = re.search(price_pattern, content)
            
            if not price_match:
                return None
            
            current_price = float(price_match.group(1).replace(',', ''))
            
            # Extract price change
            change_pattern = r'data-change="([^"]+)"'
            change_match = re.search(change_pattern, content)
            price_change = float(change_match.group(1)) if change_match else 0.0
            
            # Extract company name
            name_pattern = r'<div class="gUhQFf".*?>([^<]+)</div>'
            name_match = re.search(name_pattern, content)
            name = name_match.group(1) if name_match else symbol
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'price_change': round(price_change, 2),
                'volume': 0,  # Not easily available from Google Finance HTML
                'market_cap': 0,  # Not easily available from Google Finance HTML
                'name': name,
                'sector': 'Unknown',
                'pe_ratio': None,
                'dividend_yield': None,
                'price_to_book': None,
                'currency': 'INR' if symbol.endswith('.NS') else 'USD'
            }
            
        except Exception as e:
            print(f"Google Finance error for {symbol}: {e}")
            return None
    
    def get_display_name(self):
        return "Google Finance"
    
    def get_description(self):
        return "Alternative free data source with real-time prices"

class YahooFinanceSource:
    """Yahoo Finance data source"""
    
    def fetch_stock_data(self, symbol, timeout=10):
        """Fetch stock data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get basic info with timeout
            info = ticker.info
            
            # Get historical data (shorter for faster loading)
            hist = ticker.history(period="5d", interval="1d")
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            price_change = (current_price - previous_close) / previous_close * 100
            
            return {
                'symbol': symbol,
                'current_price': round(current_price, 2),
                'price_change': round(price_change, 2),
                'volume': int(hist['Volume'].iloc[-1]),
                'market_cap': info.get('marketCap', 0),
                'name': info.get('shortName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'price_to_book': info.get('priceToBook'),
                'currency': info.get('currency', 'USD')
            }
            
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {e}")
            return None
    
    def get_display_name(self):
        return "Yahoo Finance"
    
    def get_description(self):
        return "Free, comprehensive market data with global coverage"

class AlphaVantageSource:
    """Alpha Vantage data source"""
    
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.base_url = "https://www.alphavantage.co/query"
    
    def fetch_stock_data(self, symbol, timeout=10):
        """Fetch stock data from Alpha Vantage"""
        try:
            # Convert Indian symbol to Alpha Vantage format
            if symbol.endswith('.NS'):
                av_symbol = symbol.replace('.NS', '.BSE')
            else:
                av_symbol = symbol
            
            # Global quote endpoint
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': av_symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=timeout)
            data = response.json()
            
            if 'Global Quote' not in data:
                return None
            
            quote = data['Global Quote']
            current_price = float(quote['05. price'])
            change = float(quote['09. change'])
            change_percent = float(quote['10. change percent'].replace('%', ''))
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'price_change': round(change_percent, 2),
                'volume': int(quote['06. volume']) if quote['06. volume'] else 0,
                'market_cap': 0,  # Not available in free tier
                'name': quote['01. symbol'],
                'sector': 'Unknown',
                'pe_ratio': None,
                'dividend_yield': None,
                'price_to_book': None,
                'currency': 'USD'
            }
            
        except Exception as e:
            print(f"Alpha Vantage error for {symbol}: {e}")
            return None
    
    def get_display_name(self):
        return "Alpha Vantage"
    
    def get_description(self):
        return "Professional financial data API (requires API key)"

class FinancialModelingPrepSource:
    """Financial Modeling Prep data source"""
    
    def __init__(self):
        self.api_key = os.getenv('FMP_API_KEY', 'demo')
        self.base_url = "https://financialmodelingprep.com/api/v3"
    
    def fetch_stock_data(self, symbol, timeout=10):
        """Fetch stock data from Financial Modeling Prep"""
        try:
            # Convert Indian symbol to FMP format
            if symbol.endswith('.NS'):
                fmp_symbol = symbol.replace('.NS', '')
            else:
                fmp_symbol = symbol
            
            # Quote endpoint
            url = f"{self.base_url}/quote/{fmp_symbol}"
            params = {'apikey': self.api_key}
            
            response = requests.get(url, params=params, timeout=timeout)
            data = response.json()
            
            if not data or len(data) == 0:
                return None
            
            quote = data[0]
            
            return {
                'symbol': symbol,
                'current_price': quote['price'],
                'price_change': round(quote['changesPercentage'], 2),
                'volume': quote['volume'],
                'market_cap': quote['marketCap'],
                'name': quote['name'],
                'sector': quote['sector'],
                'pe_ratio': quote.get('pe'),
                'dividend_yield': quote.get('dividendYield'),
                'price_to_book': quote.get('priceToBook'),
                'currency': 'USD'
            }
            
        except Exception as e:
            print(f"FMP error for {symbol}: {e}")
            return None
    
    def get_display_name(self):
        return "Financial Modeling Prep"
    
    def get_description(self):
        return "Institutional-grade financial data (requires API key)"

# Global instance
multi_source_fetcher = MultiSourceDataFetcher()

def get_stock_data_multi_source(symbol, source=None, timeout=10):
    """Convenience function for multi-source data fetching"""
    return multi_source_fetcher.fetch_stock_data(symbol, source, timeout)

def get_multiple_stocks_multi_source(symbols, source=None, timeout=10):
    """Convenience function for multiple stocks"""
    return multi_source_fetcher.fetch_multiple_stocks(symbols, source, timeout)

def get_data_source_status():
    """Get status of all data sources"""
    return multi_source_fetcher.get_available_sources()

def get_major_nifty_stocks():
    """Comprehensive list of major NIFTY stocks"""
    return [
        # TOP 30 NIFTY STOCKS (Updated for 2024-25)
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'BHARTIARTL.NS',
        'SBIN.NS', 'INFY.NS', 'LICI.NS', 'ITC.NS', 'HINDUNILVR.NS',
        'LT.NS', 'BAJFINANCE.NS', 'HCLTECH.NS', 'MARUTI.NS', 'SUNPHARMA.NS',
        'ADANIENT.NS', 'KOTAKBANK.NS', 'TITAN.NS', 'ONGC.NS', 'TATAMOTORS.NS',
        'NTPC.NS', 'AXISBANK.NS', 'ADANIPORTS.NS', 'ULTRACEMCO.NS', 'ASIANPAINT.NS',
        'COALINDIA.NS', 'POWERGRID.NS', 'BAJAJFINSV.NS', 'BAJAJ-AUTO.NS', 'M&M.NS',
        
        # Next 20 Major Stocks
        'WIPRO.NS', 'NESTLEIND.NS', 'JSWSTEEL.NS', 'TATASTEEL.NS', 'LTIM.NS',
        'GRASIM.NS', 'SBILIFE.NS', 'TECHM.NS', 'HDFCLIFE.NS', 'BRITANNIA.NS',
        'INDUSINDBK.NS', 'HINDALCO.NS', 'DIVISLAB.NS', 'EICHERMOT.NS', 'CIPLA.NS',
        'DRREDDY.NS', 'BPCL.NS', 'TATACONSUM.NS', 'APOLLOHOSP.NS', 'HEROMOTOCO.NS'
    ]

def get_nifty_200_list(source=None):
    """Get list of NIFTY 200 stocks with data, sorted by market cap"""
    stocks = get_major_nifty_stocks()
    
    # Fetch data for top 30 candidates to ensure we get the real top 20
    # This is a balance between speed and accuracy
    print(f"🔄 Fetching data for {len(stocks)} candidate stocks to find Top 20...")
    data = get_multiple_stocks_multi_source(stocks, source=source)
    
    if not data:
        print("❌ Failed to fetch stock data")
        return []
        
    # Sort by market cap (descending) to get the ACTUAL top stocks
    # Use 0 as default if market_cap is missing
    data.sort(key=lambda x: x.get('market_cap', 0) or 0, reverse=True)
    
    # Return top 20
    top_20 = data[:20]
    print(f"✅ Identified Top 20 stocks by Market Cap (Top: {top_20[0]['symbol']} - {top_20[0].get('market_cap', 'N/A')})")
    
    return top_20
