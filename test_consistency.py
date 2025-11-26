import json
import requests

# Test signal consistency
print("🔍 Testing Signal Consistency...")
print("=" * 50)

# Get bulk signals
bulk_response = requests.get('http://127.0.0.1:5000/get_all_signals')
bulk_data = bulk_response.json()

# Get individual signal for MARUTI
individual_response = requests.get('http://127.0.0.1:5000/get_stock_data/MARUTI/Medium')
individual_data = individual_response.json()

# Find MARUTI in bulk data
maruti_bulk = next((s for s in bulk_data['signals'] if 'MARUTI' in s['symbol']), None)

if maruti_bulk:
    print(f"📊 MARUTI Bulk Analysis:")
    print(f"   Signal: {maruti_bulk['signal']}")
    print(f"   RSI: {maruti_bulk['rsi']}")
    print(f"   SMA50: {maruti_bulk['sma_50']}")
    print(f"   SMA200: {maruti_bulk['sma_200']}")
    print(f"   Price: {maruti_bulk['current_price']}")
    
    print(f"\n📊 MARUTI Individual Analysis:")
    print(f"   Signal: {individual_data['signal']}")
    print(f"   RSI: {individual_data['attributes']['RSI']}")
    print(f"   SMA50: {individual_data['attributes']['SMA50']}")
    print(f"   SMA200: {individual_data['attributes']['SMA200']}")
    
    # Check consistency
    rsi_match = maruti_bulk['rsi'] == float(individual_data['attributes']['RSI'])
    sma50_match = maruti_bulk['sma_50'] == float(individual_data['attributes']['SMA50'])
    sma200_match = maruti_bulk['sma_200'] == float(individual_data['attributes']['SMA200'])
    
    print(f"\n✅ Consistency Check:")
    print(f"   RSI Match: {'✅' if rsi_match else '❌'}")
    print(f"   SMA50 Match: {'✅' if sma50_match else '❌'}")
    print(f"   SMA200 Match: {'✅' if sma200_match else '❌'}")
    
    if rsi_match and sma50_match and sma200_match:
        print(f"\n🎉 PERFECT! Signals are 100% consistent!")
    else:
        print(f"\n⚠️ Still some inconsistencies found")
        
else:
    print("❌ MARUTI not found in bulk data")
