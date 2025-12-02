# Scraping Module

## 1. What Makes This Folder

This folder contains a complete scraping system designed to collect, process, and store Bitcoin (BTCUSDT) price data from the Binance API. The module performs the following tasks:

- **Data Collection**: Retrieves historical Bitcoin candle (price) data from Binance's public API
- **Data Processing**: Groups raw candle data into sets of consecutive candles and extracts relevant metrics
- **Data Calculation**: Computes additional metrics such as total return percentage, bullish candle count, day of week, and trend indicators
- **Data Storage**: Saves the processed and calculated data to a CSV file for further analysis

The output data can be used for trading analysis, machine learning models, or statistical studies of Bitcoin price patterns.

## 2. How It Functions

The scraping system follows a modular architecture with the following components:

### Components Overview

1. **EndpointGenerator** (`endpoint_generator.py`)
   - Generates API endpoint URLs for each day within a specified date range
   - Creates Binance API URLs with parameters (symbol: BTCUSDT, interval: 1m, limit: 1000)
   - Converts dates to Unix timestamps in milliseconds

2. **Consulter** (`consulter.py`)
   - Asynchronously fetches data from the generated URLs using `aiohttp`
   - Implements retry logic for failed requests (default: 3 retries)
   - Controls concurrency using semaphores (default: 10 concurrent requests)
   - Handles timeouts and network errors gracefully

3. **Procesor** (`procesor.py`)
   - Extracts candle data from API responses
   - Groups candles into consecutive sets of 5 (configurable via `candle_size`)
   - Processes each group to extract:
     - Date and time information
     - Entry and exit prices for each candle
     - Maximum and minimum prices for each candle
     - Percentage return for each candle

4. **CalculatorData** (`calculator_data.py`)
   - Calculates total return percentage across all candles in a group
   - Counts the number of bullish candles (where close > open)
   - Decomposes the date into day, month, and year
   - Determines the day of the week (in Spanish)
   - Creates a binary indicator (`is_alcista`) based on whether the total return exceeds a threshold

5. **Saver** (`save.py`)
   - Saves the processed and calculated data to a CSV file
   - Sorts data by date and time
   - Ensures the output directory exists before saving

### Workflow

The main workflow in `main.py` orchestrates the entire process:

```
1. Generate URL list → EndpointGenerator generates URLs for each day in the date range
2. Fetch data → Consulter asynchronously requests data from all URLs
3. Process candles → Procesor groups candles and extracts metrics
4. Calculate metrics → CalculatorData adds derived metrics
5. Save results → Saver writes the final data to CSV file
```

## 3. How to Execute

### Prerequisites

Make sure you have the required Python packages installed:
- `aiohttp` - For asynchronous HTTP requests
- `pandas` - For data manipulation and CSV operations
- Python 3.7+ (with `asyncio` support)

### Basic Execution

Navigate to the `scraping/src` directory and run:

```bash
cd scraping/src
python main.py
```

### Custom Configuration

You can customize the scraping parameters by modifying the `Main` class initialization in `main.py`:

```python
main = Main(
    candle_size=5,                                          # Number of candles per group
    initial_date=datetime(2024, 1, 1, 1, 0, 0),           # Start date for data collection
    end_date=datetime(2025, 10, 20, 1, 0, 0),             # End date for data collection
    percentage_return_threshold=0.05                       # Threshold for is_alcista indicator
)
```

### Output

The processed data is saved to:
```
scraping/data/bitcoin_candles.csv
```

The CSV file contains columns such as:
- `fecha`, `hora_inicial`, `hora_final`
- `entrada_vela_1` through `entrada_vela_5` (entry prices)
- `salida_vela_1` through `salida_vela_5` (exit prices)
- `Max_vela_1` through `Max_vela_5` (maximum prices)
- `Min_vela_1` through `Min_vela_5` (minimum prices)
- `porcentaje_retorno_vela_1` through `porcentaje_retorno_vela_5` (return percentages)
- `porcentaje_retorno_total` (total return across all candles)
- `velas_alcistas` (count of bullish candles)
- `dia`, `mes`, `anio` (date components)
- `dia_semana` (day of week in Spanish)
- `is_alcista` (binary trend indicator)

### Logging

The system provides detailed logging information throughout the process:
- Number of generated endpoints
- Number of successful/failed requests
- Number of processed candle groups
- Progress updates at each stage

Logs are displayed in the console and can be configured by modifying the logging level in `main.py`.
