"""
FBS Core Signals

Django signals for FBS core functionality.
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import Signal
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .utils.audit import log_audit_event


# Custom FBS signals
solution_created = Signal()  # sender: FBSSolution
solution_updated = Signal()  # sender: FBSSolution
solution_deleted = Signal()  # sender: FBSSolution

user_solution_changed = Signal()  # sender: FBSUser, old_solution, new_solution
api_token_used = Signal()  # sender: FBSAPIToken, user, endpoint
license_feature_accessed = Signal()  # sender: Solution, feature_name, user

system_setting_changed = Signal()  # sender: FBSSystemSettings, old_value, new_value


# Signal handlers
def handle_user_login(sender, request, user, **kwargs):
    """Handle user login events"""
    if hasattr(user, 'solution'):
        log_audit_event(
            action='login',
            resource_type='user',
            resource_id=str(user.id),
            solution=user.solution,
            user=user,
            details={
                'ip_address': getattr(request, 'META', {}).get('REMOTE_ADDR'),
                'user_agent': getattr(request, 'META', {}).get('HTTP_USER_AGENT'),
            },
            ip_address=getattr(request, 'META', {}).get('REMOTE_ADDR'),
            user_agent=getattr(request, 'META', {}).get('HTTP_USER_AGENT'),
        )


def handle_user_logout(sender, request, user, **kwargs):
    """Handle user logout events"""
    if hasattr(user, 'solution'):
        log_audit_event(
            action='logout',
            resource_type='user',
            resource_id=str(user.id),
            solution=user.solution,
            user=user,
            details={
                'ip_address': getattr(request, 'META', {}).get('REMOTE_ADDR'),
                'user_agent': getattr(request, 'META', {}).get('HTTP_USER_AGENT'),
            },
            ip_address=getattr(request, 'META', {}).get('REMOTE_ADDR'),
            user_agent=getattr(request, 'META', {}).get('HTTP_USER_AGENT'),
        )


def handle_solution_created(sender, instance, created, **kwargs):
    """Handle solution creation"""
    if created:
        log_audit_event(
            action='create',
            resource_type='solution',
            resource_id=str(instance.id),
            solution=instance,
            details={
                'solution_name': instance.name,
                'display_name': instance.display_name,
            }
        )

        # Send custom signal
        solution_created.send(sender=instance)


def handle_solution_updated(sender, instance, created, **kwargs):
    """Handle solution updates"""
    if not created:
        log_audit_event(
            action='update',
            resource_type='solution',
            resource_id=str(instance.id),
            solution=instance,
            details={
                'solution_name': instance.name,
                'display_name': instance.display_name,
            }
        )

        # Send custom signal
        solution_updated.send(sender=instance)


def handle_solution_deleted(sender, instance, **kwargs):
    """Handle solution deletion"""
    log_audit_event(
        action='delete',
        resource_type='solution',
        resource_id=str(instance.id),
        solution=instance,
        details={
            'solution_name': instance.name,
            'display_name': instance.display_name,
        }
    )

    # Send custom signal
    solution_deleted.send(sender=instance)


def handle_user_created(sender, instance, created, **kwargs):
    """Handle user creation"""
    if created and hasattr(instance, 'solution'):
        log_audit_event(
            action='create',
            resource_type='user',
            resource_id=str(instance.id),
            solution=instance.solution,
            user=instance,
            details={
                'username': instance.username,
                'email': instance.email,
            }
        )


def handle_user_updated(sender, instance, created, **kwargs):
    """Handle user updates"""
    if not created and hasattr(instance, 'solution'):
        log_audit_event(
            action='update',
            resource_type='user',
            resource_id=str(instance.id),
            solution=instance.solution,
            user=instance,
            details={
                'username': instance.username,
                'email': instance.email,
            }
        )


def handle_api_token_used(sender, instance, **kwargs):
    """Handle API token usage"""
    log_audit_event(
        action='access',
        resource_type='api_token',
        resource_id=str(instance.id),
        solution=instance.user.solution,
        user=instance.user,
        details={
            'token_name': instance.name,
            'endpoint': getattr(kwargs.get('request'), 'path', 'unknown'),
        }
    )

    # Send custom signal
    api_token_used.send(sender=instance, user=instance.user)


def handle_system_setting_changed(sender, instance, **kwargs):
    """Handle system setting changes"""
    # This would need to track old vs new values
    # For now, just log the change
    log_audit_event(
        action='update',
        resource_type='system_setting',
        resource_id=instance.key,
        solution=None,  # System-wide
        details={
            'setting_key': instance.key,
            'new_value': instance.value,
            'setting_type': instance.setting_type,
        }
    )

    # Send custom signal with old/new values
    old_value = getattr(instance, '_original_value', None)
    if old_value != instance.value:
        system_setting_changed.send(
            sender=instance,
            old_value=old_value,
            new_value=instance.value
        )


# Connect signals
user_logged_in.connect(handle_user_login)
user_logged_out.connect(handle_user_logout)

# Import models here to avoid circular imports
def connect_model_signals():
    """Connect model signals - called from apps.py"""
    from .models import FBSSolution, FBSUser, FBSAPIToken, FBSSystemSettings

    post_save.connect(handle_solution_created, sender=FBSSolution)
    post_save.connect(handle_solution_updated, sender=FBSSolution)
    post_delete.connect(handle_solution_deleted, sender=FBSSolution)

    post_save.connect(handle_user_created, sender=FBSUser)
    post_save.connect(handle_user_updated, sender=FBSUser)

    # API token usage signal
    api_token_used.connect(handle_api_token_used)

    # System setting changes
    pre_save.connect(
        lambda sender, instance, **kwargs: setattr(instance, '_original_value',
                                                  getattr(sender.objects.filter(pk=instance.pk).first(), 'value', None)
                                                  if instance.pk else None),
        sender=FBSSystemSettings
    )
    post_save.connect(handle_system_setting_changed, sender=FBSSystemSettings)

