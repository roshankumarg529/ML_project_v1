"""
Unit tests for the FastAPI application
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import RANDOM_STATE, TEST_SIZE, MODEL_PATH, PREPROCESSOR_PATH, MODELS_DIR
from data_generator import generate_dummy_dataset
from model import RandomForestModel
import app as app_module
from sklearn.model_selection import train_test_split


@pytest.fixture(scope="module")
def client():
    """Create FastAPI test client with trained model"""
    # Train a model for testing
    df = generate_dummy_dataset(samples=100, features=20)
    X = df.drop("target", axis=1).values
    y = df["target"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    model = RandomForestModel()
    model.train(X_train, y_train)
    model.evaluate(X_test, y_test)
    model.save()

    # Load model into the app's global variable
    app_module.model = RandomForestModel.load()

    # Return test client
    return TestClient(app_module.app)


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ML Classification API"


def test_predict_single_endpoint(client):
    """Test single prediction endpoint"""
    features = [0.1] * 20
    response = client.post("/predict-single", json={"features": features})

    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "probabilities" in data
    assert "confidence" in data
    assert isinstance(data["prediction"], int)
    assert isinstance(data["confidence"], float)


def test_predict_batch_endpoint(client):
    """Test batch prediction endpoint"""
    features = [[0.1] * 20, [0.5] * 20, [0.9] * 20]
    response = client.post("/predict", json={"features": features})

    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert "probabilities" in data
    assert "num_samples" in data
    assert data["num_samples"] == 3
    assert len(data["predictions"]) == 3


def test_metrics_endpoint(client):
    """Test metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "accuracy" in data
    assert "precision" in data
    assert "recall" in data
    assert "f1" in data


def test_invalid_input(client):
    """Test with invalid input"""
    response = client.post("/predict-single", json={"invalid_key": "value"})

    assert response.status_code == 422  # Validation error in FastAPI


def test_missing_features(client):
    """Test with missing features"""
    response = client.post("/predict", json={})

    assert response.status_code == 422


def test_single_sample_reshape(client):
    """Test that single sample is properly reshaped"""
    features = [0.1] * 20
    response = client.post("/predict", json={"features": [features]})

    assert response.status_code == 200
    data = response.json()
    assert data["num_samples"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
