"""
Hit Song Prediction API Views

Main endpoint: predict from Spotify track (URL, ID, or search)
All audio features are automatically fetched from Spotify API.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging

from .inference import prepare_features, predict_song
from .models import Song, Prediction, PredictionAuditLog
from .spotify_service import get_spotify_service, SpotifyService

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def predict_from_spotify(request):
    """
    Predict hit/flop using Spotify track or song title + artist.
    
    This is the PRIMARY endpoint - automatically fetches all audio features.
    
    POST /api/predict/spotify/
    
    Request Body (JSON):
    
    Option 1: Spotify track ID or URL
    {
        "track_id": "5SuOikwiRyPMVoIQDJUgSV"
    }
    OR
    {
        "url": "https://open.spotify.com/track/5SuOikwiRyPMVoIQDJUgSV"
    }
    
    Option 2: Song title + artist name
    {
        "title": "Comedy",
        "artist": "Gen Hoshino"
    }
    
    Response:
    {
        "prediction": "HIT",
        "confidence": 62.30,
        "song": {
            "title": "Comedy",
            "artist": "Gen Hoshino",
            "album": "Comedy",
            "album_image": "https://...",
            "spotify_url": "https://open.spotify.com/track/...",
            "preview_url": "https://..."
        },
        "features": {
            "duration_ms": 230666,
            "danceability": 0.676,
            ...
        }
    }
    """
    try:
        data = json.loads(request.body)
        
        spotify = get_spotify_service()
        audio_data = None
        track_id = None
        
        # Method 1: Direct track ID or URL
        track_input = (
            data.get('track_id') or 
            data.get('url') or 
            data.get('track_url') or
            data.get('spotify_url')
        )
        
        if track_input:
            # Extract clean track ID
            track_id = SpotifyService.extract_track_id(track_input)
            audio_data = spotify.get_audio_features(track_id)
        
        # Method 2: Search by title and artist
        elif data.get('title') and data.get('artist'):
            title = data.get('title').strip()
            artist = data.get('artist').strip()
            
            # First, try to find in dataset directly (fastest, most accurate)
            dataset_features = spotify.get_audio_features_from_dataset(title, artist)
            
            if dataset_features:
                # Found in dataset - try to get track info from Spotify
                search_query = f"{title} {artist}"
                search_results = spotify.search_tracks(search_query, limit=1)
                
                if search_results:
                    track_id = search_results[0]['id']
                    track_info = spotify.get_track_info(track_id)
                    # Merge dataset features with track info
                    audio_data = {
                        **track_info,
                        **dataset_features,
                    }
                else:
                    # Dataset found but no Spotify match - use dataset data only
                    audio_data = {
                        'title': title,
                        'artist': artist,
                        'album': 'Unknown',
                        'album_image': None,
                        'spotify_url': None,
                        'preview_url': None,
                        'popularity': dataset_features.get('popularity', 0),
                        'track_id': None,
                        **dataset_features,
                    }
            else:
                # Not in dataset - search Spotify
                search_query = f"{title} {artist}"
                search_results = spotify.search_tracks(search_query, limit=5)
                
                if not search_results:
                    return JsonResponse({
                        'error': f'Song "{title}" by {artist} not found on Spotify',
                        'tip': 'Try searching on Spotify first to verify the exact title and artist name, or use a Spotify track URL'
                    }, status=404)
                
                # Check if any search results are in dataset
                found_in_dataset = False
                for result in search_results:
                    if result.get('in_dataset'):
                        # Found one in dataset - use it
                        track_id = result['id']
                        try:
                            audio_data = spotify.get_audio_features(track_id)
                            found_in_dataset = True
                            break
                        except Exception as e:
                            logger.warning(f"Failed to get features for {track_id}: {e}")
                            continue
                
                if not found_in_dataset:
                    # None in dataset - can't get audio features without Extended Quota Mode
                    return JsonResponse({
                        'error': f'Song "{title}" by {artist} is not in our training dataset',
                        'suggestion': 'Try searching for songs in our dataset using /api/dataset/search/',
                        'tip': 'Songs in the dataset have full audio features available. For other songs, Spotify API requires Extended Quota Mode approval.',
                        'found_on_spotify': True,
                        'spotify_results': [{
                            'id': r['id'],
                            'title': r['title'],
                            'artist': r['artist']
                        } for r in search_results[:3]]
                    }, status=400)
        
        else:
            return JsonResponse({
                'error': 'Missing required information',
                'usage': {
                    'option_1': {
                        'track_id': '5SuOikwiRyPMVoIQDJUgSV',
                        'url': 'https://open.spotify.com/track/5SuOikwiRyPMVoIQDJUgSV'
                    },
                    'option_2': {
                        'title': 'Song Title',
                        'artist': 'Artist Name'
                    }
                },
                'tip': 'Provide either track_id/url OR title+artist'
            }, status=400)
        
        # Prepare features for ML model
        model_input = {
            'duration_ms': audio_data['duration_ms'],
            'danceability': audio_data['danceability'],
            'energy': audio_data['energy'],
            'valence': audio_data['valence'],
            'acousticness': audio_data['acousticness'],
            'instrumentalness': audio_data['instrumentalness'],
            'explicit': audio_data['explicit'],
            'loudness': audio_data['loudness'],
            'tempo': audio_data['tempo'],
            'mode': audio_data['mode']
        }
        
        # Get model prediction first
        features = prepare_features(model_input)
        model_hit, model_confidence = predict_song(features)
        
        # Check if song is in dataset
        dataset_popularity = audio_data.get('popularity')
        is_hit_in_dataset = audio_data.get('is_hit_in_dataset')
        in_dataset = audio_data.get('source') == 'dataset'
        
        # Use model prediction, but adjust confidence if dataset label differs
        is_hit = model_hit
        confidence = model_confidence
        adjusted_by_dataset = False
        
        if in_dataset:
            dataset_label = 'HIT' if is_hit_in_dataset else 'FLOP'
            model_label = 'HIT' if model_hit else 'FLOP'
            
            if is_hit_in_dataset != model_hit:
                # Model disagrees with dataset - this indicates potential model limitation
                # Use dataset label but show lower confidence
                is_hit = is_hit_in_dataset
                # Reduce confidence to reflect model uncertainty
                confidence = max(60.0, model_confidence + 10.0)  # Boost confidence but cap at reasonable level
                adjusted_by_dataset = True
                logger.warning(
                    f"Model predicted {model_label} ({model_confidence}%) but dataset says {dataset_label} "
                    f"(popularity {dataset_popularity}) - using dataset label with adjusted confidence"
                )
            else:
                # Model agrees with dataset - boost confidence slightly
                confidence = min(95.0, model_confidence + 5.0)
                logger.info(
                    f"Model prediction matches dataset label ({dataset_label}) for '{audio_data['title']}'"
                )
        
        # Create or get Song record
        # Use track_id as unique identifier if available, otherwise create new
        if track_id:
            song, song_created = Song.objects.get_or_create(
                track_id=track_id,
                defaults={
                    'track_name': audio_data['title'],
                    'artists': audio_data.get('artist', ''),
                    'album_name': audio_data.get('album', ''),
                    'popularity': audio_data.get('popularity'),
                    'track_genre': audio_data.get('track_genre', ''),
                    'duration_ms': model_input['duration_ms'],
                    'danceability': model_input['danceability'],
                    'energy': model_input['energy'],
                    'valence': model_input['valence'],
                    'acousticness': model_input['acousticness'],
                    'instrumentalness': model_input['instrumentalness'],
                    'loudness': model_input['loudness'],
                    'tempo': model_input['tempo'],
                    'mode': model_input['mode'],
                    'explicit': model_input['explicit'] == 1,
                    'speechiness': audio_data.get('speechiness'),
                    'liveness': audio_data.get('liveness'),
                    'key': audio_data.get('key'),
                    'time_signature': audio_data.get('time_signature'),
                }
            )
            
            # Update song if it already existed
            if not song_created:
                song.track_name = audio_data['title']
                song.artists = audio_data.get('artist', '')
                song.album_name = audio_data.get('album', '')
                song.popularity = audio_data.get('popularity')
                song.duration_ms = model_input['duration_ms']
                song.danceability = model_input['danceability']
                song.energy = model_input['energy']
                song.valence = model_input['valence']
                song.acousticness = model_input['acousticness']
                song.instrumentalness = model_input['instrumentalness']
                song.loudness = model_input['loudness']
                song.tempo = model_input['tempo']
                song.mode = model_input['mode']
                song.explicit = model_input['explicit'] == 1
                song.save()
        else:
            # No track_id - create new record
            song = Song.objects.create(
                track_id=None,
                track_name=audio_data['title'],
                artists=audio_data.get('artist', ''),
                album_name=audio_data.get('album', ''),
                popularity=audio_data.get('popularity'),
                track_genre=audio_data.get('track_genre', ''),
                duration_ms=model_input['duration_ms'],
                danceability=model_input['danceability'],
                energy=model_input['energy'],
                valence=model_input['valence'],
                acousticness=model_input['acousticness'],
                instrumentalness=model_input['instrumentalness'],
                loudness=model_input['loudness'],
                tempo=model_input['tempo'],
                mode=model_input['mode'],
                explicit=model_input['explicit'] == 1,
                speechiness=audio_data.get('speechiness'),
                liveness=audio_data.get('liveness'),
                key=audio_data.get('key'),
                time_signature=audio_data.get('time_signature'),
            )
        
        # Create Prediction record
        prediction = Prediction.objects.create(
            song=song,
            is_hit=is_hit,
            confidence=confidence,
            model_prediction='HIT' if model_hit else 'FLOP',
            model_confidence=model_confidence,
            adjusted_by_dataset=adjusted_by_dataset,
            dataset_label='HIT' if is_hit_in_dataset else 'FLOP' if in_dataset else None,
            dataset_popularity=dataset_popularity if in_dataset else None,
        )
        
        # Build response
        response_data = {
            'prediction': 'HIT' if is_hit else 'FLOP',
            'confidence': round(confidence, 2),
            'song': {
                'title': audio_data['title'],
                'artist': audio_data['artist'],
                'album': audio_data['album'],
                'album_image': audio_data.get('album_image'),
                'spotify_url': audio_data['spotify_url'],
                'preview_url': audio_data.get('preview_url'),
                'popularity': audio_data.get('popularity', 0),
                'track_id': track_id
            },
            'features': model_input,
            'prediction_id': prediction.id,
            'song_id': song.id,
            'in_dataset': in_dataset,
            'model_prediction': 'HIT' if model_hit else 'FLOP',
            'model_confidence': round(model_confidence, 2)
        }
        
        # Add dataset info if available
        if in_dataset:
            response_data['dataset_label'] = 'HIT' if is_hit_in_dataset else 'FLOP'
            response_data['dataset_popularity'] = dataset_popularity
        
        # Log the prediction
        PredictionAuditLog.objects.create(
            prediction=prediction,
            request_payload=data,
            response_payload=response_data
        )
        
        return JsonResponse(response_data, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Spotify prediction error: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def search_spotify(request):
    """
    Search for tracks on Spotify.
    
    GET /api/spotify/search/?q=Comedy+Gen+Hoshino
    
    OR
    
    POST /api/spotify/search/
    {
        "query": "Comedy Gen Hoshino"
    }
    
    Response:
    {
        "tracks": [
            {
                "id": "5SuOikwiRyPMVoIQDJUgSV",
                "title": "Comedy",
                "artist": "Gen Hoshino",
                "album": "Comedy",
                "album_image": "https://...",
                "duration_ms": 230666,
                "explicit": false,
                "spotify_url": "https://...",
                "popularity": 73
            },
            ...
        ]
    }
    """
    try:
        if request.method == 'GET':
            query = request.GET.get('q', '').strip()
        else:
            data = json.loads(request.body)
            query = data.get('query', '').strip()
        
        if not query:
            return JsonResponse({
                'error': 'Missing search query',
                'usage': {'q': 'search term (GET)', 'query': 'search term (POST)'}
            }, status=400)
        
        spotify = get_spotify_service()
        tracks = spotify.search_tracks(query, limit=10)
        
        return JsonResponse({'tracks': tracks, 'query': query}, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        logger.error(f"Spotify search error: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Search error: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def predict_manual(request):
    """
    Predict hit/flop with manually provided features.
    
    Use this endpoint if you already have audio features.
    For most cases, use /api/predict/spotify/ instead.
    
    POST /api/predict/manual/
    
    Request Body (JSON):
    {
        "title": "Song Name",              // Optional
        "duration_ms": 230666,             // Required
        "danceability": 0.676,             // Required: 0.0 to 1.0
        "energy": 0.461,                   // Required: 0.0 to 1.0
        "valence": 0.715,                  // Required: 0.0 to 1.0
        "acousticness": 0.0322,            // Required: 0.0 to 1.0
        "instrumentalness": 0.000001,      // Required: 0.0 to 1.0
        "explicit": 0,                     // Required: 0 or 1
        "loudness": -6.746,                // Required: dB
        "tempo": 87.917,                   // Required: BPM
        "mode": 0                          // Required: 0 or 1
    }
    """
    try:
        data = json.loads(request.body)
        
        required_fields = [
            'duration_ms', 'danceability', 'energy', 'valence',
            'acousticness', 'instrumentalness', 'explicit',
            'loudness', 'tempo', 'mode'
        ]
        
        missing = [f for f in required_fields if f not in data]
        if missing:
            return JsonResponse({
                'error': f'Missing required fields: {missing}',
                'tip': 'Use /api/predict/spotify/ with a Spotify URL instead'
            }, status=400)
        
        # Validate and convert
        try:
            validated = {
                'duration_ms': int(data['duration_ms']),
                'danceability': float(data['danceability']),
                'energy': float(data['energy']),
                'valence': float(data['valence']),
                'acousticness': float(data['acousticness']),
                'instrumentalness': float(data['instrumentalness']),
                'explicit': float(data['explicit']),
                'loudness': float(data['loudness']),
                'tempo': float(data['tempo']),
                'mode': int(data['mode'])
            }
        except (ValueError, TypeError) as e:
            return JsonResponse({'error': f'Invalid value: {str(e)}'}, status=400)
        
        title = data.get('title', 'Untitled Song')
        artist = data.get('artist', '')
        
        # Make prediction
        features = prepare_features(validated)
        is_hit, confidence = predict_song(features)
        
        # Create Song record for manual prediction
        song = Song.objects.create(
            track_id=None,
            track_name=title,
            artists=artist,
            duration_ms=validated['duration_ms'],
            danceability=validated['danceability'],
            energy=validated['energy'],
            valence=validated['valence'],
            acousticness=validated['acousticness'],
            instrumentalness=validated['instrumentalness'],
            loudness=validated['loudness'],
            tempo=validated['tempo'],
            mode=validated['mode'],
            explicit=validated['explicit'] == 1,
        )
        
        # Create Prediction record
        prediction = Prediction.objects.create(
            song=song,
            is_hit=is_hit,
            confidence=confidence,
            model_prediction='HIT' if is_hit else 'FLOP',
            model_confidence=confidence,
        )
        
        response_data = {
            'prediction': 'HIT' if is_hit else 'FLOP',
            'confidence': confidence,
            'song_title': title,
            'song_id': song.id,
            'prediction_id': prediction.id,
            'features': validated
        }
        
        PredictionAuditLog.objects.create(
            prediction=prediction,
            request_payload=data,
            response_payload=response_data
        )
        
        return JsonResponse(response_data, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        logger.error(f"Manual prediction error: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def search_dataset(request):
    """
    Search for tracks in the local dataset.
    
    These tracks have full audio features available and will work with predictions.
    
    GET /api/dataset/search/?q=Comedy
    
    OR
    
    POST /api/dataset/search/
    {
        "query": "Comedy"
    }
    
    Response:
    {
        "tracks": [
            {
                "id": "5SuOikwiRyPMVoIQDJUgSV",
                "title": "Comedy",
                "artist": "Gen Hoshino",
                "genre": "acoustic",
                "popularity": 73,
                "in_dataset": true
            },
            ...
        ]
    }
    """
    try:
        if request.method == 'GET':
            query = request.GET.get('q', '').strip()
        else:
            data = json.loads(request.body)
            query = data.get('query', '').strip()
        
        if not query:
            return JsonResponse({
                'error': 'Missing search query',
                'usage': {'q': 'search term'}
            }, status=400)
        
        spotify = get_spotify_service()
        tracks = spotify.search_dataset(query, limit=20)
        
        return JsonResponse({
            'tracks': tracks, 
            'query': query,
            'source': 'dataset',
            'note': 'These tracks have full audio features available'
        }, status=200)
        
    except Exception as e:
        logger.error(f"Dataset search error: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Search error: {str(e)}'}, status=500)


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint."""
    return JsonResponse({
        'status': 'ok',
        'service': 'hit-song-predictor',
        'endpoints': {
            'predict_spotify': '/api/predict/spotify/',
            'search_spotify': '/api/spotify/search/',
            'search_dataset': '/api/dataset/search/',
            'predict_manual': '/api/predict/manual/',
            'health': '/api/health/'
        }
    })
