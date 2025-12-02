# -*- coding: utf-8 -*-
import pandas as pd
import os
import logging
from imblearn.over_sampling import SMOTE


class BalanceadorClases:
    """
    Handles class balancing for temporal datasets using SMOTE with temporal safety.
    Specifically designed for time-series data where maintaining chronological order is critical.
    """

    def __init__(self, target_column: str = "is_alcista"):
        """
        Initialize the BalanceadorClases class.

        Args:
            target_column: Name of the target variable column (default: "is_alcista")
        """
        self.logger = logging.getLogger(__name__)
        self.target_column = target_column
        self.data = None
        self.data_balanced = None
        self.class_distribution_before = None
        self.class_distribution_after = None

    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load data from a CSV file.

        Args:
            file_path: Path to the CSV file to load

        Returns:
            DataFrame with loaded data
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        self.data = pd.read_csv(file_path)
        self.logger.info(f"Data loaded successfully from {file_path}")
        self.logger.info(f"Dataset shape: {self.data.shape}")

        return self.data

    def _analyze_class_distribution(self, data: pd.DataFrame, stage: str = "before") -> dict:
        """
        Analyze and log the class distribution in the dataset.

        Args:
            data: DataFrame to analyze
            stage: Stage of analysis ("before" or "after")

        Returns:
            Dictionary with class distribution information
        """
        if self.target_column not in data.columns:
            self.logger.error(f"Target column '{self.target_column}' not found in data")
            raise ValueError(f"Target column '{self.target_column}' not found in data")

        class_counts = data[self.target_column].value_counts().sort_index()
        total_samples = len(data)

        distribution_info = {}

        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"CLASS DISTRIBUTION {stage.upper()}")
        self.logger.info(f"{'='*70}")

        for class_label, count in class_counts.items():
            percentage = (count / total_samples) * 100
            distribution_info[int(class_label)] = {
                'count': count,
                'percentage': percentage
            }

            self.logger.info(
                f"Class {class_label}: {count:>10} samples ({percentage:>6.2f}%)"
            )

        # Calculate imbalance ratio
        if len(class_counts) == 2:
            class_0_count = class_counts.get(0, 0)
            class_1_count = class_counts.get(1, 0)

            if class_1_count > 0:
                imbalance_ratio = class_0_count / class_1_count
                self.logger.info(f"Imbalance Ratio (Class 0 / Class 1): {imbalance_ratio:.2f}")

        self.logger.info(f"Total Samples: {total_samples}")
        self.logger.info(f"{'='*70}\n")

        return distribution_info

    def apply_smote_temporal_safe(self, sampling_strategy: float = 0.8, k_neighbors: int = 3) -> tuple:
        """
        Apply SMOTE with temporal safety considerations.

        SMOTE parameters optimized for time-series data:
        - k_neighbors=3: Ensures interpolation with closer temporal neighbors (not 5 default)
        - sampling_strategy=0.8: Balances classes to 80% of majority class

        Args:
            sampling_strategy: The ratio of minority to majority class after resampling
                             (default: 0.8 = 80% equilibrium, not 100%)
            k_neighbors: Number of nearest neighbors for SMOTE interpolation
                        (default: 3, lower values = closer temporal neighbors)

        Returns:
            Tuple of (X_balanced, y_balanced)
        """
        self.logger.info(f"Applying SMOTE with temporal safety")
        self.logger.info(f"Initial parameters: sampling_strategy={sampling_strategy}, k_neighbors={k_neighbors}")

        # Separate features and target
        X = self.data.drop(columns=[self.target_column])
        y = self.data[self.target_column]

        # Analyze class distribution
        class_counts = y.value_counts()
        minority_class = class_counts.idxmin()
        majority_class = class_counts.idxmax()
        minority_count = class_counts[minority_class]
        majority_count = class_counts[majority_class]
        current_ratio = minority_count / majority_count

        self.logger.info(f"Class distribution: Minority class ({minority_class}): {minority_count}, Majority class ({majority_class}): {majority_count}")
        self.logger.info(f"Current ratio (minority/majority): {current_ratio:.4f}")

        # Adjust k_neighbors if necessary
        max_k_neighbors = minority_count - 1
        if k_neighbors >= minority_count:
            k_neighbors = max(1, max_k_neighbors)
            self.logger.warning(f"k_neighbors adjusted to {k_neighbors} (minority class has only {minority_count} samples)")

        # Adjust sampling_strategy if current ratio is already higher
        if current_ratio >= sampling_strategy:
            # Classes are already balanced or over-balanced
            self.logger.warning(f"Current ratio ({current_ratio:.4f}) >= target ratio ({sampling_strategy})")
            self.logger.warning("Classes are already balanced. Skipping SMOTE.")
            return X, y

        # Calculate required samples to reach target ratio
        target_minority_count = int(majority_count * sampling_strategy)
        samples_to_generate = target_minority_count - minority_count

        self.logger.info(f"Target minority count: {target_minority_count}")
        self.logger.info(f"Samples to generate: {samples_to_generate}")

        # Apply SMOTE
        smote = SMOTE(
            k_neighbors=k_neighbors,
            sampling_strategy=sampling_strategy,
            random_state=42
        )

        try:
            X_balanced, y_balanced = smote.fit_resample(X, y)
            self.logger.info(f"SMOTE applied successfully")
            self.logger.info(f"Generated {len(X_balanced) - len(X)} synthetic samples")
        except Exception as e:
            self.logger.error(f"Error applying SMOTE: {str(e)}")
            raise

        return X_balanced, y_balanced

    def show_balancing_comparison(self) -> pd.DataFrame:
        """
        Display a comparison between before and after balancing.

        Returns:
            DataFrame with comparison statistics
        """
        if self.data_balanced is None:
            self.logger.warning("No balanced data available. Apply SMOTE first.")
            return None

        self.logger.info("\n" + "="*70)
        self.logger.info("BALANCING COMPARISON (BEFORE vs AFTER)")
        self.logger.info("="*70)

        # Get distributions
        class_distribution_before = self.data[self.target_column].value_counts().sort_index()
        class_distribution_after = self.data_balanced[self.target_column].value_counts().sort_index()

        total_before = len(self.data)
        total_after = len(self.data_balanced)

        comparison_data = []

        for class_label in sorted(self.data[self.target_column].unique()):
            count_before = class_distribution_before.get(class_label, 0)
            count_after = class_distribution_after.get(class_label, 0)
            pct_before = (count_before / total_before) * 100
            pct_after = (count_after / total_after) * 100

            comparison_data.append({
                'Class': int(class_label),
                'Count Before': count_before,
                '% Before': f"{pct_before:.2f}%",
                'Count After': count_after,
                '% After': f"{pct_after:.2f}%",
                'Samples Added': count_after - count_before
            })

            self.logger.info(
                f"Class {class_label}: "
                f"Before: {count_before:>10} ({pct_before:>6.2f}%) -> "
                f"After: {count_after:>10} ({pct_after:>6.2f}%) | "
                f"Added: {count_after - count_before:>8}"
            )

        self.logger.info(f"\nTotal Samples: {total_before} -> {total_after} (+{total_after - total_before})")
        self.logger.info("="*70 + "\n")

        comparison_df = pd.DataFrame(comparison_data)
        return comparison_df

    def save_balanced_data(self, output_path: str) -> None:
        """
        Save the balanced dataset to a CSV file.

        Args:
            output_path: Path where to save the balanced CSV file
        """
        if self.data_balanced is None:
            self.logger.error("No balanced data available. Apply SMOTE first.")
            raise ValueError("No balanced data available. Apply SMOTE first.")

        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        self.data_balanced.to_csv(output_path, index=False)
        self.logger.info(f"Balanced data saved to: {output_path}")

    def main(
        self,
        input_file_path: str,
        output_file_path: str = None,
        sampling_strategy: float = 0.8,
        k_neighbors: int = 3
    ) -> pd.DataFrame:
        """
        Main method to execute the complete balancing process.

        Workflow:
        1. Load data from CSV
        2. Display original class distribution
        3. Apply SMOTE with temporal safety
        4. Display balanced class distribution
        5. Show comparison between before and after
        6. Save balanced data to CSV (if output_file_path provided)

        Args:
            input_file_path: Path to the input CSV file
            output_file_path: Path where to save the balanced CSV (optional)
            sampling_strategy: Ratio of minority to majority class (default: 0.8)
            k_neighbors: Number of nearest neighbors for SMOTE (default: 3)

        Returns:
            DataFrame with balanced data
        """
        self.logger.info("Starting class balancing process...")

        # Step 1: Load data
        self.load_data(input_file_path)

        # Step 2: Show original distribution
        self.class_distribution_before = self._analyze_class_distribution(self.data, stage="BEFORE BALANCING")

        # Step 3: Apply SMOTE
        self.apply_smote_temporal_safe(sampling_strategy=sampling_strategy, k_neighbors=k_neighbors)

        # Step 4: Show balanced distribution
        self.class_distribution_after = self._analyze_class_distribution(self.data_balanced, stage="AFTER BALANCING")

        # Step 5: Show comparison
        self.show_balancing_comparison()

        # Step 6: Save balanced data
        if output_file_path:
            self.save_balanced_data(output_file_path)
        else:
            self.logger.info("No output path provided. Balanced data not saved to file.")

        self.logger.info("Class balancing process completed successfully!")

        return self.data_balanced


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Example usage
    balanceador = BalanceadorClases(target_column="is_alcista")

    # Define paths
    input_file = "../../grouper/data/data_grouped.csv"
    output_file = "../data/data_grouped_balanced.csv"

    # Execute balancing process
    balanced_data = balanceador.main(
        input_file_path=input_file,
        output_file_path=output_file,
        sampling_strategy=0.8,
        k_neighbors=3
    )
