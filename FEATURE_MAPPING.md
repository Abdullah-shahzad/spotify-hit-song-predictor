# Feature Mapping: Frontend ↔ Dataset ↔ Model

## Overview
This document clarifies how user inputs from the frontend map to dataset columns and model features.

## Feature Mapping Table

| Frontend Input | Dataset Column | Model Feature | Notes |
|---------------|----------------|--------------|-------|
| `duration_minutes` | `duration_ms` | `duration_ms` | Converted: `minutes × 60 × 1000` |
| `danceability` | `danceability` | `danceability` | Direct mapping (0.0 to 1.0) |
| `energy` | `energy` | `energy` | Direct mapping (0.0 to 1.0) |
| `mood` | `valence` | `valence` | **User-friendly name for valence** (0.0 to 1.0) |
| `is_acoustic` | `acousticness` | `acousticness` | Converted: boolean → float (0.0 or 1.0) |
| `is_instrumental` | `instrumentalness` | `instrumentalness` | Converted: boolean → float (0.0 or 1.0) |
| `is_explicit` | `explicit` | `explicit` | Converted: boolean → float (0.0 or 1.0) |
| *(inferred)* | `loudness` | `loudness` | Inferred from `energy`: `-20 + (energy × 18)` |
| *(inferred)* | `tempo` | `tempo` | Inferred from `energy` + `danceability`: `60 + (energy × 60) + (danceability × 60)` |
| *(inferred)* | `mode` | `mode` | Inferred from `mood`: `1 if mood > 0.5 else 0` |

## Optional Fields

| Field | Required? | Used in Model? | Purpose |
|-------|----------|----------------|---------|
| `title` | ❌ No | ❌ No | Only for display/storage in database |

## Key Points

1. **Mood = Valence**: The frontend uses "mood" (user-friendly term) which maps to "valence" in the dataset. This represents the musical positiveness/happiness of the track.

2. **Title is Optional**: The song title is NOT required and is NOT used in the ML model prediction. It's only stored in the database for reference/display purposes.

3. **Inferred Features**: Three features (`loudness`, `tempo`, `mode`) are automatically calculated from user inputs, as users cannot provide these technical audio features directly.

4. **Feature Order**: The model expects features in this exact order:
   ```
   [duration_ms, danceability, energy, valence, acousticness, 
    instrumentalness, explicit, loudness, tempo, mode]
   ```

## Dataset Columns NOT Used

These columns from the dataset are **not** used in predictions:
- `track_id` - Identifier only
- `artists` - Identifier only  
- `album_name` - Identifier only
- `track_name` - Identifier only
- `popularity` - This is the target variable (used for training, not prediction)
- `key` - Not included in model
- `speechiness` - Not included in model
- `liveness` - Not included in model
- `time_signature` - Not included in model
- `track_genre` - Not included in model

