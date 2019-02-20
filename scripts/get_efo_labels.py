from __future__ import print_function
import csv
import optparse
import json
import logging
import ontologyutils as onto
import ontologyutils.efo as efo
from ontologyutils.ou_settings import OUConfig


def main():
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input', type='string', default=OUConfig.EFO_FILES['obo'], dest='efoFilename')
    parser.add_option('-o', '--output', type='string', default='/tmp/output.tsv', dest='outputFilename')

    options, args = parser.parse_args()
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    logging.info("Loading EFO classes from OBO file")
    ontology = onto.Ontology.fromOBOFile(options.efoFilename)

    # Write results to file
    with open(options.outputFilename, mode='wt', encoding='utf-8') as zf:
        writer = csv.writer(zf, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # strings are Unicode
        writer.writerow(['efo_id', 'efo_uri', 'efo_label'])
        for id in ontology.terms:

            ancestors = ontology.getAncestors(id)

            # only look at specific ancestors
            if 'EFO:0000408' in ancestors or 'EFO:0000651' in ancestors or 'EFO:0001444' in ancestors:

                try:
                    # property_value: EFO:URI
                    efo_uri = efo.EFOUtils.get_url_from_ontology_id(id)
                    efo_name = ontology.terms[id]['tags']['name'][0]
                    if "co-ode" in efo_name:
                        efo_name = efo_name.split("{")[0]
                    writer.writerow([id, efo_uri, efo_name])
                except KeyError:
                    print('No Tags found for id %s'%(id))
                    print(json.dumps(ontology.terms[id], indent=2))
                    break

if __name__ == "__main__":
    main()

