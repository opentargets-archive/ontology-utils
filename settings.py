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
        common_phenotype_annotation = '%s/hp_common_annotations_all.tab'%HPO_ANNOTATIONS_DIRECTORY
    )
