import pandas as pd
import os
import logging


class Grouper:

    def __init__(
        self,
        candle_size_to_traing: int = 5,
        candle_to_predict: int = 5,
        percentage_return_threshold: float = 0.0001,
    ):
        """
        Initialize Grouper with configuration parameters.
        
        Args:
            candle_size_to_traing: Number of candles to use for training
            candle_to_predict: Offset for the candle to predict
            percentage_return_threshold: Threshold for bullish classification
        """
        self.logger = logging.getLogger(__name__)
        self.candle_size_to_traing = candle_size_to_traing
        self.candle_to_predict = candle_to_predict
        self.percentage_return_threshold = percentage_return_threshold
        
        self.logger.info(
            f"Initializing Grouper with candle_size_to_traing={candle_size_to_traing}, "
            f"candle_to_predict={candle_to_predict}, "
            f"percentage_return_threshold={percentage_return_threshold}"
        )
        self.data = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        """
        Load data from CSV file.
        
        Returns:
            DataFrame with loaded data
        """
        self.logger.info("Loading data from CSV file")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, '../../scraping/data', 'bitcoin_candles.csv')
        
        data = pd.read_csv(file_path)
        self.logger.info(f"Data loaded successfully. Shape: {data.shape}, Columns: {len(data.columns)}")
        return data

    def _create_groups(self) -> list:
        """
        Create groups of candles (optimized version).
        Returns tuples of indices instead of heavy DataFrames.
        
        Returns:
            List of tuples (train_indices_range, predict_index)
        """
        self.logger.info("Creating groups of candles")

        n = len(self.data)
        window = self.candle_size_to_traing
        future = self.candle_to_predict

        max_index = n - window - future
        self.logger.info(f"Total data rows: {n}, Max groups to create: {max_index}")

        groups = [
            (range(i, i + window), i + window + future - 1)
            for i in range(max_index)
        ]

        self.logger.info(f"Created {len(groups)} groups successfully")
        return groups

    def _extract_candle_features(self, candle: pd.Series, position: int) -> dict:
        """
        Extract features from a single candle.
        
        Args:
            candle: Series representing a candle
            position: Position of the candle in the group
            
        Returns:
            Dictionary with candle features
        """
        vela_string = str(position)
        return {
            f"entrada_vela_{vela_string}": candle['entrada_vela_1'],
            f"salida_vela_{vela_string}": candle['salida_vela_1'],
            f"Max_vela_{vela_string}": candle['Max_vela_1'],
            f"Min_vela_{vela_string}": candle['Min_vela_1'],
            f"porcentaje_retorno_vela_{vela_string}": candle['porcentaje_retorno_vela_1'],
        }

    def _process_group(self, train_indices: range, predict_index: int) -> dict:
        """
        Process a single group to create a data row.
        
        Args:
            train_indices: Range of indices for training candles
            predict_index: Index of the candle to predict
            
        Returns:
            Dictionary representing a processed data row
        """
        train_candles = self.data.iloc[list(train_indices)]
        predict_candle = self.data.iloc[predict_index]

        data_row = {}
        for position, idx in enumerate(train_indices, start=1):
            candle = self.data.iloc[idx]
            features = self._extract_candle_features(candle, position)
            data_row.update(features)

        data_row = self._calculate_dates(data_row, train_candles)
        data_row = self._calculate_predict_candle(data_row, predict_candle)

        return data_row

    def _create_dataframe_from_groups(self, groups: list) -> pd.DataFrame:
        """
        Create a dataframe from groups of candles.
        
        Args:
            groups: List of group tuples (train_indices, predict_index)
            
        Returns:
            DataFrame with processed groups
        """
        self.logger.info(f"Creating dataframe from {len(groups)} groups")
        data_final = []
        
        for idx, (train_indices, predict_index) in enumerate(groups):
            data_row = self._process_group(train_indices, predict_index)
            data_final.append(data_row)
            
            if (idx + 1) % 10000 == 0:
                self.logger.info(f"Processed {idx + 1}/{len(groups)} groups")

        dataframe = pd.DataFrame(data_final)
        self.logger.info(
            f"Dataframe created successfully. Shape: {dataframe.shape}, "
            f"Columns: {len(dataframe.columns)}"
        )
        return dataframe

    def _calculate_predict_candle(self, data_row: dict, predict_candle: pd.Series) -> dict:
        """
        Calculate prediction candle target variable.
        
        Args:
            data_row: Dictionary with data row information
            predict_candle: Series representing the candle to predict
            
        Returns:
            Updated data_row with is_alcista classification
        """
        last_candle_position = self.candle_size_to_traing
        last_price = data_row[f'salida_vela_{last_candle_position}']
        predict_price = predict_candle['entrada_vela_1']
        return_percentage = (predict_price - last_price) / last_price
        
        data_row['is_alcista'] = 1 if return_percentage > self.percentage_return_threshold else 0
        return data_row

    def _calculate_dates(self, data_row: dict, train_candles: pd.DataFrame) -> dict:
        """
        Calculate dates from data row.
        
        Args:
            data_row: Dictionary with data row information
            train_candles: DataFrame with training candles
            
        Returns:
            Updated data_row with date information
        """
        first_candle = train_candles.iloc[0]
        data_row['fecha'] = first_candle['fecha']
        data_row['hora_inicial'] = first_candle['hora_inicial']
        data_row['hora_final'] = first_candle['hora_final']
        data_row['dia'] = first_candle['dia']
        data_row['mes'] = first_candle['mes']
        data_row['anio'] = first_candle['anio']
        data_row['dia_semana'] = first_candle['dia_semana']
        return data_row

    def _save_data(self, dataframe: pd.DataFrame) -> None:
        """
        Save dataframe to CSV file.
        
        Args:
            dataframe: DataFrame to save
        """
        self.logger.info("Saving dataframe to CSV file")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, '../data', 'data_grouped.csv')
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        dataframe.to_csv(file_path, index=False)
        self.logger.info(f"Data saved successfully to {file_path}")


    def _create_date_column(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Create a date column from the fecha column.
        """
        dataframe['date'] = pd.to_datetime(dataframe['fecha'].astype(str) + ' ' + dataframe['hora_inicial'])
        return dataframe



    def main(self) -> None:
        """
        Main method to group candles into consecutive groups of specified size.
        """
        self.logger.info("Starting main grouping process")
        groups = self._create_groups()
        dataframe = self._create_dataframe_from_groups(groups)
        dataframe = self._create_date_column(dataframe)
        self._save_data(dataframe)
        self.logger.info("Main grouping process completed successfully")

        self.logger.info(f"class 1: {dataframe[dataframe['is_alcista'] == 1]['is_alcista'].value_counts()}")
        self.logger.info(f"class 0: {dataframe[dataframe['is_alcista'] == 0]['is_alcista'].value_counts()}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    grouper = Grouper()
    grouper.main()
