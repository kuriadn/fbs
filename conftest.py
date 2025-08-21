"""
Pytest configuration for FBS App tests.

This file configures pytest-django to use SQLite for testing instead of PostgreSQL.
"""

import pytest
from django.conf import settings

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Override database setup to use SQLite for tests."""
    with django_db_blocker.unblock():
        # Force SQLite for testing
        settings.DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
        yield
