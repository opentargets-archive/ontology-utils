from __future__ import print_function
import csv
import optparse
import logging
import opentargets_ontologyutils.mapper as mapper
import opentargets_ontologyutils.ols as ols
import opentargets_ontologyutils.oxo as oxo
from pprint import pprint

def main():
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input', type='string', default=None, dest='inputFilename')
    parser.add_option('-o', '--output', type='string', default=None, dest='outputFilename')

    options, args = parser.parse_args()
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    logging.info("Loading EFO classes from OBO file")
    term = 'Wilms Tumor'
    term = 'DiGeorge Syndrome'
    id = 'Orphanet_654'
    
    ontology_mapper = mapper.OntologyMapper()

    terms = [
        'Acne',
        'Alzheimer Disease',
        'Alzheimer Sclerosis',
        'DiGeorge Syndrome',
        'Hearing loss',
        'Inflammatory Bowel Diseases',
        'Hydrocephalus',
        'HIV Infections',
        'Adenoid Cystic Carcinoma',
        'Astrocytoma',
        'Obesity',
        'Barrett Esophagus',
        'Sweat gland disease',
        'Bjornstad syndrome',
        'Disorders of trigeminal nerve',
        'dystonia'
    ]

    for term in terms:
        print(term)
        results = ontology_mapper.get_label_mappings(label=term, targets=[ols.SOURCES['efo'], ols.SOURCES['hp'], ols.SOURCES['mondo']])
        if len(results) == 0:
            print("NO MAPPING FOUND for %s"%(term))
        else:
            pprint(results)

    mesh_ids = [
        'D009202',
        'D015212',
        'D000544',
        'D010300',
        'D009765',
        'D034381',
        'C537734'
    ]
    for mesh_id in mesh_ids:
        results = ontology_mapper.get_obo_id_mappings(obo_id='MeSH:' + mesh_id,
                                                      targets=[oxo.SOURCES['efo'], oxo.SOURCES['orphanet']])
        pprint(results)

    final_mappings = dict()
    for mesh_id in mesh_ids:
        print(mesh_id)
        oxo_mapper = oxo.OXO()
        final_mappings[mesh_id] = ontology_mapper.get_full_ontology_mappings(source=oxo.SOURCES['mesh'], source_id=mesh_id, stop_dests=[oxo.SOURCES['efo']], dead_ends=ontology_mapper.dead_ends[oxo.SOURCES['efo']])

    icd10_codes = [
        'G20',
        'G24',
        'G50',
        'L70',
        'L71',
        'L74',
        'G50',
        'D59'
    ]

    final_mappings = dict()

    for icd10_code in icd10_codes:
        oxo_mapper = oxo.OXO()
        final_mappings[icd10_code] = ontology_mapper.get_full_ontology_mappings(source=oxo.SOURCES['mesh'], source_id=mesh_id, stop_dests=[oxo.SOURCES['efo']])

if __name__ == "__main__":
    main()

