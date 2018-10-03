import re
import ontologyutils as onto
import optparse
import logging
import csv
import json
import sys

def main():

    parser = optparse.OptionParser()
    parser.add_option('-s', '--source', type='string', default=None, dest='source')

    options, args = parser.parse_args()
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    ontology_filename = options.source
    print('parsing', ontology_filename)
    ontology = onto.Ontology.fromOBOFile(ontology_filename)
    print('ontology parsed')

    with open(options.output, mode='w') as zf:
        writer = csv.writer(zf, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([ 'go_id', 'go_label', 'path' ])

        c = 0
        for id in ontology.terms:

            paths = ontology.get_all_paths(id)

            # only look at specific ancestors
            '''
            if id == 'GO:0043312':
                paths = ontology.get_all_paths(id)
                for path in paths:
                    print(id, ontology.terms[id]['tags']['name'][0],'; '.join(list(path)))
                break
            '''

            if any(map(lambda x: 'GO:0006955' in x, paths)):

                c+=1
                print(ontology.terms[id]['tags']['name'][0])
                for path in paths:
                    if 'GO:0006955' in path:
                        writer.writerow(
                            [id, ontology.terms[id]['tags']['name'][0], '; '.join(path)])
                        break

                #if c > 100:
                #    break

if __name__ == "__main__":
    main()

