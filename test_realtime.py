import requests
import json

def test_real_time_data():
    print("🔍 Testing Real-Time Data Integration")
    print("=" * 50)
    
    # Test symbols
    symbols = ['RELIANCE', 'TCS', 'INFY']
    
    for symbol in symbols:
        print(f"\n📊 Testing {symbol}:")
        print("-" * 30)
        
        try:
            # Test main endpoint
            response = requests.get(f'http://127.0.0.1:5000/get_stock_data/{symbol}/Medium')
            
            if response.status_code == 200:
                data = response.json()
                
                # Basic signal data
                print(f"✅ Signal: {data.get('signal', 'N/A')}")
                print(f"💰 Entry: {data.get('entry_price', 'N/A')}")
                print(f"🎯 Exit: {data.get('exit_price', 'N/A')}")
                
                # Market news
                news = data.get('market_news', [])
                print(f"📰 News Articles: {len(news)}")
                if news:
                    for i, article in enumerate(news[:2], 1):
                        print(f"   {i}. {article.get('title', 'N/A')[:50]}...")
                        print(f"      Source: {article.get('source', 'N/A')}")
                
                # Analyst recommendations
                analyst = data.get('analyst_recommendations', {})
                total = analyst.get('total_analysts', 0)
                if total > 0:
                    print(f"📊 Analysts: {total} total")
                    print(f"   Buy: {analyst.get('buy', 0) + analyst.get('strong_buy', 0)}")
                    print(f"   Hold: {analyst.get('hold', 0)}")
                    print(f"   Sell: {analyst.get('sell', 0) + analyst.get('strong_sell', 0)}")
                    print(f"   Source: {analyst.get('source', 'N/A')}")
                else:
                    print(f"📊 Analysts: No real data available")
                
                # Market sentiment
                sentiment = data.get('market_sentiment', {})
                print(f"💭 Sentiment: {sentiment.get('sentiment', 'N/A')}")
                print(f"   Score: {sentiment.get('score', 'N/A')}")
                print(f"   Source: {sentiment.get('source', 'N/A')}")
                
                # Analysis summary
                summary = data.get('analysis_summary', '')
                if summary and len(summary) > 100:
                    print(f"📋 Summary: {summary[:100]}...")
                
                print(f"✅ {symbol} - Real-time data working!")
                
            else:
                print(f"❌ {symbol} - Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {symbol} - Exception: {e}")
    
    print(f"\n🎉 Real-Time Data Test Complete!")

if __name__ == "__main__":
    test_real_time_data()
