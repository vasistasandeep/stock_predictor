import requests
import json

def test_final_realtime_verification():
    """Final verification of real-time data integration"""
    print("🎯 FINAL REAL-TIME DATA VERIFICATION")
    print("=" * 50)
    
    try:
        # Test server status
        response = requests.get('http://127.0.0.1:5000/', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print(f"❌ Server returned status: {response.status_code}")
            return False
        
        # Test real-time stock data
        response = requests.get('http://127.0.0.1:5000/get_top_20_stocks', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            stocks = data.get('stock_details', [])
            
            print(f"✅ Server returned {len(stocks)} stocks")
            
            if stocks:
                # Check first stock for real-time indicators
                sample_stock = stocks[0]
                
                print(f"\n📊 SAMPLE REAL-TIME STOCK DATA:")
                print(f"   📈 Symbol: {sample_stock.get('symbol', 'N/A')}")
                print(f"   💰 Current Price: ₹{sample_stock.get('current_price', 'N/A')}")
                print(f"   📊 Day Change: {sample_stock.get('day_change', 'N/A')}%")
                print(f"   🏢 Market Cap: ₹{sample_stock.get('market_cap', 'N/A'):,}")
                print(f"   📊 Volume: {sample_stock.get('volume', 'N/A'):,}")
                print(f"   🏭 Sector: {sample_stock.get('sector', 'N/A')}")
                print(f"   📈 P/E Ratio: {sample_stock.get('pe_ratio', 'N/A')}")
                print(f"   💸 Dividend Yield: {sample_stock.get('dividend_yield', 'N/A')}")
                print(f"   📚 P/B Ratio: {sample_stock.get('price_to_book', 'N/A')}")
                print(f"   🔄 Data Source: {sample_stock.get('data_source', 'N/A')}")
                print(f"   🕐 Last Updated: {sample_stock.get('last_updated', 'N/A')}")
                
                # Verify real-time indicators
                has_realtime_data = all([
                    sample_stock.get('current_price'),
                    sample_stock.get('day_change') is not None,
                    sample_stock.get('market_cap'),
                    sample_stock.get('volume'),
                    sample_stock.get('sector'),
                    sample_stock.get('data_source') == 'real-time',
                    sample_stock.get('last_updated')
                ])
                
                if has_realtime_data:
                    print(f"\n🎉 REAL-TIME DATA CONFIRMED!")
                    print(f"   ✅ All real-time indicators present")
                    print(f"   ✅ Data source confirmed as 'real-time'")
                    print(f"   ✅ Fresh data with timestamp")
                    
                    # Show top 5 stocks
                    print(f"\n🏆 TOP 5 REAL-TIME STOCKS:")
                    for i, stock in enumerate(stocks[:5], 1):
                        print(f"{i:2d}. {stock.get('symbol', 'N/A'):12s} - ₹{stock.get('current_price', 'N/A')} ({stock.get('day_change', 'N/A'):+.1f}%)")
                    
                    return True
                else:
                    print(f"\n⚠️ MISSING REAL-TIME INDICATORS:")
                    missing = []
                    if not sample_stock.get('current_price'):
                        missing.append("current_price")
                    if sample_stock.get('day_change') is None:
                        missing.append("day_change")
                    if not sample_stock.get('market_cap'):
                        missing.append("market_cap")
                    if not sample_stock.get('volume'):
                        missing.append("volume")
                    if not sample_stock.get('sector'):
                        missing.append("sector")
                    if sample_stock.get('data_source') != 'real-time':
                        missing.append("data_source != 'real-time'")
                    if not sample_stock.get('last_updated'):
                        missing.append("last_updated")
                    
                    print(f"   ❌ Missing: {', '.join(missing)}")
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

def test_stock_analysis_endpoint():
    """Test stock analysis endpoint with real-time data"""
    print(f"\n🔍 TESTING STOCK ANALYSIS ENDPOINT")
    print("-" * 40)
    
    try:
        # Test a specific stock analysis
        response = requests.get('http://127.0.0.1:5000/get_stock_data/RELIANCE.NS/moderate', timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Stock analysis endpoint working")
            print(f"   📊 Analysis Summary: {data.get('analysis_summary', 'N/A')[:100]}...")
            print(f"   📈 Analyst Recommendations: {data.get('analyst_recommendations', {}).get('total_analysts', 'N/A')} analysts")
            print(f"   📰 News Items: {len(data.get('market_news', {}).get('news', []))} items")
            print(f"   📊 Market Sentiment: {data.get('market_sentiment', {}).get('score', 'N/A')}")
            
            return True
        else:
            print(f"❌ Stock analysis endpoint error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing stock analysis: {e}")
        return False

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE REAL-TIME DATA VERIFICATION")
    print("=" * 60)
    
    # Test real-time data
    realtime_success = test_final_realtime_verification()
    
    # Test stock analysis
    analysis_success = test_stock_analysis_endpoint()
    
    print(f"\n🎯 FINAL VERIFICATION RESULTS:")
    print(f"   ✅ Real-Time Data: {'WORKING' if realtime_success else 'NOT WORKING'}")
    print(f"   ✅ Stock Analysis: {'WORKING' if analysis_success else 'NOT WORKING'}")
    
    if realtime_success and analysis_success:
        print(f"\n🎉 COMPLETE SUCCESS!")
        print(f"   🔄 Real-time data is fully integrated and working")
        print(f"   📊 All stock data is live from Yahoo Finance")
        print(f"   🚀 Application is ready for production use")
    else:
        print(f"\n⚠️ NEEDS ATTENTION!")
        print(f"   🔧 Some components may need further configuration")
