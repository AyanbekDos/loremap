"""
Универсальный скрапер reddit топ-постов любого subreddit.

Использует публичный JSON-эндпоинт, без OAuth.

Запуск:
    python scrape_reddit.py --subreddit FromTVEpix --output raw/reddit/FromTVEpix/
    python scrape_reddit.py --subreddit asoiaf --posts-limit 200 --output raw/reddit/asoiaf/
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
import yaml
from tenacity import retry, stop_after_attempt, wait_exponential

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
    timeout=httpx.Timeout(45.0),
    follow_redirects=True,
    http2=False,
)


@retry(stop=stop_after_attempt(4), wait=wait_exponential(min=2, max=20))
def get_json(url: str, params: dict | None = None) -> dict:
    r = CLIENT.get(url, params=params)
    if r.status_code != 200:
        print(f"  ! HTTP {r.status_code}: {r.text[:200]}", file=sys.stderr)
    r.raise_for_status()
    return r.json()


def list_top_posts(sub: str, limit: int) -> list[dict]:
    posts: list[dict] = []
    after: str | None = None
    while len(posts) < limit:
        params = {"t": "all", "limit": min(100, limit - len(posts))}
        if after:
            params["after"] = after
        data = get_json(f"https://www.reddit.com/r/{sub}/top.json", params=params)
        children = data.get("data", {}).get("children", [])
        if not children:
            break
        for c in children:
            posts.append(c["data"])
        after = data.get("data", {}).get("after")
        if not after:
            break
        time.sleep(1.5)
    return posts[:limit]


def fetch_comments(permalink: str, limit: int) -> list[dict]:
    url = f"https://www.reddit.com{permalink}.json"
    try:
        data = get_json(url, params={"limit": limit, "sort": "top", "depth": 1})
    except Exception as e:
        return []
    if not isinstance(data, list) or len(data) < 2:
        return []
    comments = []
    for c in data[1].get("data", {}).get("children", []):
        cd = c.get("data", {})
        if cd.get("body") and cd.get("body") != "[deleted]":
            comments.append({
                "author": cd.get("author"),
                "score": cd.get("score", 0),
                "body": cd["body"],
                "created_utc": cd.get("created_utc"),
            })
        if len(comments) >= limit:
            break
    return comments


def post_to_md(sub: str, post: dict, comments: list[dict]) -> tuple[str, str]:
    created = datetime.fromtimestamp(post["created_utc"], tz=timezone.utc).isoformat()
    flair = post.get("link_flair_text", "") or ""

    front = {
        "title": post["title"],
        "post_id": post["id"],
        "subreddit": sub,
        "type": "theory" if "theor" in flair.lower() else "discussion",
        "status": "fan_theory",
        "flair": flair,
        "score": post.get("score", 0),
        "num_comments": post.get("num_comments", 0),
        "author": post.get("author"),
        "created": created,
        "source": "reddit",
        "source_url": f"https://www.reddit.com{post['permalink']}",
        "scraped_at": datetime.now(timezone.utc).date().isoformat(),
    }
    fm = yaml.safe_dump(front, allow_unicode=True, sort_keys=False).strip()

    body = post.get("selftext", "").strip() or "(no text - link or image post)"
    md_parts = [f"---\n{fm}\n---\n\n# {post['title']}\n\n{body}\n"]

    if comments:
        md_parts.append("\n## Top comments\n")
        for c in comments:
            md_parts.append(
                f"\n### {c.get('author')} ({c.get('score')} pts)\n\n{c.get('body','').strip()}\n"
            )
    return post["id"], "".join(md_parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subreddit", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--posts-limit", type=int, default=100)
    ap.add_argument("--comments-limit", type=int, default=15)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    print(f"\n=== r/{args.subreddit} ===", flush=True)
    try:
        posts = list_top_posts(args.subreddit, args.posts_limit)
    except Exception as e:
        print(f"!! list error: {e}", file=sys.stderr)
        return
    print(f"  получено {len(posts)} постов", flush=True)

    out.joinpath("_index.json").write_text(
        json.dumps([{"id": p["id"], "title": p["title"], "score": p.get("score", 0)} for p in posts],
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    saved = skipped = failed = 0
    for i, p in enumerate(posts, 1):
        out_path = out / f"{p['id']}.md"
        if args.resume and out_path.exists():
            skipped += 1
            continue
        try:
            comments = fetch_comments(p["permalink"], args.comments_limit)
            pid, md = post_to_md(args.subreddit, p, comments)
            out_path.write_text(md, encoding="utf-8")
            saved += 1
            if i % 10 == 0 or i == len(posts):
                print(f"  [{i}/{len(posts)}] saved={saved} skipped={skipped} failed={failed}", flush=True)
            time.sleep(1.2)
        except Exception as e:
            failed += 1
            print(f"  ! {p['id']}: {e}", file=sys.stderr)

    print(f"\nГотово. saved={saved}, skipped={skipped}, failed={failed}")


if __name__ == "__main__":
    main()
