from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
    name='telekit',
    version='0.0.11',
    author='romashka',
    author_email='notromashka@gmail.com',
    description='The easiest and most convenient Telegram Bot API',
    long_description=readme(),
    include_package_data=True,
    long_description_content_type='text/markdown',
    url='https://t.me/TeleKitLib',
    packages=find_packages(),
    install_requires=['pyTelegramBotAPI>=4.27.0'],
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='files speedfiles ',
    project_urls={
        "GitHub": "https://github.com/Romashkaa/telekit",
        "Telegram": "https://t.me/TeleKitLib"
    },
    python_requires='>=3.12'
)

# .venv/bin/python setup.py sdist bdist_wheel
# twine upload --repository pypi dist/*