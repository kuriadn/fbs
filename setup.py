"""
FBS App - Embeddable Django Application

A comprehensive business management application that can be installed into any Django project.
Provides MSME tools, accounting, workflows, compliance, and business intelligence capabilities.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "FBS App - Embeddable Django Application"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name='fbs-app',
    version='2.0.0',
    description='Embeddable Django application for business management',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Fayvad Team',
    author_email='team@fayvad.com',
    url='https://github.com/fayvad/fbs-app',
    packages=find_packages(include=['fbs_app', 'fbs_app.*']),
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
    keywords='django, business, msme, accounting, workflows, compliance, bi',
    project_urls={
        'Documentation': 'https://github.com/fayvad/fbs-app#readme',
        'Source': 'https://github.com/fayvad/fbs-app',
        'Tracker': 'https://github.com/fayvad/fbs-app/issues',
    },
    entry_points={
        'console_scripts': [
            'fbs-app=fbs_app.management.commands:main',
        ],
    },
)
