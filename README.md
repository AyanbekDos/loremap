# LoreMap

> **Just finished an episode and need someone smarter than your group chat to dissect it with you?**
> **Have a wild new theory about FROM? Severance? Yellowjackets?**
> **Lost track of how many wives the Sultan had in Magnificent Century?**
>
> Install LoreMap. Chill. Talk to an AI that actually knows your show.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is this

A Claude Code skill that turns any TV show or book series into a personal AI expert in 5 minutes.

You drop a show name. LoreMap goes off, scrapes the fan wiki, scrapes Reddit theories, packages everything into a clean source pack with hard separation of canon vs fan speculation, then uploads it to Google NotebookLM.

Now you have:

- A **source-grounded AI chat** that won't hallucinate (NotebookLM only answers from your sources, with inline citations)
- An **AI-generated podcast about your show** (NotebookLM's Audio Overview, ~15 min MP3)
- A **mind map** of the show's lore
- **Slide decks**, **quizzes**, **briefing docs** ... all free

Free. Runs on your Claude Code subscription. No paid APIs.

## TL;DR usage

In Claude Code, type:

```
LoreMap for Severance
```

Five minutes later you have a NotebookLM notebook with a 15-minute audio podcast about Severance and an AI that knows every fan theory from r/SeveranceAppleTVPlus.

## Why this matters

Generic LLMs hallucinate when you ask them about TV shows. They mix canon with fan theories. They confuse a character's hallucination with what actually happened on screen. They claim someone was in a scene when they were only mentioned.

Real fans spot this in 5 seconds and lose trust.

LoreMap fixes that the right way: it doesn't try to build its own RAG (which would still hallucinate). It does the boring but critical work, prepares clean, separated, properly labeled source material, and hands it to Google's NotebookLM, which is source-grounded by design.

## Install

```bash
# 1. Clone
git clone https://github.com/AyanbekDos/loremap.git ~/projects/loremap

# 2. Install as Claude Code skill
mkdir -p ~/.claude/skills/
cp -r ~/projects/loremap/skill ~/.claude/skills/loremap

# 3. Python deps for scraping
cd ~/projects/loremap
python3 -m venv .venv
source .venv/bin/activate
pip install httpx beautifulsoup4 lxml pyyaml markdownify tenacity

# 4. notebooklm-py for Google NotebookLM uploads (free)
pip install "notebooklm-py[browser]"
playwright install chromium
notebooklm login   # opens browser, one-time Google sign-in
notebooklm auth check --test --json   # verify
```

Then in Claude Code: `LoreMap for <show name>` and go.

## How it works

```
user: "LoreMap for Severance"
         |
         v
Claude Code skill:
  - discover.py        finds fandom wiki + subreddit by show name
  - scrape_fandom.py   grabs all wiki pages via MediaWiki API
  - scrape_reddit.py   grabs top theories from the subreddit
  - build_source_pack.py
       bundles into ~10 markdown files with STRICT SOURCE_CLASS labels:
       - 01_CANON_CHARACTERS.md
       - 02_CANON_LOCATIONS_AND_OBJECTS.md
       - 03+_CANON_EPISODES_S1.md, S2.md, ...
       - 07_REDDIT_THEORIES_HIGH.md      (fan speculation, NOT canon)
       - 08_REDDIT_THEORIES_LOW.md
       - 09_CREATOR_INTERVIEWS.md
       Each file starts with a STRICT instruction so NotebookLM won't mix sources.
  - import_to_notebooklm.py
       creates a NotebookLM notebook, uploads the source pack.
         |
         v
Output: https://notebooklm.google.com/notebook/<id>
You chat with NotebookLM (web or app), generate audio podcast, mind map, etc.
```

## Scopes - different shapes for different shows

```bash
--scope full           Full canon + theories
--scope s1-only        Spoiler-safe Season 1 only (perfect for catch-up)
--scope s1-s2          Canon through Season 2
--scope theories-only  Curated fan theories only
--scope characters     Per-character deep dive
```

So your friend who's only on Season 1 doesn't get spoiled.

## Source separation: the actual moat

LoreMap doesn't dump 500 raw fandom pages into NotebookLM. That would be a mess and would hit the 50-sources-per-notebook limit.

Instead it bundles them into ~10 thematic files, each with a hard label at the top:

```markdown
WARNING - SOURCE CLASS: REDDIT_THEORY
This document contains fan speculation, NOT canon.
Do NOT present claims from this document as confirmed events.
```

NotebookLM reads this and respects it. You get answers like:

> "According to one popular Reddit theory (~1200 upvotes), the Boy in White is a manifestation of the children's collective hope. However, canon material only confirms that he appears to specific people and seems to guide them through the Faraway Trees."

Not:

> "The Boy in White is..."

That's the difference between fans trusting your tool and fans laughing at it.

## Bonus: viral artifacts NotebookLM gives you for free

Once your notebook is loaded, NotebookLM can generate:

- **Audio Overview** ... a 15-minute AI podcast about your show. Yes, it's as good as you've heard. MP3 download.
- **Mind Map** ... interactive hierarchical visualization
- **Slide Deck** ... PDF or PPTX
- **Quizzes** ... "Are you a Severance MDR-level expert?"
- **Briefing Doc** ... written overview

All free. All grounded in the source pack you uploaded.

## What LoreMap is NOT

- It's not its own RAG / vector store. NotebookLM handles that.
- It's not a finale predictor. NotebookLM grounds answers in source material; it doesn't speculate. (Though you can ask it to summarize popular fan theories.)
- It doesn't transcribe video. Text sources only (wiki + Reddit + creator interviews).
- It doesn't store full episode transcripts. Only fair-use excerpts and summaries from fan wikis.

## The honest risk

[notebooklm-py](https://github.com/teng-lin/notebooklm-py) is an *unofficial* Python client for NotebookLM. Google can break it any time. If they do, LoreMap will need an update.

We accept that trade-off. The win, a grounded chat experience with a free AI podcast, is worth it.

## Tested on

- FROM (MGM+/Epix) ... 238 wiki pages, 200 Reddit theories
- Nu, Pogodi! (Soviet cartoon) ... 91 wiki pages, 10 Reddit posts (small fandom, still works)

Coming up: Severance, Yellowjackets, A Song of Ice and Fire.

## Examples folder

In `examples/` you'll find pre-built source packs for shows we tested. You can paste these directly into NotebookLM if you don't want to install anything yet.

## License

MIT. Use it, fork it, sell it. Doesn't store full subtitles or copyrighted transcripts, only public fan wikis and Reddit posts.

## Credits

- **Concept**: [Aianbek Dossumbayev](https://github.com/AyanbekDos)
- **Built with**: Claude Code (Claude Opus 4.7)
- **Powered by**: [notebooklm-py](https://github.com/teng-lin/notebooklm-py) by Teng Lin, [NotebookLM](https://notebooklm.google.com) by Google
- **Architectural inspiration**: [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) by Andrej Karpathy
