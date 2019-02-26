from __future__ import print_function

import logging

import rdflib

from opentargets_ontologyutils.rdf_utils import OntologyClassReader

logger = logging.getLogger(__name__)

HPO_TAS = [
    "http://purl.obolibrary.org/obo/HP_0005386", #"behavior/neurological phenotype",
    "http://purl.obolibrary.org/obo/HP_0005375", #"adipose tissue phenotype",
    "http://purl.obolibrary.org/obo/HP_0005385", #"cardiovascular system phenotype",
    "http://purl.obolibrary.org/obo/HP_0005384", #"cellular phenotype",
    "http://purl.obolibrary.org/obo/HP_0005382", #"craniofacial phenotype",
    "http://purl.obolibrary.org/obo/HP_0005381", #"digestive/alimentary phenotype",
    "http://purl.obolibrary.org/obo/HP_0005380", #"embryo phenotype",
    "http://purl.obolibrary.org/obo/HP_0005379", #"endocrine/exocrine phenotype",
    "http://purl.obolibrary.org/obo/HP_0005378", #"growth/size/body region phenotype",
    "http://purl.obolibrary.org/obo/HP_0005377", #"hearing/vestibular/ear phenotype",
    "http://purl.obolibrary.org/obo/HP_0005397", #"hematopoietic system phenotype",
    "http://purl.obolibrary.org/obo/HP_0005376", #"homeostasis/metabolism phenotype",
    "http://purl.obolibrary.org/obo/HP_0005387", #"immune system phenotype",
    "http://purl.obolibrary.org/obo/HP_0010771", #"integument phenotype",
    "http://purl.obolibrary.org/obo/HP_0005371", #"limbs/digits/tail phenotype",
    "http://purl.obolibrary.org/obo/HP_0005370", #"liver/biliary system phenotype",
    "http://purl.obolibrary.org/obo/HP_0010768", #"mortality/aging",
    "http://purl.obolibrary.org/obo/HP_0005369", #"muscle phenotype",
    "http://purl.obolibrary.org/obo/HP_0002006", #"neoplasm",
    "http://purl.obolibrary.org/obo/HP_0003631", #"nervous system phenotype",
    "http://purl.obolibrary.org/obo/HP_0002873", #"normal phenotype",
    "http://purl.obolibrary.org/obo/HP_0001186", #"pigmentation phenotype",
    "http://purl.obolibrary.org/obo/HP_0005367", #"renal/urinary system phenotype",
    "http://purl.obolibrary.org/obo/HP_0005389", #"reproductive system phenotype",
    "http://purl.obolibrary.org/obo/HP_0005388", #"respiratory system phenotype",
    "http://purl.obolibrary.org/obo/HP_0005390", #"skeleton phenotype",
    "http://purl.obolibrary.org/obo/HP_0005394", #"taste/olfaction phenotype",
    "http://purl.obolibrary.org/obo/HP_0005391", #"vision/eye phenotype"
]

#TODO this should be a static method
def get_hpo(ocr, uri):
    '''
    Load HPO to accept phenotype terms that are not in EFO
    :return:
    '''

    ocr.load_ontology_graph(uri)

    base_class = 'http://purl.obolibrary.org/obo/HP_0000118'
    ocr.load_ontology_classes(base_class=base_class)
    ocr.get_deprecated_classes()

    ocr.rdf_graph = None
    return ocr