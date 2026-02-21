# ML Classification Project

Production-grade machine learning classification project using Random Forest model with Flask API for predictions.

## Project Structure

```
ML_project_v1/
├── src/                      # Source code
│   ├── config.py            # Configuration settings
│   ├── data_generator.py    # Dataset generation utilities
│   ├── model.py             # Random Forest model implementation
│   ├── train.py             # Training pipeline
│   └── app.py               # Flask API server
├── data/                     # Dataset directory
├── models/                   # Trained models and artifacts
├── tests/                    # Unit tests
├── .github/workflows/        # GitHub Actions workflows
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
└── README.md               # This file
```

## Features

- **Random Forest Classifier**: Multi-class classification model with 100 estimators
- **Production-Ready API**: Flask-based REST API for making predictions
- **Dummy Dataset Generation**: Generates 1000 samples with 20 features for 3 classes
- **Model Persistence**: Save and load trained models with preprocessing
- **Comprehensive Logging**: Detailed logging throughout the pipeline
- **Docker Support**: Ready for containerization and deployment
- **CI/CD Ready**: GitHub Actions workflow included

## Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

1. Clone the repository:
```bash
git clone https://github.com/roshankumarg529/ML_project_v1.git
cd ML_project_v1
```

2. Create a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/roshankumarg529/ML_project_v1.git
cd ML_project_v1

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Train the Model

```bash
cd src
python train.py
```

**Output:**
```
==================================================
Starting ML Training Pipeline
==================================================

[Step 1] Generating dummy dataset...
Generating dummy dataset with 1000 samples and 20 features
Dataset shape: (1000, 21)
Class distribution:
0    328
1    330
2    342
Name: target, dtype: int64
Dataset saved to ../data/dataset.csv

[Step 2] Preparing training and test data...
Training set size: 800
Test set size: 200

[Step 3] Training Random Forest model...
Starting training with 800 samples
Training completed successfully

[Step 4] Evaluating model...
Model Evaluation Metrics:
  accuracy: 0.9850
  precision: 0.9851
  recall: 0.9850
  f1: 0.9850

[Step 5] Saving model artifacts...
Model saved to ../models/random_forest_classifier.pkl
Preprocessor saved to ../models/preprocessor.pkl
Metrics saved to ../models/metrics.json

==================================================
Training completed successfully!
==================================================
```

This creates:
- `data/dataset.csv` - Training dataset
- `models/random_forest_classifier.pkl` - Trained model
- `models/preprocessor.pkl` - Feature scaler
- `models/metrics.json` - Evaluation metrics

### 3. Run FastAPI Server

```bash
cd src
python app.py
```

**Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
Loading model...
Model loaded from ../models/random_forest_classifier.pkl
Preprocessor loaded from ../models/preprocessor.pkl
FastAPI server started
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:5000
```

Server is now running at `http://localhost:5000`

### 4. API Documentation

Open browser and visit:
- **Interactive Docs**: http://localhost:5000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:5000/redoc (ReDoc)

### 5. Make Predictions

#### Health Check
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ML Classification API",
  "version": "1.0.0"
}
```

#### Single Prediction
```bash
curl -X POST http://localhost:5000/predict-single \
  -H "Content-Type: application/json" \
  -d '{"features": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]}'
```

**Response:**
```json
{
  "prediction": 1,
  "probabilities": [0.12, 0.75, 0.13],
  "confidence": 0.75
}
```

#### Batch Predictions
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [
      [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
      [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
      [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]
    ]
  }'
```

**Response:**
```json
{
  "predictions": [1, 2, 0],
  "probabilities": [
    [0.12, 0.75, 0.13],
    [0.33, 0.34, 0.33],
    [0.88, 0.08, 0.04]
  ],
  "num_samples": 3
}
```

#### Get Model Metrics
```bash
curl http://localhost:5000/metrics
```

**Response:**
```json
{
  "accuracy": 0.985,
  "precision": 0.9851,
  "recall": 0.985,
  "f1": 0.9850
}
```

### 6. Run Tests

```bash
# From project root
pytest tests/ -v
```

**Output:**
```
tests/test_model.py::test_data_generation PASSED
tests/test_model.py::test_model_initialization PASSED
tests/test_model.py::test_model_training PASSED
tests/test_model.py::test_model_evaluation PASSED
tests/test_model.py::test_predictions_shape PASSED
tests/test_api.py::test_health_endpoint PASSED
tests/test_api.py::test_predict_single_endpoint PASSED
tests/test_api.py::test_predict_batch_endpoint PASSED
tests/test_api.py::test_metrics_endpoint PASSED
tests/test_api.py::test_invalid_input PASSED

=============== 10 passed in 2.34s ===============
```

## Docker Usage

### Build Docker Image
```bash
docker build -t ml-classifier:latest .
```

### Run Container
```bash
docker run -p 5000:5000 ml-classifier:latest
```

### Or Use Docker Compose
```bash
docker-compose up
```

Access API at `http://localhost:5000`

## Project Workflow Summary

```
1. Setup Environment
   └─ python -m venv venv
   └─ pip install -r requirements.txt

2. Train Model
   └─ python src/train.py
   └─ Generates dataset, trains model, saves artifacts

3. Start API Server
   └─ python src/app.py
   └─ Available at http://localhost:5000

4. Make Predictions
   └─ Via curl, Swagger UI, or any HTTP client

5. Run Tests (Optional)
   └─ pytest tests/ -v

6. Deploy (Optional)
   └─ docker build & docker run
   └─ Or use GitHub Actions for CI/CD
```

## Model Configuration

Edit `src/config.py` to customize:
- Number of samples and features
- Random Forest parameters (n_estimators, max_depth, etc.)
- Train/test split ratio
- Model paths and logging level

## Docker Deployment

Build Docker image:
```bash
docker build -t ml-classifier:latest .
```

Run container:
```bash
docker run -p 5000:5000 ml-classifier:latest
```

Using Docker Compose:
```bash
docker-compose up
```

## Testing

Run tests:
```bash
python -m pytest tests/
```

## Performance Metrics

The trained model achieves the following metrics on the test set:
- Accuracy: ~95%+
- Precision: ~95%+
- Recall: ~95%+
- F1-Score: ~95%+

## CI/CD Pipeline

GitHub Actions workflow automatically:
- Runs tests on push/PR
- Builds Docker image
- Pushes to Docker registry

See `.github/workflows/` for workflow configuration.

## Production Considerations

- Model is saved with preprocessing scaler for consistent predictions
- Logging is configured for debugging and monitoring
- API includes health check endpoint for load balancers
- Error handling for invalid inputs
- Extensible architecture for adding new models/features

## License

MIT License
