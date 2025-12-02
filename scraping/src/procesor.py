from datetime import datetime
from typing import List, Dict, Any
import logging
import pandas as pd

class Procesor:

    def __init__(self, candle_size: int = 5):
        self.candle_size = candle_size
        self.logger = logging.getLogger(__name__)
        
    def _extract_candles_from_responses(
        self, 
        responses: List[Any]
    ) -> List[List[Any]]:
        """
        Extract candle data from API responses.
        
        Args:
            responses: List of response dictionaries or lists from the API
            
        Returns:
            Flat list of all candles from all responses
        """
        all_candles = []
        for response in responses:
            # Handle different possible response structures
            if isinstance(response, list):
                # Binance API returns a list of candles directly
                candles = response
            elif isinstance(response, dict) and 'data' in response:
                candles = response['data']
            elif isinstance(response, dict):
                # If dict, try to get the first list value
                for value in response.values():
                    if isinstance(value, list):
                        candles = value
                        break
                else:
                    continue
            else:
                continue
                
            if isinstance(candles, list):
                all_candles.extend(candles)
        
        return all_candles

    def _convert_timestamp_to_readable(
        self, 
        timestamp: int
    ) -> tuple[str, str, str]:
        """
        Convert Unix timestamp to readable date and time formats.
        
        Args:
            timestamp: Unix timestamp in milliseconds
            
        Returns:
            Tuple of (date, initial_time, final_time as readable strings)
        """
        dt = datetime.fromtimestamp(timestamp / 1000)
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M:%S")
        return date_str, time_str, time_str

    def _calculate_return_percentage(
        self, 
        open_price: float, 
        close_price: float
    ) -> float:
        """
        Calculate percentage return for a candle.
        
        Args:
            open_price: Opening price of the candle
            close_price: Closing price of the candle
            
        Returns:
            Percentage return value
        """
        if open_price == 0:
            return 0.0
        return ((close_price - open_price) / open_price) * 100

    def _process_candle_group(
        self, 
        candle_group: List[List[Any]]
    ) -> Dict[str, Any]:
        """
        Process a group of 5 candles and extract required data.
        
        Args:
            candle_group: List of 5 candle data arrays
            
        Returns:
            Dictionary containing processed candle data
        """
        if len(candle_group) != self.candle_size:
            raise ValueError("Candle group must contain exactly 5 candles")
        
        # Extract data from first candle
        first_candle = candle_group[0]
        last_candle = candle_group[-1]
        
        date, initial_time, _ = self._convert_timestamp_to_readable(first_candle[0])
        _, _, final_time = self._convert_timestamp_to_readable(last_candle[0])
        
        result = {
            "fecha": date,
            "hora_inicial": initial_time,
            "hora_final": final_time
        }
        
        # Process each of the 5 candles
        for i, candle in enumerate(candle_group, start=1):
            open_price = float(candle[1])
            max_price = float(candle[2])
            min_price = float(candle[3])
            close_price = float(candle[4])
            
            # Add candle data
            result[f"entrada_vela_{i}"] = open_price
            result[f"salida_vela_{i}"] = close_price
            result[f"Max_vela_{i}"] = max_price
            result[f"Min_vela_{i}"] = min_price
            
            # Calculate return percentage
            return_pct = self._calculate_return_percentage(open_price, close_price)
            result[f"porcentaje_retorno_vela_{i}"] = round(return_pct, 4)
        
        return result

    def _group_candles(
        self, 
        candles: List[List[Any]], 
    ) -> List[List[List[Any]]]:
        """
        Group candles into consecutive groups of specified size.
        
        Args:
            candles: List of all candles
            
        Returns:
            List of candle groups
        """
        groups = []
        for i in range(0, len(candles) - self.candle_size + 1, self.candle_size):
            group = candles[i:i + self.candle_size]
            groups.append(group)
        return groups

    def main(
        self, 
        responses: List[Any]
    ) -> pd.DataFrame:
        """
        Main method to process candle data and extract 5-candle groups.
        
        Processes API responses containing Bitcoin price candles,
        groups them into consecutive sets of 5, and extracts required metrics.
        
        Args:
            responses: List of response dictionaries from the API
            
        Returns:
            List of processed candle groups with extracted metrics
        """

        # Extract all candles from responses
        candles = self._extract_candles_from_responses(responses)
        
        # Group candles into sets of 5
        candle_groups = self._group_candles(candles)
        
        # Process each group
        processed_groups = []
        for group in candle_groups:
            try:
                processed_group = self._process_candle_group(group)
                processed_groups.append(processed_group)
            except (ValueError, IndexError, TypeError) as e:
                # Log error and continue with next group
                print(f"Error processing candle group: {e}")
                continue

        self.logger.info(f"Processed {len(processed_groups)} candle groups")

        processed_data = pd.DataFrame(processed_groups)
        return processed_data