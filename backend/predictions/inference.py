"""
Hit Song Prediction Model - Inference Module

This module handles loading the pre-trained ML model and making predictions.
All 10 features are required as input - NO inference/guessing.
"""

import os
import pickle
import warnings
import numpy as np
from django.conf import settings

# Path to the trained model
MODEL_PATH = os.path.join(
    settings.BASE_DIR, 
    'predictions', 
    'ml_models', 
    'hit_song_model_selected.pkl'
)

# Cache the model in memory
MODEL = None


def load_model():
    """Load the trained model from disk (cached after first load)."""
    global MODEL
    if MODEL is None:
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')
                with open(MODEL_PATH, 'rb') as f:
                    MODEL = pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Model file not found at {MODEL_PATH}. "
                "Please ensure the model file exists."
            )
    return MODEL


def prepare_features(user_input: dict) -> np.ndarray:
    """
    Prepare feature array from user input.
    
    ALL 10 features are required - no inference, no guessing.
    This ensures accurate predictions.
    
    Required inputs:
    - duration_ms: int (song duration in milliseconds)
    - danceability: float (0.0 to 1.0)
    - energy: float (0.0 to 1.0)
    - valence: float (0.0 to 1.0, also called "mood")
    - acousticness: float (0.0 to 1.0)
    - instrumentalness: float (0.0 to 1.0)
    - explicit: float (0.0 or 1.0)
    - loudness: float (typically -60 to 0 dB)
    - tempo: float (BPM, typically 50 to 200)
    - mode: int (0 = minor, 1 = major)
    
    Returns:
        numpy.ndarray: Feature array with shape (1, 10)
    """
    # Feature order must match training data
    features = np.array([[
        float(user_input['duration_ms']),
        float(user_input['danceability']),
        float(user_input['energy']),
        float(user_input['valence']),
        float(user_input['acousticness']),
        float(user_input['instrumentalness']),
        float(user_input['explicit']),
        float(user_input['loudness']),
        float(user_input['tempo']),
        float(user_input['mode'])
    ]], dtype=np.float64)
    
    return features


def predict_song(features: np.ndarray) -> tuple:
    """
    Make a prediction using the trained model.
    
    Args:
        features: numpy.ndarray with shape (1, 10)
        
    Returns:
        tuple: (is_hit: bool, confidence: float as percentage)
    """
    model = load_model()
    
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')
        prediction = model.predict(features)[0]
        
        try:
            proba = model.predict_proba(features)[0]
            confidence = proba[1] if len(proba) > 1 else proba[0]
        except AttributeError:
            confidence = 0.5
    
    is_hit = bool(prediction)
    confidence_percent = round(confidence * 100, 2)
    
    return is_hit, confidence_percent
