import json

# Read the response file
with open('test_response.json', 'r') as f:
    content = f.read()
    
# Find the JSON part (skip HTTP headers)
json_start = content.find('{')
if json_start != -1:
    json_content = content[json_start:]
    data = json.loads(json_content)
    
    print('📊 Quick Stock Analysis Test Results:')
    print('=' * 40)
    print(f'Signal: {data.get("signal", "N/A")}')
    print(f'Entry Price: {data.get("entry_price", "N/A")}')
    print(f'Exit Price: {data.get("exit_price", "N/A")}')
    print(f'Stop Loss: {data.get("stop_loss", "N/A")}')
    
    if 'attributes' in data:
        attrs = data['attributes']
        print(f'\n📈 Technical Indicators:')
        print(f'RSI: {attrs.get("RSI", "N/A")}')
        print(f'SMA50: {attrs.get("SMA50", "N/A")}')
        print(f'SMA200: {attrs.get("SMA200", "N/A")}')
        print(f'ATR: {attrs.get("ATR", "N/A")}')
    
    print(f'\n✅ API is working! Signal: {data.get("signal", "N/A")}')
else:
    print('❌ No JSON found in response')
