"""
Configuration settings for the ML project
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
LOGS_DIR.mkdir(exist_ok=True)

# Model configuration
MODEL_NAME = "random_forest_classifier"
MODEL_PATH = MODELS_DIR / f"{MODEL_NAME}.pkl"
PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.pkl"

# Training configuration
RANDOM_STATE = 42
TEST_SIZE = 0.2
TRAIN_SIZE = 0.8
N_ESTIMATORS = 100
MAX_DEPTH = 10
MIN_SAMPLES_SPLIT = 5
MIN_SAMPLES_LEAF = 2

# Dataset configuration
DATASET_SAMPLES = 1000
N_FEATURES = 20
N_CLASSES = 3

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
