"""Setup for Habito app."""

import os
import sys
from setuptools import setup, find_packages, Command
from shutil import rmtree
from codecs import open
from os import path

# Package meta-data.
NAME = "habito"
DESCRIPTION = "Simple command line habits tracker"
URL = "https://github.com/codito/habito"
EMAIL = "arun@codito.in"
AUTHOR = "Arun Mahapatra"
VERSION = (1, 0, 0)

# Dependencies required for execution
REQUIRED = ["click", "peewee>=3.0.15", "terminaltables"]

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
about["__version__"] = '.'.join(map(str, VERSION))


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Print things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        """Initialize command options."""
        pass

    def finalize_options(self):
        """Finalize command options."""
        pass

    def run(self):
        """Run the upload command."""
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal"
                  .format(sys.executable))

        self.status("Uploading the package to PyPi via Twine…")
        os.system("twine upload dist/*")

        sys.exit()


setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    url=URL,
    author=AUTHOR,
    author_email=EMAIL,

    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    entry_points={
        "console_scripts": ["habito=habito.habito:cli"],
    },
    install_requires=REQUIRED,

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
        "Programming Language :: Python :: 3.6",

        "Topic :: Utilities",
    ],
    keywords="habits goals track tracking quantified self",
    # $ setup.py publish support.
    cmdclass={
        "upload": UploadCommand,
    },
)
