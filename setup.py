import pathlib

from setuptools import setup, find_packages

from msorm import __version__

VERSION = __version__
DESCRIPTION = 'ORM support for Mssql in python3'
# LONG_DESCRIPTION = 'A package inspired by django model system and implemented that system for mssql via using pyodbc'
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# Setting up
setup(
    name="msorm",
    version=VERSION,
    author="Mehmet Berkay Özbay",
    author_email="<berkayozbay64@gmail.com>",
    url="https://github.com/bilinenkisi/msorm",
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",

    packages=find_packages(),
    install_requires=["pyodbc"],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'MSORM', "msorm", "mssql-python", "mssql orm in python"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
