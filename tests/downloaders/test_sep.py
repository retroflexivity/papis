from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from papis.downloaders import get_downloader_by_name
from papis.downloaders.sep import SEPDownloader

if TYPE_CHECKING:
    from papis.testing import ResourceCache, TemporaryConfiguration

LB_URLS = (
    "https://plato.stanford.edu/entries/mental-representation",
    "https://plato.stanford.edu/entries/history",
)


def test_sep_match(tmp_config: TemporaryConfiguration) -> None:
    valid_urls = LB_URLS

    invalid_urls = (
        "https://plato.stanford.edu/whatever",
        "https://arxiv.org/abs/1000.00001",
    )

    for url in valid_urls:
        assert isinstance(SEPDownloader.match(url), SEPDownloader)

    for url in invalid_urls:
        assert SEPDownloader.match(url) is None


@pytest.mark.parametrize("url", LB_URLS)
def test_sep_fetch(
    tmp_config: TemporaryConfiguration,
    resource_cache: ResourceCache,
    monkeypatch: pytest.MonkeyPatch,
    url: str,
) -> None:
    cls_ = get_downloader_by_name("sep")
    assert cls_ is SEPDownloader

    down = cls_.match(url)
    assert down is not None

    uid = os.path.basename(url)
    infile = f"SEP_{uid}.html"
    outfile = f"SEP_{uid}_Out.json"

    monkeypatch.setattr(
        down, "_get_bibtex_page_body", lambda: resource_cache.get_remote_resource(infile, url)
    )
    monkeypatch.setattr(down, "download_document", lambda: None)

    down.fetch()
    extracted_data = down.ctx.data

    expected_data = resource_cache.get_local_resource(outfile, extracted_data)

    assert extracted_data == expected_data
