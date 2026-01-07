from django.db import models


class Song(models.Model):
    """
    Unified table to store:
    1. All rows from cleaned_data.csv (training dataset)
    2. User input songs (from API)
    
    All data stored in same fields regardless of source.
    """
    
    # -----------------------------
    # SONG IDENTIFIERS
    # -----------------------------
    track_id = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        db_index=True,
        help_text="Spotify track ID (extracted from URL if provided)"
    )
    track_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        db_index=True,
        help_text="Song title"
    )
    artists = models.CharField(
        max_length=500,  
        blank=True,
        null=True,
        db_index=True,
        help_text="Artist name(s)"
    )
    album_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Album name"
    )
    popularity = models.IntegerField(
        blank=True,
        null=True,
        db_index=True,
        help_text="Spotify popularity score (0-100)"
    )
    track_genre = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Genre"
    )
    
    # -----------------------------
    # AUDIO FEATURES
    # -----------------------------
    duration_ms = models.IntegerField(help_text="Duration in milliseconds")
    
    # Core features
    danceability = models.FloatField(help_text="0.0 to 1.0")
    energy = models.FloatField(help_text="0.0 to 1.0")
    valence = models.FloatField(help_text="0.0 to 1.0 (mood/positivity)")
    
    # Acoustic features
    acousticness = models.FloatField(help_text="0.0 to 1.0")
    instrumentalness = models.FloatField(help_text="0.0 to 1.0")
    speechiness = models.FloatField(
        blank=True,
        null=True,
        help_text="0.0 to 1.0"
    )
    liveness = models.FloatField(
        blank=True,
        null=True,
        help_text="0.0 to 1.0"
    )
    
    # Audio properties
    loudness = models.FloatField(help_text="dB value (typically -60 to 0)")
    tempo = models.FloatField(help_text="BPM (beats per minute)")
    mode = models.IntegerField(help_text="0=minor, 1=major")
    key = models.IntegerField(
        blank=True,
        null=True,
        help_text="Musical key (0-11)"
    )
    time_signature = models.IntegerField(
        blank=True,
        null=True,
        help_text="Time signature (3, 4, 5, etc.)"
    )
    
    # Boolean flags
    explicit = models.BooleanField(
        default=False,
        help_text="Explicit content flag"
    )
    is_acoustic = models.BooleanField(
        default=False,
        help_text="Derived: acousticness > 0.5"
    )
    is_instrumental = models.BooleanField(
        default=False,
        help_text="Derived: instrumentalness > 0.5"
    )
    
    # -----------------------------
    # HIT/FLOP LABEL (for dataset records)
    # -----------------------------
    is_hit = models.BooleanField(
        null=True,
        blank=True,
        db_index=True,
        help_text="HIT if popularity >= 50, FLOP otherwise (for dataset records)"
    )
    
    # -----------------------------
    # METADATA
    # -----------------------------
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['track_id']),
            models.Index(fields=['track_name', 'artists']),
            models.Index(fields=['popularity']),
        ]
        verbose_name = "Song"
        verbose_name_plural = "Songs"
    
    def __str__(self):
        return f"{self.track_name or 'Unknown'} by {self.artists or 'Unknown'}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate boolean flags
        if self.acousticness is not None:
            self.is_acoustic = self.acousticness > 0.5
        if self.instrumentalness is not None:
            self.is_instrumental = self.instrumentalness > 0.5
        
        # Auto-calculate is_hit based on popularity
        if self.popularity is not None:
            self.is_hit = self.popularity >= 50
        
        super().save(*args, **kwargs)


class Prediction(models.Model):
    """
    Stores ML model predictions.
    Linked to Song table via ForeignKey.
    """
    
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='predictions',
        help_text="Song this prediction is for"
    )
    
    # -----------------------------
    # ML PREDICTION RESULTS
    # -----------------------------
    is_hit = models.BooleanField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Prediction: True=HIT, False=FLOP"
    )
    confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Prediction confidence %"
    )
    
    # Raw model output
    model_prediction = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Raw model prediction: HIT or FLOP"
    )
    model_confidence = models.FloatField(
        blank=True,
        null=True,
        help_text="Raw model confidence before adjustment"
    )
    
    # Prediction adjustments
    adjusted_by_dataset = models.BooleanField(
        default=False,
        help_text="Whether prediction was adjusted based on dataset label"
    )
    dataset_label = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Dataset label if song was in dataset: HIT or FLOP"
    )
    dataset_popularity = models.IntegerField(
        blank=True,
        null=True,
        help_text="Popularity from dataset if available"
    )
    
    model_version = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Version of ML model used"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['song', 'created_at']),
            models.Index(fields=['is_hit']),
        ]
        verbose_name = "Prediction"
        verbose_name_plural = "Predictions"
    
    def __str__(self):
        hit_status = 'HIT' if self.is_hit else 'FLOP'
        return f"{self.song.track_name} | {hit_status} ({self.confidence}%)"


class ModelMetadata(models.Model):
    """
    Tracks ML model versions for auditability
    and future retraining analysis.
    """

    model_name = models.CharField(max_length=100)
    model_version = models.CharField(max_length=50)
    accuracy = models.FloatField(null=True, blank=True)
    trained_on = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-trained_on']

    def __str__(self):
        return f"{self.model_name} v{self.model_version}"


class PredictionAuditLog(models.Model):
    """
    Logs prediction requests for debugging and monitoring.
    """

    prediction = models.ForeignKey(
        Prediction,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    request_payload = models.JSONField()
    response_payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Audit log for {self.prediction.song.track_name} at {self.created_at}"
