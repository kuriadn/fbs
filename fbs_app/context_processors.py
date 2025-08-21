"""
FBS App Context Processors

Context processors for providing FBS settings to templates.
"""

from django.conf import settings


def fbs_settings(request):
    """Add FBS app settings to template context"""
    fbs_config = getattr(settings, 'FBS_APP', {})
    
    return {
        'FBS_APP': fbs_config,
        'FBS_URL_PREFIX': getattr(settings, 'FBS_URL_PREFIX', 'fbs/'),

        'FBS_STATIC_URL': getattr(settings, 'FBS_STATIC_URL', 'fbs/static/'),
        'FBS_MEDIA_URL': getattr(settings, 'FBS_MEDIA_URL', 'fbs/media/'),
    }
