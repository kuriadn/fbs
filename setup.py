"""
FBS (Fayvad Business Suite) - Odoo-Driven Business Platform

A comprehensive, embeddable Django application ecosystem that provides Odoo-driven 
business management capabilities through three core apps: FBS Core, DMS, and License Manager.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "FBS (Fayvad Business Suite) - Odoo-Driven Business Platform"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Read development requirements
def read_dev_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements-dev.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            return requirements if requirements else []
    return []

setup(
    name='fbs-suite',
    version='2.0.1',
    description='Odoo-driven business management platform for Django',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Fayvad Digital',
    author_email='team@fayvad.com',
    url='https://github.com/kuriadn/fbs',
    packages=find_packages(include=[
        'fbs_app', 'fbs_app.*',
        'fbs_dms', 'fbs_dms.*',
        'fbs_license_manager', 'fbs_license_manager.*'
    ]),
    include_package_data=True,
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=7.4.0,<8.0.0',
            'pytest-django>=4.7.0,<5.0.0',
            'pytest-cov>=4.1.0,<5.0.0',
            'pytest-mock>=3.11.0,<4.0.0',
            'pytest-xdist>=3.3.0,<4.0.0',
            'factory-boy>=3.3.0,<4.0.0',
            'faker>=19.0.0,<20.0.0',
            'coverage>=7.3.0,<8.0.0',
            'black>=23.7.0,<24.0.0',
            'flake8>=6.0.0,<7.0.0',
            'isort>=5.12.0,<6.0.0',
            'mypy>=1.5.0,<2.0.0',
        ],
        'test': [
            'pytest>=7.4.0,<8.0.0',
            'pytest-django>=4.7.0,<5.0.0',
            'pytest-cov>=4.1.0,<5.0.0',
            'pytest-mock>=3.11.0,<4.0.0',
            'pytest-xdist>=3.3.0,<4.0.0',
            'factory-boy>=3.3.0,<4.0.0',
            'faker>=19.0.0,<20.0.0',
            'coverage>=7.3.0,<8.0.0',
        ],
        'docs': [
            'sphinx>=6.0.0,<7.0.0',
            'sphinx-rtd-theme>=1.3.0,<2.0.0',
            'myst-parser>=1.0.0,<2.0.0',
        ]
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Topic :: Office/Business :: Financial :: Point of Sale',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Database :: Front-Ends',
        'Topic :: System :: Systems Administration',
        'Topic :: Text Processing :: Markup :: XML',
    ],
    keywords=[
        'django', 'odoo', 'erp', 'business', 'msme', 'accounting', 
        'workflows', 'compliance', 'bi', 'document-management', 
        'license-management', 'virtual-fields', 'multi-tenant'
    ],
    project_urls={
        'Documentation': 'https://github.com/kuriadn/fbs/tree/main/docs',
        'Source': 'https://github.com/kuriadn/fbs',
        'Tracker': 'https://github.com/kuriadn/fbs/issues',
        'Changelog': 'https://github.com/kuriadn/fbs/releases',
    },
    entry_points={
        'console_scripts': [
            'fbs-manage=fbs_app.management.commands:main',
        ],
        'django.apps': [
            'fbs_app = fbs_app.apps.FBSAppConfig',
            'fbs_dms = fbs_dms.apps.FBSDMSConfig',
            'fbs_license_manager = fbs_license_manager.apps.FBSLicenseManagerConfig',
        ],
    },
    zip_safe=False,
    platforms=['any'],
)
