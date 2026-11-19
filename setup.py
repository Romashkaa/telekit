import re
from pathlib import Path

from setuptools import setup, find_packages

ROOT = Path(__file__).resolve().parent

# -----------------------------------------------------------------------------
# Read files
# -----------------------------------------------------------------------------

def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def read_version() -> str:
    text = read("telekit/__version__.py")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    if match is None:
        raise RuntimeError("Could not find __version__ in telekit/__version__.py")
    return match.group(1)


def install_requires() -> list[str]:
    return [
        line.strip()
        for line in read("telekit/requirements.txt").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def long_description() -> str:
    return f"{read('README.md')}\n\n---\n\n# Changelog\n\n{read('CHANGELOG.md')}"


version = read_version()

# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------

setup(
    name="telekit",
    version=version,
    description="Declarative, developer-friendly framework for building Telegram bots",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    keywords="telegram bot api declarative tools bot-api",
    author="romashka",
    author_email="notromashka@gmail.com",
    url="https://github.com/Romashkaa/telekit",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires(),
    python_requires=">=3.12",
    license="GPL-3.0-or-later",
    license_files=["LICENSE"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "GitHub": "https://github.com/Romashkaa/telekit",
        "Telegram": "https://t.me/TelekitLib",
    },
)