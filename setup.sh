#!/bin/bash

# Hit Song Prediction System - Setup Script
# This script helps set up the development environment

echo "🎵 Hit Song Prediction System - Setup"
echo "======================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL is not installed. Please install PostgreSQL 12 or higher."
    echo "   macOS: brew install postgresql"
    echo "   Linux: sudo apt-get install postgresql"
    echo ""
else
    echo "✅ PostgreSQL found: $(psql --version)"
    echo ""
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing Python dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check if model file exists
echo "🤖 Checking model file..."
if [ -f "predictions/ml_models/hit_song_model_selected.pkl" ]; then
    echo "✅ Model file found"
else
    echo "⚠️  Model file not found at predictions/ml_models/hit_song_model_selected.pkl"
    echo "   Please ensure the model file is in the correct location."
fi
echo ""

# Database setup instructions
echo "🗄️  Database Setup Instructions:"
echo "   1. Make sure PostgreSQL is running"
echo "   2. Create database:"
echo "      psql postgres"
echo "      CREATE DATABASE hit_song_db;"
echo "      \\q"
echo "   3. Run migrations:"
echo "      python manage.py makemigrations"
echo "      python manage.py migrate"
echo "   4. (Optional) Create superuser:"
echo "      python manage.py createsuperuser"
echo ""

# Return to project root
cd ..

echo "✨ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Navigate to backend: cd backend"
echo "   3. Set up database (see instructions above)"
echo "   4. Start Django server: python manage.py runserver"
echo "   5. Open frontend: cd ../frontend && python3 -m http.server 3000"
echo ""
echo "📖 For detailed instructions, see README.md"

