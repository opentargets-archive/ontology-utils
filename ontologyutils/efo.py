import re
import os
import sys
import logging
from datetime import datetime
from ontologyutils.ou_settings import Config

__author__ = 'gautierk'

class EFOActions():
    DOWNLOAD='download'

class EFODownloader():

    def __init__(self):
        pass

    def download(self):

        now = datetime.utcnow()
        today = datetime.strptime("{:%Y-%m-%d}".format(datetime.now()), '%Y-%m-%d')

        for dir in [Config.EFO_DIRECTORY, Config.EFO_OBO_DIRECTORY]:
            if not os.path.exists(dir):
                os.makedirs(dir)

        for url in Config.EFO_URIS:
            directory = Config.EFO_OBO_DIRECTORY
            filename = re.match("^.+/([^/]+)\?format=raw$", url).groups()[0]
            print(filename)
            # get a new version of EFO
            req = urllib2.Request(url)

            try:
                response = urllib2.urlopen(req)

                # Open our local file for writing
                local_file = open('%s/%s'%(directory, filename), "wb")
                #Write to our local file
                local_file.write(response.read())
                local_file.close()

                logging.info("downloaded %s"%filename)

            #handle errors
            except urllib2.HTTPError as e:
                print ("HTTP Error:",e.code , url)
            except urllib2.URLError as e:
                print ("URL Error:",e.reason , url)

class EFOUtils():

    def __init__(self):
        pass

    @staticmethod
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