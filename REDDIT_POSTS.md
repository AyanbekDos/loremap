# LoreMap - Reddit posts drafts

Подготовленные посты для разных subreddits. Адаптировать под язык и тон.

---

## Version A: r/FromTVEpix (target: FROM fans)

**Title:** I built an AI that mapped every mystery in FROM and asked it to predict who Boy in White is

**Body:**

A few weeks of work later: I parsed every page on from.fandom.com (238 entities/concepts/episodes) + 200 top theories from this sub + interview quotes from Griffin and the cast. Threw it all into an LLM-managed wiki structured by canon vs fan_theory vs speculation. Built a mystery graph with 17 nodes (BIW, MIY, Township, Children, Bottle Trees, Faraway, Talismans, Symbol, Creatures, Music Box, Lighthouse, Victor, Tabitha, Miranda, Fatima/baby, Boyd, Jade) and 49 canon-evidence edges between them.

Then I asked Claude (Opus 4.7) to predict who Boy in White is. Here's the kicker - I also spawned a second AI agent whose ONLY job was to attack the prediction. Find canon facts the theory ignores. Find logical leaps. Suggest a better alternative.

**Result:**

Initial prediction by Claude: "BIW is a manifestation of the collective HOPE of the ritually murdered children." Sounds nice, right? canon_support: 8/10.

Adversarial review tore it apart:
- BIW is explicitly marked "Status: Undead" in canon. Hope manifestations aren't undead.
- BIW needs Christopher to physically cross the Bottle Tree to free the children. If he's the avatar of the system, why does he need humans?
- BIW first appears triggered by "two cars arriving same day" not by the original ritual.
- BIW + dog combo never explained by theory.

Critic's stronger alternative: BIW is a SEPARATE undead entity, a child from an early cycle of Township, who has partial knowledge of the rules and limited ability to guide newcomers. Not an avatar - just an old prisoner showing the new ones around.

Adjusted scoring: canon_support 5/10 (not 8). Verdict: REVISE.

**That's the cool part - AI vs AI catching its own hallucinations.**

I open-sourced the whole thing as a Claude Code skill called LoreMap. Works on any mystery show with a fan wiki + active subreddit. Severance, Yellowjackets, Lost, Twin Peaks - all in scope.

GitHub: https://github.com/AyanbekDos/loremap

You give it a show name. It does the rest. No API keys, runs inside your Claude Code session.

Would love to see what theories you'd get if you ran it on YOUR favorite mystery shows.

P.S. - waiting for S4E6 May 24 to validate predictions. If LoreMap turns out to actually predict episodes accurately, that's the next big experiment.

---

## Version B: r/ClaudeAI / r/PromptEngineering (target: AI builders)

**Title:** Open-source Claude Code skill that builds AI knowledge bases for any TV show or book series in 1 evening

**Body:**

Built and released LoreMap - a Claude Code skill that automates the "I want to predict the ending of [show]" workflow.

**What it does:**

1. User says show name (e.g. "Severance")
2. Skill auto-discovers fandom URL + subreddit
3. Scrapes ~500 wiki pages via MediaWiki API + 200 top reddit theories
4. Normalizes into memoriki-style structure (LLM Wiki pattern by Karpathy):

```
project/
├── raw/                    Immutable sources
├── wiki/                   Claude normalizes + owns
│   ├── entities/           Characters (status: canon)
│   ├── concepts/           Places, objects, symbols
│   ├── theories/           Fan theories (status: fan_theory)
│   └── synthesis/
│       ├── mystery_graph.yaml  Canon-evidence graph
│       └── predictions/        Locked predictions
└── CLAUDE.md               Rules for sessions
```

5. Claude (Opus in the session, no external API) builds a mystery graph by reading the wiki
6. User asks for a theory about anything
7. Claude generates prediction with 5-axis scoring (canon_support, contradiction_count, explanatory_power, simplicity, creator_plausibility)
8. **Spawns a subagent (via Agent tool) with the opposite goal: find holes**
9. Final synthesis records both perspectives with git commit hash for verifiability

**Why interesting:**

- No external API keys. Uses Claude Code session capabilities directly.
- Status-tagged knowledge prevents canon/theory mixing (big LLM failure mode)
- 8 documented anti-patterns from real LLM errors I caught during dev: temporal compression, hallucination POV confusion, scene boundary contamination, mentioned-vs-present, single-key fallacy, etc.
- Adversarial review catches AI hallucinations BY ANOTHER AI

**Architecture explained:**

The key insight: a single LLM prediction is just sophisticated guessing. Two LLMs with opposing goals (one builds, one attacks) caught real errors in my FROM showcase - the first prediction had canon_support 8/10 by its own scoring, after adversarial review it dropped to 5/10 with 3 specific contradictions cited.

**Repo:** https://github.com/AyanbekDos/loremap

MIT licensed. Cloning + installing as skill is one command. Showcase on FROM (MGM+) included.

If you build something on top of it, let me know.

---

## Version C: r/LocalLLaMA (target: technical)

**Title:** [Project] Adversarial LLM-as-a-Judge applied to fan theory prediction - open source

**Body:**

Tested an architecture I've been thinking about: use a second LLM specifically as an adversarial critic of a first LLM's prediction. Not just "verify this" but "find ways this is wrong."

Domain: mystery TV show fan theories. Test target: FROM (MGM+ sci-fi horror).

**Pipeline:**

1. Build structured wiki from fan sources (fandom MediaWiki API + Reddit top posts)
2. Status-tag every claim: `canon | fan_theory | speculation`
3. Build mystery graph with canon-evidence edges (17 nodes, 49 edges for FROM)
4. Generate prediction (Claude Opus): "Who is Boy in White?"
5. **Adversarial pass: spawn separate agent with explicit goal of finding holes**
6. Synthesize what survives

**Findings:**

The adversarial step found 7 specific canon contradictions and 4 logical leaps the first model missed in its own prediction. Notable patterns the adversarial agent reliably catches:

- "Theory ignores explicit canon flag" (Boy in White marked Undead, theory treated as Living)
- "Correlation interpreted as causation" (BIW appears near events != BIW controls events)
- "Single-key fallacy" (theory explains too much with one mechanism)
- "Creator-lied escape hatch" (theory requires creators to be deceiving us)

I documented 8 such anti-patterns and built them into the skill as prevention rules.

**Why this works:**

When you ask the same LLM to "verify this", it just confirms. When you ask a different LLM (or even the same one with the opposite instruction) to "attack this", it actually finds problems. Like a small-scale GAN.

**Code:** https://github.com/AyanbekDos/loremap

Works as a Claude Code skill. Run it on any fandom + subreddit. Test cases included.

Would be interesting to evaluate adversarial-LLM-as-judge on other domains - code review, scientific claims, legal analysis. Open to collaborations.

---

## Pre-post checklist

- [ ] Wait for FROM S4E6 release 24 May - get one validated prediction first for stronger Reddit hook ("AI predicted X, episode confirmed Y")
- [ ] Add 1-2 screenshots / GIFs to repo README for visual proof
- [ ] Consider creating a YouTube demo video (record terminal session)
- [ ] Tweet from @aianback_ X handle linking to repo
- [ ] Add second showcase (e.g. Severance) to repo

## Timing strategy

Best Reddit post moment = right after S4E6 airs (May 24). We post:
- "AI predicted these 4 things about S4E6 a week before release. 3 came true. Here's the prediction file with git commit hash from May 18."

That's a much stronger hook than "I built this thing."
