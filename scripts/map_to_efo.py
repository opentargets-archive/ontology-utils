import csv
import optparse
import logging
import ontologyutils.mapper as mapper
import ontologyutils.ols as ols
import ontologyutils.oxo as oxo
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
        results = ontology_mapper.getLabelMappings(label=term, targets=[ols.SOURCES['efo'], ols.SOURCES['hp'], ols.SOURCES['mondo']])
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
        results = ontology_mapper.getOboIdMappings(obo_id='MeSH:'+ mesh_id,
                                                   targets=[oxo.SOURCES['efo'], oxo.SOURCES['orphanet']])
        pprint(results)

    final_mappings = dict()
    for mesh_id in mesh_ids:
        print(mesh_id)
        curie = oxo.SOURCES['mesh'] + ':' + mesh_id
        oxo_mapper = oxo.OXO()
        final_mappings[mesh_id] = oxo_mapper.map_to_efo(source=oxo.SOURCES['mesh'], source_id=mesh_id)

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
        curie = oxo.SOURCES['icd10'] + ':' + icd10_code
        oxo_mapper = oxo.OXO()
        oxo_mapper.oxo_scan(curies=[curie])
        if oxo.SOURCES['icd10'] in oxo_mapper.oxo_source_to_dest:
            paths = oxo_mapper.oxo_paths(source=oxo.SOURCES['icd10'], stop_dest=oxo.SOURCES['efo'], curie=curie)
            # create a list of all the end nodes
            for path in paths:
                result_paths = map(lambda x: "%s (%s)" % (x, oxo_mapper.oxo_labels[x]), path)
                print(" -> ".join(result_paths))
                if path[-1].startswith(oxo.SOURCES['efo']) or path[-1].startswith(oxo.SOURCES['hp']) or path[-1].startswith(oxo.SOURCES['mp']):
                    (source, raw) = path[-1].split(":")
                    id = path[-1]
                    final_mappings[icd10_code][id] = dict(
                        id=id,
                        label=oxo_mapper.oxo_labels[id],
                        source=" -> ".join(result_paths),
                        process='oXo shortest path'
                    )

        else:
            final_mappings[icd10_code][icd10_code] = dict(
                id=icd10_code,
                label='N/A',
                source=oxo.SOURCES['icd10'],
                process="Curation Required"
            )


if __name__ == "__main__":
    main()

