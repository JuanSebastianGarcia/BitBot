import logging
import pandas as pd
from pandas import DataFrame

class CalculatorData:

    def __init__(self, percentage_return_threshold: float = 0.01):
        self.logger = logging.getLogger(__name__)
        self.percentage_return_threshold = percentage_return_threshold


    def main(self, data: DataFrame):
        """
        Calculate and add new columns to the DataFrame.
        
        Args:
            data: DataFrame with candle data (fecha, hora_inicial, hora_final, entrada_vela_X, salida_vela_X, etc.)
            threshold: Threshold for is_alcista indicator (default: 0.05)
            
        Returns:
            DataFrame with added columns: porcentaje_retorno_total, velas_alcistas, dia_semana, is_alcista
        """
        self.logger.info("Calculating data")
        
        # Detect number of candles dynamically
        candle_count = self._detect_candle_count(data)
        self.logger.info(f"Detected {candle_count} candles per row")
        
        # Calculate porcentaje_retorno_total
        data = self._calculate_total_return(data, candle_count)
        
        # Calculate velas_alcistas
        data = self._calculate_bullish_candles(data, candle_count)
        
        # descomponer la fecha
        data = self._descomponer_fecha(data)
        
        # Calculate dia_semana
        data = self._calculate_day_of_week(data)
        
        # Calculate is_alcista
        data = self._calculate_is_bullish(data)
        
        return data

    def _detect_candle_count(self, data: DataFrame) -> int:
        """Detect the number of candles based on column names."""
        return_cols = [col for col in data.columns if col.startswith('porcentaje_retorno_vela_')]
        if not return_cols:
            return 0
        # Extract numbers and find max
        candle_numbers = [int(col.replace('porcentaje_retorno_vela_', '')) for col in return_cols]
        return max(candle_numbers) if candle_numbers else 0

    def _calculate_total_return(self, data: DataFrame, candle_count: int) -> DataFrame:
        """Calculate total percentage return across all candles."""
        return_cols = [f'porcentaje_retorno_vela_{i}' for i in range(1, candle_count + 1)]
        # Filter to only existing columns
        existing_cols = [col for col in return_cols if col in data.columns]
        data['porcentaje_retorno_total'] = data[existing_cols].sum(axis=1, skipna=True)
        return data

    def _calculate_bullish_candles(self, data: DataFrame, candle_count: int) -> DataFrame:
        """Count how many candles closed bullish (salida > entrada)."""
        bullish_count = pd.Series(0, index=data.index)
        
        for i in range(1, candle_count + 1):
            entrada_col = f'entrada_vela_{i}'
            salida_col = f'salida_vela_{i}'
            if entrada_col in data.columns and salida_col in data.columns:
                bullish_count += (data[salida_col] > data[entrada_col]).astype(int)
        
        data['velas_alcistas'] = bullish_count
        return data

    def _calculate_day_of_week(self, data: DataFrame) -> DataFrame:
        """Extract day of week from fecha column in Spanish."""
        spanish_days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        data['dia_semana'] = data['fecha'].dt.dayofweek.apply(lambda x: spanish_days[x])
        return data

    def _descomponer_fecha(self, data: DataFrame) -> DataFrame:
        """Descomponer la fecha en dia, mes y año."""
        data['fecha'] = pd.to_datetime(data['fecha'])
        data['dia'] = data['fecha'].dt.day
        data['mes'] = data['fecha'].dt.month
        data['anio'] = data['fecha'].dt.year
        return data







    def _calculate_is_bullish(self, data: DataFrame) -> DataFrame:
        """Calculate binary indicator (1 if total return > threshold, else 0)."""
        data['is_alcista'] = (data['porcentaje_retorno_total'] > self.percentage_return_threshold).astype(int)
        return data