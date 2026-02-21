"""
Generate dummy dataset for training the ML model
"""

import logging
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from pathlib import Path
from config import DATA_DIR, DATASET_SAMPLES, N_FEATURES, N_CLASSES, RANDOM_STATE

logger = logging.getLogger(__name__)


def generate_dummy_dataset(
    samples=DATASET_SAMPLES,
    features=N_FEATURES,
    n_classes=N_CLASSES,
    random_state=RANDOM_STATE,
):
    """
    Generate a dummy classification dataset.

    Args:
        samples: Number of samples to generate
        features: Number of features
        n_classes: Number of classes
        random_state: Random seed for reproducibility

    Returns:
        Tuple of (X, y) - features and labels
    """
    logger.info(
        f"Generating dummy dataset with {samples} samples and {features} features"
    )

    X, y = make_classification(
        n_samples=samples,
        n_features=features,
        n_informative=int(features * 0.7),
        n_redundant=int(features * 0.3),
        n_classes=n_classes,
        n_clusters_per_class=2,
        random_state=random_state,
        shuffle=True,
    )

    # Create DataFrame with meaningful feature names
    feature_names = [f"feature_{i}" for i in range(features)]
    df = pd.DataFrame(X, columns=feature_names)
    df["target"] = y

    logger.info(f"Dataset shape: {df.shape}")
    logger.info(f"Class distribution:\n{df['target'].value_counts()}")

    return df


def save_dataset(df, output_path=None):
    """
    Save dataset to CSV file.

    Args:
        df: DataFrame to save
        output_path: Path to save the dataset (default: data/dataset.csv)
    """
    if output_path is None:
        output_path = DATA_DIR / "dataset.csv"

    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Dataset saved to {output_path}")

    return output_path


def load_dataset(path=None):
    """
    Load dataset from CSV file.

    Args:
        path: Path to the dataset file

    Returns:
        DataFrame containing the dataset
    """
    if path is None:
        path = DATA_DIR / "dataset.csv"

    df = pd.read_csv(path)
    logger.info(f"Loaded dataset from {path} with shape {df.shape}")

    return df


if __name__ == "__main__":
    # Generate and save dummy dataset
    df = generate_dummy_dataset()
    save_dataset(df)
