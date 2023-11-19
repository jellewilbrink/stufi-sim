import pandas as pd
from datetime import datetime, timedelta

class LoanScenario():
    def __init__(self, L0, B0, LC, R, start_year, end_year) -> None:
        # Setup initial variables/parameters

        self.calculated = False

        # Setup dataframe

        # Generate a list of dates for all months between start and end year
        date_range = [datetime(year, month, 1) for year in range(start_year, end_year + 1) for month in range(1, 13)]

        # Create a DataFrame with the Date column
        self.df = pd.DataFrame({'Date': date_range})

        # Convert 'Date' column to Pandas datetime object
        self.df['Date'] = pd.to_datetime(self.df['Date'])

        # Add other columns with NaN values
        self.df['R'] = [0.0] * len(self.df)
        self.df['LC'] = [0.0] * len(self.df)
        self.df['L'] = [0.0] * len(self.df)
        self.df['B'] = [0.0] * len(self.df)

        # Set each cell in the 'R' column equal to a variable called R
        self.df['R'] = R
        self.df['LC'] = LC

        # Set the initial values for 'L' and 'B'
        self.df.at[0, 'L'] = L0
        self.df.at[0, 'B'] = B0

    def calculate(self):
        if self.calculated:
            # Don't calculate twice
            return
        else:
            self.calculated = True
        
        # Calculate time difference in years between each row of 'Date'
        self.df['TimeDifference'] = self.df['Date'].diff() / pd.to_timedelta(1, unit='days')
        days_in_year = 365.25
        self.df['PartOfYear'] =self.df['TimeDifference']/days_in_year

        self.df['r'] = (1.0 + (self.df["R"]/100)) ** (self.df['PartOfYear'])


        self.df.fillna(0, inplace=True)
        self.df = self.calculate_L(self.df)
        self.df = self.calculate_B(self.df)        


    @staticmethod
    def calculate_L(df):
        for i in range(1, len(df)):
            df.at[i, 'L'] = (df.at[i - 1, 'L'] - df.at[i, 'LC']) * df.at[i, 'r']

        # Loan cannot be less than 0
        df["L"] = df["L"].apply(lambda x: 0 if x < 0 else x)
        return df
    
    @staticmethod
    def calculate_B(df):
        for i in range(1, len(df)):
            df.at[i, 'B'] = df.at[i - 1, 'B'] + df.at[i, 'LC']
        return df