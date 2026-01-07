"""
Management command to clear all data from Song and Prediction tables.

Usage:
    python manage.py clear_database
    python manage.py clear_database --confirm
"""

from django.core.management.base import BaseCommand
from predictions.models import Song, Prediction, PredictionAuditLog


class Command(BaseCommand):
    help = 'Clear all data from Song and Prediction tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt'
        )

    def handle(self, *args, **options):
        confirm = options['confirm']
        
        if not confirm:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  WARNING: This will delete ALL songs and predictions from the database!'
                )
            )
            response = input('Type "yes" to confirm: ')
            if response.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Operation cancelled.'))
                return
        
        # Count records before deletion
        song_count = Song.objects.count()
        prediction_count = Prediction.objects.count()
        audit_count = PredictionAuditLog.objects.count()
        
        self.stdout.write(f'Found {song_count} songs, {prediction_count} predictions, {audit_count} audit logs')
        
        # Delete in order (respecting foreign keys)
        self.stdout.write('Deleting audit logs...')
        PredictionAuditLog.objects.all().delete()
        
        self.stdout.write('Deleting predictions...')
        Prediction.objects.all().delete()
        
        self.stdout.write('Deleting songs...')
        Song.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully cleared database!'
            )
        )
        self.stdout.write(f'   - Deleted {song_count} songs')
        self.stdout.write(f'   - Deleted {prediction_count} predictions')
        self.stdout.write(f'   - Deleted {audit_count} audit logs')

