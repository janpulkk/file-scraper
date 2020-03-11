"""Metadata model for PSPP scraper."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class PsppMeta(BaseMeta):
    """Metadata model for pspp scraping."""

    _supported = {"application/x-spss-por": []}  # Supported mimetype
    _allow_versions = True                       # Allow any version

    def __init__(self, errors):
        """Initialize model.

        :errors: Errors from scraper
        """
        self._errors = errors

    @metadata()
    def mimetype(self):
        """
        Return MIME type.

        The file is compliant SPSS Portable file if there are no errors. This
        is only returned if predefined as SPSS Portable.
        """
        return "application/x-spss-por" if not self._errors else "(:unav)"

    @metadata()
    def version(self):
        """Return version.

        The file is compliant SPSS Portable file if there are no errors. This
        is only returned if predefined as SPSS Portable.
        """
        return "(:unap)" if not self._errors else "(:unav)"

    @metadata()
    def stream_type(self):
        """Return file type."""
        # pylint: disable=no-self-use
        return "binary"
