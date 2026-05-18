"""
Upload built source_pack/ to Google NotebookLM via notebooklm-py.

Prerequisites:
    pip install "notebooklm-py[browser]"
    playwright install chromium
    notebooklm login

Запуск:
    python import_to_notebooklm.py --pack source_pack/ --show "Severance" --scope full
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

try:
    from notebooklm import NotebookLMClient
except ImportError:
    print(
        "❌ notebooklm-py не установлен.\n"
        "Установи:\n"
        "  pip install 'notebooklm-py[browser]'\n"
        "  playwright install chromium\n"
        "  notebooklm login",
        file=sys.stderr,
    )
    sys.exit(1)


async def upload_pack(pack_dir: Path, show: str, scope: str) -> None:
    """Создать notebook в NotebookLM и залить source pack."""
    pack_files = sorted(p for p in pack_dir.glob("*.md") if not p.name.startswith("_"))
    if not pack_files:
        print(f"❌ Нет markdown файлов в {pack_dir}", file=sys.stderr)
        return

    notebook_title = f"LoreMap: {show} ({scope})"
    print(f"\n=== Creating NotebookLM notebook: '{notebook_title}' ===")

    async with await NotebookLMClient.from_storage() as client:
        nb = await client.notebooks.create(notebook_title)
        print(f"  Notebook created: id={nb.id}")
        notebook_url = f"https://notebooklm.google.com/notebook/{nb.id}"
        print(f"  URL: {notebook_url}\n")

        print(f"Uploading {len(pack_files)} sources...")
        for i, mdfile in enumerate(pack_files, 1):
            content = mdfile.read_text(encoding="utf-8")
            try:
                source = await client.sources.add_text(nb.id, title=mdfile.stem, content=content)
                print(f"  [{i}/{len(pack_files)}] {mdfile.name} ({len(content)} chars) -> {source.id if hasattr(source, 'id') else 'ok'}")
            except Exception as e:
                print(f"  ! [{i}/{len(pack_files)}] {mdfile.name}: {e}", file=sys.stderr)

        print(f"\n✓ Готово. Notebook URL:\n  {notebook_url}")
        print("\nДальше:")
        print(f"  - Открой URL в браузере и общайся с NotebookLM")
        print(f"  - Или через CLI: notebooklm chat ask {nb.id} 'твой вопрос'")
        print(f"  - Или сгенерируй бонусы:")
        print(f"      notebooklm audio create --notebook-id {nb.id}  # podcast")
        print(f"      notebooklm mindmap --notebook-id {nb.id}        # mind map")
        print(f"      notebooklm slide-deck --notebook-id {nb.id}     # PDF/PPTX")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True, help="path to source_pack/ directory")
    ap.add_argument("--show", required=True, help="Show name")
    ap.add_argument("--scope", default="full")
    args = ap.parse_args()

    pack_dir = Path(args.pack)
    if not pack_dir.exists():
        print(f"❌ {pack_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    asyncio.run(upload_pack(pack_dir, args.show, args.scope))


if __name__ == "__main__":
    main()
