import sys
import os
import pandas as pd
from coinbase.wallet.client import Client
from datetime import datetime
from typing import Dict, List, Optional
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from notify import EmailNotifier

class CryptoTrader:
    def __init__(self):
        self.client = Client(config.COINBASE_API_KEY, config.COINBASE_API_SECRET)
        self.notifier = EmailNotifier()
        self.trade_history = self._load_trade_history()
        
    def _load_trade_history(self) -> pd.DataFrame:
        """Load or create trade history DataFrame."""
        if os.path.exists(config.TRADE_HISTORY_FILE):
            return pd.read_csv(config.TRADE_HISTORY_FILE)
        return pd.DataFrame(columns=[
            'timestamp', 'symbol', 'action', 'amount_usd', 
            'crypto_amount', 'price', 'status'
        ])
        
    def _save_trade_history(self):
        """Save trade history to CSV file."""
        self.trade_history.to_csv(config.TRADE_HISTORY_FILE, index=False)
        
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a cryptocurrency."""
        try:
            ticker = self.client.get_spot_price(currency_pair=f'{symbol}-USD')
            return float(ticker.amount)
        except Exception as e:
            print(f"Error getting price for {symbol}: {str(e)}")
            return None
            
    def _place_order(self, symbol: str, action: str, amount_usd: float) -> Dict:
        """Place a buy or sell order."""
        try:
            # Get current price
            price = self._get_current_price(symbol)
            if not price:
                return None
                
            # Calculate crypto amount
            crypto_amount = amount_usd / price
            
            # Send notification
            self.notifier.send_trade_notification(
                symbol=symbol,
                action=action,
                amount_usd=amount_usd,
                price=price
            )
            
            # Place order
            if action == 'buy':
                order = self.client.buy(
                    amount=str(amount_usd),
                    currency_pair=f'{symbol}-USD',
                    payment_method='usd_wallet'
                )
            else:  # sell
                order = self.client.sell(
                    amount=str(crypto_amount),
                    currency_pair=f'{symbol}-USD',
                    payment_method='usd_wallet'
                )
            
            # Record trade
            trade_record = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'action': action,
                'amount_usd': amount_usd,
                'crypto_amount': crypto_amount,
                'price': price,
                'status': 'completed'
            }
            self.trade_history = pd.concat([
                self.trade_history,
                pd.DataFrame([trade_record])
            ], ignore_index=True)
            self._save_trade_history()
            
            return order
            
        except Exception as e:
            print(f"Error placing {action} order for {symbol}: {str(e)}")
            return None
            
    def _check_stop_loss_take_profit(self):
        """Check and execute stop-loss and take-profit orders."""
        recent_buys = self.trade_history[
            (self.trade_history['action'] == 'buy') &
            (self.trade_history['status'] == 'completed')
        ].copy()
        
        for _, trade in recent_buys.iterrows():
            current_price = self._get_current_price(trade['symbol'])
            if not current_price:
                continue
                
            purchase_price = trade['price']
            price_change = ((current_price - purchase_price) / purchase_price) * 100
            
            # Check stop-loss
            if price_change <= -config.STOP_LOSS_PERCENTAGE:
                self._place_order(
                    trade['symbol'],
                    'sell',
                    trade['amount_usd'] * (current_price / purchase_price)
                )
                
            # Check take-profit
            elif price_change >= config.TAKE_PROFIT_PERCENTAGE:
                self._place_order(
                    trade['symbol'],
                    'sell',
                    trade['amount_usd'] * (current_price / purchase_price)
                )
                
    def execute_trades(self, trading_signals: Dict[str, List[str]]):
        """Execute trades based on trading signals."""
        # First, check stop-loss and take-profit conditions
        self._check_stop_loss_take_profit()
        
        # Execute new trades
        for symbol in trading_signals['buy']:
            self._place_order(symbol, 'buy', config.TRADE_AMOUNT_USD)
            time.sleep(1)  # Rate limiting
            
        for symbol in trading_signals['sell']:
            # Check if we own the asset
            try:
                account = self.client.get_account(f'{symbol}-USD')
                if float(account.balance.amount) > 0:
                    self._place_order(symbol, 'sell', config.TRADE_AMOUNT_USD)
                    time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"Error checking balance for {symbol}: {str(e)}")
                
    def get_portfolio_summary(self) -> pd.DataFrame:
        """Get current portfolio summary."""
        accounts = self.client.get_accounts()
        portfolio = []
        
        for account in accounts.data:
            if float(account.balance.amount) > 0:
                portfolio.append({
                    'symbol': account.currency,
                    'balance': float(account.balance.amount),
                    'value_usd': float(account.native_balance.amount)
                })
                
        return pd.DataFrame(portfolio)

if __name__ == "__main__":
    from analyze_sentiment import SentimentAnalyzer
    from fetch_news import NewsFetcher
    
    # Test the trading pipeline
    fetcher = NewsFetcher()
    news_data = fetcher.get_latest_news()
    
    if not news_data.empty:
        analyzer = SentimentAnalyzer()
        sentiment_results = analyzer.analyze_news_sentiment(news_data)
        trading_signals = analyzer.get_trading_signals(sentiment_results)
        
        trader = CryptoTrader()
        trader.execute_trades(trading_signals)
        
        # Print portfolio summary
        portfolio = trader.get_portfolio_summary()
        print("\nCurrent Portfolio:")
        print(portfolio) 