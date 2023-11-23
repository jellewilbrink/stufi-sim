import pandas as pd
from datetime import datetime, timedelta


class LoanScenario:
    def __init__(
        self,
        L0: float,
        B0: float,
        start_year: int,
        end_year: int,
        LC_dict: dict[int, float],
        BC_dict: dict[int, float],
        R_dict: dict[int, float],
    ) -> None:
        # Setup initial variables/parameters
        self.calculated = False

        # Store the input variables
        self.L0 = L0
        self.B0 = B0
        self.start_year = start_year
        self.end_year = end_year
        self.LC_dict = LC_dict
        self.BC_dict = BC_dict
        self.R_dict = R_dict

        # Setup dataframe

        # Generate a list of dates for all months between start and end year
        date_range = [
            datetime(year, month, 1)
            for year in range(start_year, end_year + 1)
            for month in range(1, 13)
        ]

        # Create a DataFrame with the Date column
        self.df = pd.DataFrame({"Date": date_range})

        # Convert 'Date' column to Pandas datetime object
        self.df["Date"] = pd.to_datetime(self.df["Date"])

        # Add the R column
        self.df = self.fill_column_by_date(self.df, column="R", values_dict=R_dict)
        # Add the LC column
        self.df = self.fill_column_by_date(self.df, column="LC", values_dict=LC_dict)
        # Add the BC column
        self.df = self.fill_column_by_date(self.df, column="BC", values_dict=BC_dict)

        # Add L and B columns
        self.df["L"] = [0.0] * len(self.df)
        self.df["B"] = [0.0] * len(self.df)
        self.df.at[0, "L"] = L0
        self.df.at[0, "B"] = B0

    def calculate(self):
        if self.calculated:
            # Don't calculate twice
            return
        else:
            self.calculated = True

        # Calculate time difference in years between each row of 'Date'
        self.df["TimeDifference"] = self.df["Date"].diff() / pd.to_timedelta(
            1, unit="days"
        )
        days_in_year = 365.25
        self.df["PartOfYear"] = self.df["TimeDifference"] / days_in_year

        self.df["r"] = (1.0 + (self.df["R"] / 100)) ** (self.df["PartOfYear"])

        self.df.fillna(0, inplace=True)
        self.df = self.calculate_L(self.df)
        self.df = self.calculate_B(self.df)

    def get_total_interest(self):
        """
        Calculate the total interest paid:
        L_end_date - (L0 + sum(LC))

        Returns:
        float: total interest paid, if self.calculated = True, else returns 0.
        """
        if not self.calculated:
            return 0.0

        # Don't count the last row , because that is only added to L in the next month
        LC_total = self.df["LC"].sum() - self.df["LC"].iloc[-1]
        L_total = self.df["L"].iloc[-1]        
        total_interest = L_total - (self.L0 + LC_total)
        
        return total_interest

    @staticmethod
    def calculate_L(df):
        for i in range(1, len(df)):
            df.at[i, "L"] = (df.at[i - 1, "L"] + df.at[i - 1, "LC"]) * df.at[i, "r"]

        # Loan cannot be less than 0
        df["L"] = df["L"].apply(lambda x: 0 if x < 0 else x)
        return df

    @staticmethod
    def calculate_B(df):
        for i in range(1, len(df)):
            df.at[i, "B"] = df.at[i - 1, "B"] + df.at[i - 1, "LC"] + df.at[i, "BC"]
        return df

    @staticmethod
    def fill_column_by_date(df: pd.DataFrame, column: str, values_dict: dict[int, int]):
        """
        Fill  `column` of the dataframe with values from the values_dict,
        matching values matching the 'Date' column. Use the closest earlier date for extrapolation.

        Parameters:
        - df (pd.DataFrame): DataFrame with 'Date' and 'x' columns.
        - values_dict (dict): Dictionary with dates as keys and values as values.

        Returns:
        pd.DataFrame: Updated DataFrame with the `column` filled and extrapolated.
        """
        # Convert the 'Date' column to datetime type
        df["Date"] = pd.to_datetime(df["Date"])

        # Create a new DataFrame using the provided dictionary
        values_df = pd.DataFrame(list(values_dict.items()), columns=["Date", column])
        values_df["Date"] = pd.to_datetime(values_df["Date"])

        # Merge the original DataFrame with the values DataFrame using 'Date'
        merged_df = pd.merge(df, values_df, on="Date", how="left")

        # Forward-fill missing values
        merged_df[column].ffill(inplace=True)

        # The forward filling may leave NaNs in the first rows
        # So add a 0 fill for those rows
        merged_df[column].fillna(value=0.0, inplace=True)

        return merged_df
