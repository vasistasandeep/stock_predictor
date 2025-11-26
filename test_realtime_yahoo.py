import yfinance as yf

def test_realtime_single_stock():
    """Test real-time data for a single stock"""
    print("🔍 Testing REAL-TIME data for RELIANCE.NS...")
    
    try:
        ticker = yf.Ticker('RELIANCE.NS')
        info = ticker.info
        hist = ticker.history(period="5d", interval="1d")
        
        if hist.empty:
            print("❌ No historical data available")
            return False
        
        current_price = hist['Close'].iloc[-1]
        previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        price_change = (current_price - previous_close) / previous_close * 100
        
        market_cap = info.get('marketCap', 0)
        if market_cap and market_cap > 0:
            usd_to_inr = 83.5
            market_cap_inr_cr = (market_cap * usd_to_inr) / 10000000
            
            volume = hist['Volume'].iloc[-1]
            avg_volume = ticker.history(period="1mo", interval="1d")['Volume'].mean()
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1
            
            print(f"✅ REAL-TIME DATA SUCCESS:")
            print(f"   📊 Name: {info.get('shortName', 'N/A')}")
            print(f"   💰 Current Price: ₹{current_price:.2f}")
            print(f"   📈 Price Change: {price_change:+.1f}%")
            print(f"   🏢 Market Cap: ₹{market_cap_inr_cr:,.0f} cr")
            print(f"   📊 Volume: {volume:,} ({volume_ratio:.1f}x avg)")
            print(f"   🏭 Sector: {info.get('sector', 'N/A')}")
            print(f"   📈 P/E Ratio: {info.get('trailingPE', 'N/A')}")
            print(f"   💸 Dividend Yield: {info.get('dividendYield', 'N/A')}")
            print(f"   📚 P/B Ratio: {info.get('priceToBook', 'N/A')}")
            print(f"   🕐 Last Updated: {hist.index[-1]}")
            
            return True
        else:
            print("❌ No market cap data available")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_multiple_stocks():
    """Test real-time data for multiple stocks"""
    print("\n🔍 Testing REAL-TIME data for multiple stocks...")
    
    stocks = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS']
    success_count = 0
    
    for symbol in stocks:
        print(f"\n📊 Testing {symbol}...")
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d", interval="1d")
            
            if not hist.empty and info.get('marketCap'):
                current_price = hist['Close'].iloc[-1]
                market_cap = info.get('marketCap', 0)
                print(f"✅ {symbol}: ₹{current_price:.2f} | ₹{market_cap/10000000*83.5:,.0f} cr")
                success_count += 1
            else:
                print(f"❌ {symbol}: No data available")
                
        except Exception as e:
            print(f"❌ {symbol}: Error - {e}")
    
    print(f"\n📈 Result: {success_count}/{len(stocks)} stocks fetched successfully")
    return success_count == len(stocks)

if __name__ == "__main__":
    print("🚀 TESTING REAL-TIME YAHOO FINANCE DATA")
    print("=" * 50)
    
    # Test single stock
    single_success = test_realtime_single_stock()
    
    # Test multiple stocks
    multiple_success = test_multiple_stocks()
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"   ✅ Single Stock Test: {'PASS' if single_success else 'FAIL'}")
    print(f"   ✅ Multiple Stock Test: {'PASS' if multiple_success else 'FAIL'}")
    
    if single_success and multiple_success:
        print(f"\n🎉 REAL-TIME DATA IS WORKING PERFECTLY!")
        print(f"   🔄 The server should use real-time data instead of fallback!")
    else:
        print(f"\n⚠️ REAL-TIME DATA HAS ISSUES!")
        print(f"   🔧 Check network connectivity or Yahoo Finance availability")
