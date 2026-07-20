import requests 
from bs4 import BeautifulSoup

from app.services.parsing import _normalize_whitespace

REQUEST_TIMEOUT_SECONDS = 10

NOISE_TAGS = ["script", "style", "nav", "header", "footer", "aside", "form", "noscript"]


def fetch_and_extract_text_from_url(url:str) -> list[dict]:
    """
    Fetches a uRL and extracts its main readable text, stripping nav/footer/script/
    style clutter. HTML heading tags (h1-h6) are converted into short 
    standalone lines so the existing heading-detection heuristic picks  them up,
    matching the same behaviour as PDF/DOCX/Markdown parsing
    
    Returns a list with a single {"page_number": None, "text": str} dict.
    """
    
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT_SECONDS,
        headers={"User-Agent": "RagdocSupportBot/1.0"},
    )
    
    response.raise_for_status()
    
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    for tag_name in NOISE_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()
            
    lines = []
    for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
        text = element.get_text(strip=True)
        if text:
            lines.append(text)

    full_text = "\n".join(lines)
    cleaned_text = _normalize_whitespace(full_text)

    return [{"page_number": None, "text": cleaned_text}]