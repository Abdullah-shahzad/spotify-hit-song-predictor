#!/usr/bin/env python3
"""
Retrain the Hit Song Prediction Model with ONLY user-providable features.

This is the PERMANENT FIX for the inference problem.

The original model used 10 features including loudness, tempo, and mode
which cannot be accurately provided by users. This script retrains the model
using only the 5 features that users CAN provide.

Features used:
1. duration_ms - User provides duration in minutes
2. danceability - User provides via slider
3. energy - User provides via slider
4. valence - User provides via slider (called "mood")
5. explicit - User provides via checkbox

Features REMOVED (cannot be accurately provided by users):
- loudness (requires audio analysis)
- tempo (requires audio analysis)
- mode (requires audio analysis)
- acousticness (continuous value, not boolean)
- instrumentalness (continuous value, not boolean)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import os

def load_and_prepare_data(csv_path='cleaned_data.csv', hit_threshold=50):
    """Load dataset and prepare for training."""
    print("Loading dataset...")
    df = pd.read_csv(csv_path)
    print(f"Total samples: {len(df)}")
    
    # Create target variable (hit = 1 if popularity >= threshold)
    df['is_hit'] = (df['popularity'] >= hit_threshold).astype(int)
    
    hit_count = df['is_hit'].sum()
    flop_count = len(df) - hit_count
    print(f"Hit threshold: {hit_threshold}")
    print(f"Hits: {hit_count} ({hit_count/len(df)*100:.1f}%)")
    print(f"Flops: {flop_count} ({flop_count/len(df)*100:.1f}%)")
    
    return df

def train_simplified_model(df):
    """Train model with only user-providable features."""
    
    # ONLY use features that users can accurately provide
    feature_columns = [
        'duration_ms',
        'danceability',
        'energy',
        'valence',      # User calls this "mood"
        'explicit'      # Boolean, user can provide
    ]
    
    print(f"\nUsing {len(feature_columns)} features: {feature_columns}")
    
    # Prepare features and target
    X = df[feature_columns].copy()
    y = df['is_hit']
    
    # Convert explicit to numeric if needed
    X['explicit'] = X['explicit'].astype(float)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train Random Forest (same type as original model)
    print("\nTraining RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=20,           # Slightly less depth to prevent overfitting
        min_samples_split=10,
        min_samples_leaf=5,
        max_features='sqrt',
        bootstrap=True,
        oob_score=True,         # Enable OOB score for validation
        random_state=42,
        n_jobs=-1,
        class_weight='balanced' # Handle imbalanced classes
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    print("\n" + "="*50)
    print("MODEL EVALUATION")
    print("="*50)
    
    # Training accuracy
    train_pred = model.predict(X_train)
    train_acc = accuracy_score(y_train, train_pred)
    print(f"\nTraining Accuracy: {train_acc:.4f}")
    
    # Test accuracy
    test_pred = model.predict(X_test)
    test_acc = accuracy_score(y_test, test_pred)
    print(f"Test Accuracy: {test_acc:.4f}")
    
    # OOB Score (out-of-bag, good for detecting overfitting)
    print(f"OOB Score: {model.oob_score_:.4f}")
    
    # Overfitting check
    overfit_gap = train_acc - test_acc
    print(f"\nOverfitting Check:")
    print(f"  Train-Test Gap: {overfit_gap:.4f}")
    if overfit_gap < 0.05:
        print("  ✓ Model is NOT overfitted")
    elif overfit_gap < 0.10:
        print("  ⚠ Slight overfitting, but acceptable")
    else:
        print("  ❌ Model may be overfitted")
    
    # Cross-validation
    print("\nCross-Validation (5-fold):")
    cv_scores = cross_val_score(model, X, y, cv=5)
    print(f"  Scores: {cv_scores}")
    print(f"  Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
    
    # Classification report
    print("\nClassification Report (Test Set):")
    print(classification_report(y_test, test_pred, target_names=['FLOP', 'HIT']))
    
    # Feature importance
    print("\nFeature Importances:")
    for name, importance in sorted(zip(feature_columns, model.feature_importances_), 
                                    key=lambda x: x[1], reverse=True):
        print(f"  {name}: {importance:.4f}")
    
    return model, feature_columns

def save_model(model, feature_columns, output_path='hit_song_model_simplified.pkl'):
    """Save the trained model."""
    model_data = {
        'model': model,
        'feature_columns': feature_columns,
        'version': '2.0-simplified',
        'description': 'Trained with only user-providable features'
    }
    
    with open(output_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"\n✓ Model saved to: {output_path}")
    print(f"  Features: {feature_columns}")
    return output_path

def test_prediction(model, feature_columns):
    """Test the model with sample input."""
    print("\n" + "="*50)
    print("TESTING WITH SAMPLE INPUT")
    print("="*50)
    
    # Comedy song values (actual dataset values)
    test_input = {
        'duration_ms': 230666,
        'danceability': 0.676,
        'energy': 0.461,
        'valence': 0.715,
        'explicit': 0.0
    }
    
    print("\nInput (Comedy song from dataset):")
    for k, v in test_input.items():
        print(f"  {k}: {v}")
    
    # Create feature array
    features = np.array([[test_input[col] for col in feature_columns]])
    
    # Predict
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]
    
    result = "HIT" if prediction == 1 else "FLOP"
    confidence = probability[1] * 100  # Probability of being a hit
    
    print(f"\nPrediction: {result}")
    print(f"Confidence: {confidence:.2f}%")
    print(f"Expected: HIT (popularity 73 in dataset)")

def main():
    print("="*60)
    print("HIT SONG PREDICTION MODEL - RETRAINING")
    print("Using ONLY user-providable features")
    print("="*60)
    
    # Check if dataset exists
    if not os.path.exists('cleaned_data.csv'):
        print("Error: cleaned_data.csv not found!")
        print("Please ensure the dataset is in the current directory.")
        return
    
    # Load data
    df = load_and_prepare_data('cleaned_data.csv', hit_threshold=50)
    
    # Train model
    model, feature_columns = train_simplified_model(df)
    
    # Test prediction
    test_prediction(model, feature_columns)
    
    # Save model
    save_path = save_model(model, feature_columns, 'hit_song_model_simplified.pkl')
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. Copy the new model to the backend:
   cp hit_song_model_simplified.pkl backend/predictions/ml_models/

2. Update inference.py to use only 5 features
   (I will provide the updated code)

3. Restart Django server

The new model uses ONLY features users can provide:
- duration_ms (from duration_minutes)
- danceability (slider)
- energy (slider)
- valence/mood (slider)
- explicit (checkbox)

NO MORE inference needed for loudness, tempo, mode, etc.!
""")

if __name__ == '__main__':
    main()

