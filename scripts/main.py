import sys
import os
import schedule
import time
from datetime import datetime
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from fetch_news import NewsFetcher
from analyze_sentiment import SentimentAnalyzer
from trade import CryptoTrader
from notify import EmailNotifier
from visualize import PortfolioVisualizer

class CryptoTradingBot:
    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.trader = CryptoTrader()
        self.notifier = EmailNotifier()
        self.visualizer = PortfolioVisualizer()
        
    def execute_trading_cycle(self):
        """Execute one complete trading cycle."""
        try:
            print(f"\nStarting trading cycle at {datetime.now()}")
            
            # 1. Fetch news data
            print("Fetching news data...")
            news_data = self.news_fetcher.get_latest_news()
            
            if news_data.empty:
                raise Exception("No news data retrieved")
                
            # 2. Analyze sentiment
            print("Analyzing sentiment...")
            sentiment_results = self.sentiment_analyzer.analyze_news_sentiment(news_data)
            
            # 3. Generate trading signals
            print("Generating trading signals...")
            trading_signals = self.sentiment_analyzer.get_trading_signals(sentiment_results)
            
            # 4. Execute trades
            print("Executing trades...")
            self.trader.execute_trades(trading_signals)
            
            # 5. Generate and send performance report
            print("Generating performance report...")
            stats = self.visualizer.generate_performance_report()
            
            # 6. Send performance update
            print("Sending performance update...")
            self.notifier.send_performance_update(
                pd.DataFrame([stats]).to_string()
            )
            
            print("Trading cycle completed successfully")
            
        except Exception as e:
            error_message = f"Error in trading cycle: {str(e)}"
            print(error_message)
            self.notifier.send_error_notification(error_message)
            
    def run(self):
        """Run the trading bot with scheduled execution."""
        print("Starting Crypto Trading Bot...")
        
        # Schedule weekly execution (every Monday at 00:00)
        schedule.every().monday.at("00:00").do(self.execute_trading_cycle)
        
        # Execute one cycle immediately on startup
        self.execute_trading_cycle()
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check schedule every minute

def setup_data_directory():
    """Create necessary directories if they don't exist."""
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/reports', exist_ok=True)

if __name__ == "__main__":
    # Setup directories
    setup_data_directory()
    
    # Create and run the trading bot
    bot = CryptoTradingBot()
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\nStopping Crypto Trading Bot...")
    except Exception as e:
        error_message = f"Critical error: {str(e)}"
        print(error_message)
        
        # Send error notification
        notifier = EmailNotifier()
        notifier.send_error_notification(error_message) 