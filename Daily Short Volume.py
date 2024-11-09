import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
import os
import webbrowser
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShortVolumeTracker:
    def __init__(self):
        try:
            self.console = Console()
            logger.info("Initializing ShortVolumeTracker")
            self.symbols = {
                'IGV': 'iShares Expand Tech-STW Sect',
                'JBLU': 'JetBlue Airways Corp',
                'PLTR': 'Palantir Technologies Inc',
                'QQQ': 'QQQQ Trust Nasdaq 100',
                'SPY': 'SPDR S&P500 ETF',
                'TSLA': 'Tesla Inc',
                'USHY': 'iShares US High Yld Corp',
                'VOO': 'Vanguard S&P 500',
                'XLE': 'Energy Select SPDR Fund',
                'XLF': 'SPDR Financial Select Sector',
                'XLV': 'Health Care Select SPDR Fund'
            }
            self.data_dir = "historical_data"
            os.makedirs(self.data_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error in initialization: {str(e)}")
            raise

    def fetch_stock_data(self, symbol, days=5):
        """Fetch stock data from Yahoo Finance"""
        try:
            # Add some buffer days for market closures
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days + 5)
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            # Get short data
            short_data = ticker.info.get('sharesShort', 0)
            short_ratio = ticker.info.get('shortRatio', 0)
            
            return df, short_data, short_ratio
            
        except Exception as e:
            self.console.print(f"Error fetching data for {symbol}: {str(e)}", style="red")
            return None, None, None

    def process_daily_data(self, days=5):
        """Process last N days of data"""
        all_data = []
        
        for symbol, name in self.symbols.items():
            df, short_data, short_ratio = self.fetch_stock_data(symbol, days)
            if df is not None and not df.empty:
                # Get last N trading days
                df = df.tail(days)
                
                for date, row in df.iterrows():
                    volume = row['Volume']
                    # Estimate short volume using volume and short ratio
                    estimated_short = int(volume * (short_ratio / 100) if short_ratio else volume * 0.3)
                    bought = estimated_short
                    sold = volume - bought
                    buy_ratio = round(bought/sold, 2) if sold > 0 else 0
                    
                    # Calculate dark pools percentage (estimated)
                    dark_pools = round((volume * 0.15), 1)  # Assuming ~15% dark pool activity
                    
                    all_data.append({
                        'Date': date.strftime("%Y%m%d"),
                        'Symbol': symbol,
                        'Name': name,
                        'Bought': bought,
                        '%Avg': round((bought/volume)*100, 1) if volume > 0 else 0,
                        'Sold': sold,
                        'Buy Ratio': buy_ratio,
                        'Total': volume,
                        'Dark Pools': round((dark_pools/volume)*100, 1) if volume > 0 else 0
                    })
        
        return pd.DataFrame(all_data)

    def create_rich_table(self, df):
        """Create a formatted Rich table"""
        table = Table(title="Daily Trading Volume Analysis")
        
        # Add columns
        columns = ['Date', 'Symbol', 'Name', 'Bought', '%Avg', 'Sold', 'Buy Ratio', 'Total', 'Dark Pools']
        for col in columns:
            table.add_column(col, justify="right")

        # Calculate average buy ratios per symbol
        symbol_groups = df.groupby('Symbol')
        avg_buy_ratios = symbol_groups['Buy Ratio'].mean()

        # Add rows with conditional formatting
        for _, row in df.iterrows():
            avg_ratio = avg_buy_ratios[row['Symbol']]
            style = "green" if row['Buy Ratio'] > avg_ratio else "red"
            
            table.add_row(
                str(row['Date']),
                row['Symbol'],
                row['Name'],
                f"{row['Bought']:,.0f}",
                f"{row['%Avg']}%",
                f"{row['Sold']:,.0f}",
                f"{row['Buy Ratio']:.2f}",
                f"{row['Total']:,.0f}",
                f"{row['Dark Pools']}%",
                style=style
            )

        return table

    def export_data(self, df, format='csv'):
        """Export data to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if format == 'csv':
            filename = f"trading_volume_data_{timestamp}.csv"
            df.to_csv(filename, index=False)
        elif format == 'excel':
            filename = f"trading_volume_data_{timestamp}.xlsx"
            df.to_excel(filename, index=False)
        self.console.print(f"Data exported to {filename}", style="green")

    def generate_html(self, df):
        """Generate HTML content similar to the original image"""
        
        # Calculate averages for color coding
        symbol_groups = df.groupby('Symbol')
        avg_buy_ratios = symbol_groups['Buy Ratio'].mean()

        # HTML template with dark theme
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    background-color: #1a1a1a;
                    color: #ffffff;
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }
                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }
                .title {
                    font-size: 18px;
                    font-weight: bold;
                }
                .date {
                    color: #888;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                th {
                    background-color: #2d2d2d;
                    padding: 8px;
                    text-align: right;
                    border-bottom: 1px solid #444;
                }
                td {
                    padding: 8px;
                    text-align: right;
                    border-bottom: 1px solid #333;
                }
                .symbol-group {
                    background-color: #2d2d2d;
                }
                .symbol-header {
                    font-size: 16px;
                    padding: 5px;
                    background-color: #2d2d2d;
                }
                .positive {
                    color: #00ff00;
                }
                .negative {
                    color: #ff4444;
                }
                .summary {
                    margin-top: 20px;
                    padding: 10px;
                    background-color: #2d2d2d;
                    border-radius: 5px;
                }
                .dark-pools {
                    color: #00ff00;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">Daily Institutional Short Sale Volume</div>
                <div class="date">Last Update: """ + datetime.now().strftime("%m/%d/%Y") + """</div>
            </div>
        """

        # Add table
        html_content += """
            <table>
                <tr>
                    <th>Date</th>
                    <th>Symbol</th>
                    <th>Name</th>
                    <th>Bought</th>
                    <th>%Avg</th>
                    <th>Sold</th>
                    <th>Buy Ratio</th>
                    <th>Total</th>
                    <th>Dark Pools</th>
                </tr>
        """

        # Group by symbol for better organization
        for symbol in df['Symbol'].unique():
            symbol_data = df[df['Symbol'] == symbol]
            avg_ratio = avg_buy_ratios[symbol]
            
            # Add symbol group header
            html_content += f"""
                <tr class="symbol-group">
                    <td colspan="9" class="symbol-header">{symbol}</td>
                </tr>
            """
            
            for _, row in symbol_data.iterrows():
                ratio_class = "positive" if row['Buy Ratio'] > avg_ratio else "negative"
                html_content += f"""
                    <tr>
                        <td>{row['Date']}</td>
                        <td>{row['Symbol']}</td>
                        <td>{row['Name']}</td>
                        <td>{row['Bought']:,.0f}</td>
                        <td>{row['%Avg']}%</td>
                        <td>{row['Sold']:,.0f}</td>
                        <td class="{ratio_class}">{row['Buy Ratio']:.2f}</td>
                        <td>{row['Total']:,.0f}</td>
                        <td class="dark-pools">{row['Dark Pools']}%</td>
                    </tr>
                """

        # Add summary statistics
        total_volume = df['Total'].sum()
        total_bought = df['Bought'].sum()
        total_sold = df['Sold'].sum()
        avg_total_volume = total_volume / len(df['Symbol'].unique())
        avg_buy_ratio = round(total_bought / total_sold, 2) if total_sold > 0 else 0

        html_content += f"""
            </table>
            <div class="summary">
                <div>Total Volume: {total_volume:,.0f}</div>
                <div>Total Bought: {total_bought:,.0f}</div>
                <div>Total Sold: {total_sold:,.0f}</div>
                <div>Average Total Volume: {avg_total_volume:,.0f}</div>
                <div>Average Buy-Sell Ratio: {avg_buy_ratio:.2f}</div>
            </div>
        </body>
        </html>
        """

        return html_content

    def generate_leaderboard(self, output_format='html'):
        """Generate and display the leaderboard"""
        try:
            logger.info("Starting leaderboard generation")
            df = self.process_daily_data()
            
            if df.empty:
                logger.warning("No data available")
                print("No data available")
                return
            
            logger.info("Data processed successfully")
            # Sort by date and symbol
            df = df.sort_values(['Date', 'Symbol'], ascending=[False, True])
            
            if output_format == 'html':
                # Generate HTML and save to file
                html_content = self.generate_html(df)
                html_file = "short_volume_report.html"
                
                with open(html_file, 'w') as f:
                    f.write(html_content)
                
                # Open in default browser
                webbrowser.open('file://' + os.path.realpath(html_file))
            else:
                # Export to CSV/Excel as before
                self.export_data(df, output_format)
        except Exception as e:
            logger.error(f"Error generating leaderboard: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        logger.info("Starting application")
        tracker = ShortVolumeTracker()
        tracker.generate_leaderboard(output_format='html')
        logger.info("Application completed successfully")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)
