import os
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
import json

class CryptoDataDownloader:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.output_dir = os.path.join(os.path.dirname(__file__), 'CRYPTO_data')
        os.makedirs(self.output_dir, exist_ok=True)
        
    def get_top_coins(self, limit=100):
        """Get top coins by market cap"""
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': False
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except Exception as e:
            print(f"Error getting top coins: {e}")
            return []
    
    def get_historical_data(self, coin_id, days=365):
        """Get historical data for a specific coin with retry logic"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}/coins/{coin_id}/market_chart"
                params = {
                    'vs_currency': 'usd',
                    'days': days,
                    'interval': 'daily'
                }
                
                response = requests.get(url, params=params)
                
                if response.status_code == 429:  # Rate limit
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"Rate limited, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                if 'prices' not in data or not data['prices']:
                    return pd.DataFrame()
                
                # Convert to DataFrame
                df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
                df['Date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d')
                
                # Get volume data
                volumes = data.get('total_volumes', [])
                if volumes:
                    volume_df = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
                    volume_df['Date'] = pd.to_datetime(volume_df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d')
                    df = df.merge(volume_df[['Date', 'volume']], on='Date', how='left')
                else:
                    df['volume'] = None
                
                # Get market cap data
                market_caps = data.get('market_caps', [])
                if market_caps:
                    mcap_df = pd.DataFrame(market_caps, columns=['timestamp', 'market_cap'])
                    mcap_df['Date'] = pd.to_datetime(mcap_df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d')
                    df = df.merge(mcap_df[['Date', 'market_cap']], on='Date', how='left')
                else:
                    df['market_cap'] = None
                
                # For daily data, we need to calculate OHLC from the price data
                df['Open'] = df['price']
                df['High'] = df['price']
                df['Low'] = df['price']
                df['Close'] = df['price']
                df['Volume'] = df['volume']
                df['Market Cap'] = df['market_cap']
                
                return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Market Cap']]
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"Request failed, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Error getting historical data for {coin_id}: {e}")
                    return pd.DataFrame()
        
        return pd.DataFrame()
    
    def download_crypto_batch(self, batch_size=10, total_coins=100):
        """Download crypto data in batches to avoid rate limiting"""
        print(f"Downloading top {total_coins} cryptocurrencies in batches of {batch_size}")
        
        # Get top coins
        coins = self.get_top_coins(total_coins)
        
        if not coins:
            print("No coins found")
            return
        
        successful_downloads = 0
        failed_downloads = 0
        
        # Process in batches
        for i in range(0, len(coins), batch_size):
            batch = coins[i:i+batch_size]
            print(f"\nProcessing batch {i//batch_size + 1}/{(len(coins) + batch_size - 1)//batch_size}")
            
            for coin in batch:
                symbol = coin['symbol'].upper()
                coin_id = coin['id']
                name = coin['name']
                
                print(f"Downloading {symbol} ({name})...")
                
                # Get historical data
                df = self.get_historical_data(coin_id, days=365)
                
                if df.empty:
                    print(f"No data for {symbol}")
                    failed_downloads += 1
                    continue
                
                # Save to CSV
                output_path = os.path.join(self.output_dir, f"{symbol}.csv")
                df.to_csv(output_path, index=False)
                print(f"Saved {output_path} ({len(df)} records)")
                
                successful_downloads += 1
                
                # Small delay between requests in the same batch
                time.sleep(0.5)
            
            # Longer delay between batches to avoid rate limiting
            if i + batch_size < len(coins):
                print("Waiting 5 seconds before next batch...")
                time.sleep(5)
        
        print(f"\nDownload completed!")
        print(f"Successful downloads: {successful_downloads}")
        print(f"Failed downloads: {failed_downloads}")
        print(f"Total files in {self.output_dir}: {len(os.listdir(self.output_dir))}")
    
    def get_market_summary(self):
        """Get a summary of the current crypto market"""
        try:
            url = f"{self.base_url}/global"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            return data['data']
            
        except Exception as e:
            print(f"Error getting market summary: {e}")
            return None

def main():
    downloader = CryptoDataDownloader()
    
    # Get market summary
    print("Getting market summary...")
    market_summary = downloader.get_market_summary()
    
    if market_summary:
        print(f"Total market cap: ${market_summary['total_market_cap']['usd']:,.0f}")
        print(f"Total volume (24h): ${market_summary['total_volume']['usd']:,.0f}")
        print(f"Market cap change (24h): {market_summary['market_cap_change_percentage_24h_usd']:.2f}%")
    
    # Download crypto data in batches
    print("\nStarting batch download...")
    downloader.download_crypto_batch(
        batch_size=5,    # Small batches to avoid rate limiting
        total_coins=50   # Start with top 50 coins
    )

if __name__ == "__main__":
    main() 