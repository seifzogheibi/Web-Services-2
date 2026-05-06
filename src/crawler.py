import requests


def fetch_page(url):
    """
    Fetch the HTML content for a single page.

    Raises an exception if the request fails.
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text