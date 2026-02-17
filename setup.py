from setuptools import setup, find_packages

import shutil
import os

from telekit._version import __version__ as version

# -----------------------------------------------------------------------------
# Remove old builds
# -----------------------------------------------------------------------------

for folder in ("build", "dist"):
    if os.path.exists(folder):
        shutil.rmtree(folder)

for egg in [d for d in os.listdir('.') if d.endswith(".egg-info")]:
    shutil.rmtree(egg)

# -----------------------------------------------------------------------------
# Read files
# -----------------------------------------------------------------------------

def readme():
    with open('README.md', 'r') as f:
        return f.read()
  
def changelog():
    with open('CHANGELOG.md', 'r') as f:
        return f.read()

def install_requires():
    with open('telekit/requirements.txt', 'r') as f:
        return f.read().split("\n")
    
def long_description():
    return f"{readme()}\n\n---\n\n# Changes in version {version}\n\n{changelog()}"
    
# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------

setup(
    name='telekit',
    version=version,
    description='Declarative, developer-friendly library for building Telegram bots',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    keywords='telegram bot api declarative tools bot-api',
    license="GPLv3",
    author='romashka',
    author_email='notromashka@gmail.com',
    url='https://github.com/Romashkaa/telekit',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires(),
    python_requires=">=3.12",
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    project_urls={
        "GitHub": "https://github.com/Romashkaa/telekit",
        "Telegram": "https://t.me/TelekitLib"
    }
)

print(f"TELEKIT VERSION: {version}")