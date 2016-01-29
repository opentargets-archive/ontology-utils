from settings import Config
from ontologyutils.hpo import HPODownloader
import logging

hpo = HPODownloader()
hpo.download()