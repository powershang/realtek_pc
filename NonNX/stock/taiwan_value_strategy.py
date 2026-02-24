#!/usr/bin/env python3
"""
Taiwan Stock Valuation Strategy Backtesting Script

Requirements.txt:
yfinance==0.2.18
pandas==2.0.3
numpy==1.24.3
matplotlib==3.7.1
seaborn==0.12.2
pyyaml==6.0
twstock==1.3.1
argparse
"""

import os
import sys
import argparse
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
import yaml
from pathlib import Path

# Suppress warnings
warnings.filterwarnings('ignore')

# Configuration
PE_BANDS = {
    "2330": (20, 23),
    "3034": (15, 17),
    "2884": (15, 17),
    "2886": (14, 16),
    "2891": (14, 16),
    "2892": (14, 16),
    "5871": (11, 13),
}

PB_BANDS = {  # Only for financial stocks
    "2884": (1.6, 1.8),
    "2886": (1.4, 1.6),
    "2891": (1.4, 1.6),
    "2892": (1.4, 1.6),
}

DEFAULT_CONFIG = {
    'tickers': ['2330', '2884', '2886', '2891', '2892', '3034', '5871'],
    'benchmark': '^TWII',
    'start_date': '2014-01-01',
    'end_date': '2025-07-10',
    'initial_cash': 1_000_000,
    'rebalance_month': 7,
    'rebalance_day': 1,
    'pe_bands': PE_BANDS,
    'pb_bands': PB_BANDS,
    'buy_threshold': 0.9,
    'sell_threshold': 1.1,
}


class TaiwanValueStrategy:
    """Taiwan Stock Valuation Strategy Backtesting System"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the strategy with configuration"""
        self.config = config
        self.tickers = config['tickers']
        self.benchmark = config['benchmark']
        self.start_date = config['start_date']
        self.end_date = config['end_date']
        self.initial_cash = config['initial_cash']
        self.pe_bands = config['pe_bands']
        self.pb_bands = config['pb_bands']
        self.buy_threshold = config['buy_threshold']
        self.sell_threshold = config['sell_threshold']
        
        # Initialize data containers
        self.stock_data = {}
        self.benchmark_data = None
        self.fundamentals_data = None
        self.trades = []
        self.portfolio_value = []
        self.holdings = {}
        self.cash = self.initial_cash
        
    def fetch_data(self) -> None:
        """Fetch stock price data using yfinance with Taiwan stock suffix"""
        print("Fetching stock data...")
        
        # Add .TW suffix for Taiwan stocks
        tw_tickers = [f"{ticker}.TW" for ticker in self.tickers]
        
        try:
            # Fetch stock data
            for i, ticker in enumerate(tw_tickers):
                print(f"Fetching {ticker}...")
                stock = yf.Ticker(ticker)
                hist = stock.history(start=self.start_date, end=self.end_date)
                
                if hist.empty:
                    print(f"Warning: No data found for {ticker}")
                    continue
                    
                # Store with original ticker name (without .TW)
                self.stock_data[self.tickers[i]] = hist
                
            # Fetch benchmark data
            print(f"Fetching benchmark {self.benchmark}...")
            benchmark = yf.Ticker(self.benchmark)
            self.benchmark_data = benchmark.history(start=self.start_date, end=self.end_date)
            
            # Handle missing data
            self._handle_missing_data()
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            print("Consider using alternative data sources like twstock")
            
    def _handle_missing_data(self) -> None:
        """Handle missing data by forward filling"""
        for ticker in self.stock_data:
            if not self.stock_data[ticker].empty:
                self.stock_data[ticker].fillna(method='ffill', inplace=True)
                self.stock_data[ticker].dropna(inplace=True)
                
    def load_fundamentals(self) -> pd.DataFrame:
        """Load EPS and BVPS forecast data from CSV"""
        csv_path = Path('eps_forecast.csv')
        
        if not csv_path.exists():
            print("Creating sample eps_forecast.csv...")
            self._create_sample_eps_data()
            
        try:
            df = pd.read_csv(csv_path)
            df['date'] = pd.to_datetime(df['date'])
            self.fundamentals_data = df
            print(f"Loaded {len(df)} fundamental data records")
            return df
            
        except Exception as e:
            print(f"Error loading fundamentals: {e}")
            return pd.DataFrame()
            
    def _create_sample_eps_data(self) -> None:
        """Create sample EPS forecast data for demonstration"""
        # Note: In real usage, update this CSV from TEJ/Bloomberg API
        sample_data = []
        
        # Generate sample data for each year and ticker
        for year in range(2014, 2026):
            for ticker in self.tickers:
                # Sample EPS values (these should be real forecast data)
                base_eps = {
                    '2330': 15.0, '2884': 2.5, '2886': 2.0, '2891': 2.2,
                    '2892': 2.1, '3034': 8.0, '5871': 12.0
                }
                
                base_bvps = {
                    '2330': 50.0, '2884': 18.0, '2886': 15.0, '2891': 16.0,
                    '2892': 15.5, '3034': 80.0, '5871': 120.0
                }
                
                # Add some random variation
                eps_variation = np.random.uniform(0.8, 1.2)
                bvps_variation = np.random.uniform(0.9, 1.1)
                
                sample_data.append({
                    'date': f'{year}-06-30',
                    'ticker': ticker,
                    'eps_next_fy': base_eps[ticker] * eps_variation,
                    'bvps_now': base_bvps[ticker] * bvps_variation
                })
                
        df = pd.DataFrame(sample_data)
        df.to_csv('eps_forecast.csv', index=False)
        print("Sample eps_forecast.csv created")
        
    def generate_signals(self, date: datetime, ticker: str) -> str:
        """Generate buy/hold/sell signals based on valuation bands"""
        try:
            # Get current price
            price_data = self.stock_data[ticker]
            current_price = price_data.loc[price_data.index <= date, 'Close'].iloc[-1]
            
            # Get latest fundamental data
            fund_data = self.fundamentals_data[
                (self.fundamentals_data['ticker'] == ticker) & 
                (self.fundamentals_data['date'] <= date)
            ]
            
            if fund_data.empty:
                return 'hold'
                
            latest_fund = fund_data.iloc[-1]
            eps_next = latest_fund['eps_next_fy']
            bvps_now = latest_fund['bvps_now']
            
            # Calculate valuation bands
            pe_lower, pe_upper = self.pe_bands.get(ticker, (15, 18))
            pb_lower, pb_upper = self.pb_bands.get(ticker, (1.0, 2.0))
            
            # Calculate fair value range
            pe_lower_price = pe_lower * eps_next
            pe_upper_price = pe_upper * eps_next
            
            if ticker in self.pb_bands:
                # For financial stocks, use max of PE and PB
                pb_lower_price = pb_lower * bvps_now
                pb_upper_price = pb_upper * bvps_now
                
                fair_value_lower = max(pe_lower_price, pb_lower_price)
                fair_value_upper = max(pe_upper_price, pb_upper_price)
            else:
                fair_value_lower = pe_lower_price
                fair_value_upper = pe_upper_price
            
            # Generate signals
            if current_price <= fair_value_lower * self.buy_threshold:
                return 'buy'
            elif current_price >= fair_value_upper * self.sell_threshold:
                return 'sell'
            else:
                return 'hold'
                
        except Exception as e:
            print(f"Error generating signal for {ticker} on {date}: {e}")
            return 'hold'
            
    def backtest(self) -> None:
        """Run the backtest with annual rebalancing"""
        print("Starting backtest...")
        
        # Get rebalance dates (first trading day of July each year)
        rebalance_dates = self._get_rebalance_dates()
        
        # Initialize portfolio tracking
        portfolio_values = []
        benchmark_values = []
        
        for i, rebalance_date in enumerate(rebalance_dates):
            print(f"Rebalancing on {rebalance_date.strftime('%Y-%m-%d')}")
            
            # Generate signals for all tickers
            signals = {}
            for ticker in self.tickers:
                if ticker in self.stock_data and not self.stock_data[ticker].empty:
                    signals[ticker] = self.generate_signals(rebalance_date, ticker)
                    
            # Execute trades
            self._execute_rebalance(rebalance_date, signals)
            
            # Calculate portfolio value over the holding period
            if i < len(rebalance_dates) - 1:
                next_date = rebalance_dates[i + 1]
            else:
                next_date = pd.to_datetime(self.end_date)
                
            period_values = self._calculate_period_values(rebalance_date, next_date)
            portfolio_values.extend(period_values)
            
        # Store results
        self.portfolio_value = portfolio_values
        
    def _get_rebalance_dates(self) -> List[datetime]:
        """Get rebalance dates (first trading day of July each year)"""
        dates = []
        start_year = pd.to_datetime(self.start_date).year
        end_year = pd.to_datetime(self.end_date).year
        
        for year in range(start_year, end_year + 1):
            # Try to find first trading day of July
            july_first = pd.to_datetime(f'{year}-07-01')
            
            # Check if we have benchmark data for this date
            if self.benchmark_data is not None:
                trading_days = self.benchmark_data.index
                valid_days = trading_days[trading_days >= july_first]
                
                if len(valid_days) > 0:
                    dates.append(valid_days[0])
                    
        return dates
        
    def _execute_rebalance(self, date: datetime, signals: Dict[str, str]) -> None:
        """Execute rebalancing trades"""
        # Clear all current positions
        for ticker in list(self.holdings.keys()):
            if ticker in self.stock_data and date in self.stock_data[ticker].index:
                price = self.stock_data[ticker].loc[date, 'Close']
                shares = self.holdings[ticker]
                self.cash += shares * price
                
                # Record trade
                self.trades.append({
                    'date': date,
                    'ticker': ticker,
                    'action': 'sell',
                    'price': price,
                    'shares': shares,
                    'reason': 'rebalance'
                })
                
        # Clear holdings
        self.holdings = {}
        
        # Calculate new positions
        buy_signals = [ticker for ticker, signal in signals.items() if signal == 'buy']
        
        if buy_signals:
            # Equal weight allocation
            weight_per_stock = 1.0 / len(buy_signals)
            cash_per_stock = self.cash * weight_per_stock
            
            for ticker in buy_signals:
                if ticker in self.stock_data and date in self.stock_data[ticker].index:
                    price = self.stock_data[ticker].loc[date, 'Close']
                    shares = int(cash_per_stock / price)
                    
                    if shares > 0:
                        cost = shares * price
                        self.cash -= cost
                        self.holdings[ticker] = shares
                        
                        # Record trade
                        self.trades.append({
                            'date': date,
                            'ticker': ticker,
                            'action': 'buy',
                            'price': price,
                            'shares': shares,
                            'reason': signals[ticker]
                        })
                        
    def _calculate_period_values(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Calculate portfolio values over a period"""
        values = []
        
        # Get all trading days in the period
        if self.benchmark_data is not None:
            trading_days = self.benchmark_data.index
            period_days = trading_days[(trading_days >= start_date) & (trading_days <= end_date)]
            
            for date in period_days:
                # Calculate portfolio value
                portfolio_value = self.cash
                
                for ticker, shares in self.holdings.items():
                    if ticker in self.stock_data and date in self.stock_data[ticker].index:
                        price = self.stock_data[ticker].loc[date, 'Close']
                        portfolio_value += shares * price
                        
                # Get benchmark value
                benchmark_value = None
                if date in self.benchmark_data.index:
                    benchmark_value = self.benchmark_data.loc[date, 'Close']
                    
                values.append({
                    'date': date,
                    'portfolio_value': portfolio_value,
                    'benchmark_value': benchmark_value
                })
                
        return values
        
    def analyze_performance(self) -> Dict[str, float]:
        """Analyze strategy performance and generate reports"""
        print("Analyzing performance...")
        
        if not self.portfolio_value:
            print("No portfolio data available")
            return {}
            
        # Convert to DataFrame
        df = pd.DataFrame(self.portfolio_value)
        df.set_index('date', inplace=True)
        
        # Calculate returns
        df['portfolio_return'] = df['portfolio_value'].pct_change()
        df['benchmark_return'] = df['benchmark_value'].pct_change()
        
        # Calculate cumulative returns
        df['portfolio_cumret'] = (1 + df['portfolio_return']).cumprod()
        df['benchmark_cumret'] = (1 + df['benchmark_return']).cumprod()
        
        # Calculate performance metrics
        metrics = self._calculate_metrics(df)
        
        # Generate plots
        self._plot_performance(df)
        self._plot_allocation()
        
        # Save trades
        self._save_trades()
        
        # Save performance summary
        self._save_performance_summary(metrics)
        
        return metrics
        
    def _calculate_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate performance metrics"""
        portfolio_returns = df['portfolio_return'].dropna()
        benchmark_returns = df['benchmark_return'].dropna()
        
        # Calculate CAGR
        total_return = (df['portfolio_value'].iloc[-1] / df['portfolio_value'].iloc[0]) - 1
        years = len(df) / 252  # Approximate trading days per year
        cagr = (1 + total_return) ** (1/years) - 1
        
        # Calculate benchmark CAGR
        bench_total_return = (df['benchmark_value'].iloc[-1] / df['benchmark_value'].iloc[0]) - 1
        bench_cagr = (1 + bench_total_return) ** (1/years) - 1
        
        # Calculate maximum drawdown
        cumulative = df['portfolio_cumret']
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Calculate volatility and Sharpe ratio
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = cagr / volatility if volatility != 0 else 0
        
        # Calculate win rate
        win_rate = (portfolio_returns > 0).mean()
        
        metrics = {
            'CAGR': cagr,
            'Benchmark_CAGR': bench_cagr,
            'Max_Drawdown': max_drawdown,
            'Volatility': volatility,
            'Sharpe_Ratio': sharpe_ratio,
            'Win_Rate': win_rate,
            'Total_Return': total_return,
            'Benchmark_Total_Return': bench_total_return
        }
        
        return metrics
        
    def _plot_performance(self, df: pd.DataFrame) -> None:
        """Plot performance comparison"""
        plt.figure(figsize=(12, 8))
        
        # Plot cumulative returns
        plt.subplot(2, 1, 1)
        plt.plot(df.index, df['portfolio_cumret'], label='Strategy', linewidth=2)
        plt.plot(df.index, df['benchmark_cumret'], label='Benchmark (^TWII)', linewidth=2)
        plt.title('Cumulative Returns Comparison')
        plt.legend()
        plt.grid(True)
        
        # Plot drawdown
        plt.subplot(2, 1, 2)
        cumulative = df['portfolio_cumret']
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        plt.fill_between(df.index, drawdown, 0, alpha=0.3, color='red')
        plt.plot(df.index, drawdown, color='red')
        plt.title('Strategy Drawdown')
        plt.ylabel('Drawdown')
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('performance_chart.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def _plot_allocation(self) -> None:
        """Plot asset allocation over time"""
        if not self.trades:
            return
            
        # Group trades by year
        trades_df = pd.DataFrame(self.trades)
        trades_df['year'] = pd.to_datetime(trades_df['date']).dt.year
        
        # Get buy trades for each year
        buy_trades = trades_df[trades_df['action'] == 'buy']
        
        if buy_trades.empty:
            return
            
        # Calculate allocation by year
        allocation_by_year = {}
        for year in buy_trades['year'].unique():
            year_trades = buy_trades[buy_trades['year'] == year]
            total_value = (year_trades['price'] * year_trades['shares']).sum()
            
            allocations = {}
            for ticker in year_trades['ticker'].unique():
                ticker_trades = year_trades[year_trades['ticker'] == ticker]
                ticker_value = (ticker_trades['price'] * ticker_trades['shares']).sum()
                allocations[ticker] = ticker_value / total_value
                
            allocation_by_year[year] = allocations
            
        # Plot allocation
        if allocation_by_year:
            plt.figure(figsize=(12, 6))
            
            years = list(allocation_by_year.keys())
            tickers = list(set().union(*[alloc.keys() for alloc in allocation_by_year.values()]))
            
            bottom = np.zeros(len(years))
            
            for ticker in tickers:
                values = [allocation_by_year[year].get(ticker, 0) for year in years]
                plt.bar(years, values, bottom=bottom, label=ticker)
                bottom += values
                
            plt.title('Asset Allocation by Year (July Rebalance)')
            plt.xlabel('Year')
            plt.ylabel('Allocation Weight')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('allocation_chart.png', dpi=300, bbox_inches='tight')
            plt.show()
            
    def _save_trades(self) -> None:
        """Save trading records to CSV"""
        if self.trades:
            trades_df = pd.DataFrame(self.trades)
            trades_df.to_csv('trades.csv', index=False)
            print("Trades saved to trades.csv")
            
    def _save_performance_summary(self, metrics: Dict[str, float]) -> None:
        """Save performance summary to text file"""
        with open('performance_summary.txt', 'w') as f:
            f.write("Taiwan Value Strategy Performance Summary\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Strategy CAGR: {metrics['CAGR']:.2%}\n")
            f.write(f"Benchmark CAGR: {metrics['Benchmark_CAGR']:.2%}\n")
            f.write(f"Excess Return: {metrics['CAGR'] - metrics['Benchmark_CAGR']:.2%}\n\n")
            
            f.write(f"Total Return: {metrics['Total_Return']:.2%}\n")
            f.write(f"Benchmark Total Return: {metrics['Benchmark_Total_Return']:.2%}\n\n")
            
            f.write(f"Maximum Drawdown: {metrics['Max_Drawdown']:.2%}\n")
            f.write(f"Volatility: {metrics['Volatility']:.2%}\n")
            f.write(f"Sharpe Ratio: {metrics['Sharpe_Ratio']:.2f}\n")
            f.write(f"Win Rate: {metrics['Win_Rate']:.2%}\n\n")
            
            f.write(f"Number of Trades: {len(self.trades)}\n")
            
        print("Performance summary saved to performance_summary.txt")
        
        # Print summary to console
        print("\n" + "=" * 50)
        print("PERFORMANCE SUMMARY")
        print("=" * 50)
        print(f"Strategy CAGR: {metrics['CAGR']:.2%}")
        print(f"Benchmark CAGR: {metrics['Benchmark_CAGR']:.2%}")
        print(f"Excess Return: {metrics['CAGR'] - metrics['Benchmark_CAGR']:.2%}")
        print(f"Max Drawdown: {metrics['Max_Drawdown']:.2%}")
        print(f"Sharpe Ratio: {metrics['Sharpe_Ratio']:.2f}")
        print(f"Win Rate: {metrics['Win_Rate']:.2%}")
        print(f"Total Trades: {len(self.trades)}")
        print("=" * 50)


def load_config(config_path: str = 'config.yml') -> Dict[str, Any]:
    """Load configuration from YAML file"""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return {**DEFAULT_CONFIG, **config}
    else:
        # Create default config file
        with open(config_path, 'w') as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
        print(f"Created default config file: {config_path}")
        return DEFAULT_CONFIG


def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(description='Taiwan Value Strategy Backtest')
    parser.add_argument('--start', type=str, default='2014-01-01',
                        help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default='2025-07-10',
                        help='End date (YYYY-MM-DD)')
    parser.add_argument('--cash', type=float, default=1_000_000,
                        help='Initial cash amount')
    parser.add_argument('--config', type=str, default='config.yml',
                        help='Configuration file path')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override with command line arguments
    config['start_date'] = args.start
    config['end_date'] = args.end
    config['initial_cash'] = args.cash
    
    # Initialize and run strategy
    strategy = TaiwanValueStrategy(config)
    
    # Fetch data
    strategy.fetch_data()
    
    # Load fundamentals
    strategy.load_fundamentals()
    
    # Run backtest
    strategy.backtest()
    
    # Analyze performance
    metrics = strategy.analyze_performance()
    
    return strategy, metrics


if __name__ == "__main__":
    print("Taiwan Value Strategy Backtest")
    print("=" * 50)
    
    # Run example backtest
    strategy, metrics = main()
    
    print("\nBacktest completed successfully!")
    print("Check the following outputs:")
    print("- performance_chart.png: Performance comparison chart")
    print("- allocation_chart.png: Asset allocation by year")
    print("- trades.csv: Detailed trading records")
    print("- performance_summary.txt: Performance metrics summary")
    print("- config.yml: Configuration file (created if not exists)")
    print("- eps_forecast.csv: EPS forecast data (sample created if not exists)") 