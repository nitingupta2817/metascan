from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from scraper import get_meta_data, crawl_site, normalise_url

app = FastAPI(title="MetaScan API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ────────────────────────────────────────────────────────────────────
class ScanRequest(BaseModel):
    urls: list[str]


class CrawlRequest(BaseModel):
    root_url: str
    max_pages: Optional[int] = 50
    max_depth: Optional[int] = 3
    delay_ms: Optional[int] = 200
    same_domain_only: Optional[bool] = True
    ignore_robots_txt: Optional[bool] = False
    include_noindex_pages: Optional[bool] = True


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "MetaScan API running"}


@app.post("/scan")
def scan_urls(request: ScanRequest):
    results = []
    for url in request.urls:
        url = normalise_url(url)
        if url:
            results.append(get_meta_data(url))
    return {"results": results, "total": len(results)}


@app.post("/crawl")
def crawl(request: CrawlRequest):
    root_url = normalise_url(request.root_url)
    if not root_url:
        return {"error": "Invalid URL", "results": []}
    results = crawl_site(
        root_url=root_url,
        max_pages=request.max_pages,
        max_depth=request.max_depth,
        delay_ms=request.delay_ms,
        same_domain_only=request.same_domain_only,
        ignore_robots_txt=request.ignore_robots_txt,
        include_noindex_pages=request.include_noindex_pages,
    )
    return {"results": results, "total": len(results), "root_url": root_url}


@app.get("/health")
def health():
    return {"status": "ok"}