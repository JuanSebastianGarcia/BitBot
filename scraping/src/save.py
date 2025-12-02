import pandas as pd
import os
from typing import List, Dict, Any
import logging

class Saver:

    def __init__(self, file_path: str):
        """
        Initialize the Saver class.
        
        Args:
            file_path: Path to the CSV file where data will be saved
        """
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)

    def _ensure_directory_exists(self, directory_path: str):
        """
        Ensure the directory exists, creating it if necessary.
        
        Args:
            directory_path: Path to the directory
        """
        if directory_path and not os.path.exists(directory_path):
            os.makedirs(directory_path)

    def main(self, data: pd.DataFrame):
        """
        Main method to save data to CSV file using DataFrame.
        
        Args:
            data: List of dictionaries containing processed candle data
        """
        
        # Convert to DataFrame
        df = data
        
        # Create datetime column for sorting
        df['datetime'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora_inicial'])
        
        # Sort by date and time
        df = df.sort_values('datetime')
        
        # Drop the temporary datetime column
        df = df.drop(columns=['datetime'])
        
        # Ensure directory exists
        self._ensure_directory_exists(os.path.dirname(self.file_path))
        
        # Save to CSV
        df.to_csv(self.file_path, index=False, encoding='utf-8')
        self.logger.info(f"Data successfully saved to {self.file_path}") 