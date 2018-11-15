'''
Copyright 2014-2018 Biogen, Celgene Corporation, EMBL - European Bioinformatics Institute, GlaxoSmithKline, Takeda Pharmaceutical Company and Wellcome Sanger Institute

This software was developed as part of the Open Targets project. For more information please see: http://www.opentargets.org

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
import os

try:
    from setuptools import setup
except ImportError:
    from distutils import setup

long_description = open(os.path.join(os.path.dirname(__file__), "README.md")).read()

setup(
    name="ontologyutils",
    version="0.4",
    description=long_description.split("\n")[0],
    long_description=long_description,
    author="Gautier Koscielny",
    author_email="gautier.x.koscielny@gsk.com",
    url="https://github.com/opentargets",
    packages=["ontologyutils"],
    #make sure this matches requirements.txt
    install_requires=[
        'requests','numpy','rdflib','configparser','future','tqdm'
      ],
    license="Apache2",
    classifiers=[
        "License :: Apache 2",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    #make sure this matches requirements.txt
    extras_require={'dev': ['pytest-cov','codecov','tox']}
)

