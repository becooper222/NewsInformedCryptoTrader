# News-Informed Crypto Trader

An automated cryptocurrency trading system that uses news sentiment analysis to make informed trading decisions. The system analyzes news trends using the Perplexity AI API, performs sentiment analysis using OpenAI's models, and executes trades through the Coinbase API.

## Features

- **News Data Collection**
  - Fetches and summarizes insights on top 10 most discussed crypto entities
  - Filters for recent, high-engagement content from reliable sources
  - Stores structured news data for analysis

- **Sentiment Analysis**
  - Aggregates insights across multiple articles
  - Implements a weighted scoring system
  - Rates entities on five key sentiment categories
  - Generates comprehensive sentiment reports

- **Automated Trading**
  - Executes trades based on sentiment analysis
  - Implements stop-loss and take-profit mechanisms
  - Sends email notifications before trades
  - Maintains detailed trade history

- **Performance Visualization**
  - Interactive charts for portfolio value
  - Trade history visualization
  - Sentiment trend analysis
  - Comprehensive performance reports

## Setup

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd NewsInformedCryptoTrader
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the project root with the following variables:
   ```
   PERPLEXITY_API_KEY=your_perplexity_api_key
   OPENAI_API_KEY=your_openai_api_key
   COINBASE_API_KEY=your_coinbase_api_key
   COINBASE_API_SECRET=your_coinbase_api_secret
   EMAIL_SENDER=your_email@gmail.com
   EMAIL_PASSWORD=your_email_app_password
   EMAIL_RECIPIENT=recipient@email.com
   ```

## Usage

1. **Start the Trading Bot**
   ```bash
   python scripts/main.py
   ```
   The bot will:
   - Execute an initial trading cycle immediately
   - Schedule weekly executions (Mondays at 00:00)
   - Send email notifications for trades and errors
   - Generate performance reports

2. **View Performance Reports**
   - Check the `data/reports` directory for:
     - Portfolio value charts
     - Trade history visualizations
     - Sentiment trend analysis
     - Performance statistics

## Project Structure

```
crypto_news_trading/
│── data/                  # Stores CSV files and reports
│── scripts/
│   │── fetch_news.py      # News data collection
│   │── analyze_sentiment.py # Sentiment analysis
│   │── trade.py           # Trade execution
│   │── notify.py          # Email notifications
│   │── visualize.py       # Performance visualization
│   │── main.py           # Main orchestration
│── config.py             # Configuration settings
│── requirements.txt      # Project dependencies
│── README.md            # Project documentation
```

## Configuration

Edit `config.py` to modify:
- Trading parameters (amount, stop-loss, take-profit)
- News analysis settings
- Email notification preferences
- File paths and storage locations

## Safety Features

- Email notifications before trade execution
- Stop-loss and take-profit mechanisms
- Error handling and notifications
- Detailed logging and trade history

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Cryptocurrency trading carries significant risks. Use this system at your own risk. The authors are not responsible for any financial losses incurred while using this system. 