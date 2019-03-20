#!/usr/bin/env python
import os

try:
    from setuptools import setup
except ImportError:
    from distutils import setup

pkg_dir = os.path.dirname(__file__)
# importing __<vars>__ into the namespace
#https://packaging.python.org/guides/single-sourcing-package-version/#single-sourcing-the-version
with open(os.path.join(pkg_dir, 'opentargets_ontologyutils', 'version.py')) as fv:
    exec(fv.read())

long_description = open(os.path.join(pkg_dir, "README.md")).read()

setup(
    name=__pkgname__,
    version=__version__,
    description=__description__,
    long_description=long_description,
    long_description_content_type='text/markdown; charset=UTF-8',
    author=__author__,
    author_email=__author_email__,
    url=__homepage__,
    packages=["opentargets_ontologyutils"],
    license=__license__,
    download_url=__homepage__ + '/archive/' + __version__ + '.tar.gz',
    keywords=['opentargets', 'bioinformatics', 'ontology'],
    platforms=['any'],
    #make sure this matches requirements.txt
    install_requires=[
        'opentargets-urlzsource==1.0.0','rdflib','future'
      ],
    include_package_data=True,
    entry_points={},
    data_files=[],
    scripts=[],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    #make sure this matches requirements.txt
    extras_require={'dev': ['pytest>=4.0.0,<4.1.0','pytest-cov', 'pylint','codecov','tox', 'pipdeptree']}
)

