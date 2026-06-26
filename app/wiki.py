import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote

W_API = "https://en.wikipedia.org/w/api.php"

SKIP_PREFIXES = (
    "File:", "Talk:", "Wikipedia:", "Help:", "Portal:",
    "Special:", "Template:", "User:", "Category:", "Draft:",
    "Module:", "MediaWiki:",
)


def get_random_article():
    r = requests.get(W_API, params={
        "action": "query",
        "list": "random",
        "rnnamespace": "0",
        "rnlimit": "1",
        "format": "json",
    }, timeout=10)
    r.raise_for_status()
    return r.json()["query"]["random"][0]["title"]


def get_article(title):
    r = requests.get(W_API, params={
        "action": "parse",
        "page": title,
        "prop": "text",
        "disablelimitreport": "1",
        "format": "json",
        "redirects": "1",
    }, timeout=15)
    r.raise_for_status()
    data = r.json()

    if "error" in data:
        return None

    parse = data["parse"]
    actual_title = parse["title"]
    soup = BeautifulSoup(parse["text"]["*"], "lxml")

    for sel in (
        ".reflist", ".references", ".navbox", ".navbox-inner",
        ".mw-empty-elt", ".hatnote", ".noprint", ".mw-editsection",
        ".sidebar", "style",
    ):
        for el in soup.select(sel):
            el.decompose()

    for a in list(soup.find_all("a", href=True)):
        href = a.get("href", "")
        if href.startswith("/wiki/"):
            raw = href[6:].split("#")[0]
            decoded = unquote(raw)
            if not decoded or any(decoded.startswith(p) for p in SKIP_PREFIXES):
                a.unwrap()
            else:
                a.attrs = {"href": f"/play/{raw}", "class": "wiki-link", "title": a.get("title", "")}
        elif href.startswith("#"):
            pass
        else:
            a.unwrap()

    return {"title": actual_title, "html": str(soup)}
