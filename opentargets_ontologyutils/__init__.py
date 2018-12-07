from builtins import object

import functools
from contextlib import contextmanager
import gzip
import zipfile
import tempfile
import logging

import requests 
import requests_file

def urllify(string_name):
    """return a file:// urlified simple path to a file:// is :// is not contained in it"""
    return string_name if '://' in string_name else 'file://' + string_name

class URLZSource(object):
    def __init__(self, filename, *args, **kwargs):
        """Easy way to open multiple types of URL protocol (e.g. http:// and file://)
        as well as handling compressed content (e.g. .gz or .zip) if appropriate.

        Just in case you need to use proxies for url use it as normal
        named arguments to requests.

        >>> # proxies = {}
        >>> # if Config.HAS_PROXY:
        ...    # self.proxies = {"http": Config.PROXY,
        ...                      # "https": Config.PROXY}
        >>> # with URLZSource('http://var.foo/noname.csv',proxies=proxies).open() as f:

        """

        self.logger = logging.getLogger(__name__)

        self.filename = urllify(filename)
        self.args = args
        self.kwargs = kwargs

    @contextmanager
    def _open_local(self, filename, mode):
        """
        This is an internal function to handle opening the temporary file 
        that the URL has been downloaded to, including handling compression
        if appropriate
        """
        open_f = None

        if filename.endswith('.gz'):
            open_f = functools.partial(gzip.open, mode='rb')

        elif filename.endswith('.zip'):
            zipped_data = zipfile.ZipFile(filename)
            info = zipped_data.getinfo(zipped_data.filelist[0].orig_filename)

            filename = info
            open_f = functools.partial(zipped_data.open)
        else:
            open_f = functools.partial(open, mode='r')

        with open_f(filename) as fd:
            yield fd

    @contextmanager
    def open(self, mode='r'):
        """
        This downloads the URL to a temporary file, naming the file
        based on the URL. 
        """

        if self.filename.startswith('ftp://'):
            raise NotImplementedError('finish ftp')

        elif self.filename.startswith('file://'):
            #if its already a file, we can handle it directly
            file_to_open = self.filename[7:]
            with self._open_local(file_to_open, mode) as fd:
                yield fd
        else:
            file_to_open = None

            with requests.Session() as r_session:
                #get the remote url
                r_session.mount('file://', requests_file.FileAdapter())
                f = r_session.get(url=self.filename, stream=True, **self.kwargs)
                f.raise_for_status()


                local_filename = self.filename.split('://')[-1].split('/')[-1]

                #this has to be "delete=false" so that it can be re-opened with the same filename
                #to be read out again
                #name the temporary file similar to the url so we can find it and tell if it 
                #needs to be uncompressed
                with tempfile.NamedTemporaryFile(mode='wb', suffix=local_filename, delete=False) as fd:
                    file_to_open = fd.name

                    self.logger.debug("downloading %s to %s", self.filename, file_to_open)

                    # write data into file in streaming fashion
                    for block in f.iter_content(1024):
                        fd.write(block)

            with self._open_local(file_to_open, mode) as fd:
                yield fd