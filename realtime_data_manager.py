import yfinance as yf
import requests
from datetime import datetime
import threading
import time

# Global variables
top_20_stocks = []
real_time_stock_data = {}
last_data_update = None

def get_major_nifty_stocks():
    """Get COMPREHENSIVE list of major NIFTY stocks for real-time analysis"""
    try:
        # Comprehensive list of NIFTY stocks (real-time data fetching)
        major_stocks = [
            # TOP 20 LARGE CAP (always included)
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS',
            'INFY.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS',
            'AXISBANK.NS', 'DMART.NS', 'MARUTI.NS', 'ASIANPAINT.NS', 'HCLTECH.NS',
            'ULTRACEMCO.NS', 'BAJFINANCE.NS', 'WIPRO.NS', 'NESTLEIND.NS', 'DRREDDY.NS',
            
            # LARGE CAP BANKS & FINANCIALS
            'LT.NS', 'SUNPHARMA.NS', 'TITAN.NS', 'M&M.NS', 'POWERGRID.NS',
            'NTPC.NS', 'COALINDIA.NS', 'BPCL.NS', 'GAIL.NS', 'ONGC.NS',
            'HDFCLIFE.NS', 'SBILIFE.NS', 'GRASIM.NS', 'ADANIPORTS.NS', 'TECHM.NS',
            
            # LARGE CAP CONSUMER & RETAIL
            'DIVISLAB.NS', 'BRITANNIA.NS', 'DLF.NS', 'BAJAJFINSV.NS', 'DABUR.NS',
            'PIDILITEIND.NS', 'HEROMOTOCO.NS', 'TATASTEEL.NS', 'EICHERMOT.NS', 'BALKRISIND.NS',
            'APOLLOHOSP.NS', 'SHREECEM.NS', 'TATACONSUM.NS', 'GODREJCP.NS', 'UBL.NS',
            
            # LARGE CAP SERVICES & TECHNOLOGY
            'ICICIGI.NS', 'TATAMOTORS.NS', 'JIOFINANCIAL.NS', 'CHOLAHLDNG.NS', 'INDUSINDBK.NS',
            'HDFCAMC.NS', 'SBICARD.NS', 'PNB.NS', 'BANKBARODA.NS', 'CANBK.NS',
            'INDIGO.NS', 'MUTHOOTFIN.NS', 'NAUKRI.NS', 'PAGEIND.NS', 'AMBUJACEM.NS',
            
            # MID CAP & LARGE CAP MIX
            'ACC.NS', 'GMRINFRA.NS', 'TATACOMM.NS', 'SIEMENS.NS', 'L&TFH.NS',
            'COFORGE.NS', 'MRF.NS', 'CEATLTD.NS', 'AUBANK.NS', 'FEDERALBNK.NS',
            'IDFC.NS', 'PFC.NS', 'REC.NS', 'IRCTC.NS', 'IRFC.NS',
            
            # INFRASTRUCTURE & INDUSTRIALS
            'RVNL.NS', 'RVINFRA.NS', 'IRCON.NS', 'NBCC.NS', 'NCC.NS',
            'TATAPOWER.NS', 'JSWSTEEL.NS', 'JINDALSTEL.NS', 'HINDALCO.NS', 'VEDL.NS',
            'NMDC.NS', 'NALCO.NS', 'HINDZINC.NS', 'MOIL.NS',
            
            # PHARMA & HEALTHCARE
            'LUPIN.NS', 'CADILAHC.NS', 'BIOCON.NS', 'AUROPHARMA.NS', 'GLAXO.NS',
            'SANOFI.NS', 'PFIZER.NS', 'CROMPTON.NS', 'LAURUSLABS.NS', 'TORNTPHARM.NS',
            
            # CONSUMER DURABLES & FMCG
            'WHIRLPOOL.NS', 'VOLTAS.NS', 'CUMMINSIND.NS', 'THERMAX.NS', 'ABB.NS',
            'GODREJIND.NS', 'KAJARIACER.NS', 'CERA.NS', 'JYOTHYLAB.NS',
            
            # IT & SERVICES
            'MINDTREE.NS', 'MPHASIS.NS', 'PERSISTENT.NS', 'LTI.NS', 'OFSS.NS',
            'SONATSOFTW.NS', 'TRIGYN.NS',
            
            # AUTOMOBILE & ANCILLARIES
            'BAJAJ-AUTO.NS', 'TVSMOTOR.NS', 'ASHOKLEY.NS', 'APOLLOTYRE.NS',
            
            # REAL ESTATE & CONSTRUCTION
            'GODREJPROP.NS', 'OBEROIREALTY.NS', 'BRIGADE.NS', 'PHOENIXLTD.NS',
            'PRESTIGE.NS', 'ANANTRAJ.NS', 'ASHIANA.NS', 'MAHINDRALIFE.NS', 'PNCINFRA.NS',
            
            # TELECOM & MEDIA
            'TATATELE.NS', 'DISHTV.NS', 'DEN.NS', 'ZEEL.NS', 'SUNTV.NS',
            'BALAJITELE.NS', 'HATHWAY.NS', 'DISH.NS',
            
            # CHEMICALS & FERTILIZERS
            'UPL.NS', 'PIIND.NS', 'SUMICHEM.NS', 'AARTIIND.NS', 'SOLARINDS.NS',
            'COROMANDEL.NS', 'CHAMBLFERT.NS', 'URVARAK.NS', 'DEEPAKFERT.NS', 'GNFC.NS',
            
            # TEXTILES & APPAREL
            'ARVIND.NS', 'KPRMILL.NS', 'TRIDENT.NS', 'WELSPUNLIV.NS',
            'VARDHMAN.NS', 'RAYMOND.NS', 'BOMBAYDYEING.NS', 'SUTLEJTEX.NS', 'CENTURYTEX.NS'
        ]
        
        print(f"📊 Using COMPREHENSIVE NIFTY stocks list ({len(major_stocks)} stocks)")
        print("🔄 All stocks will fetch REAL-TIME data from Yahoo Finance")
        return major_stocks
        
    except Exception as e:
        print(f"Error getting major NIFTY stocks: {e}")
        return []

def fetch_realtime_data():
    """Fetch real-time data in background"""
    global top_20_stocks, real_time_stock_data, last_data_update
    
    print("🚀 Starting REAL-TIME data fetch in background...")
    
    try:
        # Get stock list
        nifty_200_stocks = get_major_nifty_stocks()
        
        if not nifty_200_stocks:
            print("❌ No stock list available")
            return
        
        print(f"📊 Processing {len(nifty_200_stocks)} stocks for REAL-TIME data...")
        
        # Fetch real-time data for all stocks
        stock_data = []
        processed_count = 0
        
        for i, symbol in enumerate(nifty_200_stocks[:200], 1):  # Limit to 200 stocks
            try:
                if i % 20 == 0:
                    print(f"🔄 Processing stock {i}/{len(nifty_200_stocks)}: {symbol}")
                
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="5d", interval="1d")
                
                if hist.empty:
                    print(f"⚠️ {symbol}: No historical data available")
                    continue
                
                current_price = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                price_change = (current_price - previous_close) / previous_close * 100
                
                # Get real-time market cap
                market_cap = info.get('marketCap', 0)
                if market_cap and market_cap > 0:
                    # Convert to INR crores
                    usd_to_inr = 83.5
                    market_cap_inr_cr = (market_cap * usd_to_inr) / 10000000
                    
                    # Get additional real-time metrics
                    volume = hist['Volume'].iloc[-1]
                    avg_volume = ticker.history(period="1mo", interval="1d")['Volume'].mean()
                    volume_ratio = volume / avg_volume if avg_volume > 0 else 1
                    
                    stock_data.append({
                        'symbol': symbol,
                        'market_cap': market_cap_inr_cr,
                        'name': info.get('shortName', symbol),
                        'sector': info.get('sector', 'Unknown'),
                        'current_price': round(current_price, 2),
                        'price_change': round(price_change, 2),
                        'volume': int(volume),
                        'volume_ratio': round(volume_ratio, 2),
                        'pe_ratio': info.get('trailingPE'),
                        'dividend_yield': info.get('dividendYield'),
                        'price_to_book': info.get('priceToBook'),
                        'data_source': 'real-time'
                    })
                    
                    processed_count += 1
                    
                else:
                    print(f"❌ {symbol}: No market cap data available")
                    continue
                    
            except Exception as e:
                print(f"❌ {symbol}: Error - {str(e)}")
                continue
        
        # Sort by market cap and get top 20
        if stock_data:
            sorted_stocks = sorted(stock_data, key=lambda x: x['market_cap'], reverse=True)
            top_20_stocks = [stock['symbol'] for stock in sorted_stocks[:20]]
            
            # Store real-time data for all stocks
            real_time_stock_data = {stock['symbol']: stock for stock in stock_data}
            
            print(f"\n🏆 TOP 20 STOCKS BY MARKET CAP:")
            for i, stock in enumerate(sorted_stocks[:20], 1):
                print(f"{i:2d}. {stock['symbol']:12s} - ₹{stock['market_cap']:,.0f} cr ({stock['name']}) | ₹{stock['current_price']} ({stock['price_change']:+.1f}%)")
            
            last_data_update = datetime.now()
            print(f"\n✅ Successfully fetched {len(top_20_stocks)} top stocks from Yahoo Finance at {last_data_update.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📊 Real-time data stored for {len(real_time_stock_data)} stocks")
            print(f"🔄 Processed {processed_count} out of {len(nifty_200_stocks)} stocks successfully")
            
        else:
            print("❌ No stock data fetched")
            
    except Exception as e:
        print(f"❌ Error in real-time data fetch: {e}")

def initialize_fallback():
    """Initialize with fallback data immediately"""
    global top_20_stocks, last_data_update
    
    fallback_stocks = [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS',
        'INFY.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS',
        'AXISBANK.NS', 'DMART.NS', 'MARUTI.NS', 'ASIANPAINT.NS', 'HCLTECH.NS',
        'ULTRACEMCO.NS', 'BAJFINANCE.NS', 'WIPRO.NS', 'NESTLEIND.NS', 'DRREDDY.NS'
    ]
    
    top_20_stocks = fallback_stocks
    last_data_update = datetime.now()
    print(f"🔄 Initialized with fallback list of {len(top_20_stocks)} stocks")

# Initialize immediately
print("🚀 Initializing stock data...")
initialize_fallback()

# Start background thread for real-time data
print("🔄 Starting background real-time data fetch...")
background_thread = threading.Thread(target=fetch_realtime_data, daemon=True)
background_thread.start()

print("✅ Ready! Real-time data will be available shortly.")
print(f"📊 Current stock list: {len(top_20_stocks)} stocks")
