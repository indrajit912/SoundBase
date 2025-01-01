# setup.py
from setuptools import setup, find_packages
from pathlib import Path

# Define the base directory
base_dir = Path(__file__).resolve().parent

# Read the version from soundbase/version.py
version = {}
version_path = base_dir / 'soundbase' / 'version.py'
with open(version_path) as f:
    exec(f.read(), version)

# Read the long description from README.md
long_description = (base_dir / 'README.md').read_text()

# Generate the install_requires list from requirements.txt
install_requires = (base_dir / 'requirements.txt').read_text().splitlines()

setup(
    name='soundbase',  # Update with your project name
    version=version['__version__'],  # Update version if necessary
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'soundbase = soundbase.cli:cli',
        ],
    },
    author='Indrajit Ghosh',
    author_email='your_email@example.com',  # Replace with your actual email
    description='A media management application for SoundBase',  # Update description
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/yourusername/soundbase",  # Replace with your repo URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Update if using a different license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',  # Minimum Python version required
)
