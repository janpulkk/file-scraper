"""
Test module for Mediainfo.

NOTE: Mediainfo accepts practically any file. We use another scrapers for
well-formed checks.

This module tests that:
    - MIME type, version, streams, and well-formedness are scraped correctly
      for wav, m1v, m2v, mp4, mp3 and ts files. For valid files scraper
      messages contains 'file was analyzed successfully' and for empty file
      scraper errors contains 'No audio or video tracks found'.
    - When well-formedness is not checked, scraper messages contains 'Skipping
      scraper' and well_formed is None.
    - The following MIME type and version combinations are supported whether
      well-formedness is checked or not:
        - video/mpeg, '1'
        - video/mp4, ''
        - video/MP1S, ''
        - video/MP2P, ''
        - video/MP2T, ''
    - These MIME types are also supported with a made up version.
    - Made up MIME types are not supported.
"""
import pytest
from file_scraper.scrapers.mediainfo import MpegMediainfo, WavMediainfo
from tests.common import parse_results, evaluate_scraper
from tests.scrapers.stream_dicts import MPEG1_VIDEO, MPEG2_VIDEO, \
    MPEG4_CONTAINER, MPEG4_VIDEO, MPEG4_AUDIO, MPEG1_AUDIO, MPEGTS_CONTAINER, \
    MPEGTS_VIDEO, MPEGTS_AUDIO, MPEGTS_OTHER, WAV_AUDIO


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid__wav.wav", {
            "purpose": "Test valid WAV.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: WAV_AUDIO.copy()}}),
        ("valid_2_bwf.wav", {
            "purpose": "Test valid BWF.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: WAV_AUDIO.copy()}}),
        ("invalid__empty.wav", {
            "purpose": "Test empty WAV.",
            "stdout_part": "",
            "stderr_part": "No audio or video tracks found"}),
    ])
def test_mediainfo_scraper_wav(filename, result_dict):
    """Test WAV scraping with Mediainfo."""
    mimetype = 'audio/x-wav'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = WavMediainfo(correct.filename, mimetype, True)
    scraper.scrape_file()
    if 'empty' in filename:
        correct.version = None
        correct.streams[0]['version'] = None
        correct.streams[0]['stream_type'] = None

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.m1v", {
            "purpose": "Test valid MPEG-1.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MPEG1_VIDEO.copy()}}),
        ("valid_2.m2v", {
            "purpose": "Test valid MPEG-2.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MPEG2_VIDEO.copy()}}),
        ("invalid_1_empty.m1v", {
            "purpose": "Test empty MPEG-1.",
            "stdout_part": "",
            "stderr_part": "No audio or video tracks found"}),
        ("invalid_2_empty.m2v", {
            "purpose": "Test empty MPEG-2.",
            "stdout_part": "",
            "stderr_part": "No audio or video tracks found"})
    ])
def test_mediainfo_scraper_mpeg(filename, result_dict):
    """Test MPEG scraping with MpegMediainfo."""
    mimetype = 'video/mpeg'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MpegMediainfo(correct.filename, mimetype, True)
    scraper.scrape_file()
    if 'empty' in filename:
        correct.version = None
        correct.streams[0]['version'] = None
        correct.streams[0]['stream_type'] = None

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid__h264_aac.mp4", {
            "purpose": "Test valid mp4.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MPEG4_CONTAINER.copy(),
                        1: MPEG4_VIDEO.copy(),
                        2: MPEG4_AUDIO.copy()}}),
        ("invalid__empty.mp4", {
            "purpose": "Test invalid MPEG-4.",
            "stdout_part": "",
            "stderr_part": "No audio or video tracks found"})
    ])
def test_mediainfo_scraper_mp4(filename, result_dict):
    """Test MP4 scraping with MpegMediainfo."""
    mimetype = 'video/mp4'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MpegMediainfo(correct.filename, mimetype, True)
    scraper.scrape_file()
    if 'empty' in filename:
        correct.version = None
        correct.streams[0]['version'] = None
        correct.streams[0]['stream_type'] = None

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.mp3", {
            "purpose": "Test valid mp3.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MPEG1_AUDIO.copy()}}),
        ("invalid__empty.mp3", {
            "purpose": "Test empty mp3",
            "stdout_part": "",
            "stderr_part": "No audio or video tracks found"})
    ])
def test_mediainfo_scraper_mp3(filename, result_dict):
    """Test MP3 scraping with MpegMediainfo."""
    mimetype = 'audio/mpeg'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MpegMediainfo(correct.filename, mimetype, True)
    scraper.scrape_file()
    if 'empty' in filename:
        correct.version = None
        correct.streams[0]['version'] = None
        correct.streams[0]['stream_type'] = None

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_.ts", {
            "purpose": "Test valid MPEG-TS.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MPEGTS_CONTAINER.copy(),
                        1: MPEGTS_VIDEO.copy(),
                        2: MPEGTS_AUDIO.copy(),
                        3: MPEGTS_OTHER.copy()}}),
        ("invalid__empty.ts", {
            "purpose": "Test empty MPEG-TS.",
            "stdout_part": "",
            "stderr_part": "No audio or video tracks found"})
    ])
def test_mediainfo_scraper_mpegts(filename, result_dict):
    """Test MPEG Transport Stream scraping with MpegMediainfo."""
    mimetype = 'video/MP2T'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MpegMediainfo(correct.filename, mimetype, True)
    scraper.scrape_file()
    if 'empty' in filename:
        correct.version = None
        correct.streams[0]['version'] = None
        correct.streams[0]['stream_type'] = None

    evaluate_scraper(scraper, correct)


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = WavMediainfo('tests/data/audio_x-wav/valid__wav.wav',
                           'audio/x-wav', False)
    scraper.scrape_file()
    assert 'Skipping scraper' not in scraper.messages()
    assert scraper.well_formed is None


def test_is_supported_wav():
    """Test is_supported method."""
    mime = 'audio/x-wav'
    ver = 2
    assert WavMediainfo.is_supported(mime, ver, True)
    assert WavMediainfo.is_supported(mime, None, True)
    assert WavMediainfo.is_supported(mime, ver, False)
    assert WavMediainfo.is_supported(mime, 'foo', True)
    assert not WavMediainfo.is_supported('foo', ver, True)


@pytest.mark.parametrize(
    ['mime', 'ver'],
    [
        ('video/mpeg', '1'),
        ('video/mp4', ''),
        ('video/MP1S', ''),
        ('video/MP2P', ''),
        ('video/MP2T', ''),
    ]
)
def test_is_supported_mpeg(mime, ver):
    """Test is_supported method."""
    assert MpegMediainfo.is_supported(mime, ver, True)
    assert MpegMediainfo.is_supported(mime, None, True)
    assert MpegMediainfo.is_supported(mime, ver, False)
    assert MpegMediainfo.is_supported(mime, 'foo', True)
    assert not MpegMediainfo.is_supported('foo', ver, True)
