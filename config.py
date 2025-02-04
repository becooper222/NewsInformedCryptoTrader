import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys (to be set in .env file)
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
COINBASE_API_KEY = os.getenv('COINBASE_API_KEY')
COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET')

# Email Configuration
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Trading Configuration
TRADE_AMOUNT_USD = 100  # Amount to trade in USD
STOP_LOSS_PERCENTAGE = 5  # Stop loss at 5% below purchase price
TAKE_PROFIT_PERCENTAGE = 10  # Take profit at 10% above purchase price
TOP_ENTITIES_TO_BUY = 3
BOTTOM_ENTITIES_TO_SELL = 3

# News Analysis Configuration
NEWS_LOOKBACK_DAYS = 7
MIN_ARTICLE_ENGAGEMENT = 100  # Minimum number of engagements for an article
RELIABLE_SOURCE_DOMAINS = [
    'bloomberg.com',
    'reuters.com',
    'coindesk.com',
    'cointelegraph.com',
    'theblockcrypto.com'
]

# File Paths
DATA_DIR = 'data'
SENTIMENT_DATA_FILE = os.path.join(DATA_DIR, 'sentiment_analysis.csv')
TRADE_HISTORY_FILE = os.path.join(DATA_DIR, 'trade_history.csv')

# Sentiment Analysis Categories
SENTIMENT_CATEGORIES = [
    'sentiment_score',  # Negative to Positive
    'objectivity_score',  # Subjective to Objective
    'agreement_score',  # Strongly Disagree to Strongly Agree
    'confidence_score',  # Highly Uncertain to Extremely Confident
    'credibility_score'  # Not Credible to Highly Credible
] 