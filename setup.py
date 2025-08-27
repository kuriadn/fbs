"""
Minimal setup.py for editable installs only.
All other packaging is handled by pyproject.toml
"""

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name='fbs-suite',
        packages=find_packages(include=[
            'fbs_app', 'fbs_app.*',
            'fbs_dms', 'fbs_dms.*',
            'fbs_license_manager', 'fbs_license_manager.*'
        ]),
        include_package_data=True,
        zip_safe=False,
    )
