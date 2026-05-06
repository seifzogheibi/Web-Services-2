import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def fetch_page(url):
    """
    Fetch the HTML content for a single page.

    Raises an exception if the request fails.
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


def extract_page_text(html):
    """
    Extract searchable text from a quotes.toscrape.com page.

    This includes quote text, author names, and tags.
    """
    soup = BeautifulSoup(html, "html.parser")
    text_parts = []

    quotes = soup.find_all("div", class_="quote")

    for quote in quotes:
        quote_text = quote.find("span", class_="text")
        author = quote.find("small", class_="author")
        tags = quote.find_all("a", class_="tag")

        if quote_text is not None:
            text_parts.append(quote_text.get_text(" ", strip=True))

        if author is not None:
            text_parts.append(author.get_text(" ", strip=True))

        for tag in tags:
            text_parts.append(tag.get_text(" ", strip=True))

    return " ".join(text_parts)


def find_next_page_url(html, current_url):
    """
    Find the URL of the next page, if one exists.
    """
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")

    if next_link is None:
        return None

    href = next_link.get("href")

    if href is None:
        return None

    return urljoin(current_url, href)