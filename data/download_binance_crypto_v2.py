import os
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
import json
import hmac
import hashlib
from urllib.parse import urlencode

class BinanceDataDownloaderV2:
    def __init__(self, api_key=None):
        # Try different Binance API endpoints
        self.endpoints = [
            "https://api.binance.com",
            "https://api1.binance.com", 
            "https://api2.binance.com",
            "https://api3.binance.com"
        ]
        self.current_endpoint = 0
        self.api_key = api_key
        self.output_dir = os.path.join(os.path.dirname(__file__), 'CRYPTO_data')
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _get_base_url(self):
        """Get the current working base URL"""
        return self.endpoints[self.current_endpoint]
    
    def _switch_endpoint(self):
        """Switch to next endpoint if current one fails"""
        self.current_endpoint = (self.current_endpoint + 1) % len(self.endpoints)
        print(f"Switching to endpoint: {self._get_base_url()}")
    
    def _make_request(self, endpoint, params=None, max_retries=3):
        """Make a request to Binance API with retry logic"""
        for attempt in range(max_retries):
            try:
                url = f"{self._get_base_url()}{endpoint}"
                
                headers = {}
                if self.api_key:
                    headers['X-MBX-APIKEY'] = self.api_key
                
                response = requests.get(url, params=params, headers=headers, timeout=30)
                
                if response.status_code == 451:
                    print(f"451 error on endpoint {self._get_base_url()}, switching...")
                    self._switch_endpoint()
                    continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                print(f"Request error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    if response.status_code == 451:
                        self._switch_endpoint()
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return None
        
        return None
    
    def test_connection(self):
        """Test if we can connect to Binance API"""
        print("Testing Binance API connection...")
        
        # Test with server time endpoint (no authentication needed)
        data = self._make_request('/api/v3/time')
        if data:
            server_time = datetime.fromtimestamp(data['serverTime'] / 1000)
            print(f"✅ Connected to Binance API. Server time: {server_time}")
            return True
        else:
            print("❌ Failed to connect to Binance API")
            return False
    
    def get_all_trading_pairs(self):
        """Get all USDT trading pairs from Binance"""
        print("Getting all trading pairs...")
        
        data = self._make_request('/api/v3/exchangeInfo')
        
        if not data:
            print("Failed to get exchange info")
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
    
    def get_24hr_ticker(self):
        """Get 24hr ticker for all symbols"""
        print("Getting 24hr ticker data...")
        
        data = self._make_request('/api/v3/ticker/24hr')
        
        if not data:
            print("Failed to get 24hr ticker")
            return []
        
        # Filter USDT pairs and sort by volume
        usdt_tickers = [item for item in data if item['symbol'].endswith('USDT')]
        usdt_tickers.sort(key=lambda x: float(x.get('quoteVolume', 0)), reverse=True)
        
        print(f"Found {len(usdt_tickers)} USDT tickers")
        return usdt_tickers
    
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
    
    def download_top_crypto_data(self, top_n=100, days_back=365, min_volume_filter=True):
        """Download data for top cryptocurrencies by volume"""
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"Downloading top {top_n} cryptocurrencies from {start_date} to {end_date}")
        
        # Get 24hr ticker to find top coins by volume
        tickers = self.get_24hr_ticker()
        
        if not tickers:
            print("No ticker data found")
            return
        
        # Take top N by volume
        top_tickers = tickers[:top_n]
        
        successful_downloads = 0
        failed_downloads = 0
        
        for i, ticker in enumerate(top_tickers):
            symbol = ticker['symbol']
            base_asset = symbol.replace('USDT', '')
            volume_24h = float(ticker.get('quoteVolume', 0))
            
            print(f"[{i+1}/{len(top_tickers)}] Downloading {symbol} (24h volume: ${volume_24h:,.0f})...")
            
            # Optional: Filter by minimum volume
            if min_volume_filter and volume_24h < 1000000:  # Less than 1M USDT volume
                print(f"Skipping {symbol} - low volume (${volume_24h:,.0f})")
                failed_downloads += 1
                continue
            
            # Get historical data
            df = self.get_historical_data(symbol, start_date, end_date)
            
            if df.empty:
                print(f"No data for {symbol}")
                failed_downloads += 1
                continue
            
            # Save to CSV
            output_path = os.path.join(self.output_dir, f"{base_asset}.csv")
            df.to_csv(output_path, index=False)
            print(f"Saved {output_path} ({len(df)} records)")
            
            successful_downloads += 1
            
            # Rate limiting - Binance allows 1200 requests per minute with API key
            time.sleep(0.1)  # 100ms delay between requests
        
        print(f"\nDownload completed!")
        print(f"Successful downloads: {successful_downloads}")
        print(f"Failed downloads: {failed_downloads}")
        print(f"Total files in {self.output_dir}: {len(os.listdir(self.output_dir))}")
    
    def save_market_stats(self):
        """Save market statistics to CSV"""
        tickers = self.get_24hr_ticker()
        
        if not tickers:
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(tickers)
        
        # Convert numeric columns
        numeric_columns = ['priceChange', 'priceChangePercent', 'weightedAvgPrice', 
                         'prevClosePrice', 'lastPrice', 'lastQty', 'bidPrice', 
                         'bidQty', 'askPrice', 'askQty', 'openPrice', 'highPrice', 
                         'lowPrice', 'volume', 'quoteVolume', 'openTime', 'closeTime', 
                         'count']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Save to CSV
        stats_path = os.path.join(self.output_dir, 'binance_market_stats.csv')
        df.to_csv(stats_path, index=False)
        print(f"Market statistics saved to {stats_path}")
        
        # Show top 20 by volume
        print("\nTop 20 cryptocurrencies by volume:")
        top_20 = df.head(20)[['symbol', 'lastPrice', 'priceChangePercent', 'quoteVolume']]
        print(top_20.to_string(index=False))

def main():
    # Your Binance API key
    api_key = "NLqlQNdj7HNJsscFW6h2QXrodT8JOPuYtXB93E1Q4FTDIB6UjsQ5lToGLIXe19B7"
    
    downloader = BinanceDataDownloaderV2(api_key)
    
    # Test connection first
    if not downloader.test_connection():
        print("Cannot connect to Binance API. Exiting.")
        return
    
    # Save market statistics
    downloader.save_market_stats()
    
    # Download historical data for top cryptocurrencies
    print("\nStarting historical data download...")
    downloader.download_top_crypto_data(
        top_n=100,           # Download top 100 by volume
        days_back=365,       # 1 year of data
        min_volume_filter=True  # Filter by minimum volume
    )

if __name__ == "__main__":
    main() 