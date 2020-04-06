from __future__ import print_function

import logging

import rdflib

from opentargets_ontologyutils.rdf_utils import OntologyClassReader,merge_classes_paths

logger = logging.getLogger(__name__)

def load_evidence_classes(ocr, uri_so, uri_eco):
    '''
    Loads evidence from ECO, SO and the Open Targets evidence classes
    :return:
    '''
    ocr.load_ontology_graph(uri_so)
    ocr.load_ontology_graph(uri_eco)

    evidence_uri = rdflib.URIRef('http://purl.obolibrary.org/obo/ECO_0000000')

    # for triple in self.rdf_graph.triples((evidence_uri, None, None)):
    #      logger.debug(triple)

    '''
        Open Targets specific evidence:
        A) Create namespace for OT evidence
        B) Add Open Targets evidence terms to graph
        C) Traverse the graph breadth first
    '''

    cttv = rdflib.Namespace(str("http://www.targetvalidation.org/disease"))
    ot = rdflib.Namespace(str("http://identifiers.org/eco"))

    #namespace_manager = NamespaceManager(self.rdf_graph)
    ocr.rdf_graph.namespace_manager.bind('cttv', cttv)
    ocr.rdf_graph.namespace_manager.bind('ot',ot)

    open_targets_terms = {
        'http://www.targetvalidation.org/disease/cttv_evidence':'CTTV evidence',
        'http://identifiers.org/eco/drug_disease':'drug-disease evidence',
        'http://identifiers.org/eco/target_drug':'biological target to drug evidence',
        'http://identifiers.org/eco/clinvar_gene_assignments':'ClinVAR SNP-gene pipeline',
        'http://identifiers.org/eco/cttv_mapping_pipeline':'CTTV-custom annotation pipeline',
        'http://identifiers.org/eco/GWAS':'Genome-wide association study evidence',
        'http://identifiers.org/eco/GWAS_fine_mapping': 'Fine-mapping study evidence',
        'http://identifiers.org/eco/somatic_mutation_evidence':'Somatic mutation evidence',
        'http://www.targetvalidation.org/evidence/genomics_evidence':'genomics evidence',
        'http://targetvalidation.org/sequence/nearest_gene_five_prime_end':'Nearest gene counting from 5&apos; end',
        'http://targetvalidation.org/sequence/regulatory_nearest_gene_five_prime_end':'Nearest regulatory gene from 5&apos; end',
        'http://www.targetvalidation.org/evidence/literature_mining':'Literature mining',
        'http://www.targetvalidation.org/provenance/DatabaseProvenance':'database provenance',
        'http://www.targetvalidation.org/provenance/ExpertProvenance':'expert provenance',
        'http://www.targetvalidation.org/provenance/GWAS_SNP_to_trait_association':'GWAS SNP to trait association',
        'http://www.targetvalidation.org/provenance/LiteratureProvenance':'literature provenance',
        'http://www.targetvalidation.org/provenance/disease_to_phenotype_association':'disease to phenotype association',
        'http://www.targetvalidation.org/provenance/gene_to_disease_association':'gene to disease association',
        'http://identifiers.org/eco/locus_to_gene_pipeline':'Open Targets Genetics portal locus to gene annotation pipeline',
        'http://identifiers.org/eco/PheWAS': 'PheWAS catalog evidence'
    }

    for uri, label in open_targets_terms.items():
        u = rdflib.URIRef(uri)
        ocr.rdf_graph.add((u, rdflib.RDF.type, rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#Class')))
        ocr.rdf_graph.add([u, rdflib.RDFS.label, rdflib.Literal(label)])
        ocr.rdf_graph.add([u, rdflib.RDFS.subClassOf, evidence_uri])

    u = rdflib.URIRef('http://identifiers.org/eco/target_drug')
    # Add the bits specific to Open Targets
    # 'Open Targets evidence' ?
    # 'biological target-disease association via drug' ECO:0000360
    # 'drug-disease evidence' http://identifiers.org/eco/drug_disease SubclassOf 'biological target-disease association via drug'
    # 'biological target to drug evidence' http://identifiers.org/eco/target_drug SubclassOf 'biological target-disease association via drug'
    # ClinVAR SNP-gene pipeline http://identifiers.org/eco/clinvar_gene_assignments SubclassOf ECO:0000246
    # CTTV-custom annotation pipeline http://identifiers.org/eco/cttv_mapping_pipeline SubclassOf ECO:0000246

    base_classes = ['http://purl.obolibrary.org/obo/ECO_0000000', 
        'http://purl.obolibrary.org/obo/SO_0000400', 
        'http://purl.obolibrary.org/obo/SO_0001260', 
        'http://purl.obolibrary.org/obo/SO_0000110', 
        'http://purl.obolibrary.org/obo/SO_0001060' ]

    #for each base class, calculate the paths and parents
    #combine each base class in a combined collection
    ocr.classes_paths = {}
    for base_class in base_classes:
        ocr.load_ontology_classes(base_class=base_class)
        classes_paths = ocr.get_classes_paths(root_uri=base_class, level=0)
        ocr.classes_paths = merge_classes_paths(ocr.classes_paths, classes_paths)
