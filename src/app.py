"""
FastAPI server for serving predictions from the trained model
"""
import logging
import sys
from pathlib import Path
from typing import List
from pydantic import BaseModel
import numpy as np
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import LOG_LEVEL, LOG_FORMAT, MODEL_PATH, PREPROCESSOR_PATH
from model import RandomForestModel

# Setup logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# Global model instance
model = None


# Request/Response models
class PredictRequest(BaseModel):
    """Request model for batch predictions"""
    features: List[List[float]]


class PredictSingleRequest(BaseModel):
    """Request model for single prediction"""
    features: List[float]


class PredictResponse(BaseModel):
    """Response model for batch predictions"""
    predictions: List[int]
    probabilities: List[List[float]]
    num_samples: int


class PredictSingleResponse(BaseModel):
    """Response model for single prediction"""
    prediction: int
    probabilities: List[float]
    confidence: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str


class MetricsResponse(BaseModel):
    """Metrics response"""
    accuracy: float
    precision: float
    recall: float
    f1: float


class ErrorResponse(BaseModel):
    """Error response"""
    error: str


def load_model_startup():
    """
    Load the trained model on startup
    """
    global model
    try:
        if MODEL_PATH.exists() and PREPROCESSOR_PATH.exists():
            model = RandomForestModel.load()
            logger.info("Model loaded successfully")
        else:
            logger.warning("Model files not found. Please run training first.")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Loading model...")
    load_model_startup()
    logger.info("FastAPI server started")
    
    yield
    
    # Shutdown
    logger.info("FastAPI server shutting down")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="ML Classification API",
    description="Random Forest classifier API for multi-class predictions",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint
    """
    return HealthResponse(
        status="healthy",
        service="ML Classification API",
        version="1.0.0"
    )


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    Make predictions on provided features.
    
    Expected request format:
    ```json
    {
        "features": [[1.2, 2.3, ...], [4.5, 5.6, ...]]
    }
    ```
    """
    try:
        if model is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model not loaded. Please run training first."
            )
        
        features = np.array(request.features)
        
        # Validate input shape
        if features.ndim == 1:
            features = features.reshape(1, -1)
        
        # Make predictions
        predictions = model.predict(features)
        probabilities = model.predict_proba(features)
        
        return PredictResponse(
            predictions=predictions.tolist(),
            probabilities=probabilities.tolist(),
            num_samples=len(predictions)
        )
        
    except ValueError as e:
        logger.error(f"Invalid input: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.post("/predict-single", response_model=PredictSingleResponse)
async def predict_single(request: PredictSingleRequest):
    """
    Make a prediction on a single sample.
    
    Expected request format:
    ```json
    {
        "features": [1.2, 2.3, 3.4, ...]
    }
    ```
    """
    try:
        if model is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model not loaded. Please run training first."
            )
        
        features = np.array(request.features).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        return PredictSingleResponse(
            prediction=int(prediction),
            probabilities=probabilities.tolist(),
            confidence=float(max(probabilities))
        )
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Get model evaluation metrics
    """
    try:
        if model is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model not loaded"
            )
        
        if model.metrics:
            return MetricsResponse(**model.metrics)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Metrics not available"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/docs", include_in_schema=False)
async def get_docs():
    """
    Swagger UI documentation
    """
    pass


if __name__ == "__main__":
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        log_level="info"
    )
