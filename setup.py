
import os

try:
    from setuptools import setup
except ImportError:
    from distutils import setup

long_description = open(os.path.join(os.path.dirname(__file__), "README.md")).read()

setup(
    name="ontologyutils",
    version="0.2",
    description=long_description.split("\n")[0],
    long_description=long_description,
    author="Gautier Koscielny",
    author_email="gautier.x.koscielny@gsk.com",
    url="https://github.com/opentargets",
    packages=["ontologyutils"],
    license="Apache2",
    classifiers=[
        "License :: Apache 2",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
)

