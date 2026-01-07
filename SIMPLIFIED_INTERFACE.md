# Simplified User Interface

## ✅ **Now Only 4 Required Fields!**

The interface has been simplified to be much more user-friendly. Users only need to provide **4 essential fields**:

### Required Fields (Minimal Set)

1. **Duration** (minutes) - e.g., 3.5
2. **Danceability** (slider: 0.0 to 1.0)
3. **Energy** (slider: 0.0 to 1.0)
4. **Mood** (slider: 0.0 to 1.0) - Maps to valence

### Optional Fields (Hidden by Default)

All other fields are now **optional** with smart defaults:

- **Acoustic** - Defaults to `False` (uses median acousticness: 0.136)
- **Instrumental** - Defaults to `False` (uses median instrumentalness: 0.0001)
- **Explicit** - Defaults to `False` (only 10.4% of songs are explicit)

These are hidden in a collapsible "Additional Options" section.

## Smart Defaults

Based on dataset analysis:

| Field | Default Value | Reason |
|-------|--------------|--------|
| `acousticness` | 0.136 | Median value from dataset |
| `instrumentalness` | 0.0001 | Median value (most songs have vocals) |
| `explicit` | 0.0 (False) | Only 10.4% of songs are explicit |
| `loudness` | Inferred from energy | Formula: `15.12 × energy - 18.01` |
| `tempo` | Inferred from energy + danceability | Formula: `29.07 × energy - 15.01 × danceability + 112.53` |
| `mode` | Inferred from mood | `1 if mood > 0.5 else 0` |

## Feature Importance

The top 8 features account for **98% of importance**:
1. duration_ms (14.5%)
2. acousticness (12.8%)
3. energy (12.6%)
4. valence/mood (12.4%)
5. danceability (12.2%)
6. loudness (11.9%)
7. tempo (11.7%)
8. instrumentalness (10.0%)

The least important features (`explicit` at 0.76% and `mode` at 1.28%) can safely use defaults.

## User Experience

### Before (7 required fields):
- ❌ Song Title
- ❌ Duration
- ❌ Danceability
- ❌ Energy
- ❌ Mood
- ❌ Acoustic (checkbox)
- ❌ Instrumental (checkbox)
- ❌ Explicit (checkbox)

### After (4 required fields):
- ✅ Duration
- ✅ Danceability
- ✅ Energy
- ✅ Mood
- ⚙️ Additional Options (collapsible, optional)

## API Changes

### Minimal Request Example:
```json
{
    "duration_minutes": 3.5,
    "danceability": 0.75,
    "energy": 0.65,
    "mood": 0.8
}
```

That's it! Everything else uses smart defaults.

### With Optional Fields:
```json
{
    "duration_minutes": 3.5,
    "danceability": 0.75,
    "energy": 0.65,
    "mood": 0.8,
    "is_acoustic": true,  // Optional
    "is_instrumental": false,  // Optional
    "is_explicit": true  // Optional
}
```

## Benefits

1. **Much simpler** - 4 fields instead of 7+
2. **Faster** - Users can predict in seconds
3. **Smart defaults** - Based on actual dataset statistics
4. **Still accurate** - Top 8 features (98% importance) are handled
5. **Flexible** - Advanced users can still provide all fields

## Testing

The model still works correctly with just the 4 required fields. The defaults are based on dataset medians and statistics, ensuring reasonable predictions even without explicit values.

