import sys
import os
import pandas as pd
import openai
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class SentimentScores(BaseModel):
    sentiment_score: float = Field(..., ge=0, le=100, description="Score from 0 (Extremely Negative) to 100 (Extremely Positive)")
    objectivity_score: float = Field(..., ge=0, le=100, description="Score from 0 (Highly Subjective) to 100 (Completely Objective)")
    agreement_score: float = Field(..., ge=0, le=100, description="Score from 0 (Strong Disagreement) to 100 (Strong Agreement)")
    confidence_score: float = Field(..., ge=0, le=100, description="Score from 0 (Highly Uncertain) to 100 (Extremely Confident)")
    credibility_score: float = Field(..., ge=0, le=100, description="Score from 0 (Not Credible) to 100 (Highly Credible)")
    entity: str
    symbol: str
    timestamp: datetime

class SentimentAnalyzer:
    def __init__(self):
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        
    def _generate_sentiment_schema(self) -> Dict:
        """Generate the JSON schema for structured sentiment analysis output."""
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "sentiment_analysis",
                "description": "Sentiment analysis scores for cryptocurrency news",
                "schema": {
                    "type": "object",
                    "properties": {
                        "sentiment_score": {
                            "type": "number",
                            "description": "Score from 0 (Extremely Negative) to 100 (Extremely Positive)",
                            "minimum": 0,
                            "maximum": 100
                        },
                        "objectivity_score": {
                            "type": "number",
                            "description": "Score from 0 (Highly Subjective) to 100 (Completely Objective)",
                            "minimum": 0,
                            "maximum": 100
                        },
                        "agreement_score": {
                            "type": "number",
                            "description": "Score from 0 (Strong Disagreement) to 100 (Strong Agreement)",
                            "minimum": 0,
                            "maximum": 100
                        },
                        "confidence_score": {
                            "type": "number",
                            "description": "Score from 0 (Highly Uncertain) to 100 (Extremely Confident)",
                            "minimum": 0,
                            "maximum": 100
                        },
                        "credibility_score": {
                            "type": "number",
                            "description": "Score from 0 (Not Credible) to 100 (Highly Credible)",
                            "minimum": 0,
                            "maximum": 100
                        }
                    },
                    "required": [
                        "sentiment_score",
                        "objectivity_score",
                        "agreement_score",
                        "confidence_score",
                        "credibility_score"
                    ],
                    "additionalProperties": False
                },
                "strict": True
            }
        }

    def analyze_entity_sentiment(self, entity_data: Dict) -> Optional[Dict]:
        """Analyze sentiment for a single entity using OpenAI with structured output."""
        try:
            system_prompt = """You are a cryptocurrency market analyst specializing in sentiment analysis.
            Your task is to analyze news data and provide numerical scores (0-100) for different sentiment dimensions.
            Focus on factual information and market trends. Be precise and consistent in your scoring."""
            
            user_prompt = f"""Analyze this cryptocurrency news for {entity_data['entity']} ({entity_data['symbol']}).

            Key Points:
            {' '.join(entity_data['key_points'])}

            Market Sentiment: {entity_data['market_sentiment']}
            Volume Change: {entity_data['volume_change']}

            Provide numerical scores (0-100) for:
            - Sentiment: How positive/negative is the overall sentiment?
            - Objectivity: How factual vs opinion-based is the information?
            - Agreement: How consistent are different sources/opinions?
            - Confidence: How certain/reliable are the statements?
            - Credibility: How trustworthy are the sources?"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using gpt-4o-mini model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=self._generate_sentiment_schema(),
                temperature=0.2  # Lower temperature for more consistent scoring
            )
            
            # Handle potential refusal or content filter
            if hasattr(response.choices[0].message, 'refusal'):
                print(f"Model refused to analyze {entity_data['entity']}: {response.choices[0].message.refusal}")
                return None
                
            if response.choices[0].finish_reason == "content_filter":
                print(f"Content filter triggered for {entity_data['entity']}")
                return None
                
            # Extract and validate scores
            if response.choices[0].message.content:
                try:
                    scores = eval(response.choices[0].message.content)
                    scores.update({
                        'entity': entity_data['entity'],
                        'symbol': entity_data['symbol'],
                        'timestamp': datetime.now()
                    })
                    # Validate using Pydantic model
                    validated_scores = SentimentScores(**scores)
                    return validated_scores.dict()
                except Exception as e:
                    print(f"Error parsing scores for {entity_data['entity']}: {str(e)}")
                    return None
            
            return None
            
        except Exception as e:
            print(f"Error analyzing sentiment for {entity_data['entity']}: {str(e)}")
            return None

    def analyze_news_sentiment(self, news_df: pd.DataFrame) -> pd.DataFrame:
        """Process sentiment analysis for all entities in the news data."""
        sentiment_results = []
        
        for _, row in news_df.iterrows():
            entity_sentiment = self.analyze_entity_sentiment(row.to_dict())
            if entity_sentiment:
                sentiment_results.append(entity_sentiment)
        
        # Convert results to DataFrame
        sentiment_df = pd.DataFrame(sentiment_results)
        
        if not sentiment_df.empty:
            # Save sentiment analysis results
            sentiment_df.to_csv(config.SENTIMENT_DATA_FILE, index=False)
        
        return sentiment_df

    def get_trading_signals(self, sentiment_df: pd.DataFrame) -> Dict[str, List[str]]:
        """Generate trading signals based on sentiment analysis."""
        if sentiment_df.empty:
            return {'buy': [], 'sell': []}
            
        # Calculate composite score (weighted average of all sentiment categories)
        weights = {
            'sentiment_score': 0.3,
            'objectivity_score': 0.2,
            'agreement_score': 0.2,
            'confidence_score': 0.15,
            'credibility_score': 0.15
        }
        
        sentiment_df['composite_score'] = sum(
            sentiment_df[col] * weight 
            for col, weight in weights.items()
        )
        
        # Sort by composite score
        sorted_df = sentiment_df.sort_values('composite_score', ascending=False)
        
        return {
            'buy': sorted_df.head(config.TOP_ENTITIES_TO_BUY)['symbol'].tolist(),
            'sell': sorted_df.tail(config.BOTTOM_ENTITIES_TO_SELL)['symbol'].tolist()
        }

if __name__ == "__main__":
    from fetch_news import NewsFetcher
    
    # Test the sentiment analysis pipeline
    fetcher = NewsFetcher()
    news_data = fetcher.get_latest_news()
    
    if not news_data.empty:
        analyzer = SentimentAnalyzer()
        sentiment_results = analyzer.analyze_news_sentiment(news_data)
        trading_signals = analyzer.get_trading_signals(sentiment_results)
        
        print("\nTrading Signals:")
        print(f"Buy: {', '.join(trading_signals['buy'])}")
        print(f"Sell: {', '.join(trading_signals['sell'])}")
        
        # Print sample sentiment scores
        if not sentiment_results.empty:
            print("\nSample Sentiment Analysis:")
            print(sentiment_results.iloc[0].to_dict()) 