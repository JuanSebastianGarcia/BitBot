from datetime import datetime, timedelta
import logging

class EndpointGenerator:

    parameters = {
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 1000,
        "startTime": 1719859200000
    }

    def __init__(self, initial_date: datetime, end_date: datetime):
        self.link = "https://www.binance.com/api/v3/uiKlines"
        self.logger = logging.getLogger(__name__)
        self.initial_date = initial_date
        self.end_date = end_date

    def generate_dates(self):
        """
        Generates a list of Unix timestamps in milliseconds for each day from January 1st, 2025
        to October 20th, 2025 at 1 AM.
        
        Returns:
            list: List of Unix timestamps in milliseconds
        """
        dates = []
        start_date = self.initial_date
        end_date = self.end_date
        
        current_date = start_date
        
        while current_date <= end_date:
            # Convert to Unix timestamp in milliseconds
            timestamp = int(current_date.timestamp() * 1000)
            dates.append(timestamp)
            # Move to next day
            current_date += timedelta(days=1)
        
        
        return dates

    def generate_url(self, start_time):
        """
        Generates a URL with the specified start time.
        
        Args:
            start_time (int): Unix timestamp in milliseconds
            
        Returns:
            str: Complete URL with parameters
        """
        params = self.parameters.copy()
        params["startTime"] = start_time
        
        # Build URL with query parameters
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{self.link}?{param_string}"
        
        return url

    def main(self):
        """
        Generates a list of URLs with different start times for each day.
        
        Returns:
            list: List of complete URLs
        """
        url_list = []
        
        # Generate dates
        dates = self.generate_dates()
        
        # Generate URL for each date
        for date in dates:
            url = self.generate_url(date)
            url_list.append(url)
    
        self.logger.info(f"Generated {len(url_list)} URLs")
        return url_list



if __name__ == "__main__":
    endpoint_generator = EndpointGenerator()
    endpoint_generator.main()