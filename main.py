"""
BitBot Main Pipeline Orchestrator

This script orchestrates the complete data pipeline:
1. Scraping - Collects Bitcoin price data from Binance API
2. Grouper - Groups candles into training samples
3. Cleaning - Cleans and prepares data for model training

All parameters for each module can be configured in the CONFIGURATION section below.
"""

import sys
import os
import logging
import asyncio
import importlib.util
from datetime import datetime


def load_module(module_path, class_name):
    """Load a class from a module file."""
    module_dir = os.path.dirname(module_path)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location("module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


# Load modules
base_dir = os.path.dirname(__file__)
ScrapingMain = load_module(os.path.join(base_dir, 'scraping', 'src', 'main.py'), 'Main')
Grouper = load_module(os.path.join(base_dir, 'grouper', 'src', 'main.py'), 'Grouper')
Cleaner = load_module(os.path.join(base_dir, 'limpieza', 'src', 'main.py'), 'Cleaner')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION - Modify parameters for each module here
# ============================================================================

# Scraping Module Parameters
SCRAPING_CONFIG = {
    'candle_size': 1,
    'initial_date': datetime(2024, 1, 1, 1, 0, 0),
    'end_date': datetime(2025, 10, 20, 1, 0, 0),
    'percentage_return_threshold': 0.05
}

# Grouper Module Parameters
GROUPER_CONFIG = {
    'candle_size_to_traing': 5,
    'candle_to_predict': 5,
    'percentage_return_threshold': 0.0001
}

# Cleaning Module Parameters
CLEANING_CONFIG = {
    'file_name_to_load': 'data_grouped.csv',
    'test_size': 0.2,
    'include_data_time': False,
    'sampling_strategy': 0.8  # SMOTE balancing ratio (0.8 = 80%, 1.0 = 100% balanced)
}

# Pipeline Execution Control
EXECUTE_SCRAPING = True
EXECUTE_GROUPER = True
EXECUTE_CLEANING = True

# ============================================================================


class PipelineOrchestrator:
    """
    Orchestrates the complete BitBot data pipeline.
    Executes scraping, grouping, and cleaning processes in sequence.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def run_scraping(self):
        """
        Execute the scraping process to collect Bitcoin data.
        """
        if not EXECUTE_SCRAPING:
            self.logger.info("Skipping scraping process (disabled in configuration)")
            return

        self.logger.info("=" * 80)
        self.logger.info("STEP 1: Starting Scraping Process")
        self.logger.info("=" * 80)
        self.logger.info(f"Configuration: {SCRAPING_CONFIG}")

        try:
            scraping_main = ScrapingMain(**SCRAPING_CONFIG)
            await scraping_main.main()
            self.logger.info("Scraping process completed successfully")
        except Exception as e:
            self.logger.error(f"Error in scraping process: {str(e)}")
            raise

    def run_grouper(self):
        """
        Execute the grouper process to create training samples.
        """
        if not EXECUTE_GROUPER:
            self.logger.info("Skipping grouper process (disabled in configuration)")
            return

        self.logger.info("=" * 80)
        self.logger.info("STEP 2: Starting Grouper Process")
        self.logger.info("=" * 80)
        self.logger.info(f"Configuration: {GROUPER_CONFIG}")

        try:
            grouper = Grouper(**GROUPER_CONFIG)
            grouper.main()
            self.logger.info("Grouper process completed successfully")
        except Exception as e:
            self.logger.error(f"Error in grouper process: {str(e)}")
            raise

    def run_cleaning(self):
        """
        Execute the cleaning process to prepare final datasets.
        """
        if not EXECUTE_CLEANING:
            self.logger.info("Skipping cleaning process (disabled in configuration)")
            return

        self.logger.info("=" * 80)
        self.logger.info("STEP 3: Starting Cleaning Process")
        self.logger.info("=" * 80)
        self.logger.info(f"Configuration: {CLEANING_CONFIG}")

        try:
            cleaner = Cleaner(**CLEANING_CONFIG)
            cleaner.main()
            self.logger.info("Cleaning process completed successfully")
        except Exception as e:
            self.logger.error(f"Error in cleaning process: {str(e)}")
            raise

    async def run_pipeline(self):
        """
        Execute the complete pipeline in the correct order.
        """
        self.logger.info("=" * 80)
        self.logger.info("BitBot Pipeline Orchestrator - Starting Complete Pipeline")
        self.logger.info("=" * 80)

        try:
            # Step 1: Scraping
            await self.run_scraping()

            # Step 2: Grouper
            self.run_grouper()

            # Step 3: Cleaning
            self.run_cleaning()

            self.logger.info("=" * 80)
            self.logger.info("Pipeline completed successfully!")
            self.logger.info("Datasets are ready for model training and evaluation.")
            self.logger.info("=" * 80)

        except Exception as e:
            self.logger.error("=" * 80)
            self.logger.error(f"Pipeline failed with error: {str(e)}")
            self.logger.error("=" * 80)
            raise


def main():
    """
    Main entry point for the pipeline orchestrator.
    """
    orchestrator = PipelineOrchestrator()
    asyncio.run(orchestrator.run_pipeline())


if __name__ == "__main__":
    main()

