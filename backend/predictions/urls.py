"""
URL Configuration for Hit Song Prediction API

Primary endpoints:
- /api/predict/spotify/ - Predict from Spotify track (uses dataset for audio features)
- /api/dataset/search/ - Search songs in training dataset (guaranteed to work)
"""

from django.urls import path
from . import views

urlpatterns = [
    # Predict from Spotify track
    path('predict/spotify/', views.predict_from_spotify, name='predict_spotify'),
    
    # Search endpoints
    path('spotify/search/', views.search_spotify, name='search_spotify'),
    path('dataset/search/', views.search_dataset, name='search_dataset'),
    
    # Manual prediction (with all features)
    path('predict/manual/', views.predict_manual, name='predict_manual'),
    path('predict/', views.predict_manual, name='predict'),  # Legacy
    
    # Health check
    path('health/', views.health_check, name='health'),
]
