"""
Random Forest classifier model for classification task
"""
import logging
import pickle
import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import json
from pathlib import Path
from config import (
    MODEL_PATH, PREPROCESSOR_PATH, RANDOM_STATE, TEST_SIZE,
    N_ESTIMATORS, MAX_DEPTH, MIN_SAMPLES_SPLIT, MIN_SAMPLES_LEAF, MODELS_DIR
)

logger = logging.getLogger(__name__)


class RandomForestModel:
    """
    Random Forest classifier for binary/multi-class classification
    """
    
    def __init__(self, n_estimators=N_ESTIMATORS, max_depth=MAX_DEPTH, 
                 min_samples_split=MIN_SAMPLES_SPLIT, min_samples_leaf=MIN_SAMPLES_LEAF,
                 random_state=RANDOM_STATE):
        """
        Initialize Random Forest model with parameters
        """
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.metrics = {}
        self.feature_names = None
        
        logger.info("RandomForestModel initialized")
    
    def train(self, X_train, y_train):
        """
        Train the model on training data
        
        Args:
            X_train: Training features
            y_train: Training labels
        """
        logger.info(f"Starting training with {X_train.shape[0]} samples")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        logger.info("Training completed successfully")
    
    def predict(self, X):
        """
        Make predictions on new data
        
        Args:
            X: Features to predict on
            
        Returns:
            Array of predictions
        """
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X):
        """
        Get prediction probabilities
        
        Args:
            X: Features to predict on
            
        Returns:
            Array of prediction probabilities
        """
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model on test data and store metrics
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Dictionary of evaluation metrics
        """
        y_pred = self.predict(X_test)
        
        self.metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
            "f1": float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
        }
        
        logger.info(f"Model Evaluation Metrics:")
        for metric, value in self.metrics.items():
            logger.info(f"  {metric}: {value:.4f}")
        
        return self.metrics
    
    def save(self, model_path=None, preprocessor_path=None, metrics_path=None):
        """
        Save model and preprocessor to disk
        
        Args:
            model_path: Path to save the model
            preprocessor_path: Path to save the preprocessor
            metrics_path: Path to save the metrics
        """
        if model_path is None:
            model_path = MODEL_PATH
        if preprocessor_path is None:
            preprocessor_path = PREPROCESSOR_PATH
        if metrics_path is None:
            metrics_path = MODELS_DIR / "metrics.json"
        
        MODELS_DIR.mkdir(exist_ok=True)
        
        # Save model
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        logger.info(f"Model saved to {model_path}")
        
        # Save preprocessor
        with open(preprocessor_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        logger.info(f"Preprocessor saved to {preprocessor_path}")
        
        # Save metrics
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=4)
        logger.info(f"Metrics saved to {metrics_path}")
    
    @staticmethod
    def load(model_path=None, preprocessor_path=None, metrics_path=None):
        """
        Load model and preprocessor from disk
        
        Args:
            model_path: Path to the saved model
            preprocessor_path: Path to the saved preprocessor
            metrics_path: Path to the saved metrics
            
        Returns:
            RandomForestModel instance with loaded weights
        """
        if model_path is None:
            model_path = MODEL_PATH
        if preprocessor_path is None:
            preprocessor_path = PREPROCESSOR_PATH
        if metrics_path is None:
            metrics_path = MODELS_DIR / "metrics.json"
        
        # Create new instance
        model_instance = RandomForestModel()
        
        # Load model
        with open(model_path, 'rb') as f:
            model_instance.model = pickle.load(f)
        logger.info(f"Model loaded from {model_path}")
        
        # Load preprocessor
        with open(preprocessor_path, 'rb') as f:
            model_instance.scaler = pickle.load(f)
        logger.info(f"Preprocessor loaded from {preprocessor_path}")
        
        # Load metrics if available
        try:
            with open(metrics_path, 'r') as f:
                model_instance.metrics = json.load(f)
            logger.info(f"Metrics loaded from {metrics_path}")
        except FileNotFoundError:
            logger.warning(f"Metrics file not found at {metrics_path}")
            model_instance.metrics = {}
        
        return model_instance
