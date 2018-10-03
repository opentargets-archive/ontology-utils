import re
import ontologyutils as onto
import optparse
import logging
from ontologyutils.ou_settings import Config
import csv
import json
import sys

def main():

    parser = optparse.OptionParser()
    parser.add_option('-i', '--input', type='string', default=Config.GO_FILES['obo'], dest='goFilename')

    options, args = parser.parse_args()
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    ontology = onto.Ontology.fromOBOFile(options.goFilename)
    print('ontology parsed')

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
            for path in paths:
                if 'GO:0006955' in path:
                    print(id, ontology.terms[id]['tags']['name'][0], '; '.join(path))
                    break

            #if c > 100:
            #    break

if __name__ == "__main__":
    main()

