from django.contrib import admin
from .models import Song, Prediction, ModelMetadata, PredictionAuditLog


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('track_name', 'artists', 'popularity', 'is_hit', 'created_at')
    list_filter = ('is_hit', 'is_acoustic', 'is_instrumental', 'explicit', 'created_at')
    search_fields = ('track_name', 'artists', 'track_id')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Song Information', {
            'fields': ('track_id', 'track_name', 'artists', 'album_name', 'popularity', 'track_genre', 'is_hit')
        }),
        ('Audio Features', {
            'fields': (
                'duration_ms',
                'danceability', 'energy', 'valence',
                'acousticness', 'instrumentalness', 'speechiness', 'liveness',
                'loudness', 'tempo', 'mode', 'key', 'time_signature',
                'explicit', 'is_acoustic', 'is_instrumental'
            )
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('song', 'is_hit', 'confidence', 'model_prediction', 'created_at')
    list_filter = ('is_hit', 'adjusted_by_dataset', 'created_at')
    search_fields = ('song__track_name', 'song__artists')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Song', {
            'fields': ('song',)
        }),
        ('Prediction Results', {
            'fields': ('is_hit', 'confidence', 'model_prediction', 'model_confidence')
        }),
        ('Dataset Adjustment', {
            'fields': ('adjusted_by_dataset', 'dataset_label', 'dataset_popularity')
        }),
        ('Model Info', {
            'fields': ('model_version',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )


@admin.register(ModelMetadata)
class ModelMetadataAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'model_version', 'is_active', 'trained_on')
    list_filter = ('is_active', 'trained_on')


@admin.register(PredictionAuditLog)
class PredictionAuditLogAdmin(admin.ModelAdmin):
    list_display = ('prediction', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('prediction__song__track_name', 'prediction__song__artists')
