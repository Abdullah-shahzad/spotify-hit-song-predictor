# Spotify Hit Song Predictor 🎵

A Machine Learning system that predicts whether a song will be a **HIT** or **FLOP** based on audio features. Built with Django REST API, PostgreSQL, Random Forest Classifier, and Spotify API integration.

## ✨ Features

- 🎯 **ML Prediction**: Pre-trained Random Forest model predicts song success with confidence scores
- 🎵 **Spotify Integration**: Automatic audio feature extraction from Spotify API
- 💾 **Database Storage**: PostgreSQL database for analytics and data persistence
- 🎨 **Modern Frontend**: Clean, responsive UI with real-time predictions
- ⚡ **Optimized Performance**: Database-optimized queries for fast predictions
- 📊 **Django Admin**: Full admin interface for data management

## 🛠 Technology Stack

**Backend:** Django 4.2.7, PostgreSQL, scikit-learn, pandas, numpy  
**Frontend:** HTML5, CSS3, Vanilla JavaScript  
**ML Model:** Random Forest Classifier (10 audio features)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Abdullah-shahzad/spotify-hit-song-predictor.git
   cd spotify-hit-song-predictor
   ```

2. **Set up PostgreSQL**
   ```bash
   # Create database
   psql postgres
   CREATE DATABASE hit_song_db;
   \q
   ```

3. **Set up Python environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure database** (edit `backend/backend/settings.py` if needed)

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Add model file**
   - Place `hit_song_model_selected.pkl` in `backend/predictions/ml_models/`
   - **Note:** Model files are not included in the repository due to size limitations

7. **Start servers**
   ```bash
   # Terminal 1: Backend
   cd backend
   python manage.py runserver
   
   # Terminal 2: Frontend
   cd frontend
   python3 -m http.server 3000
   ```

8. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

## 📡 API Endpoints

### Predict Song
```http
POST /api/predict/spotify/
Content-Type: application/json

{
  "title": "Song Title",
  "artist": "Artist Name"
}
```

### Search Spotify
```http
GET /api/spotify/search/?q=query
POST /api/spotify/search/
```

### Health Check
```http
GET /api/health/
```

## 📁 Project Structure

```
project/
├── backend/              # Django backend
│   ├── predictions/      # Main app
│   │   ├── ml_models/   # ML model files (add .pkl here)
│   │   ├── models.py     # Database models
│   │   ├── views.py      # API endpoints
│   │   └── inference.py # ML prediction logic
│   └── manage.py
├── frontend/            # Frontend application
│   ├── index.html
│   ├── styles.css
│   └── script.js
└── README.md
```

## 🔧 Management Commands

```bash
# Import dataset (optional)
python manage.py import_complete_dataset

# Create admin user
python manage.py createsuperuser

# Clear database
python manage.py clear_database
```

## 🐛 Troubleshooting

**Model file not found?**
- Ensure `hit_song_model_selected.pkl` is in `backend/predictions/ml_models/`

**Database connection error?**
- Verify PostgreSQL is running: `pg_isready -h localhost`
- Check database credentials in `backend/backend/settings.py`

**Port already in use?**
- Use different port: `python manage.py runserver 8001`

**CORS errors?**
- Ensure Django server is running
- Check `CORS_ALLOW_ALL_ORIGINS = True` in settings.py

## 📝 Notes

- Model files (`.pkl`) and dataset (`cleaned_data.csv`) are not included due to size limitations
- Spotify API requires Extended Quota Mode for full audio features access
- The system falls back to local database if Spotify API is unavailable

## 📄 License

This project is for educational and research purposes.

---

**Built with ❤️ using Django, PostgreSQL, scikit-learn, and Spotify API**
