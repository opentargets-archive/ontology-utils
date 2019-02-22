from ontologyutils.rdf_utils import OntologyClassReader
import csv
import logging

def main():

    parser = optparse.OptionParser()
    parser.add_option('-f', '--filename', type='string', dest='filename')

    options, args = parser.parse_args()
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    obj = OntologyClassReader()
    obj.load_efo_classes(lightweight=False, with_uberon=True)
    obj.get_efo_disease_location()

    with open(options.filename, mode='wb') as zf:
        writer = csv.writer(zf, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ['disease_iri', 'disease_location_iri', 'disease_location_label'])

        for disease_iri in obj.disease_locations:
            for disease_location_iri in obj.disease_locations[disease_iri]:
                writer.writerow([disease_iri, disease_location_iri, obj.disease_locations[disease_iri][disease_location_iri]])

if __name__ == "__main__":
    main()
