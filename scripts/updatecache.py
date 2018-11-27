from opentargets_ontologyutils.efo import EFODownloader

__copyright__ = "Copyright 2014-2018, Open Targets"
__credits__ = ["Gautier Koscielny"]
__license__ = "Apache 2.0"
__version__ = "1.0"
__maintainer__ = "Gautier Koscielny"
__email__ = "gautier.x.koscielny@gsk.com"
__status__ = "Production"

#hpo = HPODownloader()
#hpo.download()
efo = EFODownloader()
efo.download()