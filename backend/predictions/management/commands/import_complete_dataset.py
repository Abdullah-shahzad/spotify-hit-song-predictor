"""
Complete Dataset Import Command

Clears database and imports all records from cleaned_data.csv
with progress tracking and statistics.

Usage:
    python manage.py import_complete_dataset
    python manage.py import_complete_dataset --csv ../cleaned_data.csv
    python manage.py import_complete_dataset --no-clear  # Skip clearing
"""

from django.core.management.base import BaseCommand
import pandas as pd
import os
from predictions.models import Song, Prediction, PredictionAuditLog


class Command(BaseCommand):
    help = 'Clear database and import complete dataset from cleaned_data.csv'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default='cleaned_data.csv',
            help='Path to cleaned_data.csv (default: cleaned_data.csv)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=2000,
            help='Batch size for bulk insert (default: 2000)'
        )
        parser.add_argument(
            '--no-clear',
            action='store_true',
            help='Skip clearing database before import'
        )

    def handle(self, *args, **options):
        csv_path = options['csv']
        batch_size = options['batch_size']
        clear_first = not options['no_clear']
        
        # Resolve CSV path
        if not os.path.isabs(csv_path):
            from django.conf import settings
            csv_path = os.path.join(settings.BASE_DIR, '..', csv_path)
        
        if not os.path.exists(csv_path):
            self.stdout.write(
                self.style.ERROR(f'❌ File not found: {csv_path}')
            )
            return
        
        # Clear database if requested
        if clear_first:
            self.stdout.write('🗑️  Clearing database...')
            PredictionAuditLog.objects.all().delete()
            Prediction.objects.all().delete()
            song_count = Song.objects.count()
            Song.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Cleared {song_count} songs\n')
            )
        
        # Load CSV
        self.stdout.write(f'📂 Loading {csv_path}...')
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error reading CSV: {str(e)}')
            )
            return
        
        total_records = len(df)
        self.stdout.write(f'📊 Found {total_records:,} records\n')
        
        # Validate columns
        required_columns = [
            'track_id', 'track_name', 'artists', 'album_name', 'popularity',
            'duration_ms', 'danceability', 'energy', 'valence', 'acousticness',
            'instrumentalness', 'loudness', 'tempo', 'mode', 'explicit'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            self.stdout.write(
                self.style.ERROR(f'❌ Missing required columns: {missing_columns}')
            )
            return
        
        # Import records
        self.stdout.write(f'🚀 Starting import (batch size: {batch_size:,})...\n')
        
        records = []
        imported_count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                # Calculate is_hit (>= 50 = HIT)
                popularity = int(row.get('popularity', 0)) if pd.notna(row.get('popularity')) else None
                is_hit = popularity >= 50 if popularity is not None else None
                
                record = Song(
                    track_id=str(row.get('track_id', '')) if pd.notna(row.get('track_id')) else None,
                    track_name=str(row.get('track_name', '')) if pd.notna(row.get('track_name')) else None,
                    artists=str(row.get('artists', '')) if pd.notna(row.get('artists')) else None,
                    album_name=str(row.get('album_name', '')) if pd.notna(row.get('album_name')) else None,
                    popularity=popularity,
                    track_genre=str(row.get('track_genre', '')) if pd.notna(row.get('track_genre')) else None,
                    is_hit=is_hit,
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
                    progress = (imported_count / total_records) * 100
                    self.stdout.write(
                        f'   Progress: {imported_count:,}/{total_records:,} ({progress:.1f}%)'
                    )
                    records = []
                    
            except Exception as e:
                error_count += 1
                if error_count <= 5:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Error row {idx + 1}: {str(e)}')
                    )
                continue
        
        # Create remaining records
        if records:
            Song.objects.bulk_create(records, ignore_conflicts=True)
            imported_count += len(records)
        
        # Final statistics
        total_in_db = Song.objects.count()
        hit_count = Song.objects.filter(is_hit=True).count()
        flop_count = Song.objects.filter(is_hit=False).count()
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ IMPORT COMPLETE'))
        self.stdout.write('='*60)
        self.stdout.write(f'📊 Imported: {imported_count:,} records')
        if error_count > 0:
            self.stdout.write(f'⚠️  Errors: {error_count} records')
        self.stdout.write(f'\n📈 Database Statistics:')
        self.stdout.write(f'   Total songs: {total_in_db:,}')
        self.stdout.write(f'   🎉 HIT songs: {hit_count:,} ({hit_count/total_in_db*100:.1f}%)')
        self.stdout.write(f'   📉 FLOP songs: {flop_count:,} ({flop_count/total_in_db*100:.1f}%)')
        
        if total_in_db == total_records:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ All {total_records:,} records imported!')
            )