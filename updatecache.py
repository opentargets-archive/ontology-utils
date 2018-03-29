from ou_settings import Config
from ontologyutils.hpo import HPODownloader
from ontologyutils.efo import EFODownloader
import logging

#hpo = HPODownloader()
#hpo.download()
efo = EFODownloader()
efo.download()