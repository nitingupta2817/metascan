import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque
import re
import time


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def normalise_url(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    url, _ = urldefrag(url)
    return url.rstrip("/")


def get_meta_data(url: str) -> dict:
    result = {
        "url": url, "title": "", "title_len": 0,
        "description": "", "desc_len": 0,
        "h1_texts": [], "h2_texts": [],
        "robots_content": "", "x_robots": "",
        "is_noindex": False, "is_nofollow": False,
        "canonical": "", "canonical_mismatch": False,
        "og_title": "", "og_desc": "",
        "img_data": [], "imgs_total": 0,
        "imgs_no_alt": 0, "imgs_with_alt": 0,
        "error": "", "blocked": False,
    }
    try:
        r = requests.get(url, timeout=15, headers=HEADERS, allow_redirects=True)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "lxml")

        # Title
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""
        result["title"] = title or "No title found"
        result["title_len"] = len(title)

        # Description
        desc_tag = soup.find("meta", attrs={"name": "description"})
        desc = desc_tag.get("content", "").strip() if desc_tag else ""
        result["description"] = desc or "No description found"
        result["desc_len"] = len(desc)

        # Headings
        result["h1_texts"] = [t.get_text(strip=True) for t in soup.find_all("h1") if t.get_text(strip=True)]
        result["h2_texts"] = [t.get_text(strip=True) for t in soup.find_all("h2") if t.get_text(strip=True)]

        # Robots
        robots_tag = soup.find("meta", attrs={"name": re.compile(r"robots", re.I)})
        robots_content = robots_tag.get("content", "").lower().strip() if robots_tag else ""
        result["robots_content"] = robots_content
        result["is_noindex"] = "noindex" in robots_content
        result["is_nofollow"] = "nofollow" in robots_content

        x_robots = r.headers.get("X-Robots-Tag", "").lower()
        result["x_robots"] = x_robots
        if "noindex" in x_robots:
            result["is_noindex"] = True
        if "nofollow" in x_robots:
            result["is_nofollow"] = True

        # Canonical
        can_tag = soup.find("link", rel=lambda v: v and "canonical" in v)
        canonical = can_tag.get("href", "").strip() if can_tag else ""
        result["canonical"] = canonical
        result["canonical_mismatch"] = bool(canonical and canonical.rstrip("/") != url.rstrip("/"))

        # Open Graph
        og_t = soup.find("meta", property="og:title")
        og_d = soup.find("meta", property="og:description")
        result["og_title"] = og_t.get("content", "").strip() if og_t else ""
        result["og_desc"] = og_d.get("content", "").strip() if og_d else ""

        # Images
        imgs = soup.find_all("img")
        img_data = []
        for img in imgs:
            src = img.get("src", "").strip()
            alt = img.get("alt", "").strip()
            if src and not src.startswith("http"):
                src = urljoin(url, src)
            img_data.append({
                "src": src or "(no src)",
                "alt": alt,
                "has_alt": bool(alt),
                "width": img.get("width", ""),
                "height": img.get("height", ""),
            })
        result["img_data"] = img_data
        result["imgs_total"] = len(img_data)
        result["imgs_no_alt"] = sum(1 for i in img_data if not i["has_alt"])
        result["imgs_with_alt"] = result["imgs_total"] - result["imgs_no_alt"]

    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response else ""
        if code == 403:
            result["error"] = "403 Forbidden — site blocked automated scanning."
            result["blocked"] = True
        else:
            result["error"] = str(e)
    except requests.exceptions.RequestException as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = f"Unexpected error: {e}"

    return result


def get_robots_disallowed(root_url: str) -> set:
    disallowed = set()
    try:
        parsed = urlparse(root_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        r = requests.get(robots_url, timeout=8, headers=HEADERS)
        if r.status_code == 200:
            ua_applies = False
            for line in r.text.splitlines():
                line = line.strip()
                if line.lower().startswith("user-agent:"):
                    agent = line.split(":", 1)[1].strip()
                    ua_applies = agent == "*"
                elif ua_applies and line.lower().startswith("disallow:"):
                    path = line.split(":", 1)[1].strip()
                    if path:
                        disallowed.add(path)
    except Exception:
        pass
    return disallowed


def is_same_domain(url: str, root_netloc: str) -> bool:
    return urlparse(url).netloc == root_netloc


def is_crawlable_url(url: str) -> bool:
    skip_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico",
                 ".pdf", ".doc", ".docx", ".zip", ".mp3", ".mp4",
                 ".css", ".js", ".woff", ".woff2", ".ttf", ".json", ".xml"}
    path = urlparse(url).path
    ext = "." + path.split(".")[-1].lower() if "." in path.split("/")[-1] else ""
    return ext not in skip_exts


def extract_links(soup, base_url: str) -> list:
    links = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        full = urljoin(base_url, href)
        full, _ = urldefrag(full)
        full = full.rstrip("/")
        if full.startswith("http"):
            links.append(full)
    return links


def crawl_site(
    root_url: str,
    max_pages: int = 50,
    max_depth: int = 3,
    delay_ms: int = 200,
    same_domain_only: bool = True,
    ignore_robots_txt: bool = False,
    include_noindex_pages: bool = True,
    progress_callback=None,
) -> list:
    root_url = normalise_url(root_url)
    root_netloc = urlparse(root_url).netloc

    disallowed = set()
    if not ignore_robots_txt:
        disallowed = get_robots_disallowed(root_url)

    visited = set()
    queue = deque([(root_url, 0)])
    results = []
    session = requests.Session()

    while queue and len(results) < max_pages:
        url, depth = queue.popleft()
        url = url.rstrip("/")

        if url in visited:
            continue
        if same_domain_only and not is_same_domain(url, root_netloc):
            continue
        if not is_crawlable_url(url):
            continue
        if not ignore_robots_txt:
            path = urlparse(url).path
            if any(path.startswith(p) for p in disallowed):
                continue

        visited.add(url)

        if progress_callback:
            progress_callback(url, len(results) + 1)

        try:
            r = session.get(url, timeout=15, headers=HEADERS, allow_redirects=True)
            status = r.status_code
            soup = BeautifulSoup(r.content, "lxml")

            title_tag = soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else ""

            desc_tag = soup.find("meta", attrs={"name": "description"})
            desc = desc_tag.get("content", "").strip() if desc_tag else ""

            h1s = [h.get_text(strip=True) for h in soup.find_all("h1") if h.get_text(strip=True)]
            h2s = [h.get_text(strip=True) for h in soup.find_all("h2") if h.get_text(strip=True)]

            robots_tag = soup.find("meta", attrs={"name": re.compile(r"robots", re.I)})
            robots_content = robots_tag.get("content", "").lower().strip() if robots_tag else ""
            noindex = "noindex" in robots_content

            can_tag = soup.find("link", rel=lambda v: v and "canonical" in v)
            canonical = can_tag.get("href", "").strip() if can_tag else ""

            og_t = soup.find("meta", property="og:title")
            og_d = soup.find("meta", property="og:description")

            imgs = soup.find_all("img")
            imgs_no_alt = sum(1 for i in imgs if not i.get("alt", "").strip())

            word_count = len(soup.get_text(separator=" ", strip=True).split())
            links = extract_links(soup, url)

            page = {
                "url": url,
                "status": status,
                "title": title,
                "title_len": len(title),
                "description": desc,
                "desc_len": len(desc),
                "h1_count": len(h1s),
                "h1_first": h1s[0] if h1s else "",
                "h2_count": len(h2s),
                "robots_meta": robots_content,
                "noindex": noindex,
                "canonical": canonical,
                "og_title": og_t.get("content", "").strip() if og_t else "",
                "og_description": og_d.get("content", "").strip() if og_d else "",
                "word_count": word_count,
                "images_count": len(imgs),
                "images_no_alt": imgs_no_alt,
                "error": "",
                "issues": [],
                "score": 100,
            }

            # Score
            issues = []
            if not title: issues.append("no_title")
            elif len(title) > 60: issues.append("title_long")
            if not desc: issues.append("no_desc")
            elif len(desc) > 160: issues.append("desc_long")
            if len(h1s) == 0: issues.append("no_h1")
            elif len(h1s) > 1: issues.append("multi_h1")
            if len(h2s) == 0: issues.append("no_h2")
            if noindex: issues.append("noindex")
            if imgs_no_alt > 0: issues.append("img_no_alt")

            WEIGHTS = {"no_title": 25, "no_desc": 22, "no_h1": 20,
                       "title_long": 10, "desc_long": 10, "multi_h1": 10,
                       "img_no_alt": 18, "no_h2": 8, "noindex": 12}
            score = max(0, 100 - sum(WEIGHTS.get(i, 5) for i in issues))

            page["issues"] = issues
            page["score"] = score
            results.append(page)

            if depth < max_depth and (not noindex or include_noindex_pages):
                for link in links:
                    if link not in visited:
                        queue.append((link, depth + 1))

        except Exception as e:
            results.append({
                "url": url, "status": None, "title": "", "title_len": 0,
                "description": "", "desc_len": 0, "h1_count": 0, "h1_first": "",
                "h2_count": 0, "robots_meta": "", "noindex": False, "canonical": "",
                "og_title": "", "og_description": "", "word_count": 0,
                "images_count": 0, "images_no_alt": 0,
                "error": str(e), "issues": ["fetch_error"], "score": 0,
            })

        if delay_ms > 0:
            time.sleep(delay_ms / 1000)

    return results