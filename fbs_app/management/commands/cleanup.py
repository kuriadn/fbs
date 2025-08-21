"""
Django management command for system cleanup and maintenance.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger('fbs_app')


class Command(BaseCommand):
    help = 'Perform system cleanup and maintenance tasks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup-type',
            type=str,
            choices=['all', 'logs', 'cache', 'notifications', 'audit_trails', 'temp_files'],
            default='all',
            help='Type of cleanup to perform'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to keep data (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned without actually doing it'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force cleanup without confirmation'
        )
        parser.add_argument(
            '--solution',
            type=str,
            help='Specific solution to clean up'
        )
    
    def handle(self, *args, **options):
        try:
            cleanup_type = options['cleanup_type']
            days = options['days']
            dry_run = options['dry_run']
            force = options['force']
            solution_name = options.get('solution')
            
            if dry_run:
                self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))
            
            # Calculate cutoff date
            cutoff_date = timezone.now() - timedelta(days=days)
            
            self.stdout.write(f"Performing {cleanup_type} cleanup for data older than {days} days")
            self.stdout.write(f"Cutoff date: {cutoff_date}")
            
            if cleanup_type in ['all', 'logs']:
                self._cleanup_request_logs(cutoff_date, dry_run, force, solution_name)
            
            if cleanup_type in ['all', 'cache']:
                self._cleanup_cache_entries(cutoff_date, dry_run, force, solution_name)
            
            if cleanup_type in ['all', 'notifications']:
                self._cleanup_notifications(cutoff_date, dry_run, force, solution_name)
            
            if cleanup_type in ['all', 'audit_trails']:
                self._cleanup_audit_trails(cutoff_date, dry_run, force, solution_name)
            
            if cleanup_type in ['all', 'temp_files']:
                self._cleanup_temp_files(dry_run, force)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Cleanup completed successfully for type: {cleanup_type}"
                )
            )
            
        except Exception as e:
            logger.error(f"Error in cleanup command: {str(e)}")
            raise CommandError(f"Cleanup failed: {str(e)}")
    
    def _cleanup_request_logs(self, cutoff_date, dry_run, force, solution_name):
        """Clean up old request logs"""
        try:
            from fbs_app.models import RequestLog
            
            # Build query
            query = {'created_at__lt': cutoff_date}
            if solution_name:
                query['solution_name'] = solution_name
            
            # Count records to be deleted
            logs_to_delete = RequestLog.objects.filter(**query)
            count = logs_to_delete.count()
            
            if count == 0:
                self.stdout.write("No old request logs found to clean up")
                return
            
            self.stdout.write(f"Found {count} old request logs to clean up")
            
            if not force and not dry_run:
                confirm = input(f"Delete {count} old request logs? (y/N): ")
                if confirm.lower() != 'y':
                    self.stdout.write("Request log cleanup cancelled")
                    return
            
            if not dry_run:
                logs_to_delete.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Deleted {count} old request logs"
                    )
                )
            else:
                self.stdout.write(f"Would delete {count} old request logs")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Error cleaning up request logs: {str(e)}"
                )
            )
    
    def _cleanup_cache_entries(self, cutoff_date, dry_run, force, solution_name):
        """Clean up old cache entries"""
        try:
            from fbs_app.models import CacheEntry
            
            # Build query
            query = {'created_at__lt': cutoff_date}
            if solution_name:
                query['solution_name'] = solution_name
            
            # Count records to be deleted
            cache_to_delete = CacheEntry.objects.filter(**query)
            count = cache_to_delete.count()
            
            if count == 0:
                self.stdout.write("No old cache entries found to clean up")
                return
            
            self.stdout.write(f"Found {count} old cache entries to clean up")
            
            if not force and not dry_run:
                confirm = input(f"Delete {count} old cache entries? (y/N): ")
                if confirm.lower() != 'y':
                    self.stdout.write("Cache cleanup cancelled")
                    return
            
            if not dry_run:
                cache_to_delete.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Deleted {count} old cache entries"
                    )
                )
            else:
                self.stdout.write(f"Would delete {count} old cache entries")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Error cleaning up cache entries: {str(e)}"
                )
            )
    
    def _cleanup_notifications(self, cutoff_date, dry_run, force, solution_name):
        """Clean up old notifications"""
        try:
            from fbs_app.models import Notification
            
            # Build query
            query = {'created_at__lt': cutoff_date}
            if solution_name:
                query['solution_name'] = solution_name
            
            # Count records to be deleted
            notifications_to_delete = Notification.objects.filter(**query)
            count = notifications_to_delete.count()
            
            if count == 0:
                self.stdout.write("No old notifications found to clean up")
                return
            
            self.stdout.write(f"Found {count} old notifications to clean up")
            
            if not force and not dry_run:
                confirm = input(f"Delete {count} old notifications? (y/N): ")
                if confirm.lower() != 'y':
                    self.stdout.write("Notification cleanup cancelled")
                    return
            
            if not dry_run:
                notifications_to_delete.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Deleted {count} old notifications"
                    )
                )
            else:
                self.stdout.write(f"Would delete {count} old notifications")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Error cleaning up notifications: {str(e)}"
                )
            )
    
    def _cleanup_audit_trails(self, cutoff_date, dry_run, force, solution_name):
        """Clean up old audit trails"""
        try:
            from fbs_app.models import AuditTrail
            
            # Build query
            query = {'timestamp__lt': cutoff_date}
            if solution_name:
                query['solution_name'] = solution_name
            
            # Count records to be deleted
            audit_trails_to_delete = AuditTrail.objects.filter(**query)
            count = audit_trails_to_delete.count()
            
            if count == 0:
                self.stdout.write("No old audit trails found to clean up")
                return
            
            self.stdout.write(f"Found {count} old audit trails to clean up")
            
            if not force and not dry_run:
                confirm = input(f"Delete {count} old audit trails? (y/N): ")
                if confirm.lower() != 'y':
                    self.stdout.write("Audit trail cleanup cancelled")
                    return
            
            if not dry_run:
                audit_trails_to_delete.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Deleted {count} old audit trails"
                    )
                )
            else:
                self.stdout.write(f"Would delete {count} old audit trails")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Error cleaning up audit trails: {str(e)}"
                )
            )
    
    def _cleanup_temp_files(self, dry_run, force):
        """Clean up temporary files"""
        try:
            import os
            import tempfile
            
            # Get temp directory
            temp_dir = tempfile.gettempdir()
            
            # Look for FBS-related temp files
            fbs_temp_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.startswith('fbs_') or file.endswith('_fbs'):
                        file_path = os.path.join(root, file)
                        fbs_temp_files.append(file_path)
            
            if not fbs_temp_files:
                self.stdout.write("No FBS temporary files found to clean up")
                return
            
            self.stdout.write(f"Found {len(fbs_temp_files)} FBS temporary files to clean up")
            
            if not force and not dry_run:
                confirm = input(f"Delete {len(fbs_temp_files)} temporary files? (y/N): ")
                if confirm.lower() != 'y':
                    self.stdout.write("Temporary file cleanup cancelled")
                    return
            
            deleted_count = 0
            for file_path in fbs_temp_files:
                try:
                    if not dry_run:
                        os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Could not delete {file_path}: {str(e)}"
                        )
                    )
            
            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Deleted {deleted_count} temporary files"
                    )
                )
            else:
                self.stdout.write(f"Would delete {deleted_count} temporary files")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Error cleaning up temporary files: {str(e)}"
                )
            )
    
    def _get_cleanup_summary(self, solution_name=None):
        """Get summary of cleanup operations"""
        try:
            from fbs_app.models import RequestLog, CacheEntry, Notification, AuditTrail
            
            summary = {
                'request_logs': 0,
                'cache_entries': 0,
                'notifications': 0,
                'audit_trails': 0
            }
            
            # Count records by type
            if solution_name:
                summary['request_logs'] = RequestLog.objects.filter(solution_name=solution_name).count()
                summary['cache_entries'] = CacheEntry.objects.filter(solution_name=solution_name).count()
                summary['notifications'] = Notification.objects.filter(solution_name=solution_name).count()
                summary['audit_trails'] = AuditTrail.objects.filter(solution_name=solution_name).count()
            else:
                summary['request_logs'] = RequestLog.objects.count()
                summary['cache_entries'] = CacheEntry.objects.count()
                summary['notifications'] = Notification.objects.count()
                summary['audit_trails'] = AuditTrail.objects.count()
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting cleanup summary: {str(e)}")
            return {}
