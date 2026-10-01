import os

from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient

import requests
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re

load_dotenv(override=True)

@tool
def search_url(query: str) -> str:
    """Search the web for recent and reliable information on a topic"""

    api_key = os.getenv("TAVILY_API_KEY", "").strip()

    if not api_key:
        return "TAVILY_API_KEY is missing from your .env file."

    tavily_client = TavilyClient(api_key=api_key)

    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=True,
        )
    except Exception as exc:
        return f"Web search failed: {exc}"

    results = response.get("results", [])

    if not results:
        return f"No web-search results found for: {query}"

    out = []

    answer = response.get("answer")
    if answer:
        out.append(f"Summary:\n{answer}\n")

    for result in results:
        title = result.get("title", "Untitled result")
        url = result.get("url", "No URL available")
        content = result.get("content", "No snippet available")

        out.append(
            f"Title: {title}\n"
            f"URL: {url}\n"
            f"Snippet: {content[:300]}...\n"
        )

    return "\n---\n".join(out)

@tool
def scrape_web(url: str) -> str:
    """ Scrape and extract clean readable content fron a url.
     Use multiple strategies for better readability """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=20,
            allow_redirects=True,
        )
        response.raise_for_status()

    except requests.Timeout:
        return "Error: The website took too long to respond."

    except requests.TooManyRedirects:
        return "Error: The website redirected too many times."

    except requests.RequestException as exc:
        return f"Error: Could not fetch the URL. Details: {exc}"

    content_type = response.headers.get("Content-Type", "").lower()

    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
        return (
            "Error: This URL does not appear to be an HTML web page. "
            f"Received content type: {content_type or 'unknown'}"
        )

    html_content = response.text

    if not html_content.strip():
        return "Error: The page returned no readable HTML content."

    title = ""
    extracted_text = ""

    try:
        extracted_text = trafilatura.extract(
            html_content,
            include_comments=False,
            include_tables=True,
            include_links=False,
            favor_precision=True,
        ) or ""

    except Exception:
        extracted_text = ""

    if len(extracted_text.strip()) < 200:
        try:
            readable_document = Document(html_content)
            title = readable_document.short_title() or ""

            article_html = readable_document.summary()
            article_soup = BeautifulSoup(article_html, "lxml")

            extracted_text = article_soup.get_text(
                separator="\n",
                strip=True,
            )

        except Exception:
            extracted_text = ""

    if len(extracted_text.strip()) < 100:
        try:
            soup = BeautifulSoup(html_content, "lxml")

            page_title = soup.title.get_text(strip=True) if soup.title else ""
            title = title or page_title

            for unwanted_tag in soup(
                [
                    "script",
                    "style",
                    "noscript",
                    "iframe",
                    "svg",
                    "nav",
                    "footer",
                    "header",
                    "aside",
                    "form",
                ]
            ):
                unwanted_tag.decompose()

            extracted_text = soup.get_text(
                separator="\n",
                strip=True,
            )

        except Exception as exc:
            return f"Error: Content extraction failed. Details: {exc}"

    clean_lines = []
    seen_lines = set()

    for line in extracted_text.splitlines():
        line = " ".join(line.split())

        if line and line not in seen_lines:
            clean_lines.append(line)
            seen_lines.add(line)

    clean_text = "\n".join(clean_lines).strip()

    if not clean_text:
        return (
            "Error: No readable article content could be extracted. "
            "The page may require JavaScript, authentication, or may block scraping."
        )

    max_characters = 15_000
    if len(clean_text) > max_characters:
        clean_text = (
            clean_text[:max_characters]
            + "\n\n[Content truncated after 15,000 characters.]"
        )

    title_section = f"Title: {title}\n" if title else ""

    return (
        f"Source URL: {response.url}\n"
        f"{title_section}"
        f"\nContent:\n{clean_text}"
    )