from unittest.mock import Mock, patch

import pytest
import requests

from src.crawler import crawl_website, extract_page_text, fetch_page, find_next_page_url

SAMPLE_HTML = """
<html>
    <body>
        <div class="quote">
            <span class="text">“The world as we have created it is a process of our thinking.”</span>
            <small class="author">Albert Einstein</small>
            <div class="tags">
                <a class="tag">change</a>
                <a class="tag">thinking</a>
            </div>
        </div>
        <nav>
            <ul class="pager">
                <li class="next">
                    <a href="/page/2/">Next</a>
                </li>
            </ul>
        </nav>
    </body>
</html>
"""


def test_extract_page_text_includes_quote_text():
    text = extract_page_text(SAMPLE_HTML)

    assert "The world as we have created it" in text


def test_extract_page_text_includes_author():
    text = extract_page_text(SAMPLE_HTML)

    assert "Albert Einstein" in text


def test_extract_page_text_includes_tags():
    text = extract_page_text(SAMPLE_HTML)

    assert "change" in text
    assert "thinking" in text


def test_find_next_page_url_returns_absolute_url():
    next_url = find_next_page_url(SAMPLE_HTML, "https://quotes.toscrape.com/")

    assert next_url == "https://quotes.toscrape.com/page/2/"


def test_find_next_page_url_returns_none_when_missing():
    html = """
    <html>
        <body>
            <div class="quote">
                <span class="text">No next page here.</span>
            </div>
        </body>
    </html>
    """

    next_url = find_next_page_url(html, "https://quotes.toscrape.com/page/10/")

    assert next_url is None


def test_extract_page_text_returns_empty_string_for_no_quotes():
    html = "<html><body><p>No quote divs here.</p></body></html>"

    text = extract_page_text(html)

    assert text == ""


@patch("src.crawler.requests.get")
def test_fetch_page_uses_requests_get(mock_get):
    mock_response = Mock()
    mock_response.text = "<html>Success</html>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = fetch_page("https://quotes.toscrape.com/")

    mock_get.assert_called_once_with("https://quotes.toscrape.com/", timeout=10)
    assert result == "<html>Success</html>"


@patch("src.crawler.requests.get")
def test_fetch_page_raises_request_exception(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("Server error")
    mock_get.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        fetch_page("https://quotes.toscrape.com/")


@patch("src.crawler.time.sleep")
@patch("src.crawler.fetch_page")
def test_crawl_website_uses_next_links_and_delay(mock_fetch_page, mock_sleep):
    first_page = """
    <html>
        <body>
            <div class="quote">
                <span class="text">First page quote.</span>
                <small class="author">Author One</small>
            </div>
            <li class="next">
                <a href="/page/2/">Next</a>
            </li>
        </body>
    </html>
    """

    second_page = """
    <html>
        <body>
            <div class="quote">
                <span class="text">Second page quote.</span>
                <small class="author">Author Two</small>
            </div>
        </body>
    </html>
    """

    mock_fetch_page.side_effect = [first_page, second_page]

    pages = crawl_website(
        start_url="https://quotes.toscrape.com/",
        delay=6
    )

    assert len(pages) == 2
    assert "https://quotes.toscrape.com/" in pages
    assert "https://quotes.toscrape.com/page/2/" in pages
    assert "First page quote" in pages["https://quotes.toscrape.com/"]
    assert "Second page quote" in pages["https://quotes.toscrape.com/page/2/"]
    mock_sleep.assert_called_once_with(6)


@patch("src.crawler.fetch_page")
def test_crawl_website_stops_on_request_error(mock_fetch_page):
    mock_fetch_page.side_effect = requests.RequestException("Network error")

    pages = crawl_website(
        start_url="https://quotes.toscrape.com/",
        delay=0
    )

    assert pages == {}
