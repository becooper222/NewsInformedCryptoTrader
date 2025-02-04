import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class PortfolioVisualizer:
    def __init__(self):
        self.trade_history = pd.read_csv(config.TRADE_HISTORY_FILE)
        self.sentiment_data = pd.read_csv(config.SENTIMENT_DATA_FILE)
        
    def plot_portfolio_value(self, save_path: str = None):
        """Create an interactive plot of portfolio value over time."""
        # Group trades by day and calculate daily portfolio value
        daily_value = self.trade_history.copy()
        daily_value['date'] = pd.to_datetime(daily_value['timestamp']).dt.date
        daily_value['value'] = daily_value['amount_usd']
        daily_value = daily_value.groupby('date')['value'].sum().cumsum()
        
        # Create figure
        fig = go.Figure()
        
        # Add portfolio value line
        fig.add_trace(go.Scatter(
            x=daily_value.index,
            y=daily_value.values,
            mode='lines+markers',
            name='Portfolio Value',
            line=dict(color='blue')
        ))
        
        # Update layout
        fig.update_layout(
            title='Portfolio Value Over Time',
            xaxis_title='Date',
            yaxis_title='Value (USD)',
            hovermode='x unified'
        )
        
        if save_path:
            fig.write_html(save_path)
        return fig
        
    def plot_trade_history(self, save_path: str = None):
        """Create an interactive plot of trade history."""
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add buy trades
        buys = self.trade_history[self.trade_history['action'] == 'buy']
        fig.add_trace(
            go.Scatter(
                x=pd.to_datetime(buys['timestamp']),
                y=buys['amount_usd'],
                mode='markers',
                name='Buy',
                marker=dict(color='green', size=10)
            ),
            secondary_y=False
        )
        
        # Add sell trades
        sells = self.trade_history[self.trade_history['action'] == 'sell']
        fig.add_trace(
            go.Scatter(
                x=pd.to_datetime(sells['timestamp']),
                y=sells['amount_usd'],
                mode='markers',
                name='Sell',
                marker=dict(color='red', size=10)
            ),
            secondary_y=False
        )
        
        # Update layout
        fig.update_layout(
            title='Trade History',
            xaxis_title='Date',
            yaxis_title='Amount (USD)',
            hovermode='x unified'
        )
        
        if save_path:
            fig.write_html(save_path)
        return fig
        
    def plot_sentiment_trends(self, save_path: str = None):
        """Create an interactive plot of sentiment trends."""
        # Calculate average sentiment scores by date
        sentiment_trends = self.sentiment_data.copy()
        sentiment_trends['date'] = pd.to_datetime(sentiment_trends['timestamp']).dt.date
        
        # Create figure
        fig = go.Figure()
        
        # Add lines for each sentiment category
        for category in config.SENTIMENT_CATEGORIES:
            daily_avg = sentiment_trends.groupby('date')[category].mean()
            fig.add_trace(go.Scatter(
                x=daily_avg.index,
                y=daily_avg.values,
                mode='lines+markers',
                name=category.replace('_', ' ').title()
            ))
            
        # Update layout
        fig.update_layout(
            title='Sentiment Trends Over Time',
            xaxis_title='Date',
            yaxis_title='Score',
            hovermode='x unified'
        )
        
        if save_path:
            fig.write_html(save_path)
        return fig
        
    def generate_performance_report(self, output_dir: str = 'data/reports'):
        """Generate a complete performance report with all visualizations."""
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate and save all plots
        self.plot_portfolio_value(
            os.path.join(output_dir, 'portfolio_value.html')
        )
        self.plot_trade_history(
            os.path.join(output_dir, 'trade_history.html')
        )
        self.plot_sentiment_trends(
            os.path.join(output_dir, 'sentiment_trends.html')
        )
        
        # Generate summary statistics
        stats = {
            'total_trades': len(self.trade_history),
            'buy_trades': len(self.trade_history[self.trade_history['action'] == 'buy']),
            'sell_trades': len(self.trade_history[self.trade_history['action'] == 'sell']),
            'total_volume_usd': self.trade_history['amount_usd'].sum(),
            'avg_trade_size_usd': self.trade_history['amount_usd'].mean()
        }
        
        # Save statistics to file
        stats_df = pd.DataFrame([stats])
        stats_df.to_csv(os.path.join(output_dir, 'performance_stats.csv'), index=False)
        
        return stats

if __name__ == "__main__":
    # Test the visualization system
    visualizer = PortfolioVisualizer()
    
    # Generate complete performance report
    stats = visualizer.generate_performance_report()
    print("\nPerformance Statistics:")
    print(stats) 