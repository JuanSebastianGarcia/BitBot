# BitBot - Bitcoin Price Prediction Project

## Introduction

BitBot is a machine learning project focused on predicting Bitcoin (BTCUSDT) price movements. This project aims to develop predictive models that can forecast future Bitcoin price trends by analyzing historical market data patterns.

**Current Phase: Data Pipeline**

This first phase of the project consists of a complete data pipeline that collects, groups, cleans, and prepares Bitcoin market data for machine learning model training and testing. The pipeline is designed to transform raw market data into structured, feature-rich datasets ready for supervised learning algorithms and model evaluation.

## Project Overview

The BitBot data pipeline is organized into three main components, each responsible for a specific stage of data processing:

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

The **Cleaning** module takes the grouped data and prepares it for machine learning by performing essential preprocessing tasks. This is the final step that generates the train and test datasets:

- **Data Exploration**: Analyzes dataset structure and characteristics
- **Data Partitioning**: Splits data into training and testing sets (80/20 default)
- **Outlier Detection**: Identifies and visualizes atypical data points using IQR method
- **Categorical Encoding**: Converts categorical variables (e.g., day of week) to numeric format
- **Correlation Analysis**: Calculates and visualizes feature relationships
- **Class Distribution Analysis**: Assesses target variable balance

**Output:** Cleaned datasets (`x_train.csv`, `x_test.csv`, `y_train.csv`, `y_test.csv`) and analysis reports - ready for model evaluation

## Workflow

The complete data pipeline follows this sequential workflow:

```
1. Scraping
   ↓
   [Raw Bitcoin candle data from Binance API]
   ↓
2. Grouper
   ↓
   [Grouped datasets with features and targets]
   ↓
3. Cleaning
   ↓
   [Cleaned, encoded, and partitioned train/test datasets]
   ↓
   Ready for ML Model Training and Evaluation
```

## Getting Started

### Prerequisites

- Python 3.7+
- Required packages: `pandas`, `numpy`, `aiohttp`, `matplotlib`, `seaborn`, `scikit-learn`

### Execution Order

To process data through the complete pipeline, execute the modules in this order:

1. **Run Scraping Module:**
   ```bash
   cd scraping/src
   python main.py
   ```

2. **Run Grouper Module:**
   ```bash
   cd grouper/src
   python main.py
   ```

3. **Run Cleaning Module:**
   ```bash
   cd limpieza/src
   python main.py
   ```

The cleaning module will generate the final train and test datasets ready for model evaluation.

Each module can be configured independently. See the individual README files in each module's directory for detailed configuration options.

## Project Structure

```
BitBot/
├── scraping/          # Data collection module
│   ├── data/         # Collected Bitcoin candle data
│   ├── src/          # Source code
│   └── readme.md     # Detailed scraping documentation
├── limpieza/         # Data cleaning module
│   ├── data/         # Cleaned datasets (train/test splits)
│   ├── results/      # Analysis reports and visualizations
│   ├── src/          # Source code
│   └── readme.md     # Detailed cleaning documentation
├── grouper/          # Data grouping module
│   ├── data/         # Grouped training datasets
│   ├── src/          # Source code
│   └── readme.md     # Detailed grouping documentation
└── readme.md         # This file
```

## Next Steps

After completing the data pipeline phase, the processed datasets will be used for:

- Training machine learning models (e.g., Random Forest, XGBoost, Neural Networks)
- Model evaluation and validation
- Hyperparameter tuning
- Prediction and backtesting
- Deployment of prediction models

## Documentation

For detailed information about each module, please refer to the individual README files:

- [Scraping Module Documentation](scraping/Readme.md)
- [Cleaning Module Documentation](limpieza/readme.md)
- [Grouper Module Documentation](grouper/readme.md)

