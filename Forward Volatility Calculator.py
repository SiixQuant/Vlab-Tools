import numpy as np
import pandas as pd
from datetime import datetime

class ImpliedForwardVolCalculator:
    def __init__(self):
        """Initialize the calculator"""
        pass
    
    def _calculate_days_between(self, date1: datetime, date2: datetime) -> float:
        """Calculate business days between two dates"""
        # Convert strings to datetime if needed
        if isinstance(date1, str):
            date1 = datetime.strptime(date1, '%Y-%m-%d')
        if isinstance(date2, str):
            date2 = datetime.strptime(date2, '%Y-%m-%d')
        
        return (date2 - date1).days  # Could be enhanced to use business days
    
    def calculate_forward_variance(self, vol1: float, date1, vol2: float, date2, trade_date=None) -> float:
        """
        Calculate forward variance between two time periods
        
        Parameters:
        - vol1: Volatility of first period (in percentage form, e.g. 40 for 40%)
        - date1: First expiry date (datetime or string 'YYYY-MM-DD')
        - vol2: Volatility of second period (in percentage form)
        - date2: Second expiry date (datetime or string 'YYYY-MM-DD')
        - trade_date: Optional trade date (defaults to today)
        """
        # Convert percentage volatilities to decimal form
        vol1 = vol1 / 100
        vol2 = vol2 / 100
        
        # Handle date conversions
        if isinstance(date1, str):
            date1 = datetime.strptime(date1, '%Y-%m-%d')
        if isinstance(date2, str):
            date2 = datetime.strptime(date2, '%Y-%m-%d')
        
        trade_date = trade_date or datetime.now()
        if isinstance(trade_date, str):
            trade_date = datetime.strptime(trade_date, '%Y-%m-%d')
        
        t1 = self._calculate_days_between(trade_date, date1)
        t2 = self._calculate_days_between(trade_date, date2)
        
        if t2 <= t1:
            raise ValueError("Second expiry must be after first expiry")
            
        # Convert volatilities to variance (vol squared)
        var1 = vol1 * vol1
        var2 = vol2 * vol2
        
        # Calculate total variance for each period
        total_var1 = var1 * t1
        total_var2 = var2 * t2
        
        # Calculate forward variance
        forward_var = (total_var2 - total_var1) / (t2 - t1)
        
        return forward_var
    
    def calculate_forward_vol(self, vol1: float, date1, vol2: float, date2, trade_date=None) -> float:
        """
        Calculate forward volatility between two time periods
        
        Parameters:
        - vol1: Volatility of first period (in percentage form, e.g. 40 for 40%)
        - date1: First expiry date (datetime or string 'YYYY-MM-DD')
        - vol2: Volatility of second period (in percentage form)
        - date2: Second expiry date (datetime or string 'YYYY-MM-DD')
        - trade_date: Optional trade date (defaults to today)
        """
        # Handle date conversions
        if isinstance(date1, str):
            date1 = datetime.strptime(date1, '%Y-%m-%d')
        if isinstance(date2, str):
            date2 = datetime.strptime(date2, '%Y-%m-%d')
        
        if trade_date and isinstance(trade_date, str):
            trade_date = datetime.strptime(trade_date, '%Y-%m-%d')
        
        forward_var = self.calculate_forward_variance(vol1, date1, vol2, date2, trade_date)
        return np.sqrt(forward_var)
    
    def create_forward_vol_matrix(self, expiries: list, vols: list) -> pd.DataFrame:
        """
        Create a matrix of forward volatilities for all expiry combinations
        
        Parameters:
        - expiries: List of expiry dates (datetime or string 'YYYY-MM-DD')
        - vols: List of corresponding volatilities (in percentage form)
        
        Returns:
        - DataFrame containing forward volatilities
        """
        n = len(expiries)
        matrix = np.zeros((n, n))
        
        # Convert expiries to datetime if they're strings
        expiry_dates = []
        for expiry in expiries:
            if isinstance(expiry, str):
                expiry_dates.append(datetime.strptime(expiry, '%Y-%m-%d'))
            else:
                expiry_dates.append(expiry)
        
        # Fill the matrix
        for i in range(n):
            for j in range(i+1, n):
                forward_vol = self.calculate_forward_vol(
                    vols[i], expiry_dates[i],
                    vols[j], expiry_dates[j]
                )
                matrix[i][j] = forward_vol
        
        # Create DataFrame with labeled axes
        df = pd.DataFrame(
            matrix,
            index=[expiry.strftime('%Y-%m-%d') for expiry in expiry_dates],
            columns=[expiry.strftime('%Y-%m-%d') for expiry in expiry_dates]
        )
        
        return df

# Example usage
if __name__ == "__main__":
    calc = ImpliedForwardVolCalculator()
    
    # Example with dates
    trade_date = datetime(2024, 3, 1)
    expiry1 = datetime(2024, 3, 21)
    expiry2 = datetime(2024, 3, 31)
    
    fwd_vol = calc.calculate_forward_vol(
        vol1=40,  # 40%
        date1=expiry1,
        vol2=42,  # 42%
        date2=expiry2,
        trade_date=trade_date
    )
    print(f"Forward volatility: {fwd_vol:.1%}")
    
    # Create full matrix of forward vols
    expiries = ['2024-03-21', '2024-03-31', '2024-04-30', '2024-05-31']
    vols = [40, 42, 44, 46]  # percentages
    matrix = calc.create_forward_vol_matrix(expiries, vols)
    print("\nForward Volatility Matrix:")
    print(matrix)
