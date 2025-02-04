import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class EmailNotifier:
    def __init__(self):
        self.sender_email = config.EMAIL_SENDER
        self.sender_password = config.EMAIL_PASSWORD
        self.recipient_email = config.EMAIL_RECIPIENT
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        
    def _send_email(self, subject: str, body: str):
        """Send an email using SMTP."""
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            message["Subject"] = subject
            
            # Add body
            message.attach(MIMEText(body, "plain"))
            
            # Create SMTP session
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
                
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            
    def send_trade_notification(self, symbol: str, action: str, amount_usd: float, price: float):
        """Send a notification about an upcoming trade."""
        subject = f"Crypto Trade Alert: {action.upper()} {symbol}"
        
        body = f"""
        Trade Details:
        --------------
        Action: {action.upper()}
        Symbol: {symbol}
        Amount: ${amount_usd:.2f} USD
        Price: ${price:.2f}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        This trade will be executed shortly.
        """
        
        self._send_email(subject, body)
        
    def send_error_notification(self, error_message: str):
        """Send a notification about an error."""
        subject = "Crypto Trading Bot Error Alert"
        
        body = f"""
        Error Details:
        --------------
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Error: {error_message}
        
        Please check the system and take necessary action.
        """
        
        self._send_email(subject, body)
        
    def send_performance_update(self, portfolio_summary: str):
        """Send a periodic performance update."""
        subject = "Crypto Trading Bot Performance Update"
        
        body = f"""
        Portfolio Summary:
        -----------------
        {portfolio_summary}
        
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        self._send_email(subject, body)
        
    def send_sentiment_trade_notification(
        self,
        trade_date: str,
        buy_pairs: list,  # List of (symbol, score) tuples
        sell_pairs: list,  # List of (symbol, score) tuples
        stop_loss_percentage: float,
        take_profit_percentage: float,
        portfolio_balance: float
    ):
        """Send a notification about trades based on sentiment analysis."""
        subject = "Crypto Trading Bot - Sentiment-Based Trade Alert"
        
        # Format buy and sell entries
        buy_1, buy_1_score = buy_pairs[0] if len(buy_pairs) > 0 else ("N/A", "N/A")
        buy_2, buy_2_score = buy_pairs[1] if len(buy_pairs) > 1 else ("N/A", "N/A")
        buy_3, buy_3_score = buy_pairs[2] if len(buy_pairs) > 2 else ("N/A", "N/A")
        
        sell_1, sell_1_score = sell_pairs[0] if len(sell_pairs) > 0 else ("N/A", "N/A")
        sell_2, sell_2_score = sell_pairs[1] if len(sell_pairs) > 1 else ("N/A", "N/A")
        sell_3, sell_3_score = sell_pairs[2] if len(sell_pairs) > 2 else ("N/A", "N/A")
        
        body = f"""Hello,

Your automated crypto trading algorithm has identified the following trades based on the latest sentiment analysis of news trends.

📅 **Trade Execution Date:** {trade_date}

🔹 **Top 3 Buys (Most Positive Sentiment):**
1️⃣ {buy_1} – Sentiment Score: {buy_1_score}
2️⃣ {buy_2} – Sentiment Score: {buy_2_score}
3️⃣ {buy_3} – Sentiment Score: {buy_3_score}

🔻 **Top 3 Sells (Most Negative Sentiment):**
1️⃣ {sell_1} – Sentiment Score: {sell_1_score}
2️⃣ {sell_2} – Sentiment Score: {sell_2_score}
3️⃣ {sell_3} – Sentiment Score: {sell_3_score}

📊 **Trade Execution Details:**
- **Stop Loss:** {stop_loss_percentage}%
- **Take Profit:** {take_profit_percentage}%
- **Portfolio Balance Before Trade:** ${portfolio_balance:,.2f}

⚡ These trades will be executed automatically via Coinbase API. If you wish to **cancel or modify the trades**, please take action before execution.

Best,
🚀 **Crypto Trading Bot**"""

        self._send_email(subject, body)

if __name__ == "__main__":
    # Test the notification system
    notifier = EmailNotifier()
    
    # Test trade notification
    notifier.send_trade_notification(
        symbol="BTC",
        action="buy",
        amount_usd=1000.0,
        price=50000.0
    )
    
    # Test error notification
    notifier.send_error_notification(
        "Test error message"
    )
    
    # Test performance update
    notifier.send_performance_update(
        "Test portfolio summary"
    ) 