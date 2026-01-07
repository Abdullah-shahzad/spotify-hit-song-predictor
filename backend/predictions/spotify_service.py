"""
Spotify API Integration Service

Fetches track info from Spotify and audio features from local dataset.
Note: Spotify's audio-features endpoint requires Extended Quota Mode approval.
This implementation uses the local dataset for audio features.
"""

import os
import time
import requests
import logging
import pandas as pd
from typing import Dict, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

# Spotify API endpoints
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

# Spotify credentials
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID', 'e0e4dc1563804fbfb8cfa357c92b2812')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET', '2e59eec2762a4d879cefd03f7abee4eb')

# Local dataset path
DATASET_PATH = os.path.join(settings.BASE_DIR, '..', 'cleaned_data.csv')

# Cache for dataset
_dataset_cache: Optional[pd.DataFrame] = None


def get_dataset() -> pd.DataFrame:
    """Load and cache the dataset."""
    global _dataset_cache
    if _dataset_cache is None:
        try:
            _dataset_cache = pd.read_csv(DATASET_PATH)
            logger.info(f"Loaded dataset with {len(_dataset_cache)} tracks")
        except FileNotFoundError:
            logger.error(f"Dataset not found at {DATASET_PATH}")
            _dataset_cache = pd.DataFrame()
    return _dataset_cache


class SpotifyService:
    """Service for interacting with Spotify Web API and local dataset."""
    
    def __init__(self):
        self.access_token: Optional[str] = None
        self.token_expires_at: float = 0
        
    def _get_access_token(self) -> str:
        """Get or refresh Spotify access token using Client Credentials flow."""
        if self.access_token and time.time() < (self.token_expires_at - 60):
            return self.access_token
        
        if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
            raise ValueError("Spotify credentials not configured.")
        
        logger.info("Requesting new Spotify access token...")
        
        auth_response = requests.post(
            SPOTIFY_TOKEN_URL,
            data={'grant_type': 'client_credentials'},
            auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        
        if auth_response.status_code != 200:
            error_msg = auth_response.json().get('error_description', 'Unknown error')
            raise Exception(f"Failed to get Spotify token: {error_msg}")
        
        token_data = auth_response.json()
        self.access_token = token_data['access_token']
        self.token_expires_at = time.time() + token_data.get('expires_in', 3600)
        
        logger.info("Spotify access token obtained successfully")
        return self.access_token
    
    def _make_request(self, endpoint: str) -> Dict:
        """Make authenticated request to Spotify API."""
        token = self._get_access_token()
        
        url = f"{SPOTIFY_API_BASE}{endpoint}"
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            raise ValueError("Track not found on Spotify.")
        elif response.status_code == 401:
            self.access_token = None
            token = self._get_access_token()
            headers['Authorization'] = f'Bearer {token}'
            response = requests.get(url, headers=headers, timeout=10)
        
        response.raise_for_status()
        return response.json()
    
    def get_track_info(self, track_id: str) -> Dict:
        """Get track metadata from Spotify."""
        track_info = self._make_request(f'/tracks/{track_id}')
        
        return {
            'track_id': track_id,
            'title': track_info['name'],
            'artist': ', '.join([artist['name'] for artist in track_info['artists']]),
            'album': track_info['album']['name'],
            'album_image': track_info['album']['images'][0]['url'] if track_info['album']['images'] else None,
            'spotify_url': track_info['external_urls']['spotify'],
            'preview_url': track_info.get('preview_url'),
            'popularity': track_info.get('popularity', 0),
            'duration_ms': track_info['duration_ms'],
            'explicit': 1 if track_info.get('explicit', False) else 0,
        }
    
    def get_audio_features_from_dataset(self, track_name: str, artist_name: str) -> Optional[Dict]:
        """
        Look up audio features from database (much faster than CSV).
        
        Args:
            track_name: Track title
            artist_name: Artist name(s)
            
        Returns:
            Dict with audio features or None if not found
        """
        from .models import Song
        
        # Normalize for matching
        track_clean = track_name.strip()
        artist_clean = artist_name.strip()
        artist_first = artist_clean.split(',')[0].strip()
        
        # Try exact match first (fastest - uses database indexes)
        song = Song.objects.filter(
            track_name__iexact=track_clean,
            artists__icontains=artist_first
        ).first()
        
        if not song:
            # Try case-insensitive partial match on track name
            song = Song.objects.filter(
                track_name__icontains=track_clean,
                artists__icontains=artist_first
            ).first()
        
        if not song:
            return None
        
        return {
            'duration_ms': int(song.duration_ms),
            'danceability': float(song.danceability),
            'energy': float(song.energy),
            'valence': float(song.valence),
            'acousticness': float(song.acousticness),
            'instrumentalness': float(song.instrumentalness),
            'loudness': float(song.loudness),
            'tempo': float(song.tempo),
            'mode': int(song.mode),
            'explicit': 1 if song.explicit else 0,
            'source': 'dataset',
            'track_genre': str(song.track_genre or 'unknown'),
            'popularity': int(song.popularity or 0),
            'is_hit_in_dataset': bool(song.is_hit),
            'title': song.track_name,
            'artist': song.artists,
            'album': song.album_name or 'Unknown',
        }
    
    def get_audio_features(self, track_id: str) -> Dict:
        """
        Get audio features for a track.
        
        First tries to get from Spotify API, falls back to dataset.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Dict with audio features and metadata
        """
        # Get track info from Spotify
        track_info = self.get_track_info(track_id)
        
        # Try to get audio features from dataset first
        dataset_features = self.get_audio_features_from_dataset(
            track_info['title'], 
            track_info['artist']
        )
        
        if dataset_features:
            # Found in dataset - use these features
            logger.info(f"Found '{track_info['title']}' in dataset")
            
            # Merge with track info
            result = {
                **track_info,
                **dataset_features,
            }
            return result
        
        # Not in dataset - try Spotify API
        try:
            features = self._make_request(f'/audio-features/{track_id}')
            
            if features:
                result = {
                    **track_info,
                    'duration_ms': features['duration_ms'],
                    'danceability': features['danceability'],
                    'energy': features['energy'],
                    'valence': features['valence'],
                    'acousticness': features['acousticness'],
                    'instrumentalness': features['instrumentalness'],
                    'loudness': features['loudness'],
                    'tempo': features['tempo'],
                    'mode': features['mode'],
                    'source': 'spotify_api',
                }
                return result
        except Exception as e:
            logger.warning(f"Spotify audio-features failed: {e}")
        
        # Neither available
        raise ValueError(
            f"Track '{track_info['title']}' by {track_info['artist']} is not in our dataset. "
            "The Spotify audio-features API requires Extended Quota Mode approval. "
            "Please try a song from the training dataset, or use the manual prediction endpoint."
        )
    
    def search_tracks(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for tracks on Spotify."""
        from .models import Song
        
        encoded_query = requests.utils.quote(query)
        endpoint = f'/search?q={encoded_query}&type=track&limit={limit}'
        response = self._make_request(endpoint)
        
        tracks = []
        for track in response['tracks']['items']:
            track_name = track['name']
            artist_name = ', '.join([artist['name'] for artist in track['artists']])
            artist_first = artist_name.split(',')[0].strip()
            
            # Check if track is in database (much faster than CSV)
            in_dataset = Song.objects.filter(
                track_name__iexact=track_name.strip(),
                artists__icontains=artist_first
            ).exists()
            
            tracks.append({
                'id': track['id'],
                'title': track_name,
                'artist': artist_name,
                'album': track['album']['name'],
                'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'duration_ms': track['duration_ms'],
                'explicit': track.get('explicit', False),
                'preview_url': track.get('preview_url'),
                'spotify_url': track['external_urls']['spotify'],
                'popularity': track.get('popularity', 0),
                'in_dataset': in_dataset,
            })
        
        # Sort to show tracks in dataset first
        tracks.sort(key=lambda x: (not x['in_dataset'], -x['popularity']))
        
        return tracks
    
    def search_dataset(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for tracks directly in the database (much faster than CSV).
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of tracks from database
        """
        from .models import Song
        from django.db.models import Q
        
        # Use database queries with indexes (much faster than pandas)
        songs = Song.objects.filter(
            Q(track_name__icontains=query) | Q(artists__icontains=query)
        ).order_by('-popularity')[:limit]
        
        results = []
        for song in songs:
            results.append({
                'id': song.track_id or '',
                'title': song.track_name or '',
                'artist': song.artists or '',
                'album': song.album_name or 'Unknown',
                'album_image': None,
                'duration_ms': int(song.duration_ms),
                'explicit': bool(song.explicit),
                'popularity': int(song.popularity or 0),
                'genre': str(song.track_genre or 'unknown'),
                'in_dataset': True,
            })
        
        return results
    
    @staticmethod
    def extract_track_id(input_str: str) -> str:
        """Extract Spotify track ID from various input formats."""
        input_str = input_str.strip()
        
        if 'open.spotify.com/track/' in input_str:
            return input_str.split('track/')[-1].split('?')[0].split('/')[0]
        
        if input_str.startswith('spotify:track:'):
            return input_str.split(':')[-1]
        
        return input_str


# Singleton instance
_spotify_service: Optional[SpotifyService] = None


def get_spotify_service() -> SpotifyService:
    """Get singleton Spotify service instance."""
    global _spotify_service
    if _spotify_service is None:
        _spotify_service = SpotifyService()
    return _spotify_service
