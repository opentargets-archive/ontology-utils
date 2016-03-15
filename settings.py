import uuid
from collections import defaultdict

__author__ = 'gautierk'
import os
import ConfigParser

iniparser = ConfigParser.ConfigParser()
#iniparser.read('db.ini')

class Config():

    CACHE_DIRECTORY = '/Users/koscieln/.ontologycache'
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
        obo = '%s/efo.obo'%EFO_OBO_DIRECTORY
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
