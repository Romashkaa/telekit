from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()
  
def changelog():
    with open('CHANGELOG.md', 'r') as f:
        return f.read()


setup(
    name='telekit',
    version='1.3.0',
    author='romashka',
    author_email='notromashka@gmail.com',
    description='Declarative, developer-friendly library for building Telegram bots',
    long_description=readme() + "\n\n---\n\n# Changelog:\n\n" + changelog(),
    include_package_data=True,
    long_description_content_type='text/markdown',
    url='https://github.com/Romashkaa/telekit',
    packages=find_packages(),
    install_requires=['pyTelegramBotAPI>=4.29.1', 'charset_normalizer>=3.4.2'],
    classifiers=[
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='files speedfiles ',
    project_urls={
        "GitHub": "https://github.com/Romashkaa/telekit",
        "Telegram": "https://t.me/TelekitLib"
    },
    python_requires=">=3.13.7"
)

"""
.venv/bin/python setup.py sdist bdist_wheel
twine upload --repository pypi dist/*
"""