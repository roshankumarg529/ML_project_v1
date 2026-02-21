"""
Main training script for the ML model
"""

import logging
import sys
from pathlib import Path

from sklearn.model_selection import train_test_split

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import LOG_FORMAT, LOG_LEVEL, RANDOM_STATE, TEST_SIZE
from data_generator import generate_dummy_dataset, load_dataset, save_dataset
from model import RandomForestModel

# Setup logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def main():
    """
    Main training pipeline
    """
    logger.info("=" * 50)
    logger.info("Starting ML Training Pipeline")
    logger.info("=" * 50)

    try:
        # Step 1: Generate and save dataset
        logger.info("\n[Step 1] Generating dummy dataset...")
        df = generate_dummy_dataset()
        save_dataset(df)

        # Step 2: Prepare data
        logger.info("\n[Step 2] Preparing training and test data...")
        X = df.drop("target", axis=1).values
        y = df["target"].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )

        logger.info(f"Training set size: {X_train.shape[0]}")
        logger.info(f"Test set size: {X_test.shape[0]}")

        # Step 3: Initialize and train model
        logger.info("\n[Step 3] Training Random Forest model...")
        model = RandomForestModel()
        model.train(X_train, y_train)

        # Step 4: Evaluate model
        logger.info("\n[Step 4] Evaluating model...")
        metrics = model.evaluate(X_test, y_test)

        # Step 5: Save model
        logger.info("\n[Step 5] Saving model artifacts...")
        model.save()

        logger.info("\n" + "=" * 50)
        logger.info("Training completed successfully!")
        logger.info("=" * 50)

        return 0

    except Exception as e:
        logger.error(f"Training failed with error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
