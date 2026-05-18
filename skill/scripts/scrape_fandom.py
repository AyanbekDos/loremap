"""
Универсальный скрапер любого fandom.com вики через MediaWiki API.

Прямой доступ через HTML блокируется Cloudflare, API доступен всем.

Запуск:
    python scrape_fandom.py --api https://from.fandom.com/api.php --output raw/fandom/
    python scrape_fandom.py --api https://hbo-thelastofus.fandom.com/api.php --output raw/fandom/

Опции:
    --limit N         Только N страниц (для теста)
    --resume          Пропустить уже скачанные
    --index-only      Только составить список
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote

import httpx
import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify
from tenacity import retry, stop_after_attempt, wait_exponential

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

CLIENT = httpx.Client(
    headers={"User-Agent": UA, "Accept": "application/json,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.9"},
    timeout=httpx.Timeout(45.0),
    follow_redirects=True,
    http2=False,
)


def slugify(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return s.strip("-") or "untitled"


@retry(stop=stop_after_attempt(4), wait=wait_exponential(min=1, max=15))
def api_get(api_url: str, params: dict) -> dict:
    params = {**params, "format": "json", "formatversion": "2"}
    r = CLIENT.get(api_url, params=params)
    r.raise_for_status()
    return r.json()


def list_all_pages(api_url: str) -> list[dict]:
    pages: list[dict] = []
    apcontinue: str | None = None
    while True:
        params = {"action": "query", "list": "allpages", "apnamespace": 0, "aplimit": 500}
        if apcontinue:
            params["apcontinue"] = apcontinue
        data = api_get(api_url, params)
        chunk = data.get("query", {}).get("allpages", [])
        pages.extend(chunk)
        print(f"[index] +{len(chunk)} (total {len(pages)})", flush=True)
        cont = data.get("continue", {})
        apcontinue = cont.get("apcontinue")
        if not apcontinue:
            break
        time.sleep(0.3)
    return pages


def fetch_page(api_url: str, pageid: int) -> dict:
    return api_get(api_url, {
        "action": "parse",
        "pageid": pageid,
        "prop": "text|categories|properties|sections",
        "disablelimitreport": 1,
        "disableeditsection": 1,
    })


def extract_infobox(soup: BeautifulSoup) -> dict:
    infobox: dict[str, str] = {}
    box = soup.select_one("aside.portable-infobox")
    if not box:
        return infobox
    for item in box.select(".pi-item.pi-data"):
        label = item.select_one(".pi-data-label")
        value = item.select_one(".pi-data-value")
        if label and value:
            infobox[label.get_text(strip=True)] = value.get_text(" ", strip=True)
    title_el = box.select_one(".pi-title")
    if title_el:
        infobox["_title"] = title_el.get_text(strip=True)
    box.decompose()
    return infobox


def html_to_md(html: str) -> tuple[str, dict]:
    soup = BeautifulSoup(html, "lxml")
    infobox = extract_infobox(soup)
    for sel in [
        "table.navbox", "div.toc", "div.printfooter", "div.thumb",
        "div.mw-references-wrap", "table.metadata", "span.mw-editsection",
        "div.refbegin", "figure", "noscript", "div.mbox",
        "div.notice", "div.toccolours",
    ]:
        for el in soup.select(sel):
            el.decompose()
    body_md = markdownify(str(soup), heading_style="ATX").strip()
    body_md = re.sub(r"\n{3,}", "\n\n", body_md)
    body_md = re.sub(r"[ \t]+\n", "\n", body_md)
    return body_md, infobox


def guess_type(title: str, infobox: dict, body_text: str, categories: list[str]) -> str:
    cats_str = " ".join(categories).lower()
    body = body_text.lower()
    t = title.lower()

    if "characters" in cats_str or any(k in infobox for k in ("Actor", "Portrayed by", "Status", "Origin")):
        return "character"
    if "episodes" in cats_str or re.search(r"\bseason \d\b|\bepisode \d|\bchapter \d", t):
        return "episode"
    if "monsters" in cats_str or "creatures" in cats_str:
        return "monster"
    if "locations" in cats_str or "places" in cats_str or "buildings" in cats_str:
        return "location"
    if "objects" in cats_str or "items" in cats_str or "artifacts" in cats_str:
        return "artifact"
    if "symbols" in cats_str or "symbol" in t:
        return "symbol"
    if "actors" in cats_str or "cast" in cats_str or "crew" in cats_str:
        return "person_real"
    return "unknown"


def page_to_markdown(api_base: str, page: dict, parse_data: dict) -> tuple[str, str]:
    title = page["title"]
    pageid = page["pageid"]
    parsed = parse_data["parse"]
    html = parsed["text"]
    categories = [c["category"] if isinstance(c, dict) else str(c) for c in parsed.get("categories", [])]

    body_md, infobox = html_to_md(html)
    page_type = guess_type(title, infobox, body_md, categories)

    wiki_base = api_base.replace("/api.php", "")
    front = {
        "title": title,
        "pageid": pageid,
        "type": page_type,
        "status": "canon",
        "source": "fandom",
        "source_url": f"{wiki_base}/wiki/{quote(title.replace(' ', '_'))}",
        "scraped_at": date.today().isoformat(),
        "categories": categories,
        "infobox": infobox or {},
    }
    fm = yaml.safe_dump(front, allow_unicode=True, sort_keys=False).strip()
    md = f"---\n{fm}\n---\n\n# {title}\n\n{body_md}\n"
    slug = slugify(title)
    return slug, md


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", required=True, help="https://X.fandom.com/api.php")
    ap.add_argument("--output", required=True, help="Output dir, e.g. raw/fandom")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--index-only", action="store_true")
    args = ap.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    print(f"Собираю index через {args.api}...", flush=True)
    pages = list_all_pages(args.api)
    index_path = out / "_index.json"
    index_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Всего страниц: {len(pages)}. Index → {index_path}", flush=True)

    if args.index_only:
        return

    if args.limit:
        pages = pages[: args.limit]

    saved = skipped = failed = 0
    for i, p in enumerate(pages, 1):
        slug = slugify(p["title"])
        out_md = out / f"{slug}.md"
        if args.resume and out_md.exists():
            skipped += 1
            continue
        try:
            data = fetch_page(args.api, p["pageid"])
            slug, md = page_to_markdown(args.api, p, data)
            (out / f"{slug}.md").write_text(md, encoding="utf-8")
            saved += 1
            if i % 25 == 0 or i == len(pages):
                print(f"  [{i}/{len(pages)}] saved={saved} skipped={skipped} failed={failed}", flush=True)
            time.sleep(0.25)
        except Exception as e:
            failed += 1
            print(f"  ! {p['title']} ({p['pageid']}): {e}", file=sys.stderr, flush=True)

    print(f"\nГотово. saved={saved}, skipped={skipped}, failed={failed}")


if __name__ == "__main__":
    main()
