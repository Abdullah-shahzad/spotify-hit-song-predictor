"""
Management command to import cleaned_data.csv into Song table.

Usage:
    python manage.py import_dataset ../cleaned_data.csv
"""

from django.core.management.base import BaseCommand
import pandas as pd
import os
from predictions.models import Song


class Command(BaseCommand):
    help = 'Import cleaned_data.csv into Song table'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_path',
            type=str,
            help='Path to cleaned_data.csv file'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of records to import per batch (default: 1000)'
        )

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        batch_size = options['batch_size']
        
        # Resolve path relative to project root
        if not os.path.isabs(csv_path):
            from django.conf import settings
            csv_path = os.path.join(settings.BASE_DIR, '..', csv_path)
        
        if not os.path.exists(csv_path):
            self.stdout.write(
                self.style.ERROR(f'File not found: {csv_path}')
            )
            return
        
        self.stdout.write(f'Loading {csv_path}...')
        
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading CSV: {str(e)}')
            )
            return
        
        total_records = len(df)
        self.stdout.write(f'Found {total_records} records')
        
        # Check for required columns
        required_columns = [
            'track_id', 'track_name', 'artists', 'album_name', 'popularity',
            'duration_ms', 'danceability', 'energy', 'valence', 'acousticness',
            'instrumentalness', 'loudness', 'tempo', 'mode', 'explicit'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            self.stdout.write(
                self.style.ERROR(f'Missing required columns: {missing_columns}')
            )
            return
        
        # Convert to Song records
        records = []
        imported_count = 0
        skipped_count = 0
        
        for idx, row in df.iterrows():
            try:
                # Check if record already exists
                if Song.objects.filter(
                    track_id=row.get('track_id', '')
                ).exists():
                    skipped_count += 1
                    continue
                
                # Calculate is_hit based on popularity (>= 50 = HIT)
                popularity = int(row.get('popularity', 0)) if pd.notna(row.get('popularity')) else None
                is_hit = popularity >= 50 if popularity is not None else None
                
                record = Song(
                    track_id=str(row.get('track_id', '')) if pd.notna(row.get('track_id')) else None,
                    track_name=str(row.get('track_name', '')) if pd.notna(row.get('track_name')) else None,
                    artists=str(row.get('artists', '')) if pd.notna(row.get('artists')) else None,
                    album_name=str(row.get('album_name', '')) if pd.notna(row.get('album_name')) else None,
                    popularity=popularity,
                    track_genre=str(row.get('track_genre', '')) if pd.notna(row.get('track_genre')) else None,
                    is_hit=is_hit,  # Store hit/flop based on popularity
                    duration_ms=int(row.get('duration_ms', 0)),
                    danceability=float(row.get('danceability', 0)),
                    energy=float(row.get('energy', 0)),
                    valence=float(row.get('valence', 0)),
                    acousticness=float(row.get('acousticness', 0)),
                    instrumentalness=float(row.get('instrumentalness', 0)),
                    loudness=float(row.get('loudness', 0)),
                    tempo=float(row.get('tempo', 0)),
                    mode=int(row.get('mode', 0)),
                    explicit=bool(row.get('explicit', False)),
                    key=int(row.get('key', 0)) if pd.notna(row.get('key')) else None,
                    speechiness=float(row.get('speechiness', 0)) if pd.notna(row.get('speechiness')) else None,
                    liveness=float(row.get('liveness', 0)) if pd.notna(row.get('liveness')) else None,
                    time_signature=int(row.get('time_signature', 4)) if pd.notna(row.get('time_signature')) else None,
                )
                records.append(record)
                
                # Bulk create in batches
                if len(records) >= batch_size:
                    Song.objects.bulk_create(records, ignore_conflicts=True)
                    imported_count += len(records)
                    self.stdout.write(f'Imported {imported_count}/{total_records} records...')
                    records = []
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error processing row {idx + 1}: {str(e)}')
                )
                continue
        
        # Create remaining records
        if records:
            Song.objects.bulk_create(records, ignore_conflicts=True)
            imported_count += len(records)
        
        # Show statistics
        hit_count = Song.objects.filter(is_hit=True).count()
        flop_count = Song.objects.filter(is_hit=False).count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully imported {imported_count} records from dataset!'
            )
        )
        self.stdout.write(f'   📊 HIT songs: {hit_count}')
        self.stdout.write(f'   📉 FLOP songs: {flop_count}')
        
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'   ⚠️  Skipped {skipped_count} records (already exist in database)'
                )
            )

