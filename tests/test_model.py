"""
Unit tests for the ML model
"""

import sys
from pathlib import Path
import numpy as np
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import RANDOM_STATE, TEST_SIZE
from data_generator import generate_dummy_dataset
from model import RandomForestModel
from sklearn.model_selection import train_test_split


def test_data_generation():
    """Test dummy dataset generation"""
    df = generate_dummy_dataset(samples=100, features=10, n_classes=3)

    assert df.shape[0] == 100, "Wrong number of samples"
    assert df.shape[1] == 11, "Wrong number of features (including target)"
    assert "target" in df.columns, "Target column missing"
    assert len(df["target"].unique()) == 3, "Wrong number of classes"


def test_model_initialization():
    """Test model initialization"""
    model = RandomForestModel()

    assert model.model is not None, "Model not initialized"
    assert model.scaler is not None, "Scaler not initialized"


def test_model_training():
    """Test model training"""
    # Generate data
    df = generate_dummy_dataset(samples=200, features=10, n_classes=2)
    X = df.drop("target", axis=1).values
    y = df["target"].values

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    # Train model
    model = RandomForestModel()
    model.train(X_train, y_train)

    # Test predictions
    predictions = model.predict(X_test)
    assert len(predictions) == len(y_test), "Wrong number of predictions"
    assert all(p in [0, 1] for p in predictions), "Invalid prediction values"


def test_model_evaluation():
    """Test model evaluation"""
    # Generate data
    df = generate_dummy_dataset(samples=200, features=10, n_classes=2)
    X = df.drop("target", axis=1).values
    y = df["target"].values

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    # Train and evaluate
    model = RandomForestModel()
    model.train(X_train, y_train)
    metrics = model.evaluate(X_test, y_test)

    # Check metrics
    assert "accuracy" in metrics, "Accuracy metric missing"
    assert "precision" in metrics, "Precision metric missing"
    assert "recall" in metrics, "Recall metric missing"
    assert "f1" in metrics, "F1 metric missing"

    assert 0 <= metrics["accuracy"] <= 1, "Invalid accuracy value"
    assert 0 <= metrics["precision"] <= 1, "Invalid precision value"
    assert 0 <= metrics["recall"] <= 1, "Invalid recall value"
    assert 0 <= metrics["f1"] <= 1, "Invalid f1 value"


def test_predictions_shape():
    """Test prediction output shapes"""
    # Generate data
    df = generate_dummy_dataset(samples=100, features=10)
    X = df.drop("target", axis=1).values
    y = df["target"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    # Train model
    model = RandomForestModel()
    model.train(X_train, y_train)

    # Check prediction shapes
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)

    assert predictions.shape[0] == X_test.shape[0], "Wrong prediction shape"
    assert probabilities.shape[0] == X_test.shape[0], "Wrong probability shape"
    assert probabilities.shape[1] == 3, "Wrong number of classes"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
