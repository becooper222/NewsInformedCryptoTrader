import sys
import os
import json
import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class NewsFetcher:
    def __init__(self):
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {config.PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
    def _generate_prompt(self) -> Dict:
        """Generate a structured prompt and parameters for Perplexity API."""
        system_prompt = """You are a cryptocurrency market analyst. Analyze and summarize news about cryptocurrencies.
        Focus on factual information, market trends, and significant developments.
        Format your response as a valid JSON array of objects."""
        
        user_prompt = """Analyze and summarize the top 10 most discussed cryptocurrency entities in the past week.
        For each entity, provide:
        1. Entity name and symbol
        2. Key news points (max 3 bullet points)
        3. Sources (with URLs)
        4. Overall market sentiment
        5. Trading volume change
        
        Format as JSON array with structure:
        {
            "entity": "string",
            "symbol": "string",
            "key_points": ["string"],
            "sources": [{"name": "string", "url": "string"}],
            "market_sentiment": "string",
            "volume_change": "string"
        }"""
        
        return {
            "model": "sonar",  # Using sonar model for better analysis
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,  # Lower temperature for more consistent output
            "top_p": 0.9,
            "search_domain_filter": config.RELIABLE_SOURCE_DOMAINS,
            "return_images": False,
            "return_related_questions": False,
            "search_recency_filter": "week",  # Limit to past week
            "frequency_penalty": 1,  # Reduce repetition
            "stream": False
        }

    def _filter_sources(self, sources: List[Dict]) -> List[Dict]:
        """Filter sources based on reliability and engagement."""
        return [
            source for source in sources
            if any(domain in source['url'].lower() for domain in config.RELIABLE_SOURCE_DOMAINS)
        ]

    def fetch_crypto_news(self) -> pd.DataFrame:
        """Fetch and process cryptocurrency news using Perplexity API."""
        try:
            # Prepare API request
            payload = self._generate_prompt()
            
            # Make API request
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            
            # Extract and parse the response
            result = response.json()
            news_data = json.loads(result['choices'][0]['message']['content'])
            
            # Convert to DataFrame
            df = pd.DataFrame(news_data)
            
            # Filter sources
            df['sources'] = df['sources'].apply(self._filter_sources)
            
            # Add timestamp
            df['timestamp'] = datetime.now()
            
            # Save raw data
            df.to_csv(os.path.join(config.DATA_DIR, 'raw_news_data.csv'), index=False)
            
            return df
            
        except Exception as e:
            print(f"Error fetching news data: {str(e)}")
            return pd.DataFrame()

    def get_latest_news(self) -> pd.DataFrame:
        """Main method to fetch and process news data."""
        df = self.fetch_crypto_news()
        
        if df.empty:
            print("No news data retrieved")
            return df
        
        # Filter out entries with no sources after filtering
        df = df[df['sources'].apply(len) > 0]
        
        # Sort by number of sources (as a proxy for importance)
        df['source_count'] = df['sources'].apply(len)
        df = df.sort_values('source_count', ascending=False).drop('source_count', axis=1)
        
        return df

if __name__ == "__main__":
    fetcher = NewsFetcher()
    news_data = fetcher.get_latest_news()
    
    if not news_data.empty:
        print(f"\nRetrieved news data for {len(news_data)} crypto entities")
        print("\nSample entity data:")
        print(news_data.iloc[0].to_dict()) 