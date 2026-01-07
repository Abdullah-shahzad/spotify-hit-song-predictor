# Hit Song Predictor 🎵

A comprehensive Machine Learning system that predicts whether a song will be a **HIT** or **FLOP** based on audio features. The system integrates a pre-trained Random Forest model, Django REST API, PostgreSQL database, Spotify API integration, and a modern frontend interface.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [File Descriptions](#-file-descriptions)
- [Setup Instructions](#-setup-instructions)
- [Database Schema](#-database-schema)
- [API Documentation](#-api-documentation)
- [Frontend Usage](#-frontend-usage)
- [Management Commands](#-management-commands)
- [Power BI Integration](#-power-bi-integration)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Project Overview

The Hit Song Predictor is an end-to-end ML system designed for music producers, artists, and record labels to get early indicators of song success. The system:

- **Analyzes songs** using 10 audio features (danceability, energy, valence, tempo, etc.)
- **Predicts success** using a pre-trained Random Forest Classifier
- **Integrates with Spotify** to automatically fetch audio features
- **Stores all data** in a unified PostgreSQL database for analytics
- **Provides a modern UI** for easy interaction

### How It Works

1. **User Input**: User provides song title, artist name, or Spotify link
2. **Feature Extraction**: System fetches all 10 required audio features from:
   - Local dataset (`cleaned_data.csv`) if song exists
   - Spotify API (if available and approved)
3. **ML Prediction**: Pre-trained model predicts HIT/FLOP with confidence score
4. **Data Storage**: All songs and predictions stored in unified `Song` table
5. **Analytics**: Data ready for Power BI dashboards

---

## ✨ Features

- ✅ **Spotify API Integration**: Automatic audio feature extraction
- ✅ **Hybrid Data Source**: Uses local dataset + Spotify API
- ✅ **Unified Database**: All songs (dataset + user input) in one table
- ✅ **Smart Prediction**: Adjusts confidence based on dataset labels
- ✅ **Modern Frontend**: Professional UI with animations and real-time feedback
- ✅ **Django Admin**: Full admin interface for data management
- ✅ **Power BI Ready**: Optimized database schema for analytics
- ✅ **Batch Import**: Efficient dataset import with progress tracking
- ✅ **Error Handling**: Comprehensive error handling and logging

---

## 🛠 Technology Stack

### Backend
- **Framework**: Django 4.2.7
- **Database**: PostgreSQL (via psycopg2-binary)
- **ML Library**: scikit-learn 1.8.0
- **Data Processing**: pandas, numpy
- **API Integration**: requests
- **CORS**: django-cors-headers

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with animations
- **JavaScript**: Vanilla JS (no frameworks)
- **Fonts**: Google Fonts (Plus Jakarta Sans)

### Machine Learning
- **Model Type**: Random Forest Classifier
- **Features**: 10 audio features
- **Model Format**: Pickle (.pkl)

---

## 📁 Project Structure

```
project/
│
├── backend/                          # Django backend application
│   ├── manage.py                     # Django management script
│   ├── requirements.txt              # Python dependencies
│   │
│   ├── backend/                      # Django project settings
│   │   ├── __init__.py
│   │   ├── settings.py               # Django configuration
│   │   ├── urls.py                   # Root URL configuration
│   │   ├── wsgi.py                   # WSGI configuration
│   │   └── asgi.py                   # ASGI configuration
│   │
│   └── predictions/                  # Main Django app
│       ├── __init__.py
│       ├── admin.py                  # Django admin configuration
│       ├── apps.py                   # App configuration
│       ├── models.py                 # Database models (Song, Prediction, etc.)
│       ├── views.py                  # API view functions
│       ├── urls.py                   # App URL patterns
│       ├── inference.py              # ML model loading and prediction
│       ├── spotify_service.py        # Spotify API integration
│       │
│       ├── ml_models/                # Pre-trained ML models
│       │   └── hit_song_model_selected.pkl
│       │
│       ├── management/               # Django management commands
│       │   └── commands/
│       │       ├── import_dataset.py          # Import CSV to database
│       │       ├── import_complete_dataset.py # Full import with clear
│       │       └── clear_database.py          # Clear all data
│       │
│       └── migrations/               # Database migrations
│           └── ...
│
├── frontend/                         # Frontend application
│   ├── index.html                    # Main HTML file
│   ├── styles.css                    # Styling and animations
│   └── script.js                     # Frontend logic and API calls
│
├── cleaned_data.csv                  # Training dataset (59,030 songs)
├── hit_song_model_selected.pkl      # Backup model file
├── README.md                         # This file
├── FEATURE_MAPPING.md                # Feature documentation
├── QUICKSTART.md                     # Quick start guide
└── TROUBLESHOOTING.md                # Troubleshooting guide
```

---

## 📄 File Descriptions

### Backend Files

#### `backend/manage.py`
Django's command-line utility for administrative tasks. Used to run migrations, start the server, create superusers, and execute management commands.

**Usage:**
```bash
python manage.py runserver
python manage.py migrate
python manage.py createsuperuser
```

---

#### `backend/backend/settings.py`
Django project configuration file. Contains:
- Database settings (PostgreSQL connection)
- Installed apps (`predictions`, `corsheaders`)
- Middleware configuration
- CORS settings
- Static files configuration
- Security settings

**Key Settings:**
- `DATABASES`: PostgreSQL connection details
- `INSTALLED_APPS`: List of Django apps
- `CORS_ALLOW_ALL_ORIGINS`: Allows all origins (development only)

---

#### `backend/backend/urls.py`
Root URL configuration. Routes requests to app-specific URLs:
- `/admin/` → Django admin panel
- `/api/` → Predictions app URLs

---

#### `backend/predictions/models.py`
**Database Models** - Defines the database schema:

**`Song` Model:**
- Stores all songs (from dataset and user input)
- Fields: `track_id`, `track_name`, `artists`, `album_name`, `popularity`, `track_genre`
- Audio features: `duration_ms`, `danceability`, `energy`, `valence`, `acousticness`, `instrumentalness`, `speechiness`, `liveness`, `loudness`, `tempo`, `mode`, `key`, `time_signature`
- Flags: `explicit`, `is_acoustic`, `is_instrumental`, `is_hit`
- Auto-calculates `is_hit` based on `popularity >= 50`

**`Prediction` Model:**
- Stores ML model predictions
- Linked to `Song` via ForeignKey
- Fields: `is_hit`, `confidence`, `model_prediction`, `model_confidence`
- Tracks adjustments: `adjusted_by_dataset`, `dataset_label`, `dataset_popularity`

**`ModelMetadata` Model:**
- Tracks ML model versions for auditability

**`PredictionAuditLog` Model:**
- Logs prediction requests for debugging

---

#### `backend/predictions/views.py`
**API View Functions** - Handles HTTP requests:

**`predict_from_spotify(request)`:**
- **Endpoint**: `POST /api/predict/spotify/`
- **Purpose**: Main prediction endpoint
- **Input**: Spotify track ID/URL OR song title + artist
- **Process**:
  1. Fetches audio features from dataset or Spotify API
  2. Prepares features for ML model
  3. Makes prediction
  4. Creates/updates `Song` record
  5. Creates `Prediction` record
  6. Adjusts confidence if song is in dataset
- **Output**: JSON with prediction, confidence, song info, features

**`search_spotify(request)`:**
- **Endpoint**: `POST /api/spotify/search/`
- **Purpose**: Search songs on Spotify
- **Input**: Query string
- **Output**: List of matching tracks

**`search_dataset(request)`:**
- **Endpoint**: `POST /api/dataset/search/`
- **Purpose**: Search songs in local dataset
- **Input**: Query string
- **Output**: List of matching songs from dataset

**`predict_manual(request)`:**
- **Endpoint**: `POST /api/predict/manual/`
- **Purpose**: Direct prediction with all 10 features
- **Input**: All 10 audio features
- **Output**: Prediction result

**`health_check(request)`:**
- **Endpoint**: `GET /api/health/`
- **Purpose**: Health check endpoint
- **Output**: Service status

---

#### `backend/predictions/urls.py`
**URL Patterns** - Maps URLs to view functions:
- `predict/spotify/` → `predict_from_spotify`
- `spotify/search/` → `search_spotify`
- `dataset/search/` → `search_dataset`
- `predict/manual/` → `predict_manual`
- `health/` → `health_check`

---

#### `backend/predictions/inference.py`
**ML Model Inference** - Handles model loading and predictions:

**`load_model()`:**
- Loads pre-trained model from `ml_models/hit_song_model_selected.pkl`
- Caches model in memory after first load
- Suppresses scikit-learn version warnings

**`prepare_features(user_input)`:**
- Converts user input dict to NumPy array
- Requires all 10 features (no inference/guessing)
- Feature order: `duration_ms`, `danceability`, `energy`, `valence`, `acousticness`, `instrumentalness`, `explicit`, `loudness`, `tempo`, `mode`

**`predict_song(features)`:**
- Makes prediction using loaded model
- Returns: `(is_hit: bool, confidence: float)`
- Confidence is percentage (0-100)

---

#### `backend/predictions/spotify_service.py`
**Spotify API Integration** - Handles Spotify API and dataset lookups:

**`SpotifyService` Class:**
- **`__init__()`**: Initializes with client credentials
- **`_get_access_token()`**: Gets OAuth 2.0 access token
- **`_make_request()`**: Makes authenticated API requests
- **`get_track_info(track_id)`**: Fetches track metadata (title, artist, album, images)
- **`get_audio_features_from_dataset(title, artist)`**: Searches local dataset for audio features
- **`get_audio_features(track_id)`**: Hybrid method - tries dataset first, then Spotify API
- **`search_tracks(query, limit)`**: Searches Spotify for tracks
- **`extract_track_id(url_or_id)`**: Extracts clean track ID from URL

**Key Features:**
- Uses Client Credentials flow (server-to-server)
- Falls back to dataset if Spotify API unavailable
- Caches dataset in memory for fast lookups
- Handles 403 errors gracefully (Extended Quota Mode required)

---

#### `backend/predictions/admin.py`
**Django Admin Configuration** - Customizes admin interface:

**`SongAdmin`:**
- List display: `track_name`, `artists`, `popularity`, `is_hit`, `created_at`
- Filters: `is_hit`, `is_acoustic`, `is_instrumental`, `explicit`, `created_at`
- Search: `track_name`, `artists`, `track_id`
- Fieldsets: Organized by Song Info, Audio Features, Metadata

**`PredictionAdmin`:**
- List display: `song`, `is_hit`, `confidence`, `model_prediction`, `created_at`
- Filters: `is_hit`, `adjusted_by_dataset`, `created_at`
- Search: `song__track_name`, `song__artists`

---

#### `backend/predictions/management/commands/import_dataset.py`
**Dataset Import Command** - Imports CSV to database:

**Usage:**
```bash
python manage.py import_dataset ../cleaned_data.csv --batch-size 2000
```

**Features:**
- Batch processing for efficiency
- Progress tracking
- Error handling
- Calculates `is_hit` based on popularity

---

#### `backend/predictions/management/commands/import_complete_dataset.py`
**Complete Dataset Import** - Clears database and imports all records:

**Usage:**
```bash
python manage.py import_complete_dataset
python manage.py import_complete_dataset --no-clear  # Skip clearing
python manage.py import_complete_dataset --csv ../cleaned_data.csv --batch-size 2000
```

**Features:**
- Clears all existing data (optional)
- Imports all 59,030 records
- Shows progress every 2000 records
- Displays statistics (HIT/FLOP counts, percentages)

---

#### `backend/predictions/management/commands/clear_database.py`
**Database Clear Command** - Removes all data:

**Usage:**
```bash
python manage.py clear_database
```

**Clears:**
- All `Song` records
- All `Prediction` records
- All `PredictionAuditLog` records

---

### Frontend Files

#### `frontend/index.html`
**Main HTML File** - User interface structure:

**Sections:**
- Header with logo and tagline
- Input card with form fields:
  - Song Title (optional)
  - Artist Name (optional)
  - Spotify Link (optional)
  - Quick Fill buttons (example songs)
- Results card (hidden initially):
  - Album art
  - Prediction badge (HIT/FLOP)
  - Confidence bar
  - Audio features display
  - Song metadata

**Features:**
- Responsive design
- Animated gradient background
- Glassmorphism effects
- Loading states
- Error handling

---

#### `frontend/styles.css`
**Styling** - Modern CSS with animations:

**Key Styles:**
- Dark theme with gradient background
- Glassmorphism cards
- Smooth animations and transitions
- Hover effects
- Responsive breakpoints
- Color-coded prediction badges (green for HIT, red for FLOP)

---

#### `frontend/script.js`
**Frontend Logic** - Handles user interactions and API calls:

**Functions:**
- **`handleSubmit(event)`**: Form submission handler
- **`predictSong(data)`**: Calls prediction API
- **`displayResults(data)`**: Renders prediction results
- **`displayError(message)`**: Shows error messages
- **`quickFill(title, artist)`**: Quick fill form fields
- **`resetForm()`**: Clears form and results

**API Integration:**
- Base URL: `http://127.0.0.1:8000/api` (or `http://localhost:8000/api`)
- Endpoints: `/predict/spotify/`, `/spotify/search/`, `/dataset/search/`
- Error handling with user-friendly messages

---

### Data Files

#### `cleaned_data.csv`
**Training Dataset** - Contains 59,030 songs with:
- Song metadata (title, artist, album, genre)
- Audio features (10 features required by model)
- Popularity scores (0-100)
- Used for:
  - Training the ML model
  - Fast lookups for predictions
  - Database import

---

#### `backend/predictions/ml_models/hit_song_model_selected.pkl`
**Pre-trained ML Model** - Random Forest Classifier:
- Trained on `cleaned_data.csv`
- Input: 10 audio features
- Output: HIT (1) or FLOP (0) with confidence
- Loaded at runtime and cached in memory

---

## 🚀 Setup Instructions

### Prerequisites

- **Python 3.8+** (tested with Python 3.13)
- **PostgreSQL 12+**
- **pip** (Python package manager)
- **Git** (optional, for cloning)

---

### Step 1: Install PostgreSQL

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download and install from [PostgreSQL official website](https://www.postgresql.org/download/windows/)

---

### Step 2: Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE hit_song_db;
CREATE USER postgres WITH PASSWORD 'postgres';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE hit_song_db TO postgres;
\q
```

---

### Step 3: Set Up Python Environment

```bash
# Navigate to project directory
cd /Users/monibafatima/Downloads/IDS\ PROJECT/project

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt
```

---

### Step 4: Configure Database Settings

Edit `backend/backend/settings.py` if your PostgreSQL credentials differ:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hit_song_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Or set environment variables:
```bash
export DB_NAME=hit_song_db
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_HOST=localhost
export DB_PORT=5432
```

---

### Step 5: Configure Spotify API (Optional)

The system works without Spotify API (uses local dataset), but for full functionality:

1. Create a Spotify app at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Get Client ID and Client Secret
3. Set environment variables:
```bash
export SPOTIFY_CLIENT_ID='your_client_id'
export SPOTIFY_CLIENT_SECRET='your_client_secret'
```

Or edit `backend/predictions/spotify_service.py` directly (not recommended for production).

**Note:** Spotify's `audio-features` endpoint requires "Extended Quota Mode" approval. The system falls back to the local dataset if unavailable.

---

### Step 6: Run Database Migrations

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

---

### Step 7: Import Dataset (Optional but Recommended)

Import the training dataset for fast lookups:

```bash
# Clear database and import all records
python manage.py import_complete_dataset

# Or import without clearing
python manage.py import_complete_dataset --no-clear

# With custom CSV path
python manage.py import_complete_dataset --csv ../cleaned_data.csv --batch-size 2000
```

This will import all 59,030 songs and calculate `is_hit` based on popularity.

---

### Step 8: Create Superuser (Optional)

For Django admin access:

```bash
python manage.py createsuperuser
```

Follow prompts to create admin user.

---

### Step 9: Start Django Server

```bash
cd backend
python manage.py runserver
```

The API will be available at `http://localhost:8000`

**Verify it's working:**
```bash
curl http://localhost:8000/api/health/
```

---

### Step 10: Start Frontend

**Option 1: Python HTTP Server (Recommended)**
```bash
cd frontend
python3 -m http.server 3000
```

**Option 2: Node.js HTTP Server**
```bash
cd frontend
npx http-server -p 3000
```

**Option 3: Open Directly**
Simply open `frontend/index.html` in your browser (may have CORS issues).

Open your browser and navigate to: `http://localhost:3000`

---

## 🗄️ Database Schema

### Song Table

**Purpose**: Unified table storing all songs (dataset + user input)

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer (PK) | Auto-increment primary key |
| `track_id` | CharField(50) | Spotify track ID (indexed) |
| `track_name` | CharField(200) | Song title (indexed) |
| `artists` | CharField(500) | Artist name(s) (indexed) |
| `album_name` | CharField(200) | Album name |
| `popularity` | Integer | Spotify popularity (0-100, indexed) |
| `track_genre` | CharField(100) | Genre |
| `duration_ms` | Integer | Duration in milliseconds |
| `danceability` | FloatField | 0.0 to 1.0 |
| `energy` | FloatField | 0.0 to 1.0 |
| `valence` | FloatField | 0.0 to 1.0 (mood/positivity) |
| `acousticness` | FloatField | 0.0 to 1.0 |
| `instrumentalness` | FloatField | 0.0 to 1.0 |
| `speechiness` | FloatField | 0.0 to 1.0 (nullable) |
| `liveness` | FloatField | 0.0 to 1.0 (nullable) |
| `loudness` | FloatField | dB value (typically -60 to 0) |
| `tempo` | FloatField | BPM (beats per minute) |
| `mode` | IntegerField | 0=minor, 1=major |
| `key` | IntegerField | Musical key (0-11, nullable) |
| `time_signature` | IntegerField | Time signature (nullable) |
| `explicit` | BooleanField | Explicit content flag |
| `is_acoustic` | BooleanField | Derived: acousticness > 0.5 |
| `is_instrumental` | BooleanField | Derived: instrumentalness > 0.5 |
| `is_hit` | BooleanField | HIT if popularity >= 50 (indexed) |
| `created_at` | DateTimeField | Creation timestamp (indexed) |

**Indexes:**
- `track_id`
- `track_name`, `artists`
- `popularity`
- `is_hit`
- `created_at`

---

### Prediction Table

**Purpose**: Stores ML model predictions

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer (PK) | Auto-increment primary key |
| `song` | ForeignKey(Song) | Linked song record |
| `is_hit` | BooleanField | Prediction: True=HIT, False=FLOP (indexed) |
| `confidence` | FloatField | Prediction confidence % |
| `model_prediction` | CharField(10) | Raw model output: HIT or FLOP |
| `model_confidence` | FloatField | Raw model confidence before adjustment |
| `adjusted_by_dataset` | BooleanField | Whether adjusted based on dataset label |
| `dataset_label` | CharField(10) | Dataset label if in dataset: HIT or FLOP |
| `dataset_popularity` | IntegerField | Popularity from dataset if available |
| `model_version` | CharField(50) | Version of ML model used |
| `created_at` | DateTimeField | Creation timestamp (indexed) |

**Indexes:**
- `song`, `created_at`
- `is_hit`

---

### ModelMetadata Table

**Purpose**: Tracks ML model versions

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer (PK) | Auto-increment primary key |
| `model_name` | CharField(100) | Model name |
| `model_version` | CharField(50) | Model version |
| `accuracy` | FloatField | Model accuracy |
| `trained_on` | DateTimeField | Training timestamp |
| `is_active` | BooleanField | Whether model is active |

---

### PredictionAuditLog Table

**Purpose**: Logs prediction requests for debugging

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer (PK) | Auto-increment primary key |
| `prediction` | ForeignKey(Prediction) | Linked prediction record |
| `request_payload` | JSONField | Original request data |
| `response_payload` | JSONField | Response data |
| `created_at` | DateTimeField | Creation timestamp |

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000/api
```

---

### 1. Predict from Spotify

**Endpoint:** `POST /api/predict/spotify/`

**Description:** Main prediction endpoint. Automatically fetches audio features from dataset or Spotify API.

**Request Body (Option 1 - Spotify Track):**
```json
{
    "track_id": "5SuOikwiRyPMVoIQDJUgSV"
}
```
OR
```json
{
    "url": "https://open.spotify.com/track/5SuOikwiRyPMVoIQDJUgSV"
}
```

**Request Body (Option 2 - Song Title + Artist):**
```json
{
    "title": "Comedy",
    "artist": "Gen Hoshino"
}
```

**Response:**
```json
{
    "prediction": "HIT",
    "confidence": 62.30,
    "song": {
        "title": "Comedy",
        "artist": "Gen Hoshino",
        "album": "Comedy",
        "album_image": "https://i.scdn.co/image/...",
        "spotify_url": "https://open.spotify.com/track/...",
        "preview_url": "https://p.scdn.co/mp3-preview/...",
        "popularity": 75,
        "track_id": "5SuOikwiRyPMVoIQDJUgSV"
    },
    "features": {
        "duration_ms": 230666,
        "danceability": 0.676,
        "energy": 0.561,
        "valence": 0.652,
        "acousticness": 0.525,
        "instrumentalness": 0.0,
        "explicit": 0,
        "loudness": -8.761,
        "tempo": 87.917,
        "mode": 1
    },
    "prediction_id": 123,
    "song_id": 456,
    "in_dataset": true,
    "model_prediction": "HIT",
    "model_confidence": 62.30
}
```

**Error Response:**
```json
{
    "error": "Song not found. Please provide a valid Spotify link or song title + artist."
}
```

---

### 2. Search Spotify

**Endpoint:** `GET /api/spotify/search/` or `POST /api/spotify/search/`

**Description:** Search for songs on Spotify.

**Request (GET):**
```
GET /api/spotify/search/?q=Comedy+Gen+Hoshino
```

**Request (POST):**
```json
{
    "query": "Comedy Gen Hoshino"
}
```

**Response:**
```json
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
            "preview_url": "https://...",
            "spotify_url": "https://...",
            "popularity": 73,
            "in_dataset": true
        }
    ],
    "query": "Comedy Gen Hoshino"
}
```

---

### 3. Search Dataset

**Endpoint:** `POST /api/dataset/search/`

**Description:** Search songs in local training dataset.

**Request Body:**
```json
{
    "query": "Comedy"
}
```

**Response:**
```json
{
    "songs": [
        {
            "track_name": "Comedy",
            "artists": "Gen Hoshino",
            "popularity": 75,
            "is_hit": true
        }
    ]
}
```

---

### 4. Manual Prediction

**Endpoint:** `POST /api/predict/manual/`

**Description:** Direct prediction with all 10 features provided.

**Request Body:**
```json
{
    "duration_ms": 230666,
    "danceability": 0.676,
    "energy": 0.561,
    "valence": 0.652,
    "acousticness": 0.525,
    "instrumentalness": 0.0,
    "explicit": 0,
    "loudness": -8.761,
    "tempo": 87.917,
    "mode": 1
}
```

**Response:**
```json
{
    "prediction": "HIT",
    "confidence": 62.30
}
```

---

### 5. Health Check

**Endpoint:** `GET /api/health/`

**Description:** Check API health status.

**Response:**
```json
{
    "status": "ok",
    "service": "hit-song-predictor",
    "endpoints": {
        "predict_spotify": "/api/predict/spotify/",
        "search_spotify": "/api/spotify/search/",
        "search_dataset": "/api/dataset/search/",
        "predict_manual": "/api/predict/manual/",
        "health": "/api/health/"
    }
}
```

---

## 🎨 Frontend Usage

### Opening the Frontend

1. Start the Django backend server:
```bash
cd backend
python manage.py runserver
```

2. Start the frontend server:
```bash
cd frontend
python3 -m http.server 3000
```

3. Open browser: `http://localhost:3000`

---

### Using the Interface

1. **Enter Song Information:**
   - Option 1: Paste a Spotify link
   - Option 2: Enter song title and artist name
   - Option 3: Use "Quick Fill" buttons for example songs

2. **Click "Predict Song":**
   - System fetches audio features
   - ML model makes prediction
   - Results displayed with:
     - Album art
     - Prediction badge (HIT/FLOP)
     - Confidence percentage
     - Audio features breakdown
     - Song metadata

3. **View Results:**
   - Green badge = HIT
   - Red badge = FLOP
   - Confidence bar shows prediction strength
   - Audio features displayed in cards

---

## 🔧 Management Commands

### Import Dataset

**Import all records from CSV:**
```bash
python manage.py import_complete_dataset
```

**Options:**
- `--csv PATH`: Custom CSV file path (default: `cleaned_data.csv`)
- `--batch-size N`: Batch size for bulk insert (default: 2000)
- `--no-clear`: Skip clearing database before import

**Example:**
```bash
python manage.py import_complete_dataset --csv ../cleaned_data.csv --batch-size 2000
```

---

### Clear Database

**Remove all data:**
```bash
python manage.py clear_database
```

**Warning:** This deletes all songs, predictions, and audit logs!

---

### Django Shell

**Interactive Python shell:**
```bash
python manage.py shell
```

**Example queries:**
```python
from predictions.models import Song, Prediction

# Count songs
Song.objects.count()

# Get HIT songs
Song.objects.filter(is_hit=True).count()

# Get recent predictions
Prediction.objects.all()[:10]
```

---

## 📊 Power BI Integration

### Connect to PostgreSQL

1. **Open Power BI Desktop**
2. **Get Data** → **Database** → **PostgreSQL database**
3. **Enter connection details:**
   - Server: `localhost`
   - Database: `hit_song_db`
   - Username: `postgres`
   - Password: `postgres`
   - Data connectivity mode: `Import` or `DirectQuery`

---

### Recommended Tables

- **`predictions_song`**: All songs with features and labels
- **`predictions_prediction`**: ML predictions with confidence scores

---

### Recommended Visualizations

1. **Hit vs Flop Distribution**
   - Pie chart: `is_hit` field
   - Filter by `created_at` for time-based analysis

2. **Confidence Distribution**
   - Histogram: `confidence` field
   - Separate by `is_hit`

3. **Feature Impact Analysis**
   - Scatter plot: `danceability` vs `energy`
   - Color by `is_hit`

4. **Popularity vs Prediction**
   - Scatter plot: `popularity` vs `confidence`
   - Size by `is_hit`

5. **Time Series Analysis**
   - Line chart: Predictions over time (`created_at`)
   - Group by `is_hit`

---

### Auto-Refresh Setup

1. **In Power BI Desktop:**
   - File → Options and settings → Options → Data source settings
   - Configure credentials

2. **In Power BI Service (if publishing):**
   - Dataset → Schedule refresh
   - Set refresh frequency (hourly, daily, etc.)

---

## 🐛 Troubleshooting

### Model File Not Found

**Error:** `Model file not found at ...`

**Solution:**
1. Ensure `hit_song_model_selected.pkl` exists in `backend/predictions/ml_models/`
2. Check file permissions
3. Verify path in `inference.py`

---

### Database Connection Error

**Error:** `could not connect to server`

**Solution:**
1. Verify PostgreSQL is running:
```bash
psql -U postgres
```

2. Check database credentials in `settings.py`

3. Ensure database exists:
```sql
CREATE DATABASE hit_song_db;
```

4. Check PostgreSQL service:
```bash
# macOS
brew services list

# Linux
sudo systemctl status postgresql
```

---

### CORS Error in Frontend

**Error:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:**
1. Ensure Django server is running
2. Check `CORS_ALLOW_ALL_ORIGINS = True` in `settings.py`
3. Verify `django-cors-headers` is installed
4. Check middleware order in `settings.py` (CorsMiddleware should be first)

---

### Port Already in Use

**Error:** `That port is already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 $(lsof -ti:8000)

# Or use a different port
python manage.py runserver 8001
```

---

### Spotify API 403 Error

**Error:** `403 Forbidden` when fetching audio features

**Solution:**
- This is expected if "Extended Quota Mode" is not approved
- The system automatically falls back to the local dataset
- For full Spotify API access, request Extended Quota Mode in Spotify Developer Dashboard

---

### Migration Errors

**Error:** `ForeignKeyViolation` or `relation does not exist`

**Solution:**
1. Clear database:
```bash
python manage.py clear_database
```

2. Delete migration files (except `__init__.py`):
```bash
rm backend/predictions/migrations/0*.py
```

3. Recreate migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Import Errors

**Error:** `value too long for type character varying(300)`

**Solution:**
1. Check field `max_length` in `models.py`
2. Increase if needed (e.g., `artists` field to 500)
3. Create and apply migration:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 📝 License

This project is for educational and research purposes.

---

## 👥 Contributing

This is a project implementation. For improvements or bug fixes, please follow standard development practices.

---

## 📧 Support

For issues or questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review project documentation
3. Check Django and PostgreSQL logs

---

**Built with ❤️ using Django, PostgreSQL, scikit-learn, and Spotify API**
