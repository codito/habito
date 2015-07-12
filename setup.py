"""Setup for Habito app."""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, "readme.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="habito",

    version="1.0a1",

    description="Simple command line habits tracker",
    long_description=long_description,

    # The project"s main homepage.
    url="https://github.com/codito/habito",

    # Author details
    author="Arun Mahapatra",
    author_email="pratikarun+habito@gmail.com",

    # Choose your license
    license="MIT",

    classifiers=[
        "Development Status :: 3 - Alpha",

        "Environment :: Console",

        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",

        "License :: OSI Approved :: MIT License",

        "Operating System :: MacOS",
        "Operating System :: Microsoft",
        "Operating System :: POSIX :: Linux",

        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",

        "Topic :: Utilities",
    ],

    keywords="habits goals track tracking quantified self",

    packages=find_packages(exclude=["contrib", "docs", "tests*"]),

    install_requires=["click", "peewee", "terminaltables"],

    entry_points={
        "console_scripts": [
            "habito=habito.habito:cli",
        ],
    },
)
