#!/usr/bin/env python3
"""
Quick test script to verify predictions with actual dataset values.
This bypasses the inference approximations and uses exact values.
"""
import requests
import json

# API endpoint
API_URL = "http://localhost:8000/api/predict/"

# Example: "Comedy" song from dataset
# Dataset values:
# duration_ms: 230666 = 3.844 minutes
# danceability: 0.676
# energy: 0.461
# valence: 0.715
# acousticness: 0.0322 (very low, so is_acoustic = False)
# instrumentalness: 1.01e-06 (very low, so is_instrumental = False)
# explicit: 0 (False)
# loudness: -6.746
# tempo: 87.917
# mode: 0

test_data = {
    "title": "Comedy (Test)",
    "duration_minutes": 3.844,  # 230666 / 60000
    "danceability": 0.676,
    "energy": 0.461,
    "mood": 0.715,  # valence
    "is_acoustic": False,  # checkbox (will be overridden by acousticness)
    "is_instrumental": False,  # checkbox (will be overridden by instrumentalness)
    "is_explicit": False,
    # Use actual values from dataset (bypasses inference and boolean conversion)
    "loudness": -6.746,
    "tempo": 87.917,
    "mode": 0,
    "acousticness": 0.0322,  # Actual float value (not boolean!)
    "instrumentalness": 1.01e-06  # Actual float value (not boolean!)
}

print("Testing with actual dataset values...")
print(f"Song: {test_data['title']}")
print(f"Duration: {test_data['duration_minutes']} minutes")
print(f"Danceability: {test_data['danceability']}")
print(f"Energy: {test_data['energy']}")
print(f"Mood (valence): {test_data['mood']}")
print(f"Loudness: {test_data['loudness']} dB")
print(f"Tempo: {test_data['tempo']} BPM")
print(f"Mode: {test_data['mode']}")
print()

try:
    response = requests.post(API_URL, json=test_data)
    result = response.json()
    
    print("=" * 50)
    print("PREDICTION RESULT:")
    print("=" * 50)
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['confidence']}%")
    
    if 'debug' in result:
        print()
        print("Features sent to model:")
        for key, value in result['debug']['features_sent_to_model'].items():
            print(f"  {key}: {value}")
    
except requests.exceptions.ConnectionError:
    print("❌ Error: Could not connect to API.")
    print("Make sure Django server is running: python manage.py runserver")
except Exception as e:
    print(f"❌ Error: {e}")

