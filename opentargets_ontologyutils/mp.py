from __future__ import print_function

import logging

import rdflib

from opentargets_ontologyutils.rdf_utils import OntologyClassReader

logger = logging.getLogger(__name__)

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

    ocr.get_deprecated_classes()