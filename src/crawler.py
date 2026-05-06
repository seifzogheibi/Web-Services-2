import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://quotes.toscrape.com/"
POLITENESS_DELAY = 6


def fetch_page(url: str) -> str:    
    """
    Fetch the HTML content for a single page.

    Raises an exception if the request fails.
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


def extract_page_text(html: str) -> str:
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


def find_next_page_url(html: str, current_url: str) -> str | None:
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


def crawl_website(start_url: str = BASE_URL, delay: int = POLITENESS_DELAY) -> dict[str, str]:
    """
    Crawl all quote pages starting from the given URL.

    Returns a dictionary mapping page URLs to extracted searchable text.
    """
    pages = {}
    current_url = start_url
    visited_urls = set()

    while current_url is not None:
        if current_url in visited_urls:
            print(f"Already visited {current_url}. Stopping crawl to avoid a loop.")
            break

        visited_urls.add(current_url)
        print(f"Crawling: {current_url}")

        try:
            html = fetch_page(current_url)
        except requests.RequestException as error:
            print(f"Failed to fetch {current_url}: {error}")
            break

        page_text = extract_page_text(html)
        pages[current_url] = page_text

        next_url = find_next_page_url(html, current_url)

        if next_url is not None:
            time.sleep(delay)

        current_url = next_url

    return pages