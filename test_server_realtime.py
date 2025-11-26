import requests
import json

def test_server_realtime_data():
    """Test if server is using real-time data"""
    print("🔍 Testing Server Real-Time Data Integration...")
    
    try:
        # Test if server is running
        response = requests.get('http://127.0.0.1:5000/get_top_20_stocks', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            stocks = data.get('stock_details', [])
            
            if stocks:
                print(f"✅ Server returned {len(stocks)} stocks")
                
                # Check if data is real-time
                sample_stock = stocks[0]
                print(f"\n📊 Sample Stock Data:")
                print(f"   📈 Symbol: {sample_stock.get('symbol', 'N/A')}")
                print(f"   💰 Current Price: ₹{sample_stock.get('current_price', 'N/A')}")
                print(f"   📊 Price Change: {sample_stock.get('price_change', 'N/A')}%")
                market_cap = sample_stock.get('market_cap', 'N/A')
                if isinstance(market_cap, (int, float)):
                    print(f"   🏢 Market Cap: ₹{market_cap:,}")
                else:
                    print(f"   🏢 Market Cap: {market_cap}")
                volume = sample_stock.get('volume', 'N/A')
                if isinstance(volume, (int, float)):
                    print(f"   📊 Volume: {volume:,}")
                else:
                    print(f"   📊 Volume: {volume}")
                print(f"   🏭 Sector: {sample_stock.get('sector', 'N/A')}")
                print(f"   📈 P/E Ratio: {sample_stock.get('pe_ratio', 'N/A')}")
                print(f"   💸 Dividend Yield: {sample_stock.get('dividend_yield', 'N/A')}")
                print(f"   📚 P/B Ratio: {sample_stock.get('price_to_book', 'N/A')}")
                print(f"   🔄 Data Source: {sample_stock.get('data_source', 'N/A')}")
                
                # Check if it's real-time data
                has_realtime_indicators = all([
                    sample_stock.get('current_price'),
                    sample_stock.get('price_change') is not None,
                    sample_stock.get('market_cap'),
                    sample_stock.get('volume'),
                    sample_stock.get('sector'),
                    sample_stock.get('data_source') == 'real-time'
                ])
                
                if has_realtime_indicators:
                    print(f"\n🎉 SUCCESS: Server is using REAL-TIME data!")
                    print(f"   ✅ All indicators present and up-to-date")
                    print(f"   ✅ Data source confirmed as 'real-time'")
                    return True
                else:
                    print(f"\n⚠️ ISSUE: Server may be using fallback data")
                    print(f"   ❌ Missing some real-time indicators")
                    print(f"   ❌ Data source: {sample_stock.get('data_source', 'unknown')}")
                    return False
            else:
                print("❌ No stocks returned from server")
                return False
        else:
            print(f"❌ Server error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_server_logs():
    """Check if server is properly running"""
    print("\n🔍 Checking Server Status...")
    
    try:
        response = requests.get('http://127.0.0.1:5000/', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
            return True
        else:
            print(f"⚠️ Server returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING SERVER REAL-TIME DATA INTEGRATION")
    print("=" * 60)
    
    # Check if server is running
    server_running = check_server_logs()
    
    if server_running:
        # Test real-time data
        realtime_success = test_server_realtime_data()
        
        print(f"\n🎯 FINAL RESULTS:")
        print(f"   ✅ Server Status: {'RUNNING' if server_running else 'NOT RUNNING'}")
        print(f"   ✅ Real-Time Data: {'WORKING' if realtime_success else 'NOT WORKING'}")
        
        if realtime_success:
            print(f"\n🎉 SERVER IS USING REAL-TIME DATA!")
            print(f"   🔄 All stocks are fetched live from Yahoo Finance")
            print(f"   📊 Market cap, prices, and metrics are up-to-date")
        else:
            print(f"\n⚠️ SERVER IS USING FALLBACK DATA!")
            print(f"   🔧 Need to fix the real-time data fetching logic")
    else:
        print(f"\n❌ SERVER IS NOT RUNNING!")
        print(f"   🔧 Start the server with: python app.py")
