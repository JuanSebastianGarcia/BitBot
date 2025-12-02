# BitBot - Bitcoin Price Prediction Project

## Introduction

BitBot is a machine learning project focused on predicting Bitcoin (BTCUSDT) price movements. This project aims to develop predictive models that can forecast future Bitcoin price trends by analyzing historical market data patterns.

**Current Phase: Data Pipeline**

This first phase consists of a complete automated data pipeline that collects, groups, cleans, and prepares Bitcoin market data for machine learning model training. The pipeline is fully configurable through a single orchestrator script ([main.py](main.py)) that manages all three processing stages.

## Pipeline Orchestration

The entire pipeline can be executed from a single entry point:

```bash
python main.py
```

All pipeline parameters are configured in [main.py](main.py#L46-L70) through three configuration dictionaries:

```python
# Scraping Module Parameters
SCRAPING_CONFIG = {
    'candle_size': 1,                                      # Candle interval in minutes
    'initial_date': datetime(2024, 1, 1, 1, 0, 0),        # Start date for data collection
    'end_date': datetime(2025, 10, 20, 1, 0, 0),          # End date for data collection
    'percentage_return_threshold': 0.05                    # Return threshold for trend classification
}

# Grouper Module Parameters
GROUPER_CONFIG = {
    'candle_size_to_traing': 5,                           # Number of candles per training sample
    'candle_to_predict': 5,                               # Number of candles to predict ahead
    'percentage_return_threshold': 0.0001                 # Minimum return threshold
}

# Cleaning Module Parameters
CLEANING_CONFIG = {
    'file_name_to_load': 'data_grouped.csv',              # Input file from grouper
    'test_size': 0.2,                                     # Test set proportion (0.2 = 20%)
    'include_data_time': False,                           # Include temporal features
    'sampling_strategy': 0.8                              # SMOTE balance ratio (0.8=80%, 1.0=100%)
}
```

Individual modules can be disabled using execution control flags:
```python
EXECUTE_SCRAPING = True   # Set to False to skip scraping
EXECUTE_GROUPER = True    # Set to False to skip grouping
EXECUTE_CLEANING = True   # Set to False to skip cleaning
```

## Pipeline Components

The BitBot data pipeline consists of three sequential modules:

### 1. Scraping Module

The **Scraping** module is responsible for collecting raw Bitcoin price data from external sources. It retrieves historical candle (price) data from the Binance API, processes the raw data into structured groups, and calculates relevant metrics such as:

- Entry and exit prices for each candle
- Maximum and minimum prices
- Return percentages
- Bullish candle counts
- Temporal features (date, time, day of week)
- Trend indicators

**Output:** Processed Bitcoin candle data saved as `bitcoin_candles.csv`

### 2. Grouper Module

The **Grouper** module transforms individual candle data into training-ready samples using a sliding window approach. It takes the scraped data and creates groups of consecutive candles, extracting features for supervised learning:

- **Group Creation**: Generates sliding window groups of consecutive candles
- **Feature Extraction**: Extracts and reorganizes candle features (entry, exit, max, min, returns)
- **Target Calculation**: Calculates target variables based on future candle performance
- **Data Transformation**: Structures data into rows suitable for ML model training

**Output:** Grouped dataset (`data_grouped.csv`) with features from multiple candles and target variables

### 3. Cleaning Module (Limpieza)

The **Cleaning** module prepares grouped data for machine learning by performing preprocessing tasks:

- **Data Exploration**: Analyzes dataset structure and characteristics
- **Chronological Partitioning**: Splits data into train/test sets maintaining temporal order (default 80/20)
- **Categorical Encoding**: Converts day of week to ordinal numeric values
- **Temporal Column Management**: Removes/keeps temporal features based on configuration
- **Class Balancing**: Applies SMOTE with configurable ratio (0.8=80% balanced, 1.0=100% balanced)
  - Automatic detection of already-balanced classes
  - Auto-adjustment of k_neighbors for small datasets
  - See [SAMPLING_STRATEGY_GUIDE.md](SAMPLING_STRATEGY_GUIDE.md) for detailed configuration

**Output:** Train/test datasets (`x_train.csv`, `x_test.csv`, `y_train.csv`, `y_test.csv`) ready for model training

## Pipeline Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                       main.py                               │
│                  Pipeline Orchestrator                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │  STEP 1: Scraping                     │
        │  • Binance API data collection        │
        │  • Candle processing                  │
        │  Output: bitcoin_candles.csv          │
        └───────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │  STEP 2: Grouper                      │
        │  • Sliding window grouping            │
        │  • Feature extraction                 │
        │  Output: data_grouped.csv             │
        └───────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │  STEP 3: Cleaning                     │
        │  • Chronological train/test split     │
        │  • Encoding & preprocessing           │
        │  • SMOTE class balancing              │
        │  Output: x_train, x_test, y_train,    │
        │          y_test (CSV files)           │
        └───────────────────────────────────────┘
                            │
                            ▼
              Ready for ML Model Training
```

## Quick Start

### Prerequisites

- Python 3.7+
- Required packages: `pandas`, `numpy`, `aiohttp`, `scikit-learn`, `imbalanced-learn`

### Execution

**Option 1: Run Complete Pipeline (Recommended)**
```bash
python main.py
```

**Option 2: Run Individual Modules**
```bash
# Step 1: Scraping
cd scraping/src && python main.py

# Step 2: Grouper
cd grouper/src && python main.py

# Step 3: Cleaning
cd limpieza/src && python main.py
```

### Configuration

All parameters are centralized in [main.py](main.py#L46-L70). Modify the configuration dictionaries to customize the pipeline behavior. Key configurable parameters include:

- **Scraping**: Date range, candle size, return thresholds
- **Grouper**: Training window size, prediction horizon
- **Cleaning**: Test split ratio, temporal features, SMOTE balance ratio

See [SAMPLING_STRATEGY_GUIDE.md](SAMPLING_STRATEGY_GUIDE.md) for detailed SMOTE configuration options.

## Project Structure

```
BitBot/
├── main.py                          # Pipeline orchestrator - single entry point
├── SAMPLING_STRATEGY_GUIDE.md       # SMOTE configuration guide
│
├── scraping/                        # Data collection module
│   ├── data/                        # Output: bitcoin_candles.csv
│   ├── src/                         # Source code
│   │   └── main.py                  # Scraping implementation
│   └── readme.md                    # Module documentation
│
├── grouper/                         # Data grouping module
│   ├── data/                        # Output: data_grouped.csv
│   ├── src/                         # Source code
│   │   └── main.py                  # Grouping implementation
│   └── readme.md                    # Module documentation
│
├── limpieza/                        # Data cleaning module
│   ├── data/                        # Output: x_train, x_test, y_train, y_test
│   ├── src/                         # Source code
│   │   ├── main.py                  # Cleaning orchestrator
│   │   └── balance_clases.py        # SMOTE balancing implementation
│   └── readme.md                    # Module documentation
│
└── readme.md                        # This file
```

## Module Documentation

For detailed implementation information:

- [Scraping Module](scraping/Readme.md) - Data collection from Binance API
- [Grouper Module](grouper/readme.md) - Sliding window feature extraction
- [Cleaning Module](limpieza/readme.md) - Preprocessing and balancing
- [SMOTE Configuration Guide](SAMPLING_STRATEGY_GUIDE.md) - Class balancing options

## Next Steps

The processed datasets are ready for:
- Machine learning model training (Random Forest, XGBoost, Neural Networks)
- Model evaluation and validation
- Hyperparameter tuning
- Backtesting and deployment

