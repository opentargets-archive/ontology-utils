import re
import os
import urllib2
import logging
from datetime import datetime
from ou_settings import Config

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
            print filename
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
            except urllib2.HTTPError, e:
                print "HTTP Error:",e.code , url
            except urllib2.URLError, e:
                print "URL Error:",e.reason , url