from setuptools import setup, find_packages
setup(
    name="Flocker Admin Tools",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'jira-backup = admin.jira.backup:main',
        ],
    },
)
