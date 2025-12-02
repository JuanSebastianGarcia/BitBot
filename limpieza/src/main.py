# -*- coding: utf-8 -*-
import pandas as pd
import os
import logging
from balance_clases import BalanceadorClases


class Cleaner:

    def __init__(self,
    file_name_to_load: str = 'data_grouped.csv',
    test_size: float = 0.2,
    include_data_time: bool = False
    ):
        self.logger = logging.getLogger(__name__)
        self.load_data(file_name_to_load)
        self.test_size = test_size
        self.include_data_time = include_data_time

    def load_data(self, file_name: str):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, '../../grouper/data', file_name)

        self.data = pd.read_csv(file_path)
        self.logger.info(f"Data loaded successfully from {file_path}")

    def main(self):

        #exploracion
        self._explore_data()

        #particion
        x_train, x_test, y_train, y_test = self.partition_data()

        self.x_train = x_train
        self.x_test = x_test
        self.y_train = y_train
        self.y_test = y_test

        #encoding categoricas
        self.encode_dia_semana_ordinal()

        #manejo de columnas temporales
        self._handle_temporal_columns()

        #balanceo de clases
        self._balance_classes()

        #save data
        self.save_data()


    from sklearn.model_selection import train_test_split

    def partition_data(
        self,
        date_column: str = "date",   # name of the time column
        random_state: int = 42
    ):
        """
        Partition the dataset into train and test sets based on chronological order.
        
        Args:
            date_column: Name of the datetime column used for sorting
            random_state: Random seed (kept for consistency in logging, unused here)
            
        Returns:
            Tuple of (x_train, x_test, y_train, y_test)
        """
        # Ensure data is sorted by time
        self.data = self.data.sort_values(by=date_column).reset_index(drop=True)
        
        # Split features and target
        y = self.data["is_alcista"]
        x = self.data.drop(columns=["is_alcista"])
        
        # Determine split index
        split_index = int(len(self.data) * (1 - self.test_size))
        
        # Chronological split (no shuffling)
        x_train, x_test = x.iloc[:split_index], x.iloc[split_index:]
        y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]
        
        self.logger.info(
            f"Dataset partitioned chronologically: "
            f"Train size = {len(x_train)}, Test size = {len(x_test)} "
            f"({self.test_size*100:.1f}% split), Features = {len(x.columns)}"
        )
        
        return x_train, x_test, y_train, y_test


        


    def encode_dia_semana_ordinal(self):
        """
        Apply ordinal encoding to dia_semana column.
        Maps days of the week to integers: Lunes=0, Martes=1, Miércoles=2, 
        Jueves=3, Viernes=4, Sábado=5, Domingo=6.
        """
        if 'dia_semana' not in self.x_train.columns:
            self.logger.warning("Column 'dia_semana' not found in data")
            return
        
        day_mapping = {
            'Lunes': 0,
            'Martes': 1,
            'Miércoles': 2,
            'Jueves': 3,
            'Viernes': 4,
            'Sábado': 5,
            'Domingo': 6
        }
        
        self.x_train['dia_semana'] = self.x_train['dia_semana'].map(day_mapping)
        self.x_test['dia_semana'] = self.x_test['dia_semana'].map(day_mapping)
        self.logger.info("Ordinal encoding applied to dia_semana column")


    def _explore_data(self):
        """Perform initial data exploration."""
        self.logger.info("Starting data exploration")
        self.logger.info(f"Data shape: {self.data.shape}")
        self.logger.info(f"Columns: {list(self.data.columns)}")
        self.logger.info(f"Data info:\n{self.data.info()}")

    def _handle_temporal_columns(self):
        """
        Handle temporal columns based on include_data_time setting.
        If include_data_time is False, removes date/time related columns.
        If include_data_time is True, keeps all columns.

        Temporal columns removed when include_data_time=False:
        - date: Date column (used for sorting)
        - fecha: Date column
        - hora_inicial: Initial time
        - hora_final: Final time
        - dia: Day of month
        - mes: Month
        - anio: Year
        - dia_semana: Day of week
        """
        if self.include_data_time:
            self.logger.info("Keeping temporal columns (include_data_time=True)")
            return

        temporal_columns = ['date', 'fecha', 'hora_inicial', 'hora_final', 'dia', 'mes', 'anio', 'dia_semana']
        columns_to_drop = [col for col in temporal_columns if col in self.x_train.columns]

        if columns_to_drop:
            self.logger.info(f"Removing temporal columns (include_data_time=False): {columns_to_drop}")
            self.x_train = self.x_train.drop(columns=columns_to_drop)
            self.x_test = self.x_test.drop(columns=columns_to_drop)
            self.logger.info(f"Temporal columns removed. New training shape: {self.x_train.shape}")
        else:
            self.logger.info("No temporal columns found to remove")

    def _balance_classes(self, sampling_strategy: float = 0.8, k_neighbors: int = 3):
        """
        Apply class balancing to training data using SMOTE with temporal safety.

        Args:
            sampling_strategy: Ratio of minority to majority class after resampling (default: 0.8)
            k_neighbors: Number of nearest neighbors for SMOTE (default: 3)
        """
        # Combine x_train and y_train temporarily for balancing
        temp_df = self.x_train.copy()
        temp_df['is_alcista'] = self.y_train.values

        self.logger.info("Starting class balancing with SMOTE (temporal-safe)...")

        # Create balancer instance
        balanceador = BalanceadorClases(target_column="is_alcista")

        # Set data before applying SMOTE
        balanceador.data = temp_df

        # Apply SMOTE directly without file I/O
        X_balanced, y_balanced = balanceador.apply_smote_temporal_safe(
            sampling_strategy=sampling_strategy,
            k_neighbors=k_neighbors
        )
        balanceador.data_balanced = X_balanced.copy()
        balanceador.data_balanced['is_alcista'] = y_balanced

        # Show comparison
        balanceador.show_balancing_comparison()

        # Update x_train and y_train with balanced data
        self.x_train = X_balanced.reset_index(drop=True)
        self.y_train = y_balanced.reset_index(drop=True)

        self.logger.info(f"Class balancing completed. New training set shape: {self.x_train.shape}")

    def save_data(self):
        """
        Save the data to a CSV file.
        """
        self.logger.info("Saving data")
        output_dir = os.path.join(os.path.dirname(__file__), '../data/')
        self.x_train.to_csv(os.path.join(output_dir, 'x_train.csv'), index=False)
        self.x_test.to_csv(os.path.join(output_dir, 'x_test.csv'), index=False)
        self.y_train.to_csv(os.path.join(output_dir, 'y_train.csv'), index=False)
        self.y_test.to_csv(os.path.join(output_dir, 'y_test.csv'), index=False)
        self.logger.info("Data saved successfully")





if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Ejecutar limpieza sin columnas temporales (RECOMENDADO)
    cleaner = Cleaner(
        file_name_to_load='data_grouped.csv',
        test_size=0.2,
        include_data_time=False
    )
    cleaner.main()