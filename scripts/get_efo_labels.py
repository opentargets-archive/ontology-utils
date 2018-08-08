import sys
import csv
import optparse
import json
import logging
import ontologyutils as onto
from ou_settings import Config

efo = None


def get_url_from_ontology_id(id):
    base_code = id.replace(':', '_')
    if "Orphanet_" in base_code:
        return 'http://www.orpha.net/ORDO/' + base_code
    elif "EFO_" in base_code:
        return 'http://www.ebi.ac.uk/efo/' + base_code
    elif "GO_" in base_code or "HP_" in base_code or "DOID_" in base_code or "MP_" in base_code or "OBI_" in base_code:
        # http://purl.obolibrary.org/obo/
        return "http://purl.obolibrary.org/obo/" + base_code
    else:
        print("Unknown code!!! %s" %(id))
        sys.exit(1)

def main():
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input', type='string', default=Config.EFO_FILES['obo'], dest='efoFilename')
    parser.add_option('-o', '--output', type='string', default='/tmp/output.tsv', dest='outputFilename')

    options, args = parser.parse_args()
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    logging.info("Loading EFO classes from OBO file")
    efo = onto.Ontology.fromOBOFile(options.efoFilename)

    # Write results to file
    with open(options.outputFilename, mode='w') as zf:
        writer = csv.writer(zf, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # strings are Unicode
        writer.writerow(['efo_id', 'efo_uri', 'efo_label'])
        for id in efo.terms:

            ancestors = efo.getAncestors(id)

            # only look at specific ancestors
            if 'EFO:0000408' in ancestors or 'EFO:0000651' in ancestors or 'EFO:0001444' in ancestors:

                try:
                    # property_value: EFO:URI
                    efo_uri = get_url_from_ontology_id(id)
                    efo_name = efo.terms[id]['tags']['name'][0]
                    if "co-ode" in efo_name:
                        efo_name = efo_name.split("{")[0]
                    writer.writerow([id, efo_uri, efo_name])
                except KeyError:
                    print('No Tags found for id %s'%(id))
                    print(json.dumps(efo.terms[id], indent=2))
                    break

if __name__ == "__main__":
    main()

