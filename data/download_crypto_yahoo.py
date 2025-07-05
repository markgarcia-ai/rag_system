import os
import pandas as pd
import yfinance as yf
import time
from datetime import datetime, timedelta

class YahooCryptoDownloader:
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), 'CRYPTO_data')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # List of major cryptocurrencies with their Yahoo Finance tickers
        self.crypto_tickers = {
            'BTC': 'BTC-USD',
            'ETH': 'ETH-USD',
            'BNB': 'BNB-USD',
            'SOL': 'SOL-USD',
            'XRP': 'XRP-USD',
            'ADA': 'ADA-USD',
            'AVAX': 'AVAX-USD',
            'DOGE': 'DOGE-USD',
            'DOT': 'DOT-USD',
            'MATIC': 'MATIC-USD',
            'LINK': 'LINK-USD',
            'UNI': 'UNI-USD',
            'ATOM': 'ATOM-USD',
            'LTC': 'LTC-USD',
            'INJ': 'INJ-USD',
            'OP': 'OP-USD',
            'ARB': 'ARB-USD',
            'SEI': 'SEI-USD',
            'USDT': 'USDT-USD',
            'USDC': 'USDC-USD',
            'TRX': 'TRX-USD',
            'BCH': 'BCH-USD',
            'XLM': 'XLM-USD',
            'TON': 'TON-USD',
            'SHIB': 'SHIB-USD',
            'HBAR': 'HBAR-USD',
            'XMR': 'XMR-USD',
            'NEAR': 'NEAR-USD',
            'ICP': 'ICP-USD',
            'CRO': 'CRO-USD',
            'ETC': 'ETC-USD',
            'APT': 'APT-USD',
            'AAVE': 'AAVE-USD',
            'PEPE': 'PEPE-USD',
            'DAI': 'DAI-USD',
            'OKB': 'OKB-USD',
            'TAO': 'TAO-USD',
            'JITOSOL': 'JITOSOL-USD',
            'FIL': 'FIL-USD',
            'ALGO': 'ALGO-USD',
            'WLD': 'WLD-USD',
            'FDUSD': 'FDUSD-USD',
            'SEI': 'SEI-USD',
            'BONK': 'BONK-USD',
            'KCS': 'KCS-USD',
            'JUP': 'JUP-USD',
            'NEXO': 'NEXO-USD',
            'RETH': 'RETH-USD',
            'FARTCOIN': 'FARTCOIN-USD',
            'SPX': 'SPX6900-USD',
            'FLR': 'FLR-USD',
            'TIA': 'TIA-USD',
            'XDC': 'XDC-USD',
            'VIRTUAL': 'VIRTUAL-USD',
            'S': 'S-USD',
            'PENGU': 'PENGU-USD',
            'STX': 'STX-USD',
            'METH': 'METH-USD',
            'SYRUPUSDC': 'SYRUPUSDC-USD',
            'PAXG': 'PAXG-USD',
            'SOLVBTC': 'SOLVBTC-USD',
            'KAIA': 'KAIA-USD',
            'WBTC': 'WBTC-USD',
            'PYUSD': 'PYUSD-USD',
            'WBNB': 'WBNB-USD',
            'EZETH': 'EZETH-USD',
            'WIF': 'WIF-USD',
            'XAUT': 'XAUT-USD',
            'IP': 'IP-USD',
            'GRT': 'GRT-USD',
            'IMX': 'IMX-USD',
            'CAKE': 'CAKE-USD',
            'JUPSOL': 'JUPSOL-USD',
            'A': 'A-USD',
            'MSOL': 'MSOL-USD',
            'LSETH': 'LSETH-USD',
            'FLOKI': 'FLOKI-USD',
            'JTO': 'JTO-USD',
            'CRV': 'CRV-USD',
            'THETA': 'THETA-USD',
            'USDX': 'USDX-USD',
            'LDO': 'LDO-USD',
            'USDY': 'USDY-USD',
            'ZEC': 'ZEC-USD',
            'AERO': 'AERO-USD',
            'GALA': 'GALA-USD',
            'WHYPE': 'WHYPE-USD',
            'ENS': 'ENS-USD',
            'IOTA': 'IOTA-USD',
            'BTT': 'BTT-USD',
            'SYRUP': 'SYRUP-USD',
            'SAND': 'SAND-USD',
            'USD0': 'USD0-USD',
            'JASMY': 'JASMY-USD',
            'SAROS': 'SAROS-USD',
            'WAL': 'WAL-USD',
            'TBTC': 'TBTC-USD',
            'SUPEROETH': 'SUPEROETH-USD',
            'PYTH': 'PYTH-USD',
            'RAY': 'RAY-USD',
            'XTZ': 'XTZ-USD',
            'PENDLE': 'PENDLE-USD',
            'WETH': 'WETH-USD',
            'USDF': 'USDF-USD',
            'XSOLVBTC': 'XSOLVBTC-USD',
            'CMETH': 'CMETH-USD',
            'AB': 'AB-USD',
            'BTC.B': 'BTC.B-USD',
            'FLOW': 'FLOW-USD',
            'CORE': 'CORE-USD',
            'TUSD': 'TUSD-USD',
            'MANA': 'MANA-USD',
            'STHYPE': 'STHYPE-USD',
            'RLUSD': 'RLUSD-USD',
            'BSV': 'BSV-USD',
            'APE': 'APE-USD',
            'XCN': 'XCN-USD',
            'USDC.E': 'USDC.E-USD',
            'RUNE': 'RUNE-USD',
            'NFT': 'NFT-USD',
            'BDX': 'BDX-USD',
            'DEXE': 'DEXE-USD',
            'MORPHO': 'MORPHO-USD',
            'VENOM': 'VENOM-USD',
            'KAVA': 'KAVA-USD',
            'USDD': 'USDD-USD',
            'BRETT': 'BRETT-USD',
            'MOVE': 'MOVE-USD',
            'DOG': 'DOG-USD',
            'HNT': 'HNT-USD',
            'RSR': 'RSR-USD',
            'STRK': 'STRK-USD',
            'DYDX': 'DYDX-USD',
            'COMP': 'COMP-USD',
            'NEO': 'NEO-USD',
            'EGLD': 'EGLD-USD',
            'MOG': 'MOG-USD',
            'KAITO': 'KAITO-USD',
            'AIOZ': 'AIOZ-USD',
            'CFX': 'CFX-USD',
            'XEC': 'XEC-USD',
            'EBTC': 'EBTC-USD',
            'DEEP': 'DEEP-USD',
            'B': 'B-USD',
            'AXS': 'AXS-USD',
            'TEL': 'TEL-USD',
            'CBETH': 'CBETH-USD',
            'ETHFI': 'ETHFI-USD',
            'EIGEN': 'EIGEN-USD',
            'JST': 'JST-USD',
            'EOS': 'EOS-USD',
            'KET': 'KET-USD',
            'CHZ': 'CHZ-USD',
            'OHM': 'OHM-USD',
            'USDG': 'USDG-USD',
            'AR': 'AR-USD',
            'SUN': 'SUN-USD'
        }
    
    def get_historical_data(self, symbol, yahoo_ticker, days_back=365):
        """Get historical data for a cryptocurrency"""
        try:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            
            print(f"Downloading {symbol} ({yahoo_ticker})...")
            
            # Download data from Yahoo Finance
            ticker = yf.Ticker(yahoo_ticker)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                print(f"No data for {symbol}")
                return pd.DataFrame()
            
            # Reset index to get Date as a column
            data = data.reset_index()
            
            # Rename columns to match expected format
            data = data.rename(columns={
                'Date': 'Date',
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Close': 'Close',
                'Volume': 'Volume'
            })
            
            # Add Market Cap column (will be None as Yahoo Finance doesn't provide this)
            data['Market Cap'] = None
            
            # Format date
            data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%Y-%m-%d')
            
            return data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Market Cap']]
            
        except Exception as e:
            print(f"Error getting historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def download_all_crypto_data(self, days_back=365, batch_size=10):
        """Download data for all available cryptocurrencies"""
        print(f"Downloading crypto data for the last {days_back} days")
        print(f"Total cryptocurrencies to download: {len(self.crypto_tickers)}")
        
        successful_downloads = 0
        failed_downloads = 0
        
        # Process in batches
        ticker_items = list(self.crypto_tickers.items())
        
        for i in range(0, len(ticker_items), batch_size):
            batch = ticker_items[i:i+batch_size]
            print(f"\nProcessing batch {i//batch_size + 1}/{(len(ticker_items) + batch_size - 1)//batch_size}")
            
            for symbol, yahoo_ticker in batch:
                # Get historical data
                df = self.get_historical_data(symbol, yahoo_ticker, days_back)
                
                if df.empty:
                    failed_downloads += 1
                    continue
                
                # Save to CSV
                output_path = os.path.join(self.output_dir, f"{symbol}.csv")
                df.to_csv(output_path, index=False)
                print(f"Saved {output_path} ({len(df)} records)")
                
                successful_downloads += 1
                
                # Small delay between requests
                time.sleep(0.5)
            
            # Longer delay between batches
            if i + batch_size < len(ticker_items):
                print("Waiting 3 seconds before next batch...")
                time.sleep(3)
        
        print(f"\nDownload completed!")
        print(f"Successful downloads: {successful_downloads}")
        print(f"Failed downloads: {failed_downloads}")
        print(f"Total files in {self.output_dir}: {len(os.listdir(self.output_dir))}")
    
    def get_market_summary(self):
        """Get current market data for top cryptocurrencies"""
        print("Getting current market data...")
        
        market_data = []
        
        # Get data for top 20 cryptocurrencies
        top_symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOGE', 'DOT', 'MATIC',
                      'LINK', 'UNI', 'ATOM', 'LTC', 'INJ', 'OP', 'ARB', 'SEI', 'USDT', 'USDC']
        
        for symbol in top_symbols:
            if symbol in self.crypto_tickers:
                try:
                    ticker = yf.Ticker(self.crypto_tickers[symbol])
                    info = ticker.info
                    
                    market_data.append({
                        'symbol': symbol,
                        'name': info.get('longName', symbol),
                        'price': info.get('currentPrice', 0),
                        'market_cap': info.get('marketCap', 0),
                        'volume': info.get('volume', 0),
                        'change_24h': info.get('regularMarketChangePercent', 0)
                    })
                    
                except Exception as e:
                    print(f"Error getting info for {symbol}: {e}")
        
        if market_data:
            df = pd.DataFrame(market_data)
            df = df.sort_values('market_cap', ascending=False)
            
            print("\nTop cryptocurrencies by market cap:")
            print(df.to_string(index=False))
            
            # Save market summary
            summary_path = os.path.join(self.output_dir, 'yahoo_market_summary.csv')
            df.to_csv(summary_path, index=False)
            print(f"\nMarket summary saved to {summary_path}")
        
        return market_data

def main():
    downloader = YahooCryptoDownloader()
    
    # Get market summary first
    downloader.get_market_summary()
    
    # Download historical data
    print("\nStarting historical data download...")
    downloader.download_all_crypto_data(
        days_back=365,    # 1 year of data
        batch_size=10     # Process in batches of 10
    )

if __name__ == "__main__":
    main() 