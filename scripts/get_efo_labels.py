import csv
import optparse
import json
import logging
import ontologyutils as onto
from ou_settings import Config

efo = None

def main():
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input', type='string', default=Config.EFO_FILES['obo'], dest='efoFilename')
    parser.add_option('-o', '--output', type='string', default='/tmp/output.tsv', dest='outputFilename')

    options, args = parser.parse_args()
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    logging.info("Loading EFO classes from OBO file")
    efo = onto.Ontology.fromOBOFile(options.efoFilename)

    # Write results to file
    with open(options.outputFilename, mode='wb') as zf:
        writer = csv.writer(zf, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['efo_id', 'efo_label'])
        for id in efo.terms:

            ancestors = efo.getAncestors(id)

            # only look at specific ancestors
            if 'EFO:0000408' in ancestors or 'EFO:0000651' in ancestors or 'EFO:0001444' in ancestors:
                try:
                    writer.writerow([id, efo.terms[id]['tags']['name'][0]])
                except KeyError:
                    print('No Tags found for id %s'%(id))
                    print(json.dumps(efo.terms[id], indent=2))
                    break

if __name__ == "__main__":
    main()

