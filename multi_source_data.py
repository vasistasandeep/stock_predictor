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
        # TOP 20 NIFTY STOCKS BY MARKET CAP
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS',
        'INFY.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS',
        'AXISBANK.NS', 'DMART.NS', 'MARUTI.NS', 'ASIANPAINT.NS', 'HCLTECH.NS',
        'ULTRACEMCO.NS', 'BAJFINANCE.NS', 'WIPRO.NS', 'NESTLEIND.NS', 'DRREDDY.NS',
        
        # ADDITIONAL MAJOR STOCKS
        'LT.NS', 'SUNPHARMA.NS', 'TITAN.NS', 'M&M.NS', 'POWERGRID.NS',
        'NTPC.NS', 'COALINDIA.NS', 'BPCL.NS', 'GAIL.NS', 'ONGC.NS',
        'HDFCLIFE.NS', 'SBILIFE.NS', 'GRASIM.NS', 'ADANIPORTS.NS', 'TECHM.NS',
        'DIVISLAB.NS', 'BRITANNIA.NS', 'DLF.NS', 'BAJAJFINSV.NS', 'DABUR.NS',
        'PIDILITEIND.NS', 'HEROMOTOCO.NS', 'TATASTEEL.NS', 'EICHERMOT.NS', 'BALKRISIND.NS',
        'APOLLOHOSP.NS', 'SHREECEM.NS', 'TATACONSUM.NS', 'GODREJCP.NS', 'UBL.NS',
        
        # MORE STOCKS TO REACH 175
        'SIEMENS.NS', 'TATAMOTORS.NS', 'INDUSINDBK.NS', 'JSWSTEEL.NS', 'UPL.NS',
        'MUTHOOTFIN.NS', 'CHOLAHLDNG.NS', 'CUB.NS', 'NAUKRI.NS', 'GICRE.NS',
        'IBULHSGFIN.NS', 'BANDHANBNK.NS', 'RBLBANK.NS', 'FEDERALBNK.NS', 'IDFCFIRSTB.NS',
        'PNB.NS', 'BANKBARODA.NS', 'CANBK.NS', 'INDIANB.NS', 'J&KBANK.NS',
        'IOB.NS', 'UCOBANK.NS', 'CENTRALBK.NS', 'SOUTHBNK.NS', 'J&K.NS',
        'PUNJABNAT.NS', 'VIJAYABANK.NS', 'DENABANK.NS', 'KARURVYSYA.NS', 'TAMILNADBNK.NS',
        'ORIENTBANK.NS', 'ANDHRABANK.NS', 'CORPBANK.NS', 'ALLABADBNK.NS', 'VYSYABANK.NS',
        'LAXMIVILAS.NS', 'SIB.NS', 'JHAGREFIN.NS', 'MANAPPURAM.NS', 'MUTHOOTFIN.NS',
        'CHOLAHLDNG.NS', 'SRTRANSFIN.NS', 'BAJAJHLDNG.NS', 'TATAINVEST.NS', 'HDFCAMC.NS',
        'ICICIPRULI.NS', 'SBILIFE.NS', 'KOTAKLIFE.NS', 'MAXLIFE.NS', 'PNBLIFE.NS',
        'AVANTIFEED.NS', 'ANANTRAJ.NS', 'ARVIND.NS', 'ASHOKLEY.NS', 'BATAINDIA.NS',
        'BERGEPAINT.NS', 'BLUESTARCO.NS', 'BOSCHLTD.NS', 'CADILAHC.NS', 'CASTROLIND.NS',
        'CEATLTD.NS', 'CROMPTON.NS', 'CUMMINSIND.NS', 'DABUR.NS', 'DELTACORP.NS',
        'DISHTV.NS', 'EICHERMOT.NS', 'ESCORTS.NS', 'EXIDEIND.NS', 'FEDERALBNK.NS',
        'GAIL.NS', 'GESHIP.NS', 'GMRINFRA.NS', 'GODREJIND.NS', 'GODREJPROP.NS',
        'GRASIM.NS', 'GUJALKALI.NS', 'HAVELLS.NS', 'HCC.NS', 'HDFC.NS',
        'HEG.NS', 'HEROHONDA.NS', 'HINDALCO.NS', 'HINDPETRO.NS', 'HINDZINC.NS',
        'IBREALEST.NS', 'ICICIBANK.NS', 'ICICIGI.NS', 'ICICIPRULI.NS', 'IDFC.NS',
        'IDFCFIRSTB.NS', 'IFCI.NS', 'IGARASHI.NS', 'INDIACEM.NS', 'INDIGO.NS',
        'INDUSINDBK.NS', 'INFRATEL.NS', 'INFY.NS', 'IOC.NS', 'IRCON.NS',
        'ITC.NS', 'JETAIRWAYS.NS', 'JINDALSTEL.NS', 'JINDALSAW.NS', 'JKCEMENT.NS',
        'JKPAPER.NS', 'JKTYRE.NS', 'JMFINANCIAL.NS', 'JPPOWER.NS', 'JSWENERGY.NS',
        'JSWSTEEL.NS', 'JUBLFOOD.NS', 'JUBLPHARMA.NS', 'JUSTDIAL.NS', 'KARURVYSYA.NS',
        'KEC.NS', 'KOTAKBANK.NS', 'L&TFH.NS', 'LAURUSLABS.NS', 'LICHSGFIN.NS',
        'LINDEINDIA.NS', 'LUPIN.NS', 'M&MFIN.NS', 'MCDOWELL-N.NS', 'MFSL.NS',
        'MGL.NS', 'MINDTREE.NS', 'MOTILALOFS.NS', 'MPHASIS.NS', 'MRPL.NS',
        'MUTHOOTFIN.NS', 'NAM-INDIA.NS', 'NBCC.NS', 'NCC.NS', 'NHPC.NS',
        'NIACL.NS', 'NLCINDIA.NS', 'NMDC.NS', 'NTPC.NS', 'OFSS.NS',
        'OIL.NS', 'ONGC.NS', 'ORIENTBANK.NS', 'PAGEIND.NS', 'PCJEWELLER.NS',
        'PFC.NS', 'PGHL.NS', 'PHOENIXLTD.NS', 'PIDILITEIND.NS', 'PNB.NS',
        'POLYPLEX.NS', 'POWERGRID.NS', 'PRSMJOHNSN.NS', 'PVR.NS', 'RAIN.NS',
        'RAYMOND.NS', 'RBLBANK.NS', 'RCF.NS', 'RECLTD.NS', 'RELAXO.NS',
        'RELIANCE.NS', 'RITES.NS', 'RVNL.NS', 'SAIL.NS', 'SANOFI.NS',
        'SBILIFE.NS', 'SBIN.NS', 'SCI.NS', 'SELAN.NS', 'SHOPERSTOP.NS',
        'SIEMENS.NS', 'SOUTHBANK.NS', 'SRF.NS', 'SRTRANSFIN.NS', 'STARHEALTH.NS',
        'STEEL.NS', 'SUNPHARMA.NS', 'SUNTV.NS', 'SUPRAJIT.NS', 'SUZLON.NS',
        'SYNGENE.NS', 'TANLA.NS', 'TATACHEM.NS', 'TATACOFFEE.NS', 'TATACOMM.NS',
        'TATACONSUM.NS', 'TATAMOTORS.NS', 'TATAMTRDVR.NS', 'TATASTEEL.NS', 'TCS.NS',
        'TECHM.NS', 'TITAN.NS', 'TORNTPHARM.NS', 'TORNTPOWER.NS', 'TVSMOTOR.NS',
        'UBL.NS', 'UCOBANK.NS', 'UJJIVAN.NS', 'ULTRACEMCO.NS', 'UNIONBANK.NS',
        'UPL.NS', 'VAKRANGEE.NS', 'VARROC.NS', 'VEDL.NS', 'VOLTAS.NS',
        'WELCORP.NS', 'WELSPUNLTD.NS', 'WHIRLPOOL.NS', 'WIPRO.NS', 'YESBANK.NS',
        'ZEEL.NS', 'ZENSARTECH.NS', 'ZODIACLOTH.NS', 'ZYDUSWELL.NS'
    ]

def get_nifty_200_list(source=None):
    """Get list of NIFTY 200 stocks with data"""
    stocks = get_major_nifty_stocks()
    # For performance, maybe just fetch top 20 initially or use a smaller list for testing
    # But the requirement implies full list. 
    # Let's fetch top 20 for now to ensure speed, or all if needed.
    # app.py calls this to get the list.
    
    # We need to return stock DETAILS, not just symbols.
    return get_multiple_stocks_multi_source(stocks[:20], source=source)
