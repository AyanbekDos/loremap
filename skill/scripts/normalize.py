"""
Универсальный нормализатор raw/ -> wiki/ по доменам.

Маршрутизация по полю type из frontmatter:
- character -> wiki/entities/
- monster | location | artifact | symbol -> wiki/concepts/
- episode -> wiki/episodes/
- person_real -> wiki/sources/people/
- theory (reddit) -> wiki/theories/
- redirect stub -> wiki/_redirects/
- unknown -> wiki/concepts/_unknown/

Также конвертирует /wiki/X markdown-ссылки в [[X]].

Запуск:
    python normalize.py --raw raw/ --wiki wiki/
    python normalize.py --raw raw/ --wiki wiki/ --dry-run
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

LINK_RE = re.compile(r'\[([^\]]+)\]\(/wiki/([^)\s"]+)(?:\s+"[^"]*")?\)')
CITE_RE = re.compile(r'\[\[\d+\]\]\(#cite[^)]*\)')
INLINE_CITE_RE = re.compile(r'\[[^\]]*\]\(#cite[^)]*\)')

CATEGORY_MAP = [
    (("Actors", "Actresses", "Cast", "Crew", "Directors", "Writers"), "person_real"),
    (("Episodes",), "episode"),
    (("Characters", "Townsfolk", "Newcomers", "Originals", "Visitors", "Protagonist", "Antagonist"), "character"),
    (("Monsters", "Creatures"), "monster"),
    (("Locations", "Places", "Buildings"), "location"),
    (("Objects", "Items", "Artifacts", "Talismans"), "artifact"),
    (("Symbols",), "symbol"),
]


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    return yaml.safe_load(text[4:end]) or {}, text[end + 5:]


def dump_frontmatter(front: dict) -> str:
    return "---\n" + yaml.safe_dump(front, allow_unicode=True, sort_keys=False).strip() + "\n---\n"


def reclassify(front: dict, body: str) -> str:
    snippet = body[:300].lower()
    if "redirect to:" in snippet and len(body) < 500:
        return "redirect"

    cats = [c.replace("_", " ") for c in (front.get("categories") or [])]
    for needles, t in CATEGORY_MAP:
        if any(any(n.lower() in c.lower() for n in needles) for c in cats):
            return t

    infobox = front.get("infobox") or {}
    if any(k in infobox for k in ("Actor", "Portrayed by", "Status", "Occupation", "Family")):
        return "character"

    return front.get("type", "unknown")


def convert_links(body: str) -> tuple[str, list[str]]:
    links: list[str] = []

    def repl(m: re.Match) -> str:
        title = m.group(1).strip()
        slug = m.group(2).replace("_", " ")
        canonical = slug if slug.lower() == title.lower().replace("_", " ") else title
        links.append(canonical)
        return f"[[{canonical}]]"

    body = LINK_RE.sub(repl, body)
    body = CITE_RE.sub("", body)
    body = INLINE_CITE_RE.sub("", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body, links


def normalize_fandom(raw_dir: Path, wiki_dir: Path, dry: bool) -> Counter:
    buckets = {
        "character": wiki_dir / "entities",
        "monster": wiki_dir / "concepts",
        "location": wiki_dir / "concepts",
        "artifact": wiki_dir / "concepts",
        "symbol": wiki_dir / "concepts",
        "episode": wiki_dir / "episodes",
        "person_real": wiki_dir / "sources" / "people",
        "redirect": wiki_dir / "_redirects",
        "unknown": wiki_dir / "concepts" / "_unknown",
    }
    counts: Counter = Counter()
    paths = sorted(p for p in (raw_dir / "fandom").glob("*.md") if not p.name.startswith("_"))

    for p in paths:
        text = p.read_text(encoding="utf-8")
        front, body = parse_frontmatter(text)
        if not front:
            continue

        page_type = reclassify(front, body)
        bucket = buckets.get(page_type, buckets["unknown"])
        bucket.mkdir(parents=True, exist_ok=True)

        body_new, links = convert_links(body)
        top_links = [k for k, _ in Counter(links).most_common(20)]

        front_new = {
            "title": front.get("title"),
            "type": page_type,
            "status": front.get("status", "canon"),
            "source": front.get("source"),
            "source_url": front.get("source_url"),
            "scraped_at": front.get("scraped_at"),
            "updated": date.today().isoformat(),
            "categories": front.get("categories", []),
            "infobox": front.get("infobox", {}),
            "links": [f"[[{l}]]" for l in top_links],
        }
        md = dump_frontmatter(front_new) + "\n" + body_new.strip() + "\n"
        out = bucket / p.name
        if not dry:
            out.write_text(md, encoding="utf-8")
        counts[page_type] += 1
    return counts


def normalize_reddit(raw_dir: Path, wiki_dir: Path, dry: bool) -> Counter:
    out_dir = wiki_dir / "theories"
    out_dir.mkdir(parents=True, exist_ok=True)
    counts: Counter = Counter()
    reddit_dir = raw_dir / "reddit"
    if not reddit_dir.exists():
        return counts

    THEORY_FLAIRS = ("theory", "speculation", "spoiler theory", "discussion", "opinion")

    for sub_dir in sorted(p for p in reddit_dir.iterdir() if p.is_dir()):
        for path in sorted(sub_dir.glob("*.md")):
            if path.name.startswith("_"):
                continue
            text = path.read_text(encoding="utf-8")
            front, body = parse_frontmatter(text)
            if not front:
                continue
            flair = (front.get("flair") or "").lower()
            score = front.get("score", 0)
            if not any(f in flair for f in THEORY_FLAIRS):
                continue
            if score < 50:
                continue
            self_text = body.split("## Top comments", 1)[0] if "## Top comments" in body else body
            self_text = re.sub(r"^# .+\n", "", self_text, count=1).strip()
            if len(self_text) < 200:
                continue

            front_new = {
                "title": front.get("title"),
                "type": "theory",
                "status": "fan_theory",
                "source": "reddit",
                "subreddit": front.get("subreddit"),
                "source_url": front.get("source_url"),
                "score": score,
                "num_comments": front.get("num_comments"),
                "flair": front.get("flair"),
                "author": front.get("author"),
                "created": front.get("created"),
                "updated": date.today().isoformat(),
            }
            out = out_dir / f"{sub_dir.name.lower()}-{front.get('post_id')}.md"
            if not dry:
                out.write_text(dump_frontmatter(front_new) + "\n" + body, encoding="utf-8")
            counts["theory"] += 1
    return counts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--wiki", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    raw = Path(args.raw)
    wiki = Path(args.wiki)
    wiki.mkdir(parents=True, exist_ok=True)

    fandom_counts = normalize_fandom(raw, wiki, args.dry_run)
    reddit_counts = normalize_reddit(raw, wiki, args.dry_run)

    print("\nFandom итоги по типам:")
    for t, n in sorted(fandom_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {t:14} {n}")
    print("\nReddit итоги:")
    for t, n in sorted(reddit_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {t:14} {n}")


if __name__ == "__main__":
    main()
