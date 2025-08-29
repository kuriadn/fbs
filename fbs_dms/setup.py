"""
FBS DMS - Document Management System

A standalone, embeddable document management solution for Django applications
that provides enterprise-grade document storage, workflow management, and Odoo integration.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "FBS DMS - Document Management System"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name='fbs-dms',
    version='2.0.4',
    description='Embeddable Django application for document management',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Fayvad Team',
    author_email='team@fayvad.com',
    url='https://github.com/fayvad/fbs-dms',
    packages=find_packages(include=['fbs_dms', 'fbs_dms.*']),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='django, document, management, dms, workflow, approval',
    project_urls={
        'Documentation': 'https://github.com/fayvad/fbs-dms#readme',
        'Source': 'https://github.com/fayvad/fbs-dms',
        'Tracker': 'https://github.com/fayvad/fbs-dms/issues',
    },
    entry_points={
        'console_scripts': [
            'fbs-dms=fbs_dms.management.commands:main',
        ],
    },
)
