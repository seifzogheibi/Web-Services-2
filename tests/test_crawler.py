from src.crawler import extract_page_text, find_next_page_url


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
    