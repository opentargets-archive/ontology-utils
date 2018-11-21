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
from __future__ import print_function
from builtins import object
import os
import configparser
import pkg_resources as res

__copyright__ = "Copyright 2014-2018 Biogen, Celgene Corporation, EMBL - European Bioinformatics Institute, GlaxoSmithKline, Takeda Pharmaceutical Company and Wellcome Sanger Institute"
__credits__ = ["Gautier Koscielny"]
__license__ = "Apache 2.0"
__version__ = "0.4"
__maintainer__ = "Gautier Koscielny"
__email__ = "gautier.x.koscielny@gsk.com"
__status__ = "Production"

def file_or_resource(fname=None):
    '''get filename and check if in getcwd then get from
    the package resources folder
    '''
    filename = os.path.expanduser(fname)
    print(filename)
    resource_package = __name__
    resource_path = '/'.join(('resources', filename))
    print(resource_path)
    if filename is not None:
        abs_filename = os.path.join(os.path.abspath(os.getcwd()), filename) \
                       if not os.path.isabs(filename) else filename

        return abs_filename if os.path.isfile(abs_filename) \
            else res.resource_filename(resource_package, resource_path)

iniparser = configparser.ConfigParser()
env_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'env.ini')
if os.path.isfile(env_file):
    iniparser.read(env_file)

class Config(object):
    # print "OS SEP %s %s"%(os.sep, os.path.sep)
    HAS_PROXY = iniparser.has_section('proxy')
    if HAS_PROXY:
        PROXY = iniparser.get('proxy', 'protocol') + "://" + iniparser.get('proxy', 'username') + ":" + iniparser.get(
            'proxy', 'password') + "@" + iniparser.get('proxy', 'host') + ":" + iniparser.get('proxy', 'port')
        PROXY_PROTOCOL = iniparser.get('proxy', 'protocol')
        PROXY_USERNAME = iniparser.get('proxy', 'username')
        PROXY_PASSWORD = iniparser.get('proxy', 'password')
        PROXY_HOST = iniparser.get('proxy', 'host')
        PROXY_PORT = int(iniparser.get('proxy', 'port'))
    elif 'HTTP_PROXY' in os.environ:
        PROXY = os.environ['HTTP_PROXY']

    CACHE_DIRECTORY = ''

    HAS_CACHE = iniparser.has_section('cache')
    if HAS_CACHE:
        CACHE_DIRECTORY = iniparser.get('cache', 'directory')
    elif 'ONTOLOGYUTILS_CACHE' in os.environ:
        CACHE_DIRECTORY = os.environ['ONTOLOGYUTILS_CACHE']


    HPO_DIRECTORY = '%s/hpo'%CACHE_DIRECTORY
    HPO_OBO_DIRECTORY = '%s/obo'%HPO_DIRECTORY
    HPO_ANNOTATIONS_DIRECTORY = '%s/annotations'%HPO_DIRECTORY
    HPO_OBO_MATCH = 'http://purl.obolibrary.org/obo/(.+)$'
    HPO_ANNOTATIONS_MATCH = '^.http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/misc/(.+)$'
    HPO_URIS = [
        'http://purl.obolibrary.org/obo/hp.obo',
        'http://purl.obolibrary.org/obo/hp.owl',
        'http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/misc/curator-statistics.tab',
        'http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/misc/data_version.txt',
        'http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/misc/negative_phenotype_annotation.tab',
        'http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/misc/phenotype_annotation.tab',
        'http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/misc/phenotype_annotation_hpoteam.tab',
        'http://pubmed-browser.human-phenotype-ontology.org/hp_common_annotations_all.tab'
    ]

    HPO_FILES = dict(
        obo = '%s/hp.obo'%HPO_OBO_DIRECTORY,
        owl = '%s/hp.owl'%HPO_OBO_DIRECTORY,
        negativePhenotype = '%s/negative_phenotype_annotation.tab'%HPO_ANNOTATIONS_DIRECTORY,
        rare_phenotype_annotation = '%s/phenotype_annotation.tab'%HPO_ANNOTATIONS_DIRECTORY,
        phenotypeAnnotationHPOTeam = '%s/phenotype_annotation_hpoteam.tab'%HPO_ANNOTATIONS_DIRECTORY,
        common_phenotype_annotation = '%s/hp_common_annotations_all.tab'%HPO_ANNOTATIONS_DIRECTORY,
        ic_backup = '%s/backup.json'%CACHE_DIRECTORY
    )

    EFO_DIRECTORY = '%s/efo'%CACHE_DIRECTORY
    EFO_OBO_DIRECTORY = '%s/obo'%EFO_DIRECTORY
    EFO_URIS = [
        'http://sourceforge.net/p/efo/code/HEAD/tree/trunk/src/efoinobo/efo.obo?format=raw',
    ]
    EFO_FILES = dict(
        obo = '%s/efo.obo'%EFO_OBO_DIRECTORY,
        obo_full='%s/efo_full.obo' % EFO_OBO_DIRECTORY
    )

    GO_DIRECTORY = '%s/go'%CACHE_DIRECTORY
    GO_OBO_DIRECTORY = '%s/obo'%GO_DIRECTORY
    GO_URIS = [
        'http://www.geneontology.org/ontology/go.obo',
    ]
    GO_FILES = dict(
        obo = '%s/go.obo'%GO_OBO_DIRECTORY,
    )

    MESH_DIRECTORY = '%s/mesh'%CACHE_DIRECTORY
    MESH_CSV_DIRECTORY = '%s/csv'%MESH_DIRECTORY
    MESH_URIS = [
        'http://data.bioontology.org/ontologies/MESH/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv',
        'ftp://nlmpubs.nlm.nih.gov/online/mesh/.asciimesh/d2016.bin'
        'ftp://nlmpubs.nlm.nih.gov/online/mesh/.asciimesh/q2016.bin'
    ]
    MESH_FILES = dict(
        csv = '%s/mesh.csv.gz'%MESH_CSV_DIRECTORY
    )

    SIM_DIRECTORY = '%s/sim'%CACHE_DIRECTORY
    SIM_DISEASES_BACKUP = '%s/diseases_backup.json'%SIM_DIRECTORY
    SIM_MICAS_BACKUP = '%s/micas_backup.bin'%SIM_DIRECTORY
