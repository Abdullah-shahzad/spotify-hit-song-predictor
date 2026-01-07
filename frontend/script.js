/**
 * Hit Song Predictor - Professional UI
 * Spotify + Machine Learning Integration
 */

const API_BASE = 'http://127.0.0.1:8000/api';

// DOM Elements
const form = document.getElementById('prediction-form');
const songTitleInput = document.getElementById('song-title');
const artistNameInput = document.getElementById('artist-name');
const spotifyLinkInput = document.getElementById('spotify-link');
const predictBtn = document.getElementById('predict-btn');

const resultCard = document.getElementById('result-card');
const newPredictionBtn = document.getElementById('new-prediction-btn');

const errorToast = document.getElementById('error-toast');
const errorMessage = document.getElementById('error-message');

// Example chips
const exampleChips = document.querySelectorAll('.example-chip');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Form submission
    form.addEventListener('submit', handleSubmit);
    
    // New prediction button
    newPredictionBtn.addEventListener('click', resetForm);
    
    // Example chips
    exampleChips.forEach(chip => {
        chip.addEventListener('click', () => {
            songTitleInput.value = chip.dataset.title;
            artistNameInput.value = chip.dataset.artist;
            spotifyLinkInput.value = '';
            
            // Trigger label animation
            songTitleInput.dispatchEvent(new Event('input'));
            artistNameInput.dispatchEvent(new Event('input'));
        });
    });
});

/**
 * Handle form submission
 */
async function handleSubmit(e) {
    e.preventDefault();
    
    const spotifyLink = spotifyLinkInput.value.trim();
    const songTitle = songTitleInput.value.trim();
    const artistName = artistNameInput.value.trim();
    
    // Validate input
    if (spotifyLink) {
        if (!isSpotifyLink(spotifyLink)) {
            showError('Please enter a valid Spotify track URL');
            return;
        }
        await makePrediction({ url: spotifyLink });
    } else if (songTitle && artistName) {
        await makePrediction({ title: songTitle, artist: artistName });
    } else {
        showError('Please fill in Song Title and Artist Name, or paste a Spotify URL');
        return;
    }
}

/**
 * Check if input is a Spotify URL
 */
function isSpotifyLink(input) {
    return input.includes('spotify.com/track/') || 
           input.startsWith('spotify:track:');
}

/**
 * Make prediction API call
 */
async function makePrediction(data) {
    setLoading(true);
    hideError();
    
    try {
        const response = await fetch(`${API_BASE}/predict/spotify/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Prediction failed');
        }
        
        displayResult(result);
        
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
    }
}

/**
 * Display prediction result
 */
function displayResult(data) {
    const isHit = data.prediction === 'HIT';
    
    // Update result card class
    resultCard.classList.remove('hit', 'flop');
    resultCard.classList.add(isHit ? 'hit' : 'flop');
    
    // Album art
    const albumArt = document.getElementById('album-art');
    albumArt.src = data.song.album_image || 'https://via.placeholder.com/100/1a1a2e/6366f1?text=♪';
    
    // Song info
    document.getElementById('result-title').textContent = data.song.title;
    document.getElementById('result-artist').textContent = data.song.artist;
    document.getElementById('result-album').textContent = data.song.album || '';
    
    // Prediction badge
    const badge = document.getElementById('prediction-badge');
    badge.classList.remove('hit', 'flop');
    badge.classList.add(isHit ? 'hit' : 'flop');
    document.getElementById('prediction-label').textContent = data.prediction;
    
    // Confidence
    document.getElementById('confidence-value').textContent = `${data.confidence}%`;
    const confidenceFill = document.getElementById('confidence-fill');
    confidenceFill.classList.remove('hit', 'flop');
    confidenceFill.classList.add(isHit ? 'hit' : 'flop');
    confidenceFill.style.width = `${data.confidence}%`;
    
    // Features
    displayFeatures(data.features);
    
    // Spotify link
    const spotifyBtn = document.getElementById('spotify-btn');
    if (data.song.spotify_url) {
        spotifyBtn.href = data.song.spotify_url;
        spotifyBtn.style.display = 'flex';
    } else {
        spotifyBtn.style.display = 'none';
    }
    
    // Show result card
    resultCard.classList.remove('hidden');
    
    // Scroll to result
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * Display audio features
 */
function displayFeatures(features) {
    const grid = document.getElementById('features-grid');
    
    const featureConfig = [
        { key: 'danceability', label: 'Danceability', icon: '💃', percent: true },
        { key: 'energy', label: 'Energy', icon: '⚡', percent: true },
        { key: 'valence', label: 'Mood', icon: '😊', percent: true },
        { key: 'acousticness', label: 'Acoustic', icon: '🎸', percent: true },
        { key: 'tempo', label: 'Tempo', icon: '🥁', unit: ' BPM' },
        { key: 'loudness', label: 'Loudness', icon: '🔊', unit: ' dB' },
    ];
    
    grid.innerHTML = featureConfig.map(({ key, label, icon, percent, unit }) => {
        const value = features[key];
        const displayValue = percent 
            ? `${(value * 100).toFixed(0)}%`
            : `${value.toFixed(1)}${unit || ''}`;
        const barWidth = percent 
            ? value * 100 
            : (key === 'tempo' ? Math.min(100, (value / 200) * 100) : Math.min(100, ((value + 60) / 60) * 100));
        
        return `
            <div class="feature-item">
                <div class="feature-label">
                    <span>${icon}</span>
                    <span>${label}</span>
                </div>
                <div class="feature-value">${displayValue}</div>
                ${percent ? `
                    <div class="feature-bar">
                        <div class="feature-bar-fill" style="width: ${barWidth}%"></div>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

/**
 * Set loading state
 */
function setLoading(loading) {
    predictBtn.classList.toggle('loading', loading);
    predictBtn.disabled = loading;
}

/**
 * Reset form
 */
function resetForm() {
    songTitleInput.value = '';
    artistNameInput.value = '';
    spotifyLinkInput.value = '';
    resultCard.classList.add('hidden');
    songTitleInput.focus();
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorToast.classList.remove('hidden');
    
    // Auto-hide after 6 seconds
    setTimeout(hideError, 6000);
}

/**
 * Hide error message
 */
function hideError() {
    errorToast.classList.add('hidden');
}

// Expose hideError globally for onclick
window.hideError = hideError;
