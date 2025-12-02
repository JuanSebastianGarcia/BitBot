# Grouper Module

## 1. What Makes This Folder

This folder contains a data grouping system designed to transform Bitcoin candle data into training-ready datasets for machine learning models. The module performs the following tasks:

- **Data Loading**: Loads processed Bitcoin candle data from the scraping module
- **Group Creation**: Creates sliding window groups of consecutive candles for training
- **Feature Extraction**: Extracts and reorganizes candle features (entry, exit, max, min prices, returns) from each group
- **Target Calculation**: Calculates the target variable (`is_alcista`) based on future candle performance
- **Data Transformation**: Transforms individual candle data into structured rows suitable for ML model training
- **Data Export**: Saves grouped and processed datasets to CSV format

The output data is structured with features from multiple consecutive candles and a target variable indicating whether a future candle will be bullish, ready for use in supervised machine learning pipelines.

## 2. How It Functions

The grouping system follows a structured workflow with the following components:

### Components Overview

1. **Data Loading** (`_load_data`)
   - Loads CSV files from the scraping module's data directory
   - Defaults to `bitcoin_candles.csv` from `../../scraping/data/`
   - Logs data loading status, shape, and column count
   - Returns a pandas DataFrame with all candle data

2. **Group Creation** (`_create_groups`)
   - Creates sliding window groups of consecutive candles
   - Uses optimized index-based approach (returns ranges instead of DataFrames for memory efficiency)
   - Calculates maximum number of groups based on data size and window parameters
   - Returns list of tuples: `(train_indices_range, predict_index)`
   - Each group contains `candle_size_to_traing` candles for training and one future candle for prediction

3. **Feature Extraction** (`_extract_candle_features`)
   - Extracts features from a single candle
   - Creates feature names with position suffix (e.g., `entrada_vela_1`, `entrada_vela_2`)
   - Extracts: entry price, exit price, maximum price, minimum price, return percentage
   - Returns dictionary with all candle features

4. **Group Processing** (`_process_group`)
   - Processes a single group to create a complete data row
   - Extracts features from all training candles in the group
   - Adds date/time information from the first training candle
   - Calculates target variable based on future candle performance
   - Returns a complete dictionary representing one training sample

5. **DataFrame Creation** (`_create_dataframe_from_groups`)
   - Converts list of processed groups into a pandas DataFrame
   - Processes groups in batches with progress logging (every 10,000 groups)
   - Combines all feature dictionaries into a structured dataset
   - Logs final DataFrame shape and column count

6. **Target Calculation** (`_calculate_predict_candle`)
   - Calculates the target variable `is_alcista` (bullish indicator)
   - Compares the last training candle's exit price with the future candle's entry price
   - Calculates return percentage: `(predict_price - last_price) / last_price`
   - Sets `is_alcista = 1` if return exceeds threshold, otherwise `is_alcista = 0`
   - Default threshold: 0.001 (0.1%)

7. **Date Information** (`_calculate_dates`)
   - Extracts date and time information from the first training candle
   - Adds: fecha, hora_inicial, hora_final, dia, mes, anio, dia_semana
   - Preserves temporal context for each training sample

8. **Data Saving** (`_save_data`)
   - Saves processed DataFrame to CSV file
   - Creates output directory if it doesn't exist
   - Saves to `grouper/data/data_grouped.csv`
   - Logs save confirmation with file path

### Workflow

The main workflow in `main.py` orchestrates the entire grouping process:

```
1. Load data → Load CSV from scraping module
2. Create groups → Generate sliding window groups with indices
3. Process groups → Extract features and calculate targets for each group
4. Create DataFrame → Convert processed groups into structured DataFrame
5. Save data → Export grouped dataset to CSV
```

### Output Structure

Each row in the output DataFrame represents one training sample with:

**Training Features (for each candle in the group):**
- `entrada_vela_1` through `entrada_vela_N` (entry prices)
- `salida_vela_1` through `salida_vela_N` (exit prices)
- `Max_vela_1` through `Max_vela_N` (maximum prices)
- `Min_vela_1` through `Min_vela_N` (minimum prices)
- `porcentaje_retorno_vela_1` through `porcentaje_retorno_vela_N` (return percentages)

**Temporal Features:**
- `fecha` (date)
- `hora_inicial`, `hora_final` (time range)
- `dia`, `mes`, `anio` (date components)
- `dia_semana` (day of week)

**Target Variable:**
- `is_alcista` (binary: 1 if future candle is bullish, 0 otherwise)

Where `N` = `candle_size_to_traing` (default: 5)

## 3. How to Execute

### Prerequisites

Make sure you have the required Python packages installed:
- `pandas` - For data manipulation and CSV operations
- `os` - For file system operations (built-in)
- `logging` - For logging functionality (built-in)
- Python 3.7+

### Basic Execution

Navigate to the `grouper/src` directory and run:

```bash
cd grouper/src
python main.py
```

### Custom Configuration

You can customize the grouping parameters by modifying the `Grouper` class initialization in `main.py`:

```python
grouper = Grouper(
    candle_size_to_traing=5,              # Number of candles for training (default: 5)
    candle_to_predict=5,                  # Offset for prediction candle (default: 5)
    percentage_return_threshold=0.001     # Threshold for bullish classification (default: 0.001)
)
```

### Customization Options

1. **Change Training Window Size:**
   ```python
   grouper = Grouper(candle_size_to_traing=10)  # Use 10 candles for training
   ```

2. **Adjust Prediction Offset:**
   ```python
   grouper = Grouper(candle_to_predict=1)  # Predict the immediate next candle
   ```

3. **Modify Bullish Threshold:**
   ```python
   grouper = Grouper(percentage_return_threshold=0.05)  # 5% threshold
   ```

### Output

The processed data is saved to:
```
grouper/data/data_grouped.csv
```

The CSV file contains:
- One row per training sample
- Features from multiple consecutive candles (sliding window approach)
- Target variable (`is_alcista`) indicating future candle performance
- Date and time information for temporal analysis

**Example:** With `candle_size_to_traing=5` and `candle_to_predict=5`:
- Each row contains features from 5 consecutive candles
- The target variable indicates whether the 5th candle after the training window will be bullish
- Total number of rows = `total_candles - candle_size_to_traing - candle_to_predict + 1`

### Dependencies

The module expects data from the `scraping` module:
- Input data should be located in `../../scraping/data/bitcoin_candles.csv`
- The input file must contain columns: `entrada_vela_1`, `salida_vela_1`, `Max_vela_1`, `Min_vela_1`, `porcentaje_retorno_vela_1`
- Expected columns include date/time fields: `fecha`, `hora_inicial`, `hora_final`, `dia`, `mes`, `anio`, `dia_semana`

### Logging

The system provides detailed logging information throughout the process:
- Initialization parameters
- Data loading status and shape information
- Group creation progress (total rows, max groups)
- DataFrame creation progress (updates every 10,000 groups)
- Final DataFrame statistics (shape, column count)
- Data saving confirmation with file path

Logs are displayed in the console with timestamps and informative messages at each stage of the grouping process.

### Performance Considerations

- The module uses optimized index-based grouping to minimize memory usage
- Progress logging helps track processing of large datasets
- For very large datasets (hundreds of thousands of rows), processing may take several minutes
- The sliding window approach creates overlapping groups, maximizing training data from available candles