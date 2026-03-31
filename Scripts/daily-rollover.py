#!/usr/bin/env python3
"""
daily-rollover.py — Morning startup script for daily notes.

1. Creates today's daily note from the template if it doesn't exist.
2. Moves incomplete tasks from yesterday's note into today's matching sections:
     🎯 Today   → 🎯 Today
     ⏫ Next Up  → ⏫ Next Up
     🔽 Low Pri  → 🔽 Low Pri
   Completed tasks stay in yesterday's note as a record.

Usage:
    python3 ~/Morebrentbrain/Scripts/daily-rollover.py
"""

import sys
import re
from datetime import date, timedelta
from pathlib import Path

VAULT = Path(__file__).parent.parent
DAILY = VAULT / "Daily"
TEMPLATE = VAULT / "Templates" / "Daily Note.md"

TODAY = date.today()
YESTERDAY = TODAY - timedelta(days=1)

def archive_path(d: date) -> Path:
    """Path where a past note should be archived: Daily/YYYY/MM/YYYY-MM-DD.md"""
    folder = DAILY / str(d.year) / f"{d.month:02d}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{d}.md"

# Today's note always lives at the Daily root for easy access
today_file = DAILY / f"{TODAY}.md"

# Yesterday's note: check root first, then archive location
yesterday_root = DAILY / f"{YESTERDAY}.md"
yesterday_archive = archive_path(YESTERDAY)
yesterday_file = yesterday_root if yesterday_root.exists() else yesterday_archive

# Sections to roll over, in the order they appear in the note
ROLLOVER_SECTIONS = ["🎯 Today", "⏫ Next Up", "🔽 Low Pri"]

# ── Step 1: Create today's note from template if needed ──────────────────────

def render_template(template_path: Path, for_date: date) -> str:
    """Resolve Templater date expressions in the daily note template."""
    # Order matters: longer tokens must be replaced before shorter ones
    # (e.g. MMMM before MM, dddd before DD before D).
    FORMAT_MAP = {
        "dddd": "%A",
        "MMMM": "%B",
        "YYYY": "%Y",
        "MM":   "%m",
        "DD":   "%d",
        "D":    "%-d",   # day without leading zero (macOS/Linux)
    }

    def convert_format(tp_fmt: str) -> str:
        result = tp_fmt
        for tp_token, py_token in FORMAT_MAP.items():
            result = result.replace(tp_token, py_token)
        return result

    def resolve_tp_date(match):
        args = match.group(1).strip()
        fmt_match = re.match(r'"([^"]+)"(?:\s*,\s*(-?\d+))?', args)
        if not fmt_match:
            return match.group(0)
        fmt = convert_format(fmt_match.group(1))
        offset_days = int(fmt_match.group(2)) if fmt_match.group(2) else 0
        target = for_date + timedelta(days=offset_days)
        return target.strftime(fmt)

    text = template_path.read_text(encoding="utf-8")
    text = re.sub(r"<%\s*tp\.date\.now\(([^)]+)\)\s*%>", resolve_tp_date, text)
    return text

if not today_file.exists():
    if not TEMPLATE.exists():
        print(f"Template not found: {TEMPLATE}")
        sys.exit(1)
    today_file.write_text(render_template(TEMPLATE, TODAY), encoding="utf-8")
    print(f"Created {today_file.name}")

# ── Step 1b: Archive yesterday's note if it's still at root ─────────────────

if yesterday_root.exists():
    yesterday_root.rename(yesterday_archive)
    yesterday_file = yesterday_archive
    print(f"Archived {yesterday_root.name} → Daily/{YESTERDAY.year}/{YESTERDAY.month:02d}/")

# ── Step 2: Roll over incomplete tasks ───────────────────────────────────────

if not yesterday_file.exists():
    print(f"No yesterday's note found ({yesterday_file.name}) — skipping rollover.")
    sys.exit(0)

def parse_sections(text):
    """Split note text into [(heading_line, [body_lines]), ...]."""
    sections = []
    current_heading = None
    current_body = []
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            sections.append((current_heading, current_body))
            current_heading = line
            current_body = []
        else:
            current_body.append(line)
    sections.append((current_heading, current_body))
    return sections

def rebuild(sections):
    return "".join(h + "".join(b) if h else "".join(b) for h, b in sections)

INCOMPLETE = re.compile(r"^- \[ \] .+")  # task with actual content

yesterday_text = yesterday_file.read_text(encoding="utf-8")
today_text = today_file.read_text(encoding="utf-8")

yesterday_sections = parse_sections(yesterday_text)
today_sections = parse_sections(today_text)

# Extract incomplete tasks per section from yesterday
# { "🎯 Today": [...lines...], "⏫ Next Up": [...], "🔽 Low Pri": [...] }
rollover = {s: [] for s in ROLLOVER_SECTIONS}
new_yesterday_sections = []

for heading, body in yesterday_sections:
    matched = next((s for s in ROLLOVER_SECTIONS if s in (heading or "")), None)
    if matched:
        kept = []
        for line in body:
            if INCOMPLETE.match(line.rstrip()):
                rollover[matched].append(line if line.endswith("\n") else line + "\n")
            else:
                kept.append(line)
        # Keep a blank placeholder if no real tasks remain
        if not any(l.strip().startswith("- [") for l in kept):
            kept.append("- [ ] \n")
        new_yesterday_sections.append((heading, kept))
    else:
        new_yesterday_sections.append((heading, body))

total = sum(len(v) for v in rollover.values())
if total == 0:
    print("Nothing to roll over — no incomplete tasks found in yesterday's note.")
    sys.exit(0)

# Insert rolled tasks at the top of each matching section in today's note
new_today_sections = []

for heading, body in today_sections:
    matched = next((s for s in ROLLOVER_SECTIONS if s in (heading or "")), None)
    if matched and rollover[matched]:
        new_body = list(rollover[matched])
        for line in body:
            if line.strip() == "- [ ]":  # drop bare placeholders
                continue
            new_body.append(line)
        if not any(l.strip() not in ("", "- [ ]") for l in new_body):
            new_body.append("- [ ] \n")
        new_today_sections.append((heading, new_body))
    else:
        new_today_sections.append((heading, body))

yesterday_file.write_text(rebuild(new_yesterday_sections), encoding="utf-8")
today_file.write_text(rebuild(new_today_sections), encoding="utf-8")

print(f"Rolled over {total} task(s) from {yesterday_file.name} → {today_file.name}")
for section in ROLLOVER_SECTIONS:
    if rollover[section]:
        print(f"\n  {section}")
        for t in rollover[section]:
            print(f"    {t.rstrip()}")
