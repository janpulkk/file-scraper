"""Module for checking if the file is uitable as text file or not."""
from __future__ import unicode_literals

import io
import six
from file_scraper.base import BaseScraper
from file_scraper.magiclib import file_command
from file_scraper.textfile.textfile_model import (TextFileMeta,
                                                  TextEncodingMeta)


class TextfileScraper(BaseScraper):
    """
    Text file detection scraper.

    file (libmagick) checks mime-type and that if it is a text
    file with the soft option that excludes libmagick.
    """

    _supported_metadata = [TextFileMeta]

    def _file_mimetype(self):
        """
        Detect mimetype with the soft option that excludes libmagick.

        :returns: file mimetype
        """
        params = ["-be", "soft", "--mime-type"]
        shell = file_command(self.filename, params)
        if shell.stderr:
            self._errors.append(shell.stderr)

        return shell.stdout.strip()

    def scrape_file(self):
        """Check MIME type determined by libmagic."""
        self._messages.append("Trying text detection...")

        mimetype = self._file_mimetype()
        if mimetype == "text/plain":
            self._messages.append("File is a text file.")
            for md_class in self._supported_metadata:
                self.streams.append(md_class())
            self._check_supported(allow_unav_mime=True,
                                  allow_unav_version=True)
        else:
            self._errors.append("File is not a text file")


class TextEncodingScraper(BaseScraper):
    """
    Text encoding scraper.

    Tries to use decode() and checks some of illegal character values.
    """

    _supported_metadata = [TextEncodingMeta]

    def __init__(self, filename, check_wellformed=True, params=None):
        """Initialize scraper. Add given charset."""
        if params is None:
            params = {}
        self._charset = params.get("charset", "(:unav)")
        super(TextEncodingScraper, self).__init__(
            filename, check_wellformed, params)

    def scrape_file(self):
        """
        Validate the given character encoding aginst the file.
        """
        forbidden = ["\x00", "\x01", "\x02", "\x03", "\x04", "\x05", "\x06",
                     "\x07", "\x08", "\x0B", "\x0C", "\x0E", "\x0F", "\x10",
                     "\x11", "\x12", "\x13", "\x14", "\x15", "\x16", "\x17",
                     "\x18", "\x19", "\x1A", "\x1B", "\x1C", "\x1D", "\x1E",
                     "\x1F", "\xFF"]
        chunksize = 20*1024*1024  # chunk size
        limit = 100  # Limit file read in MB, 0 = unlimited

        if self._charset in [None, "(:unav)"]:
            self._errors.append("Character encoding not defined.")
            self._add_metadata()
            return
        if not self._check_wellformed:
            self._messages.append("No character encoding validation done, "
                                  "setting predefined encoding value.")
            self._add_metadata()
            return

        try:
            with io.open(self.filename, "rb") as infile:
                position = 0
                possibly_wrong = True
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break

                    self._decode_chunk(chunk, self._charset, position)
                    if self._charset.upper() in ["UTF-16", "ISO-8859-15"]:
                        try:
                            if self._charset.upper() == "ISO-8859-15":
                                try:
                                    self._decode_chunk(chunk, "ASCII", position)
                                    possibly_wrong = False
                                except (ValueError, UnicodeError) as e:
                                    self._decode_chunk(chunk, "UTF-8", position)
                            else:
                                self._decode_chunk(chunk, "UTF-8", position)
                        except (ValueError, UnicodeDecodeError):
                            possibly_wrong = False
                    else:
                        possibly_wrong = False

                    position = position + chunksize
                    if position > limit*1024*1024 and limit > 0:
                        self._messages.append(
                            "First %s MB read, we skip the remainder." % (
                                limit))
                        break

                if possibly_wrong:
                    self._errors.append(
                        "Character decoding error: The character "
                        "encoding is most likely UTF-8.")
                else:
                    self._messages.append(
                        "Character encoding validated successfully.")

        except IOError as err:
            self._errors.append("Error when reading the file: " +
                                six.text_type(err))
        except (ValueError, UnicodeDecodeError) as exception:
            self._errors.append("Character decoding error: %s" % exception)
        finally:
            if infile:
                infile.close()

        self._add_metadata()


def _decode_chunk(self, chunk, charset, position):
    """Decode given chunk."""
    forbidden = ["\x00", "\x01", "\x02", "\x03", "\x04", "\x05", "\x06",
                 "\x07", "\x08", "\x0B", "\x0C", "\x0E", "\x0F", "\x10",
                 "\x11", "\x12", "\x13", "\x14", "\x15", "\x16", "\x17",
                 "\x18", "\x19", "\x1A", "\x1B", "\x1C", "\x1D", "\x1E",
                 "\x1F", "\xFF"]
    decoded_chunk = chunk.decode(charset)
    for forb_char in forbidden:
        if self._charset.upper() == "UTF-32":
            break
        index = decoded_chunk.find(forb_char)
        if index > -1:
            raise ValueError(
                "Illegal character '%s' in position %s" % (
                    forb_char, (position+index)))

    def _add_metadata(self):
        """Add metadata."""
        for md_class in self._supported_metadata:
            self.streams.append(md_class(self._charset,
                                         self._given_mimetype,
                                         self._given_version))
        self._check_supported(allow_unav_mime=True, allow_unav_version=True)
