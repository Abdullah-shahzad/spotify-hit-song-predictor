# Troubleshooting: Why Predictions Don't Match Dataset

## Problem: Model Predicts FLOP but Dataset Shows HIT

If you're testing with a song from the dataset and getting incorrect predictions, here are the common causes:

## Root Causes

### 1. **Input Values Don't Match Dataset**

The most common issue is entering values that don't match the dataset row you're testing.

**Example from your test:**
- **Dataset**: Duration = 230666 ms = **3.84 minutes**
- **Your Input**: Duration = **2.30 minutes** ❌

**Solution**: Use the exact values from the dataset:
- Convert `duration_ms` to minutes: `230666 / 60000 = 3.84 minutes`
- Use exact `danceability`, `energy`, `valence` values
- Check `acousticness`: If < 0.5, uncheck "Acoustic" checkbox

### 2. **Inferred Features Are Approximations**

Three features (`loudness`, `tempo`, `mode`) are **inferred** from your inputs because users can't provide them directly. These are **approximations**, not exact values.

**Current Inference Formulas:**
- **Loudness**: `15.12 × energy - 18.01` (R² = 0.601 - moderate accuracy)
- **Tempo**: `29.07 × energy - 15.01 × danceability + 112.53` (R² = 0.066 - poor accuracy)
- **Mode**: `1 if mood > 0.5 else 0` (weak correlation with valence)

**Why This Matters:**
- The model was trained on **actual audio features** from Spotify
- We're sending **approximated values** that may differ significantly
- Even small differences can affect predictions

### 3. **Acoustic Checkbox Logic**

The "Acoustic" checkbox is a boolean (checked/unchecked), but the dataset has `acousticness` as a float (0.0 to 1.0).

**Rule of Thumb:**
- If `acousticness < 0.5` → **Uncheck** "Acoustic"
- If `acousticness ≥ 0.5` → **Check** "Acoustic"

**Your Test Case:**
- Dataset: `acousticness = 0.0322` (very low!)
- Should be: **Unchecked** ❌
- You had: **Checked** ❌

## How to Test Accurately

### Option 1: Use Exact Dataset Values

1. **Duration**: Convert `duration_ms` to minutes
   ```
   duration_minutes = duration_ms / 60000
   Example: 230666 / 60000 = 3.84 minutes
   ```

2. **Checkboxes**: Use threshold of 0.5
   - `acousticness < 0.5` → Uncheck
   - `acousticness ≥ 0.5` → Check
   - Same for `instrumentalness` and `explicit`

3. **Accept Approximation Error**: The inferred features (`loudness`, `tempo`, `mode`) will still be approximations, but should be closer.

### Option 2: Check Debug Output

The API now returns debug information showing exactly what features were sent to the model:

```json
{
  "prediction": "FLOP",
  "confidence": 10.35,
  "debug": {
    "features_sent_to_model": {
      "duration_ms": 138000,
      "danceability": 0.67,
      "energy": 0.46,
      "valence": 0.71,
      "acousticness": 1.0,
      "instrumentalness": 0.0,
      "explicit": 0.0,
      "loudness": -11.05,
      "tempo": 115.79,
      "mode": 1
    }
  }
}
```

Compare these with the dataset values to see the differences.

## Example: Correct Input for "Comedy" Song

From dataset row:
```
duration_ms: 230666
danceability: 0.676
energy: 0.461
valence: 0.715
acousticness: 0.0322
instrumentalness: 1.01e-06
explicit: 0
loudness: -6.746
tempo: 87.917
mode: 0
```

**Correct Frontend Input:**
- Duration: **3.84** minutes (not 2.30!)
- Danceability: **0.676** (or 0.68 rounded)
- Energy: **0.461** (or 0.46 rounded)
- Mood: **0.715** (or 0.72 rounded)
- Acoustic: **Unchecked** (0.0322 < 0.5)
- Instrumental: **Unchecked** (1.01e-06 < 0.5)
- Explicit: **Unchecked** (0 < 0.5)

**Note**: Even with correct inputs, `loudness`, `tempo`, and `mode` will be approximated:
- Inferred loudness: -11.05 (actual: -6.746) - difference of 4.3 dB
- Inferred tempo: 115.79 (actual: 87.917) - difference of 27.9 BPM
- Inferred mode: 1 (actual: 0) - mismatch!

These approximations may still cause prediction differences.

## Why This System Design?

This system is designed for **real-world use** where:
- Users don't have access to technical audio features
- We need to infer `loudness`, `tempo`, and `mode` from simple inputs
- The approximations are "good enough" for most cases

For **testing with dataset rows**, you should:
1. Use exact values where possible
2. Accept that inferred features will be approximations
3. Focus on testing with songs that have similar inferred values

## Improving Accuracy

If you need more accurate predictions:
1. **Collect actual audio features** from Spotify API or audio analysis tools
2. **Don't use inference** - use real `loudness`, `tempo`, and `mode` values
3. **Retrain the model** with a dataset that includes inferred features (to match what users will provide)

