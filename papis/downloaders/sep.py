from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup

from papis.downloaders import Downloader


class SEPDownloader(Downloader):
    """Retrieve documents from the
    Stanford Encyclopedia of Philosophy <plato.stanford.edu>__"""

    BIBTEX_CONTAINING_URL: ClassVar[str] = (
        "https://plato.stanford.edu/cgi-bin/encyclopedia/archinfo.cgi"
        "?entry={}"
    )

    DOCUMENT_URL: ClassVar[str] = (
        "https://leibniz.stanford.edu/friends/members/view/{}/sc/"        
    )

    def __init__(self, uri: str) -> None:
        super().__init__(
            uri,
            name="sep",
            expected_document_extension="pdf",
        )

    @classmethod
    def match(cls, url: str) -> Downloader | None:
        if re.match(r".*plato\.stanford\.edu/entries/.*", url):
            return SEPDownloader(url)
        else:
            return None

    @property
    def _name(self) -> str:
        """The internal name of the entry, used in URLs."""
        from urllib.parse import urlparse
        return urlparse(self.uri).path.strip("/").split("/")[-1]

    def get_data(self) -> dict[str, Any]:
        from papis.downloaders.base import parse_meta_headers

        soup = self._get_soup()
        data = parse_meta_headers(soup)

        return data

    def _get_bibtex_page_body(self) -> str | None:
        url = self.BIBTEX_CONTAINING_URL.format(self._name)
        self.logger.debug("Getting BibTeX data from: '%s'.", url)
        response = self.session.get(url, cookies=self.cookies)

        if response.ok:
            return str(response.content)

    def _extract_bibtex_data(self, content: str) -> str | None:
        soup = BeautifulSoup(content)
        tag = soup.find("pre")
        if tag:
            return (tag.string
                .replace("\\t", "\t").replace("\\n", "\n")
                .replace("\\\\url", ""))

    def get_bibtex_data(self) -> str | None:
        body = self._get_bibtex_page_body()
        if body:
            return self._extract_bibtex_data(body)


    def get_document_url(self) -> str | None:
        return self.DOCUMENT_URL.format(self._name)

    # There is no downloadable BibTeX file,
    # but the BibTeX can be extracted from a web page,
    # which `get_bibtex_data` does.
    def download_bibtex(self):
        raise NotImplementedError

