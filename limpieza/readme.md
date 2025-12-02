# Data Cleaning Module

## 1. What Makes This Folder

This folder contains a comprehensive data cleaning and preprocessing system designed to prepare Bitcoin candle data for machine learning models. The module performs the following tasks:

- **Data Loading**: Loads processed Bitcoin candle data from the scraping module
- **Data Exploration**: Analyzes dataset structure, shape, and basic information
- **Data Partitioning**: Splits data into training and testing sets for model evaluation
- **Outlier Detection**: Identifies and visualizes atypical data points using IQR (Interquartile Range) method
- **Categorical Encoding**: Converts categorical variables (like day of week) to numeric format
- **Correlation Analysis**: Calculates and visualizes Pearson correlation matrices to identify feature relationships
- **Class Distribution Analysis**: Analyzes the distribution of target classes for imbalanced data assessment
- **Data Export**: Saves cleaned and processed datasets for model training

The output data is cleaned, encoded, and partitioned, ready for use in machine learning pipelines.

## 2. How It Functions

The cleaning system follows a structured workflow with the following components:

### Components Overview

1. **Data Loading** (`load_data`)
   - Loads CSV files from the scraping module's data directory
   - Defaults to `bitcoin_candles.csv` from `../../scraping/data/`
   - Logs data loading status and file path

2. **Data Exploration** (`_explore_data`)
   - Displays dataset shape (rows, columns)
   - Lists all column names
   - Shows data types and memory usage information

3. **Data Partitioning** (`partition_data`)
   - Separates features (X) from target variable (`is_alcista`)
   - Splits data into train and test sets using `train_test_split`
   - Configurable test size (default: 20%)
   - Uses random state for reproducibility

4. **Outlier Detection** (`detect_outliers`, `plot_boxplot_outliers`, `get_outlier_summary`)
   - Uses IQR method to detect outliers (values beyond 1.5 × IQR)
   - Calculates quartiles (Q1, Q3) and bounds for each column
   - Generates visual boxplots with outlier boundaries
   - Creates summary reports with outlier counts and percentages
   - Default analysis columns: `entrada_vela_1` and `salida_vela_1`

5. **Categorical Encoding** (`encode_dia_semana_ordinal`)
   - Converts day of week strings to ordinal numbers
   - Mapping: Lunes=0, Martes=1, Miércoles=2, Jueves=3, Viernes=4, Sábado=5, Domingo=6
   - Applies encoding to both training and testing sets

6. **Correlation Analysis** (`show_pearson_matrix`)
   - Calculates Pearson correlation coefficients between all numeric features
   - Generates heatmap visualization using seaborn
   - Saves correlation matrix as CSV for further analysis
   - Helps identify multicollinearity and feature relationships

7. **Class Distribution Analysis** (`show_class_distribution`)
   - Counts samples per class
   - Calculates percentage distribution
   - Displays results in tabular format
   - Useful for identifying class imbalance

8. **Data Saving** (`save_data`)
   - Saves processed datasets to CSV files
   - Exports: `x_train.csv`, `x_test.csv`, `y_train.csv`, `y_test.csv`
   - Files saved to `limpieza/data/` directory

### Workflow

The main workflow in `main.py` orchestrates the entire cleaning process:

```
1. Load data → Load CSV from scraping module
2. Explore data → Display dataset information
3. Partition data → Split into train/test sets (80/20 default)
4. Handle outliers → Detect and visualize atypical data
5. Encode categories → Convert categorical variables to numeric
6. Analyze correlations → Calculate Pearson correlation matrix
7. Analyze class distribution → Display target class balance
8. Save data → Export cleaned datasets to CSV
```

### Output Files

The module generates several output files:

**Results (in `limpieza/results/`):**
- `correlation_matrix.csv` - Numeric correlation coefficients matrix
- `correlation_matrix.png` - Heatmap visualization of correlations
- `outlier_boxplot.png` - Boxplot visualization showing outlier boundaries
- `outlier_summary.csv` - Summary statistics of detected outliers

**Processed Data (in `limpieza/data/`):**
- `x_train.csv` - Training features
- `x_test.csv` - Testing features
- `y_train.csv` - Training target variable
- `y_test.csv` - Testing target variable

## 3. How to Execute

### Prerequisites

Make sure you have the required Python packages installed:
- `pandas` - For data manipulation and CSV operations
- `numpy` - For numerical operations
- `matplotlib` - For plotting visualizations
- `seaborn` - For correlation heatmaps
- `scikit-learn` - For train/test splitting
- `imbalanced-learn` - For class balancing techniques (SMOTE, RandomUnderSampler)
- Python 3.7+

### Basic Execution

Navigate to the `limpieza/src` directory and run:

```bash
cd limpieza/src
python main.py
```

### Custom Configuration

You can customize the cleaning parameters by modifying the `Cleaner` class initialization in `main.py`:

```python
cleaner = Cleaner(
    file_name_to_load='bitcoin_candles.csv',  # Input file name
    test_size=0.2                              # Test set proportion (20%)
)
```

### Customization Options

1. **Change Input File**:
   ```python
   cleaner = Cleaner(file_name_to_load='custom_file.csv')
   ```

2. **Adjust Test Size**:
   ```python
   cleaner = Cleaner(test_size=0.3)  # 30% test, 70% train
   ```

3. **Analyze Different Columns for Outliers**:
   ```python
   cleaner._handle_atypical_data(columns=['entrada_vela_2', 'salida_vela_2'])
   ```

4. **Custom Correlation Matrix**:
   ```python
   cleaner.show_pearson_matrix(save_path='custom_path.png', figsize=(20, 18))
   ```

### Dependencies

The module expects data from the `scraping` module:
- Input data should be located in `../../scraping/data/bitcoin_candles.csv`
- The input file must contain an `is_alcista` column (target variable)
- Expected columns include date/time fields, candle data (entrada_vela_X, salida_vela_X), and calculated metrics

### Logging

The system provides detailed logging information throughout the process:
- Data loading status
- Dataset partitioning information
- Outlier detection results
- Encoding operations
- Correlation analysis completion
- Data saving confirmation

Logs are displayed in the console with informative messages at each stage of the cleaning process.
