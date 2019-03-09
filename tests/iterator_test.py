"""Test for dpres_scraper.scrapers. The purpose of this test is to make sure
that all scrapers are able to be found."""

from dpres_scraper.iterator import iter_scrapers
import pytest


@pytest.mark.parametrize(
    ["mimetype", "version", "scraper_classes"],
    [
        ("application/x-spss-por", None, ["Pspp"]),
        ("application/warc", None, ["WarcWarctools"]),
        ("text/csv", None, ["Csv", "TextFileMagic"]),
        ("text/plain", None, ["TextFileMagic", "TextFileMagic"]),
        ("video/mpeg", None, ["MpegMediainfo"]),
        ("video/mp4", None, ["MpegMediainfo"]),
        ("application/pdf", "1.2", ["PdfFileMagic", "PdfJHove"]),
        ("application/pdf", "1.3", ["PdfFileMagic", "PdfJHove"]),
        ("application/pdf", "1.4", ["PdfFileMagic", "PdfJHove"]),
        ("application/pdf", "1.5", ["PdfFileMagic", "PdfJHove"]),
        ("application/pdf", "1.6", ["PdfFileMagic", "PdfJHove"]),
        ("application/pdf", "A-1a", ["PdfFileMagic", "GhostScript", "VeraPdf"]),
        ("application/pdf", "A-1b", ["PdfFileMagic", "GhostScript", "VeraPdf"]),
        ("application/pdf", "A-2a", ["PdfFileMagic", "GhostScript", "VeraPdf"]),
        ("application/pdf", "A-2b", ["PdfFileMagic", "GhostScript", "VeraPdf"]),
        ("application/pdf", "A-2u", ["PdfFileMagic", "GhostScript", "VeraPdf"]),
        ("application/pdf", "A-3a", ["PdfFileMagic", "GhostScript", "VeraPdf"]),
        ("application/pdf", "A-3b", ["PdfFileMagic", "GhostScript", "VeraPdf"]),
        ("application/pdf", "A-3u", ["PdfFileMagic", "GhostScript", "VeraPdf"]),
        ("application/pdf", "1.7", ["PdfFileMagic", "GhostScript"]),
        ("image/tiff", None, ["TiffJHove", "TiffFileMagic", "TiffPil", "TiffWand"]),
        ("image/jpeg", None, ["JpegJHove", "JpegFileMagic", "JpegPil", "ImageWand"]),
        ("image/gif", None, ["GifJHove", "ImagePil", "ImageWand"]),
        ("text/html", "4.01", ["HtmlJHove", "HtmlFileMagic"]),
        ("text/html", "5.0", ["Vnu", "XmlEncoding", "HtmlFileMagic"]),
        ("image/png", None, ["Pngcheck", "PngFileMagic", "ImagePil", "ImageWand"]),
        ("application/warc", None, ["WarcWarctools"]),
        ("application/x-internet-archive", None, ["ArcWarctools"]),
        ("text/xml", None, ["Xmllint", "XmlEncoding", "XmlFileMagic"]),
        ("application/xhtml+xml", None, ["HtmlJHove", "HtmlFileMagic"]),
        ("audio/x-wav", None, ["WavJHove"]),
        ("application/vnd.oasis.opendocument.text", None,
         ["Office", "OfficeFileMagic"]),
        ("application/vnd.oasis.opendocument.spreadsheet", None,
         ["Office", "OfficeFileMagic"]),
        ("application/vnd.oasis.opendocument.presentation", None,
         ["Office", "OfficeFileMagic"]),
        ("application/vnd.oasis.opendocument.graphics", None,
         ["Office", "OfficeFileMagic"]),
        ("application/vnd.oasis.opendocument.formula", None,
         ["Office", "OfficeFileMagic"]),
        ("application/msword", None, ["Office", "OfficeFileMagic"]),
        ("application/vnd.ms-excel", None, ["Office", "OfficeFileMagic"]),
        ("application/vnd.ms-powerpoint", None, ["Office", "OfficeFileMagic"]),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml."
         "document", None, ["Office", "OfficeFileMagic"]),
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         None, ["Office", "OfficeFileMagic"]),
        ("application/vnd.openxmlformats-officedocument.presentationml."
         "presentation", None, ["Office", "OfficeFileMagic"]),
    ])
def tests_iter_scrapers(mimetype, version, scraper_classes):
    """
    Test for scraper discovery.
    """
    scrapers = iter_scrapers(mimetype, version)
    assert set(
        [x.__name__ for x in scrapers]) == set(scraper_classes)