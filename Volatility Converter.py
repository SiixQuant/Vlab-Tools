import datetime
from datetime import date
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry

class VolatilityConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Volatility Converter")
        
        # Create and set up the main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Conversion type dropdown
        ttk.Label(self.main_frame, text="Conversion Type *").grid(row=0, column=0, sticky=tk.W)
        self.conversion_type = ttk.Combobox(self.main_frame, values=[
            "365-day to 252-day",
            "252-day to 365-day"
        ])
        self.conversion_type.grid(row=0, column=1, pady=5, sticky=tk.W)
        self.conversion_type.current(0)
        
        # Trade date picker
        ttk.Label(self.main_frame, text="Trade Date *").grid(row=1, column=0, sticky=tk.W)
        self.trade_date = DateEntry(self.main_frame, width=12, date_pattern='yyyy-mm-dd')
        self.trade_date.grid(row=1, column=1, pady=5, sticky=tk.W)
        
        # Expiry date picker
        ttk.Label(self.main_frame, text="Expiry *").grid(row=2, column=0, sticky=tk.W)
        self.expiry_date = DateEntry(self.main_frame, width=12, date_pattern='yyyy-mm-dd')
        self.expiry_date.grid(row=2, column=1, pady=5, sticky=tk.W)
        
        # Volatility input
        ttk.Label(self.main_frame, text="Expiry ATF volatility (%) *").grid(row=3, column=0, sticky=tk.W)
        self.volatility = ttk.Entry(self.main_frame)
        self.volatility.grid(row=3, column=1, pady=5, sticky=tk.W)
        
        # Calculate button
        ttk.Button(self.main_frame, text="Calculate", command=self.calculate).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Result label
        self.result_label = ttk.Label(self.main_frame, text="")
        self.result_label.grid(row=5, column=0, columnspan=2, pady=5)

    def calculate(self):
        try:
            # Get input values
            vol = float(self.volatility.get()) / 100  # Convert percentage to decimal
            trade_date = self.trade_date.get_date()
            expiry_date = self.expiry_date.get_date()
            
            # Calculate conversion
            if self.conversion_type.get() == "365-day to 252-day":
                result = vol * (252/365)**0.5
            else:
                result = vol * (365/252)**0.5
            
            # Display result
            self.result_label.config(text=f"Converted Volatility: {result*100:.2f}%")
            
        except ValueError:
            self.result_label.config(text="Please enter valid numbers")
        except Exception as e:
            self.result_label.config(text=f"Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VolatilityConverter(root)
    root.mainloop()
