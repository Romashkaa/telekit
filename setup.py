from setuptools import setup, find_packages

from telekit._version import __version__ as version

def readme():
    with open('README.md', 'r') as f:
        return f.read()
  
def changelog():
    with open('CHANGELOG.md', 'r') as f:
        return f.read()

def install_requires():
    with open('telekit/requirements.txt', 'r') as f:
        return f.read().split("\n")

setup(
    name='telekit',
    version=version,
    author='romashka',
    author_email='notromashka@gmail.com',
    description='Declarative, developer-friendly library for building Telegram bots',
    long_description=readme() + "\n\n---\n\n# Changelog:\n\n" + changelog(),
    include_package_data=True,
    long_description_content_type='text/markdown',
    url='https://github.com/Romashkaa/telekit',
    packages=find_packages(),
    install_requires=install_requires(),
    classifiers=[
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='telegram bot api declarative tools ',
    project_urls={
        "GitHub": "https://github.com/Romashkaa/telekit",
        "Telegram": "https://t.me/TelekitLib"
    },
    python_requires=">=3.12.11"
)

"""
.venv/bin/python setup.py sdist bdist_wheel
twine upload --repository pypi dist/*
"""

print(f"TELEKIT VERSION: {version}")