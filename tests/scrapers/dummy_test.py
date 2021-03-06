"""
Test module for dummy.py

This module tests the following scraper classes:
    - FileExists
        - Existing files, both well-formed and non-well-formed, are found and
          their mimetype and streams are identified correctly whereas version
          and well_formed should be reported as None. No errors should be
          recorded.
        - Non-existent files are reported as not well-formed and the fact that
          the file does not exist is recorded in scraper errors. This behaviour
          is independent of the given MIME type.
        - Giving None as file path results in 'No filename given' being
          reported in the scraper errors and well_formed is False.
    - ScraperNotFound
        - version and well_formed are None.
        - MIME type is what is given to the scraper.
        - Streams contain only one dict with version and stream_type as None
          and MIME type as what was given to the scraper.
    - MimeMatchScraper
        - well_formed is True if predefined file type (mimetype and version)
          and given file type match
        - well_formed is False if predefined filetype and given file type
          conflicts
    - DetectedMimeVersionScraper, DetectedMimeVersionMetadataScraper
        - Results given file format version as a scraper result
        - Results error in MIME type is not supported
"""
from __future__ import unicode_literals

import pytest
import six

from file_scraper.dummy.dummy_scraper import (
    FileExists, ScraperNotFound, MimeMatchScraper,
    DetectedMimeVersionScraper, DetectedMimeVersionMetadataScraper)
from tests.common import partial_message_included

DEFAULTSTREAMS = {0: {"index": 0, "version": "(:unav)",
                      "stream_type": "(:unav)", "mimetype": "(:unav)"}}


@pytest.mark.parametrize(
    "filepath",
    [
        "tests/data/image_gif/valid_1987a.gif",
        "tests/data/image_gif/invalid_1987a_broken_header.gif",
        "tests/data/image_gif/invalid__empty.gif",
        "tests/data/application_pdf/valid_1.4.pdf"
    ]
)
def test_existing_files(filepath):
    """
    Test that existent files are identified correctly.

    :filepath: Existing test file name
    """

    scraper = FileExists(filepath, None)
    scraper.scrape_file()

    streams = DEFAULTSTREAMS.copy()

    assert scraper.well_formed is None
    assert not scraper.errors()
    assert partial_message_included("was found", scraper.messages())
    assert scraper.info()["class"] == "FileExists"
    for stream_index, stream_metadata in six.iteritems(streams):
        scraped_metadata = scraper.streams[stream_index]
        for key, value in six.iteritems(stream_metadata):
            assert getattr(scraped_metadata, key)() == value


@pytest.mark.parametrize(
    "filepath", "tests/data/image_gif/nonexistent_file.gif"
)
def test_nonexistent_files(filepath):
    """
    Test that non-existent files are identified correctly.

    :filepath: Non-existing file path
    """
    scraper = FileExists(filepath, None)
    scraper.scrape_file()

    assert not scraper.well_formed
    assert partial_message_included("does not exist", scraper.errors())


def test_none_filename():
    """Test that giving None filename results in error."""
    scraper = FileExists(None, None)
    scraper.scrape_file()

    assert not scraper.well_formed
    assert partial_message_included("No filename given.", scraper.errors())


@pytest.mark.parametrize(
    "filepath",
    [
        "tests/data/image_gif/valid_1987a.gif",
        "tests/data/image_gif/valid_1987a.gif",
        "tests/data/image_gif/invalid_1987a_truncated.gif",
        "tests/data/video_x-matroska/valid__ffv1.mkv"
    ]
)
def test_scraper_not_found(filepath):
    """
    Check ScraperNotFound results.

    :filepath: Test file
    """
    scraper = ScraperNotFound(filepath, None)
    scraper.scrape_file()

    streams = DEFAULTSTREAMS.copy()

    assert scraper.well_formed is False
    for stream_index, stream_metadata in six.iteritems(streams):
        scraped_metadata = scraper.streams[stream_index]
        for key, value in six.iteritems(stream_metadata):
            assert getattr(scraped_metadata, key)() == value


def test_mime_match_scraper():
    """Test scraper for MIME type and version match check."""
    scraper = MimeMatchScraper(
        None, mimetype="expected_mime", version="expected_version",
        params={"mimetype": "expected_mime", "version": "expected_version"})
    scraper.scrape_file()
    assert scraper.well_formed

    scraper = MimeMatchScraper(
        None, mimetype="mismatch", version="expected_version",
        params={"mimetype": "expected_mime", "version": "expected_version"})
    scraper.scrape_file()
    assert not scraper.well_formed

    scraper = MimeMatchScraper(
        None, mimetype="expected_mime", version="mismatch",
        params={"mimetype": "expected_mime", "version": "expected_version"})
    scraper.scrape_file()
    assert not scraper.well_formed

    scraper = MimeMatchScraper(
        None, mimetype="expected_mime", version="some_version",
        params={"mimetype": "expected_mime", "version": "(:unav)"})
    scraper.scrape_file()
    assert partial_message_included(
        "File format version is not supported", scraper.errors())
    assert not scraper.well_formed

    scraper = MimeMatchScraper(
        None, mimetype="application/vnd.oasis.opendocument.text",
        version="some_version",
        params={"mimetype": "application/vnd.oasis.opendocument.text",
                "version": "(:unav)"})
    scraper.scrape_file()
    assert partial_message_included(
        "File format version can not be resolved", scraper.messages())
    assert scraper.well_formed


def test_detected_version_scraper():
    """Test detected version scraper"""
    scraper = DetectedMimeVersionMetadataScraper(
        None, "text/xml", params={"detected_version": "123"})
    scraper.scrape_file()
    assert not scraper.well_formed
    assert scraper.streams[0].version() == "123"

    scraper = DetectedMimeVersionMetadataScraper(
        None, "text/xml", params=None)
    scraper.scrape_file()
    assert scraper.well_formed
    assert scraper.streams[0].version() == "1.0"

    scraper = DetectedMimeVersionMetadataScraper(
        None, "text/plain", params=None)
    scraper.scrape_file()
    assert partial_message_included(
        "MIME type not supported", scraper.errors())

    scraper = DetectedMimeVersionScraper(
        None, "application/vnd.oasis.opendocument.text",
        params={"detected_version": "123"})
    scraper.scrape_file()
    assert not scraper.well_formed
    assert scraper.streams[0].version() == "123"
