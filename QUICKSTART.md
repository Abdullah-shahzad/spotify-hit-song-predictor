# Quick Start Guide

## 🚀 Fast Setup (5 minutes)

### 1. Run Setup Script
```bash
./setup.sh
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 3. Set Up Database
```bash
# Start PostgreSQL (if not running)
brew services start postgresql  # macOS
# or
sudo systemctl start postgresql  # Linux

# Create database
psql postgres
CREATE DATABASE hit_song_db;
\q
```

### 4. Run Migrations
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 5. Start Backend Server
```bash
python manage.py runserver
```
Backend will run on: `http://localhost:8000`

### 6. Start Frontend (New Terminal)
```bash
cd frontend
python3 -m http.server 3000
```
Frontend will run on: `http://localhost:3000`

## ✅ Verify Installation

### Test API Health
```bash
curl http://localhost:8000/api/health/
```

### Test Prediction
```bash
curl -X POST http://localhost:8000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Song",
    "duration_minutes": 3.5,
    "danceability": 0.75,
    "energy": 0.65,
    "mood": 0.8,
    "is_acoustic": false,
    "is_instrumental": false,
    "is_explicit": false
  }'
```

## 🎯 Usage

1. Open `http://localhost:3000` in your browser
2. Fill in the song details
3. Click "Predict Song"
4. View the prediction result!

## 📊 Access Django Admin

1. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

2. Visit: `http://localhost:8000/admin`

## 🔧 Troubleshooting

**Port 8000 already in use?**
```bash
python manage.py runserver 8001
```

**Database connection error?**
- Check PostgreSQL is running
- Verify database exists: `psql -l | grep hit_song_db`

**Model file not found?**
- Ensure `hit_song_model_selected.pkl` is in `backend/predictions/ml_models/`

