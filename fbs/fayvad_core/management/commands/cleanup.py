from django.core.management.base import BaseCommand
from django.utils import timezone
from fayvad_core.services import AuthService, CacheService
from fayvad_core.models import RequestLog
from datetime import timedelta


class Command(BaseCommand):
    help = 'Clean up expired tokens, cache entries, and old request logs'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete request logs older than this many days (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Starting cleanup process...')
        
        # Clean up expired tokens
        self.stdout.write('Cleaning up expired tokens...')
        expired_tokens = AuthService.cleanup_expired_tokens()
        self.stdout.write(
            self.style.SUCCESS(f'Cleaned up {expired_tokens} expired tokens')
        )
        
        # Clean up expired cache entries
        self.stdout.write('Cleaning up expired cache entries...')
        expired_cache = CacheService.cleanup_expired_cache()
        self.stdout.write(
            self.style.SUCCESS(f'Cleaned up {expired_cache} expired cache entries')
        )
        
        # Clean up old request logs
        self.stdout.write(f'Cleaning up request logs older than {options["days"]} days...')
        cutoff_date = timezone.now() - timedelta(days=options['days'])
        
        old_logs = RequestLog.objects.filter(created_at__lt=cutoff_date)
        count = old_logs.count()
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f'Would delete {count} request logs (dry run)')
            )
        else:
            old_logs.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {count} old request logs')
            )
        
        self.stdout.write(self.style.SUCCESS('Cleanup completed successfully!'))
