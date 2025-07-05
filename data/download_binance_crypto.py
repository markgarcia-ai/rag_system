import os
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
import json
import hmac
import hashlib
from urllib.parse import urlencode

class BinanceDataDownloader:
    def __init__(self, api_key=None):
        self.base_url = "https://api.binance.com"
        self.api_key = api_key
        self.output_dir = os.path.join(os.path.dirname(__file__), 'CRYPTO_data')
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _get_signed_params(self, params):
        """Generate signed parameters for authenticated requests"""
        if not self.api_key:
            return params
            
        # Add timestamp
        params['timestamp'] = int(time.time() * 1000)
        
        # Create signature
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        params['signature'] = signature
        return params
    
    def _make_request(self, endpoint, params=None, signed=False):
        """Make a request to Binance API"""
        url = f"{self.base_url}{endpoint}"
        
        headers = {}
        if self.api_key:
            headers['X-MBX-APIKEY'] = self.api_key
        
        if signed and params:
            params = self._get_signed_params(params)
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        
    def get_all_trading_pairs(self):
        """Get all USDT trading pairs from Binance"""
        try:
            data = self._make_request('/api/v3/exchangeInfo')
            
            if not data:
                return []
            
            usdt_pairs = []
            
            for symbol_info in data['symbols']:
                symbol = symbol_info['symbol']
                if symbol.endswith('USDT') and symbol_info['status'] == 'TRADING':
                    base_asset = symbol.replace('USDT', '')
                    usdt_pairs.append({
                        'symbol': symbol,
                        'base_asset': base_asset,
                        'quote_asset': 'USDT'
                    })
            
            print(f"Found {len(usdt_pairs)} USDT trading pairs")
            return usdt_pairs
            
        except Exception as e:
            print(f"Error getting trading pairs: {e}")
            return []
    
    def get_historical_data(self, symbol, start_date, end_date, interval='1d'):
        """Get historical kline data for a symbol"""
        try:
            # Convert dates to milliseconds timestamp
            start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
            end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
            
            params = {
                'symbol': symbol,
                'interval': interval,
                'startTime': start_ts,
                'endTime': end_ts,
                'limit': 1000
            }
            
            data = self._make_request('/api/v3/klines', params)
            
            if not data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert timestamp to date
            df['Date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d')
            
            # Convert string values to float
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Rename columns to match expected format
            df = df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
            
            # Add Market Cap column (will be None as Binance doesn't provide this)
            df['Market Cap'] = None
            
            return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Market Cap']]
            
        except Exception as e:
            print(f"Error getting historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def download_all_crypto_data(self, days_back=365, min_volume_filter=True, max_coins=500):
        """Download data for all available cryptocurrencies"""
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"Downloading crypto data from {start_date} to {end_date}")
        print(f"Maximum coins to download: {max_coins}")
        
        # Get all trading pairs
        trading_pairs = self.get_all_trading_pairs()
        
        if not trading_pairs:
            print("No trading pairs found")
            return
        
        # Limit the number of pairs to download
        trading_pairs = trading_pairs[:max_coins]
        
        successful_downloads = 0
        failed_downloads = 0
        
        for i, pair in enumerate(trading_pairs):
            symbol = pair['symbol']
            base_asset = pair['base_asset']
            
            print(f"[{i+1}/{len(trading_pairs)}] Downloading {symbol}...")
            
            # Get historical data
            df = self.get_historical_data(symbol, start_date, end_date)
            
            if df.empty:
                print(f"No data for {symbol}")
                failed_downloads += 1
                continue
            
            # Optional: Filter by minimum volume (last 30 days average)
            if min_volume_filter and len(df) >= 30:
                recent_volume = df.tail(30)['Volume'].mean()
                if recent_volume < 1000000:  # Less than 1M USDT volume
                    print(f"Skipping {symbol} - low volume ({recent_volume:.0f} USDT)")
                    failed_downloads += 1
                    continue
            
            # Save to CSV
            output_path = os.path.join(self.output_dir, f"{base_asset}.csv")
            df.to_csv(output_path, index=False)
            print(f"Saved {output_path} ({len(df)} records)")
            
            successful_downloads += 1
            
            # Rate limiting - Binance allows 1200 requests per minute with API key
            time.sleep(0.05)  # 50ms delay between requests
        
        print(f"\nDownload completed!")
        print(f"Successful downloads: {successful_downloads}")
        print(f"Failed downloads: {failed_downloads}")
        print(f"Total files in {self.output_dir}: {len(os.listdir(self.output_dir))}")
    
    def get_market_stats(self):
        """Get market statistics for all symbols"""
        try:
            data = self._make_request('/api/v3/ticker/24hr')
            
            if not data:
                return pd.DataFrame()
            
            # Filter USDT pairs
            usdt_stats = [item for item in data if item['symbol'].endswith('USDT')]
            
            # Convert to DataFrame
            df = pd.DataFrame(usdt_stats)
            
            # Convert numeric columns
            numeric_columns = ['priceChange', 'priceChangePercent', 'weightedAvgPrice', 
                             'prevClosePrice', 'lastPrice', 'lastQty', 'bidPrice', 
                             'bidQty', 'askPrice', 'askQty', 'openPrice', 'highPrice', 
                             'lowPrice', 'volume', 'quoteVolume', 'openTime', 'closeTime', 
                             'count']
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Sort by volume
            df = df.sort_values('quoteVolume', ascending=False)
            
            return df
            
        except Exception as e:
            print(f"Error getting market stats: {e}")
            return pd.DataFrame()

def main():
    # Your Binance API key
    api_key = "NLqlQNdj7HNJsscFW6h2QXrodT8JOPuYtXB93E1Q4FTDIB6UjsQ5lToGLIXe19B7"
    
    downloader = BinanceDataDownloader(api_key)
    
    # Get market statistics first
    print("Getting market statistics...")
    market_stats = downloader.get_market_stats()
    
    if not market_stats.empty:
        print("\nTop 20 cryptocurrencies by volume:")
        top_20 = market_stats.head(20)[['symbol', 'lastPrice', 'priceChangePercent', 'quoteVolume']]
        print(top_20.to_string(index=False))
        
        # Save market stats
        stats_path = os.path.join(downloader.output_dir, 'market_stats.csv')
        market_stats.to_csv(stats_path, index=False)
        print(f"\nMarket statistics saved to {stats_path}")
    
    # Download historical data
    print("\nStarting historical data download...")
    downloader.download_all_crypto_data(
        days_back=365, 
        min_volume_filter=True,
        max_coins=300  # Download top 300 coins
    )

if __name__ == "__main__":
    main() 