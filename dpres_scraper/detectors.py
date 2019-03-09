"""File format detectors.
"""
import ctypes

try:
    ctypes.cdll.LoadLibrary('/opt/file-5.30/lib64/libmagic.so.1')
except OSError:
    print('/opt/file-5.30/lib64/libmagic.so.1 not found, MS Office detection '
          'may not work properly if file command library is older than 5.30.')

import magic
from fido.fido import Fido, defaults
from fido.pronomutils import get_local_pronom_versions
from dpres_scraper.base import BaseDetector
from dpres_scraper.dicts import PRONOM_DICT, MIMETYPE_DICT, VERSION_DICT


class _FidoReader(Fido):
    """Fido wrapper to get pronom code, mimetype and version
    """

    # Global variable in Fido
    global defaults

    def __init__(self, filename):
        """Fido is done with old-style python and does not inherit object,
        so super() is not available.
        :filename: File path
        """
        self.filename = filename  # File path
        self.puid = None          # Identified pronom code
        self.mimetype = None      # Identified mime type
        self.version = None       # Identified file format version
        Fido.__init__(self, quiet=True)

    def identify(self):
        """Identify file format with using pronom registry
        """
        versions = get_local_pronom_versions()
        defaults['xml_pronomSignature'] = versions.pronom_signature
        defaults['containersignature_file'] = \
            versions.pronom_container_signature
        defaults['xml_fidoExtensionSignature'] = \
            versions.fido_extension_signature
        defaults['format_files'] = [defaults['xml_pronomSignature']]
        defaults['format_files'].append(
            defaults['xml_fidoExtensionSignature'])
        self.identify_file(filename=self.filename, extension=False)

    def print_matches(self, fullname, matches, delta_t, matchtype=''):
        """Use this method in FIDO to get puid, mimetype and version
        instead of printing them to stdout
        :fullname: File path
        :matches: Matches tuples in Fido
        :delta_t: Not needed here, but originates from Fido
        :matchtype: Not needed here, but originates from Fido
        """
        for (item, _) in matches:
            self.puid = self.get_puid(item)
            if self.puid in PRONOM_DICT:
                (self.mimetype, self.version) = PRONOM_DICT[self.puid]
                return

        for (item, _) in matches:
            if self.mimetype is None:
                self.puid = self.get_puid(item)
                mime = item.find('mime')
                self.mimetype = mime.text if mime is not None else None
                version = item.find('version')
                self.version = version.text if version is not None else None
                if self.mimetype in MIMETYPE_DICT:
                    self.mimetype = MIMETYPE_DICT[self.mimetype]
                if self.mimetype in VERSION_DICT:
                    if self.version in VERSION_DICT[self.mimetype]:
                        self.version = \
                            VERSION_DICT[self.mimetype][self.version]


class FidoDetector(BaseDetector):
    """Fido detector.
    """

    def detect(self):
        """Detect file format and version.
        """
        fido = _FidoReader(self.filename)
        fido.identify()
        self.mimetype = fido.mimetype
        self.version = fido.version
        self.info = {'class': self.__class__.__name__,
                     'messages': '',
                     'errors': ''}

    def is_important(self):
        """Important mime types.
        :returns: Mime type
        """
        important = {}
        if self.mimetype != 'text/html':
            important['mimetype'] = self.mimetype
        return important


class MagicDetector(BaseDetector):
    """File magic detector.
    """

    def detect(self):
        """Detect mimetype.
        """
        magic_ = magic.open(magic.MAGIC_MIME_TYPE)
        magic_.load()
        mimetype = magic_.file(self.filename)
        magic_.close()
        if mimetype in MIMETYPE_DICT:
            self.mimetype = MIMETYPE_DICT[mimetype]
        else:
            self.mimetype = mimetype
        self.info = {'class': self.__class__.__name__,
                     'messages': '',
                     'errors': ''}

    def is_important(self):
        """Important mime types.
        :returns: Mime type
        """
        important = {}
        if self.mimetype == 'application/x-internet-archive':
            important['mimetype'] = self.mimetype
        return important
