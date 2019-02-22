
Python package with a set of utilities to:
 - download latest version of specific ontologies (tested on EFO, ECO, HP, MP)
 - extract information from ontology OBO and OWL file format
 - query this information from memory
 - map ontology identifiers to other ontology identifiers
 - map ontology labels to relevant ontology identifiers

# Installation
Using python's pip installer:
```
pip install git+https://github.com/opentargets/ontology-utils.git#egg=ontologyutils
```

You have to set 2 variables, one to point to a cache where all the OBO files will reside (so that you can run locally) 
```
export ONTOLOGYUTILS_CACHE=$HOME/Documents/.ontologycache
```
and a variable to point to a local configuration file to read the latest OWL files from the Internet.
```
export ONTOLOGYUTILS_CONFIG_FILE=resources/ontology_config.ini
```

# Author

Gautier Koscielny

# License
Copyright 2014-2019 Biogen, Celgene Corporation, EMBL - European Bioinformatics Institute, GlaxoSmithKline, Takeda Pharmaceutical Company and Wellcome Sanger Institute

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
