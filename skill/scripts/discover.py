"""
Auto-discovery: по названию сериала / книги находит fandom URL + subreddit.

Запуск:
    python discover.py "Severance"
    python discover.py "The Last of Us"
    python discover.py "A Song of Ice and Fire"
"""
from __future__ import annotations

import argparse
import json
import re
import sys

import httpx

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

CLIENT = httpx.Client(
    headers={
        "User-Agent": UA,
        "Accept": "application/json,text/html,*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    },
    timeout=httpx.Timeout(15.0),
    follow_redirects=True,
    http2=False,
)


def slug_candidates(name: str) -> list[str]:
    """Возвращает варианты slug для fandom subdomain."""
    raw = name.lower().strip()
    no_articles = re.sub(r"^(the|a|an)\s+", "", raw)
    no_punct = re.sub(r"[^\w\s-]", "", raw)
    no_punct_no_articles = re.sub(r"^(the|a|an)\s+", "", no_punct)

    candidates = [
        no_punct.replace(" ", ""),
        no_punct.replace(" ", "-"),
        no_punct_no_articles.replace(" ", ""),
        no_punct_no_articles.replace(" ", "-"),
    ]
    # acronym - first letters of significant words
    words = no_punct_no_articles.split()
    if len(words) >= 3:
        acronym = "".join(w[0] for w in words if w not in ("the", "of", "and", "a", "an", "in"))
        candidates.append(acronym)
        candidates.append(acronym + "-wiki")

    # dedupe preserve order
    seen = set()
    out = []
    for c in candidates:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def test_fandom(slug: str) -> dict | None:
    """Test https://<slug>.fandom.com/api.php returns valid MediaWiki API."""
    url = f"https://{slug}.fandom.com/api.php"
    try:
        r = CLIENT.get(url, params={
            "action": "query",
            "meta": "siteinfo",
            "siprop": "general",
            "format": "json",
        })
        if r.status_code != 200:
            return None
        data = r.json()
        site = data.get("query", {}).get("general", {})
        return {
            "api_url": url,
            "site_name": site.get("sitename"),
            "main_page": site.get("base"),
            "lang": site.get("lang"),
        }
    except Exception:
        return None


def find_fandom(name: str) -> dict | None:
    for slug in slug_candidates(name):
        print(f"  trying {slug}.fandom.com...", file=sys.stderr)
        res = test_fandom(slug)
        if res:
            res["slug"] = slug
            return res
    return None


def subreddit_candidates(name: str) -> list[str]:
    raw = name.strip()
    no_articles = re.sub(r"^(The|A|An)\s+", "", raw)
    no_punct = re.sub(r"[^\w\s-]", "", no_articles).strip()
    base = no_punct.replace(" ", "")

    suffixes = ["", "TV", "Show", "Series", "TVEpix", "HBO", "FX", "AppleTV", "AppleTVPlus", "MGM", "MGMPlus", "Netflix", "AMC", "Showtime"]
    cands = []
    for variant in (base, base.lower(), base.title(), base.capitalize()):
        for s in suffixes:
            cands.append(variant + s)

    words = no_punct.lower().split()
    if len(words) >= 3:
        acronym = "".join(w[0] for w in words)
        cands.append(acronym)
        cands.append(acronym.upper())

    seen = set()
    out = []
    for c in cands:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def test_subreddit(name: str) -> dict | None:
    """/about блокирует ботов. Используем /top.json с лимитом 1 - если возвращает посты, sub существует."""
    url = f"https://www.reddit.com/r/{name}/top.json"
    try:
        r = CLIENT.get(url, params={"t": "all", "limit": 1})
        if r.status_code != 200:
            return None
        data = r.json()
        children = data.get("data", {}).get("children", [])
        if not children:
            return None
        post = children[0]["data"]
        return {
            "subreddit": post.get("subreddit"),  # canonical case
            "first_post_title": post.get("title", "")[:80],
            "score": post.get("score"),
        }
    except Exception:
        return None


def find_subreddit(name: str) -> dict | None:
    for cand in subreddit_candidates(name):
        print(f"  trying r/{cand}...", file=sys.stderr)
        res = test_subreddit(cand)
        if res:
            return res
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="Show / book series name")
    ap.add_argument("--json", action="store_true", help="Output JSON only")
    args = ap.parse_args()

    print(f"Discovering '{args.name}'...", file=sys.stderr)

    fandom = find_fandom(args.name)
    subreddit = find_subreddit(args.name)

    result = {
        "show_name": args.name,
        "fandom": fandom,
        "subreddit": subreddit,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\nName: {args.name}")
        if fandom:
            print(f"Fandom: {fandom['api_url']} ({fandom['site_name']})")
        else:
            print("Fandom: NOT FOUND - try manual search")
        if subreddit:
            tag = subreddit.get("subscribers")
            tag = f"{tag} subs" if tag else f"top post {subreddit.get('score','?')} pts"
            print(f"Subreddit: r/{subreddit['subreddit']} ({tag})")
        else:
            print("Subreddit: NOT FOUND - try manual search")


if __name__ == "__main__":
    main()
