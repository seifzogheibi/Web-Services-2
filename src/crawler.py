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
    # send a get request with a timeout so the crawler does not hang forever
    response = requests.get(url, timeout=10)

    # raise an error if the server returns an unsuccessful response
    response.raise_for_status()

    return response.text


def extract_page_text(html: str) -> str:
    """
    Extract searchable text from a quotes.toscrape.com page.

    This includes quote text, author names, and tags.
    """
    # parse the html so we can search for quote blocks and their content
    soup = BeautifulSoup(html, "html.parser")
    text_parts = []

    # each quote on the website is stored inside a div with class quote
    quotes = soup.find_all("div", class_="quote")

    for quote in quotes:
        # extract the main parts that are useful for searching
        quote_text = quote.find("span", class_="text")
        author = quote.find("small", class_="author")
        tags = quote.find_all("a", class_="tag")

        # add the quote text if it exists on the page
        if quote_text is not None:
            text_parts.append(quote_text.get_text(" ", strip=True))

        # add the author name if it exists on the page
        if author is not None:
            text_parts.append(author.get_text(" ", strip=True))

        # add each tag as extra searchable text
        for tag in tags:
            text_parts.append(tag.get_text(" ", strip=True))

    # combine all extracted text into one searchable string for this page
    return " ".join(text_parts)


def find_next_page_url(html: str, current_url: str) -> str | None:
    """
    Find the URL of the next page, if one exists.
    """
    # parse the page and look for the website's next-page link
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")

    # return none when the current page is the final page
    if next_link is None:
        return None

    href = next_link.get("href")

    # return none if the link exists but has no href value
    if href is None:
        return None

    # convert the relative next-page link into a full url
    return urljoin(current_url, href)


def crawl_website(start_url: str = BASE_URL, delay: int = POLITENESS_DELAY) -> dict[str, str]:
    """
    Crawl all quote pages starting from the given URL.

    Returns a dictionary mapping page URLs to extracted searchable text.
    """
    # store each crawled page url and the text extracted from it
    pages = {}
    current_url = start_url

    # keep track of visited urls to avoid accidental loops
    visited_urls = set()

    while current_url is not None:
        # stop if the crawler somehow reaches a page it has already seen
        if current_url in visited_urls:
            print(f"Already visited {current_url}. Stopping crawl to avoid a loop.")
            break

        visited_urls.add(current_url)
        print(f"Crawling: {current_url}")

        try:
            # download the current page
            html = fetch_page(current_url)
        except requests.RequestException as error:
            # stop cleanly if there is a network or http error
            print(f"Failed to fetch {current_url}: {error}")
            break

        # extract and store the searchable text for this page
        page_text = extract_page_text(html)
        pages[current_url] = page_text

        # find the next page before deciding whether to wait
        next_url = find_next_page_url(html, current_url)

        # respect the required politeness delay between requests
        if next_url is not None:
            time.sleep(delay)

        current_url = next_url

    return pages
