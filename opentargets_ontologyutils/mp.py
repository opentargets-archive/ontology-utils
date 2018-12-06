from __future__ import print_function

import logging

import rdflib

from opentargets_ontologyutils.rdf_utils import OntologyClassReader

logger = logging.getLogger(__name__)

def get_mp(uri):
    '''
    Load MP to accept phenotype terms that are not in EFO
    :return:
    '''
    obj = None
    obj = OntologyClassReader()

    obj.load_ontology_graph(uri)
    base_class = 'http://purl.obolibrary.org/obo/MP_0000001'
    obj.load_ontology_classes(base_class= base_class)
    obj.get_deprecated_classes()
    obj.get_top_levels(base_class= base_class)

    obj.rdf_graph = None
    return obj

def load_mammalian_phenotype_ontology(ocr, uri):
    """
        Loads the MP graph and extracts the current and obsolete classes.
        Status: production
    """
    logger.debug("load_mammalian_phenotype_ontology...")
    ocr.load_ontology_graph(uri)

    all_ns = [n for n in ocr.rdf_graph.namespace_manager.namespaces()]

    '''
    Detach the anatomical system from the mammalian phenotype node
    and load all the classes
    '''

    mp_root_uri = 'http://purl.obolibrary.org/obo/MP_0000001'
    mp_root_uriref = rdflib.URIRef(mp_root_uri)
    ocr.get_children(mp_root_uri)

    for child in ocr.children[mp_root_uri]:
        print("%s %s..."%(child['code'], child['label']))
        uri = "http://purl.obolibrary.org/obo/" + child['code']
        uriref = rdflib.URIRef(uri)
        ocr.rdf_graph.remove((uriref, None, mp_root_uriref))
        ocr.load_ontology_classes(base_class=uri)
        ocr.get_classes_paths(root_uri=uri, level=0)
        print(len(ocr.current_classes))