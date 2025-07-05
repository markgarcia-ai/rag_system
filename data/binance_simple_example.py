import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API credentials from environment variables
API_KEY = os.getenv('BINANCE_API_KEY')
SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

base_url = 'https://api.binance.com'

def make_signed_request(endpoint, params=None):
    """Make a signed request to Binance API"""
    if params is None:
        params = {}
    
    # Add timestamp to all signed requests
    params['timestamp'] = int(time.time() * 1000)
    
    # Create query string
    query_string = urlencode(params)
    
    # Generate signature
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'), 
        query_string.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    # Add signature to query string
    query_string += f'&signature={signature}'
    
    # Prepare headers
    headers = {'X-MBX-APIKEY': API_KEY}
    
    # Build URL
    url = f'{base_url}{endpoint}?{query_string}'
    
    # Make request
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None

def example_1_account_info():
    """Example 1: Get account information"""
    print("=== Example 1: Get Account Information ===")
    endpoint = '/api/v3/account'
    result = make_signed_request(endpoint)
    
    if result:
        print("✅ Success!")
        print(f"Account Type: {result.get('accountType', 'N/A')}")
        print(f"Can Trade: {result.get('canTrade', 'N/A')}")
        print(f"Can Withdraw: {result.get('canWithdraw', 'N/A')}")
        print(f"Can Deposit: {result.get('canDeposit', 'N/A')}")
    else:
        print("❌ Failed to get account info")
    
    return result

def example_2_open_orders():
    """Example 2: Get open orders"""
    print("\n=== Example 2: Get Open Orders ===")
    endpoint = '/api/v3/openOrders'
    result = make_signed_request(endpoint)
    
    if result:
        if isinstance(result, list):
            print(f"✅ Success! Found {len(result)} open orders")
            if len(result) > 0:
                print(f"First order: {result[0]}")
        else:
            print("✅ Success! No open orders")
    else:
        print("❌ Failed to get open orders")
    
    return result

def example_3_all_orders():
    """Example 3: Get all orders for a symbol"""
    print("\n=== Example 3: Get All Orders for BTCUSDT ===")
    endpoint = '/api/v3/allOrders'
    params = {
        'symbol': 'BTCUSDT',
        'limit': 5
    }
    result = make_signed_request(endpoint, params)
    
    if result:
        if isinstance(result, list):
            print(f"✅ Success! Found {len(result)} orders")
            if len(result) > 0:
                print(f"First order: {result[0]}")
        else:
            print("✅ Success! No orders found")
    else:
        print("❌ Failed to get orders")
    
    return result

def example_4_trade_history():
    """Example 4: Get trade history"""
    print("\n=== Example 4: Get Trade History for BTCUSDT ===")
    endpoint = '/api/v3/myTrades'
    params = {
        'symbol': 'BTCUSDT',
        'limit': 5
    }
    result = make_signed_request(endpoint, params)
    
    if result:
        if isinstance(result, list):
            print(f"✅ Success! Found {len(result)} trades")
            if len(result) > 0:
                print(f"First trade: {result[0]}")
        else:
            print("✅ Success! No trades found")
    else:
        print("❌ Failed to get trade history")
    
    return result

def example_5_deposit_history():
    """Example 5: Get deposit history"""
    print("\n=== Example 5: Get Deposit History ===")
    endpoint = '/sapi/v1/capital/deposit/hisrec'
    params = {
        'limit': 5
    }
    result = make_signed_request(endpoint, params)
    
    if result:
        if isinstance(result, list):
            print(f"✅ Success! Found {len(result)} deposits")
            if len(result) > 0:
                print(f"First deposit: {result[0]}")
        else:
            print("✅ Success! No deposits found")
    else:
        print("❌ Failed to get deposit history")
    
    return result

def main():
    print("Binance API Signed Request Examples")
    print("=" * 50)
    
    # Check if API credentials are loaded
    if not API_KEY or not SECRET_KEY:
        print("❌ API credentials not found in .env file")
        print("Please make sure your .env file contains:")
        print("BINANCE_API_KEY=your_api_key")
        print("BINANCE_SECRET_KEY=your_secret_key")
        return
    
    if SECRET_KEY == 'your_secret_key_here':
        print("❌ Please update your SECRET_KEY in the .env file")
        print("Replace 'your_secret_key_here' with your actual Binance secret key")
        return
    
    print(f"✅ API Key loaded: {API_KEY[:10]}...")
    print(f"✅ Secret Key loaded: {SECRET_KEY[:10]}...")
    
    # Run examples
    try:
        example_1_account_info()
        example_2_open_orders()
        example_3_all_orders()
        example_4_trade_history()
        example_5_deposit_history()
        
        print("\n" + "=" * 50)
        print("✅ All examples completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 