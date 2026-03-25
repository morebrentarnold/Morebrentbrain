#!/usr/bin/env python3
"""
rollover.py — Morning task rollover for daily notes.

Moves incomplete tasks from yesterday's 🎯 Today section into
today's ⏫ Next Up section, then removes them from yesterday's note.

Usage:
    python3 /path/to/Morebrentbrain/Scripts/rollover.py
"""

import sys
import re
from datetime import date, timedelta
from pathlib import Path

VAULT = Path(__file__).parent.parent
DAILY = VAULT / "Daily"

TODAY = date.today()
YESTERDAY = TODAY - timedelta(days=1)

yesterday_file = DAILY / f"{YESTERDAY}.md"
today_file = DAILY / f"{TODAY}.md"

# ── Sanity checks ────────────────────────────────────────────────────────────

if not yesterday_file.exists():
    print(f"Nothing to roll over — yesterday's note not found: {yesterday_file.name}")
    sys.exit(0)

if not today_file.exists():
    print(f"Today's note not found: {today_file.name}")
    print("Create today's note first (run the Templater daily note template), then re-run this script.")
    sys.exit(1)

# ── Parse yesterday's note ───────────────────────────────────────────────────

def parse_sections(text):
    """Split note into a list of (heading_line, body_lines) tuples.
    The first item's heading_line will be None for any content before the first heading."""
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

yesterday_text = yesterday_file.read_text(encoding="utf-8")
today_text = today_file.read_text(encoding="utf-8")

yesterday_sections = parse_sections(yesterday_text)
today_sections = parse_sections(today_text)

# ── Extract incomplete tasks from 🎯 Today ───────────────────────────────────

INCOMPLETE = re.compile(r"^- \[ \] .+")  # must have content after "- [ ] "

rollover_tasks = []
new_yesterday_sections = []

for heading, body in yesterday_sections:
    if heading and "🎯 Today" in heading:
        kept = []
        for line in body:
            if INCOMPLETE.match(line.rstrip()):
                rollover_tasks.append(line if line.endswith("\n") else line + "\n")
            else:
                kept.append(line)
        # Leave a blank placeholder so the section isn't empty
        if not any(INCOMPLETE.match(l.rstrip()) or l.strip().startswith("- [") for l in kept):
            kept.append("- [ ] \n")
        new_yesterday_sections.append((heading, kept))
    else:
        new_yesterday_sections.append((heading, body))

if not rollover_tasks:
    print("No incomplete tasks in yesterday's 🎯 Today section — nothing to roll over.")
    sys.exit(0)

# ── Insert into today's ⏫ Next Up ────────────────────────────────────────────

new_today_sections = []
inserted = False

for heading, body in today_sections:
    if heading and "⏫ Next Up" in heading:
        # Find insertion point: after any existing tasks, before the first blank-placeholder line
        # We insert at the top of the section so rollovers are visible immediately.
        new_body = list(rollover_tasks)
        for line in body:
            # Skip bare placeholder lines ("- [ ] \n") if we're adding real tasks
            if line.strip() == "- [ ]":
                continue
            new_body.append(line)
        # If body had nothing real, ensure there's still a placeholder at the end
        has_real = any(l.strip() not in ("", "- [ ]") for l in new_body)
        if not has_real:
            new_body.append("- [ ] \n")
        new_today_sections.append((heading, new_body))
        inserted = True
    else:
        new_today_sections.append((heading, body))

if not inserted:
    print("Warning: could not find ⏫ Next Up section in today's note. No changes made.")
    sys.exit(1)

# ── Rebuild and write files ───────────────────────────────────────────────────

def rebuild(sections):
    parts = []
    for heading, body in sections:
        if heading:
            parts.append(heading)
        parts.extend(body)
    return "".join(parts)

yesterday_file.write_text(rebuild(new_yesterday_sections), encoding="utf-8")
today_file.write_text(rebuild(new_today_sections), encoding="utf-8")

print(f"Rolled over {len(rollover_tasks)} task(s) from {yesterday_file.name} → {today_file.name}")
for t in rollover_tasks:
    print(f"  {t.rstrip()}")
