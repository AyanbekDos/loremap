"""
Build NotebookLM-ready source pack from scraped raw/ directory.

Bundles 500+ raw fandom/reddit pages into ~10 curated Markdown files с жёсткими
SOURCE_CLASS labels, чтобы NotebookLM не смешивал канон с теориями.

Запуск:
    python build_source_pack.py --raw raw/ --output source_pack/ --scope full
    python build_source_pack.py --raw raw/ --output source_pack/ --scope s1-only
    python build_source_pack.py --raw raw/ --output source_pack/ --scope theories-only
"""
from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

import yaml


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    return yaml.safe_load(text[4:end]) or {}, text[end + 5:]


def strict_label(source_class: str, scope: str, spoiler_level: str, reading_priority: int, instructions: str) -> str:
    return (
        f"---\n"
        f"source_class: {source_class}\n"
        f"scope: {scope}\n"
        f"spoiler_level: {spoiler_level}\n"
        f"reading_priority: {reading_priority}\n"
        f"generated_at: {date.today().isoformat()}\n"
        f"---\n\n"
        f"⚠️ **SOURCE CLASS: {source_class}**\n\n"
        f"{instructions}\n\n"
        f"---\n\n"
    )


def episode_season(text: str, fm: dict) -> int | None:
    """Try to extract season number from episode page content."""
    m = re.search(r"Season:?\s*['\"]?(\d+)", text[:2000])
    if m:
        return int(m.group(1))
    m = re.search(r"\bSeason\s+(\d+)\b", text[:2000])
    if m:
        return int(m.group(1))
    inf = fm.get("infobox") or {}
    if isinstance(inf, dict):
        s = inf.get("Season")
        if s and isinstance(s, str):
            m = re.search(r"\d+", s)
            if m:
                return int(m.group(0))
    return None


def collect_by_type(raw_dir: Path) -> dict[str, list[Path]]:
    """Группируем raw/fandom/*.md по type из frontmatter."""
    buckets: dict[str, list[Path]] = {
        "character": [],
        "monster": [],
        "location": [],
        "artifact": [],
        "symbol": [],
        "episode": [],
        "event": [],
        "person_real": [],
        "unknown": [],
    }
    fandom_dir = raw_dir / "fandom"
    if not fandom_dir.exists():
        return buckets
    for p in sorted(fandom_dir.glob("*.md")):
        if p.name.startswith("_"):
            continue
        text = p.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        t = fm.get("type", "unknown")
        buckets.setdefault(t, []).append(p)
    return buckets


def collect_reddit(raw_dir: Path) -> list[tuple[Path, dict, str]]:
    """Возвращает [(path, frontmatter, body)] reddit постов."""
    out = []
    reddit_dir = raw_dir / "reddit"
    if not reddit_dir.exists():
        return out
    for sub_dir in sorted(p for p in reddit_dir.iterdir() if p.is_dir()):
        for p in sorted(sub_dir.glob("*.md")):
            if p.name.startswith("_"):
                continue
            text = p.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            if fm:
                out.append((p, fm, body))
    return out


def build_bundle(pages: list[Path], section_title: str, max_chars_per_page: int = 4000) -> str:
    """Конкатенирует несколько страниц в один markdown bundle."""
    out = [f"# {section_title}\n"]
    for p in pages:
        text = p.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        title = fm.get("title") or p.stem
        source_url = fm.get("source_url", "")
        body_trimmed = body.strip()[:max_chars_per_page]
        out.append(f"\n## {title}\n\n")
        if source_url:
            out.append(f"Source: {source_url}\n\n")
        out.append(body_trimmed)
        out.append("\n\n---\n")
    return "\n".join(out)


def build_episodes_bundle(episodes: list[Path], season_filter: int | None = None) -> tuple[str, dict[int, list[Path]]]:
    """Возвращает (bundle text, episodes_by_season)."""
    by_season: dict[int, list[Path]] = {}
    for p in episodes:
        text = p.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        s = episode_season(text, fm)
        if s is None:
            continue
        by_season.setdefault(s, []).append(p)

    if season_filter is not None:
        eps = by_season.get(season_filter, [])
        return build_bundle(eps, f"Season {season_filter} Episodes"), {season_filter: eps}
    return "", by_season


def filter_reddit(reddit: list, min_score: int = 500, flair_hint: list[str] | None = None) -> list:
    flair_hint = flair_hint or ["theory", "speculation", "discussion", "opinion"]
    out = []
    for p, fm, body in reddit:
        flair = (fm.get("flair") or "").lower()
        score = fm.get("score", 0) or 0
        if score < min_score:
            continue
        if flair_hint and not any(f in flair for f in flair_hint):
            continue
        out.append((p, fm, body))
    return out


def build_reddit_bundle(items: list, title: str, max_per_post: int = 2500) -> str:
    out = [f"# {title}\n"]
    for p, fm, body in items[:80]:  # cap 80 posts per bundle
        post_title = fm.get("title") or p.stem
        score = fm.get("score", 0)
        author = fm.get("author")
        url = fm.get("source_url", "")
        out.append(f"\n## {post_title}\n\n")
        out.append(f"_score: {score}, author: {author}_\n")
        if url:
            out.append(f"\nSource: {url}\n")
        out.append("\n" + body.strip()[:max_per_post])
        out.append("\n\n---\n")
    return "\n".join(out)


def build_manifest(scope: str, show_name: str, files: list[str]) -> str:
    files_lines = "\n".join(f"- `{f}`" for f in files)
    return f"""---
source_class: MANIFEST
scope: {scope}
generated_at: {date.today().isoformat()}
---

# LoreMap Source Pack: {show_name}

## Scope: {scope}

{"- Full canon + theories + interpretations" if scope == "full" else f"- {scope}"}

## Reading Order (приоритет источников)

В этом source pack строгая иерархия:

1. **CREATOR_QUOTE** (наивысший trust) - прямые цитаты шоураннеров/создателей
2. **CANON** - подтверждённые события из эпизодов
3. **FANDOM_INTERPRETATION** - wiki-страницы с интерпретациями (не канон, помечено)
4. **REDDIT_THEORY_HIGH** - топ-теории фанов (упомянуты как теории, не факты)
5. **REDDIT_THEORY_LOW** - менее проверенные теории

## Files

{files_lines}

## INSTRUCTIONS FOR AI (читай внимательно)

1. CANON и REDDIT_THEORY - разные классы источников. НЕ смешивай.
2. Если утверждение есть только в REDDIT_THEORY - всегда говори "Один из топ-фанатских теорий предполагает..." а не "Это так".
3. Если canon противоречит fan theory - говори об этом прямо.
4. Spoiler scope этого notebook'а: **{scope}**. Не упоминай события вне scope.
5. Inline citations обязательны для каждого утверждения.
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="path to raw/ directory")
    ap.add_argument("--output", required=True, help="path to source_pack/ output directory")
    ap.add_argument("--show", required=True, help="Show name (e.g. 'Severance')")
    ap.add_argument("--scope", default="full", choices=["full", "s1-only", "s1-s2", "theories-only", "characters"])
    args = ap.parse_args()

    raw = Path(args.raw)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    print(f"Building source pack for '{args.show}' (scope: {args.scope})...")

    buckets = collect_by_type(raw)
    reddit_all = collect_reddit(raw)

    files_created = []

    # 01 CHARACTERS
    if buckets.get("character"):
        chars_md = strict_label(
            "CANON",
            args.scope,
            args.scope,
            1,
            "Canon character information from the show. Treat as confirmed unless explicitly noted otherwise.",
        )
        chars_md += build_bundle(buckets["character"], "Canon Characters")
        p = out / "01_CANON_CHARACTERS.md"
        p.write_text(chars_md, encoding="utf-8")
        files_created.append(p.name)
        print(f"  {p.name}: {len(buckets['character'])} characters")

    # 02 LOCATIONS + CONCEPTS
    location_pages = buckets.get("location", []) + buckets.get("symbol", []) + buckets.get("monster", []) + buckets.get("artifact", [])
    if location_pages:
        md = strict_label(
            "CANON",
            args.scope,
            args.scope,
            1,
            "Canon locations, monsters, symbols, artifacts. Treat as confirmed.",
        )
        md += build_bundle(location_pages, "Canon Locations / Symbols / Monsters / Artifacts")
        p = out / "02_CANON_LOCATIONS_AND_OBJECTS.md"
        p.write_text(md, encoding="utf-8")
        files_created.append(p.name)
        print(f"  {p.name}: {len(location_pages)} entries")

    # 03+ EPISODES by season (или filtered по scope)
    episodes = buckets.get("episode", [])
    _, by_season = build_episodes_bundle(episodes)
    season_filter = None
    if args.scope == "s1-only":
        season_filter = 1
    elif args.scope == "s1-s2":
        season_filter = None  # обработаем ниже

    for s, eps in sorted(by_season.items()):
        if args.scope == "s1-only" and s != 1:
            continue
        if args.scope == "s1-s2" and s > 2:
            continue
        md = strict_label(
            "CANON",
            args.scope,
            f"safe-to-s{s}",
            2,
            f"Canon episode recaps Season {s}. Each recap is a synthesis from fandom-wiki, not 100% verbatim transcript.",
        )
        md += build_bundle(eps, f"Season {s} Episodes")
        p = out / f"0{3+s}_CANON_EPISODES_S{s}.md"
        p.write_text(md, encoding="utf-8")
        files_created.append(p.name)
        print(f"  {p.name}: {len(eps)} episodes")

    # 07 REDDIT THEORIES HIGH (score >= 1000, theory flairs)
    if args.scope != "s1-only":  # spoiler-safe не включает теории
        high_theories = filter_reddit(reddit_all, min_score=1000, flair_hint=["theory", "speculation"])
        if high_theories:
            md = strict_label(
                "REDDIT_THEORY",
                args.scope,
                "theories-may-contain-spoilers",
                4,
                "FAN SPECULATION ONLY. These are popular fan theories from Reddit. Score >= 1000. Do NOT present these as canon facts. Always say 'One popular fan theory suggests...' or similar.",
            )
            md += build_reddit_bundle(high_theories, "Top Reddit Theories (score >= 1000)")
            p = out / "07_REDDIT_THEORIES_HIGH.md"
            p.write_text(md, encoding="utf-8")
            files_created.append(p.name)
            print(f"  {p.name}: {len(high_theories)} theories")

        # 08 REDDIT THEORIES LOW + opinions
        low_theories = filter_reddit(reddit_all, min_score=100, flair_hint=["theory", "speculation", "discussion", "opinion"])
        low_theories = [t for t in low_theories if t not in high_theories]
        if low_theories:
            md = strict_label(
                "REDDIT_THEORY",
                args.scope,
                "theories-may-contain-spoilers",
                5,
                "FAN SPECULATION (lower signal). Score 100-1000. Even more cautious treatment.",
            )
            md += build_reddit_bundle(low_theories, "Reddit Theories Mid-Tier (score 100-1000)")
            p = out / "08_REDDIT_THEORIES_LOW.md"
            p.write_text(md, encoding="utf-8")
            files_created.append(p.name)
            print(f"  {p.name}: {len(low_theories)} theories")

    # 09 INTERVIEWS (creator quotes)
    interviews_dir = raw / "interviews"
    if interviews_dir.exists():
        md = strict_label(
            "CREATOR_QUOTE",
            args.scope,
            "may-contain-spoilers",
            1,
            "DIRECT QUOTES FROM CREATORS / CAST / WRITERS. Highest trust tier. Treat as canonical authorial statement.",
        )
        md += "# Creator and Cast Interviews\n\n"
        for p in sorted(interviews_dir.glob("*.md")):
            if p.name.startswith("_"):
                continue
            md += "\n" + p.read_text(encoding="utf-8") + "\n\n---\n"
        out_path = out / "09_CREATOR_INTERVIEWS.md"
        out_path.write_text(md, encoding="utf-8")
        files_created.append(out_path.name)
        print(f"  {out_path.name}")

    # 00 MANIFEST
    manifest = build_manifest(args.scope, args.show, sorted(files_created))
    (out / "00_MANIFEST.md").write_text(manifest, encoding="utf-8")
    files_created = ["00_MANIFEST.md"] + files_created
    print(f"\nTotal files: {len(files_created)}")
    print(f"Output: {out.absolute()}")


if __name__ == "__main__":
    main()
