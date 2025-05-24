import yfinance as yf
import pandas as pd
import os


class YfRequester:
    """
    A class to fetch financial data using the yfinance library.
    """

    def fetch_historical_data(
        self, ticker: str, start_date=None, end_date=None
    ) -> pd.DataFrame | None:
        """
        Fetches historical data for a given ticker and date range.

        Args:
            ticker: The stock ticker symbol (e.g., "AAPL").
            start_date: The start date in "YYYY-MM-DD" format.
            end_date: The end date in "YYYY-MM-DD" format.

        Returns:
            A pandas DataFrame containing the historical data, or None if fetching fails.
        """
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None


def save_data_to_csv(data: pd.DataFrame, filename: str):
    """
    Saves a pandas DataFrame to a CSV file in the ./csv_outputs directory.

    Args:
        data: The pandas DataFrame to save.
        filename: The name of the output CSV file (e.g., "AAPL_historical.csv").
    """
    output_dir = "./csv_outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    filepath = os.path.join(output_dir, filename)
    try:
        data.to_csv(filepath)
        print(f"Data successfully saved to {filepath}")
        return filepath, filename
    except Exception as e:
        print(f"Error saving data to {filepath}: {e}")


if __name__ == "__main__":
    # Example usage:
    requester = YfRequester()
    ticker_symbol = "MSFT"
    start = "2023-01-01"
    end = "2023-12-31"

    historical_data = requester.fetch_historical_data(ticker_symbol, start, end)

    if historical_data is not None:
        save_data_to_csv(historical_data, f"{ticker_symbol}_historical.csv")
