import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class BinanceSignedAPI:
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.secret_key = os.getenv('BINANCE_SECRET_KEY')
        self.base_url = "https://api.binance.com"
        
        # Validate credentials
        if not self.api_key or not self.secret_key:
            raise ValueError("API credentials not found in .env file")
        
        if self.secret_key == 'your_secret_key_here':
            raise ValueError("Please update your SECRET_KEY in the .env file")
        
    def _generate_signature(self, params):
        """Generate HMAC SHA256 signature for the request"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_signed_request(self, endpoint, params=None):
        """Make a signed request to Binance API"""
        if params is None:
            params = {}
        
        # Add timestamp to all signed requests
        params['timestamp'] = int(time.time() * 1000)
        
        # Generate signature
        signature = self._generate_signature(params)
        params['signature'] = signature
        
        # Prepare headers
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        
        # Build URL
        query_string = urlencode(params)
        url = f'{self.base_url}{endpoint}?{query_string}'
        
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
    
    def get_account_info(self):
        """Get account information"""
        print("=== Getting Account Information ===")
        endpoint = '/api/v3/account'
        result = self._make_signed_request(endpoint)
        
        if result:
            print(f"Account Type: {result.get('accountType', 'N/A')}")
            print(f"Maker Commission: {result.get('makerCommission', 'N/A')}")
            print(f"Taker Commission: {result.get('takerCommission', 'N/A')}")
            print(f"Buyer Commission: {result.get('buyerCommission', 'N/A')}")
            print(f"Seller Commission: {result.get('sellerCommission', 'N/A')}")
            print(f"Can Trade: {result.get('canTrade', 'N/A')}")
            print(f"Can Withdraw: {result.get('canWithdraw', 'N/A')}")
            print(f"Can Deposit: {result.get('canDeposit', 'N/A')}")
            
            # Show balances
            balances = result.get('balances', [])
            non_zero_balances = [b for b in balances if float(b.get('free', 0)) > 0 or float(b.get('locked', 0)) > 0]
            
            if non_zero_balances:
                print("\nNon-zero balances:")
                for balance in non_zero_balances[:10]:  # Show first 10
                    asset = balance['asset']
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    total = free + locked
                    if total > 0:
                        print(f"  {asset}: Free={free}, Locked={locked}, Total={total}")
            else:
                print("No non-zero balances found")
        
        return result
    
    def get_open_orders(self, symbol=None):
        """Get open orders"""
        print(f"\n=== Getting Open Orders ===")
        endpoint = '/api/v3/openOrders'
        
        params = {}
        if symbol:
            params['symbol'] = symbol
            print(f"Symbol: {symbol}")
        
        result = self._make_signed_request(endpoint, params)
        
        if result:
            if isinstance(result, list) and len(result) > 0:
                print(f"Found {len(result)} open orders:")
                for order in result[:5]:  # Show first 5 orders
                    print(f"  Order ID: {order['orderId']}")
                    print(f"  Symbol: {order['symbol']}")
                    print(f"  Side: {order['side']}")
                    print(f"  Type: {order['type']}")
                    print(f"  Quantity: {order['origQty']}")
                    print(f"  Price: {order['price']}")
                    print(f"  Status: {order['status']}")
                    print(f"  Time: {order['time']}")
                    print("  ---")
            else:
                print("No open orders found")
        else:
            print("Failed to get open orders")
        
        return result
    
    def get_all_orders(self, symbol, limit=10):
        """Get all orders for a symbol"""
        print(f"\n=== Getting All Orders for {symbol} ===")
        endpoint = '/api/v3/allOrders'
        
        params = {
            'symbol': symbol,
            'limit': limit
        }
        
        result = self._make_signed_request(endpoint, params)
        
        if result:
            if isinstance(result, list) and len(result) > 0:
                print(f"Found {len(result)} orders:")
                for order in result[:5]:  # Show first 5 orders
                    print(f"  Order ID: {order['orderId']}")
                    print(f"  Symbol: {order['symbol']}")
                    print(f"  Side: {order['side']}")
                    print(f"  Type: {order['type']}")
                    print(f"  Quantity: {order['origQty']}")
                    print(f"  Price: {order['price']}")
                    print(f"  Status: {order['status']}")
                    print(f"  Time: {order['time']}")
                    print("  ---")
            else:
                print("No orders found")
        else:
            print("Failed to get orders")
        
        return result
    
    def get_trade_history(self, symbol, limit=10):
        """Get trade history for a symbol"""
        print(f"\n=== Getting Trade History for {symbol} ===")
        endpoint = '/api/v3/myTrades'
        
        params = {
            'symbol': symbol,
            'limit': limit
        }
        
        result = self._make_signed_request(endpoint, params)
        
        if result:
            if isinstance(result, list) and len(result) > 0:
                print(f"Found {len(result)} trades:")
                for trade in result[:5]:  # Show first 5 trades
                    print(f"  Trade ID: {trade['id']}")
                    print(f"  Symbol: {trade['symbol']}")
                    print(f"  Side: {trade['isBuyer']}")
                    print(f"  Quantity: {trade['qty']}")
                    print(f"  Price: {trade['price']}")
                    print(f"  Commission: {trade['commission']}")
                    print(f"  Time: {trade['time']}")
                    print("  ---")
            else:
                print("No trades found")
        else:
            print("Failed to get trade history")
        
        return result
    
    def get_dust_log(self):
        """Get dust log (small amounts that can be converted to BNB)"""
        print(f"\n=== Getting Dust Log ===")
        endpoint = '/sapi/v1/asset/dribblet'
        
        result = self._make_signed_request(endpoint)
        
        if result:
            print(f"Total: {result.get('total', 'N/A')}")
            user_asset_dribblets = result.get('userAssetDribblets', [])
            if user_asset_dribblets:
                print(f"Found {len(user_asset_dribblets)} dust conversion records")
                for record in user_asset_dribblets[:3]:  # Show first 3
                    print(f"  Time: {record.get('operateTime', 'N/A')}")
                    print(f"  Total Service Charge: {record.get('totalServiceCharge', 'N/A')}")
                    print(f"  Total Transfered: {record.get('totalTransfered', 'N/A')}")
                    print("  ---")
            else:
                print("No dust conversion records found")
        else:
            print("Failed to get dust log")
        
        return result
    
    def get_deposit_history(self, limit=10):
        """Get deposit history"""
        print(f"\n=== Getting Deposit History ===")
        endpoint = '/sapi/v1/capital/deposit/hisrec'
        
        params = {
            'limit': limit
        }
        
        result = self._make_signed_request(endpoint, params)
        
        if result:
            if isinstance(result, list) and len(result) > 0:
                print(f"Found {len(result)} deposits:")
                for deposit in result[:5]:  # Show first 5 deposits
                    print(f"  Amount: {deposit['amount']} {deposit['coin']}")
                    print(f"  Status: {deposit['status']}")
                    print(f"  Time: {deposit['insertTime']}")
                    print("  ---")
            else:
                print("No deposits found")
        else:
            print("Failed to get deposit history")
        
        return result
    
    def get_withdraw_history(self, limit=10):
        """Get withdrawal history"""
        print(f"\n=== Getting Withdrawal History ===")
        endpoint = '/sapi/v1/capital/withdraw/history'
        
        params = {
            'limit': limit
        }
        
        result = self._make_signed_request(endpoint, params)
        
        if result:
            if isinstance(result, list) and len(result) > 0:
                print(f"Found {len(result)} withdrawals:")
                for withdrawal in result[:5]:  # Show first 5 withdrawals
                    print(f"  Amount: {withdrawal['amount']} {withdrawal['coin']}")
                    print(f"  Status: {withdrawal['status']}")
                    print(f"  Time: {withdrawal['applyTime']}")
                    print("  ---")
            else:
                print("No withdrawals found")
        else:
            print("Failed to get withdrawal history")
        
        return result

def main():
    print("Binance API Signed Request Examples")
    print("=" * 50)
    
    try:
        # Initialize API client
        api = BinanceSignedAPI()
        
        print(f"✅ API Key loaded: {api.api_key[:10]}...")
        print(f"✅ Secret Key loaded: {api.secret_key[:10]}...")
        
        # Test different endpoints
        # 1. Get account information
        account_info = api.get_account_info()
        
        # 2. Get open orders (if any)
        open_orders = api.get_open_orders()
        
        # 3. Get recent orders for BTCUSDT (example)
        all_orders = api.get_all_orders('BTCUSDT', limit=5)
        
        # 4. Get trade history for BTCUSDT (example)
        trade_history = api.get_trade_history('BTCUSDT', limit=5)
        
        # 5. Get dust log
        dust_log = api.get_dust_log()
        
        # 6. Get deposit history
        deposit_history = api.get_deposit_history(limit=5)
        
        # 7. Get withdrawal history
        withdraw_history = api.get_withdraw_history(limit=5)
        
        print("\n" + "=" * 50)
        print("✅ All API calls completed successfully!")
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nTo fix this:")
        print("1. Make sure your .env file exists in the data/ directory")
        print("2. Update BINANCE_SECRET_KEY in .env with your actual secret key")
        print("3. Run the script again")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 