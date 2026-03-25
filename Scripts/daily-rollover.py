#!/usr/bin/env python3
"""
rollover.py — Morning startup script for daily notes.

1. Creates today's daily note from the template if it doesn't exist.
2. Moves incomplete tasks from yesterday's 🎯 Today section into
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
TEMPLATE = VAULT / "Templates" / "Daily Note.md"

TODAY = date.today()
YESTERDAY = TODAY - timedelta(days=1)

yesterday_file = DAILY / f"{YESTERDAY}.md"
today_file = DAILY / f"{TODAY}.md"

# ── Step 1: Create today's note from template if needed ──────────────────────

def render_template(template_path: Path, for_date: date) -> str:
    """Resolve Templater date expressions in the daily note template."""
    # Map Templater format tokens to Python strftime equivalents.
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
        # Pull the quoted format string, then look for an optional integer offset after it
        fmt_match = re.match(r'"([^"]+)"(?:\s*,\s*(-?\d+))?', args)
        if not fmt_match:
            return match.group(0)  # leave unrecognised expressions untouched
        fmt = convert_format(fmt_match.group(1))
        offset_days = int(fmt_match.group(2)) if fmt_match.group(2) else 0
        target = for_date + timedelta(days=offset_days)
        return target.strftime(fmt)

    text = template_path.read_text(encoding="utf-8")
    # Replace all <% tp.date.now(...) %> expressions
    text = re.sub(r"<%\s*tp\.date\.now\(([^)]+)\)\s*%>", resolve_tp_date, text)
    return text

if not today_file.exists():
    if not TEMPLATE.exists():
        print(f"Template not found: {TEMPLATE}")
        sys.exit(1)
    note_content = render_template(TEMPLATE, TODAY)
    today_file.write_text(note_content, encoding="utf-8")
    print(f"Created {today_file.name}")

# ── Step 2: Roll over incomplete tasks ───────────────────────────────────────

if not yesterday_file.exists():
    print(f"No yesterday's note found ({yesterday_file.name}) — skipping rollover.")
    sys.exit(0)

def parse_sections(text):
    """Split note text into [(heading_line, [body_lines]), ...].
    Content before the first ## heading gets heading_line=None."""
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

# Extract incomplete tasks from yesterday's 🎯 Today, remove them from that section
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
        # Keep a blank placeholder if no real tasks remain
        if not any(l.strip().startswith("- [") for l in kept):
            kept.append("- [ ] \n")
        new_yesterday_sections.append((heading, kept))
    else:
        new_yesterday_sections.append((heading, body))

if not rollover_tasks:
    print("Nothing to roll over — no incomplete tasks in yesterday's 🎯 Today.")
    sys.exit(0)

# Insert rollover tasks at the top of today's ⏫ Next Up
new_today_sections = []
inserted = False

for heading, body in today_sections:
    if heading and "⏫ Next Up" in heading:
        new_body = list(rollover_tasks)
        for line in body:
            if line.strip() == "- [ ]":  # drop bare placeholders
                continue
            new_body.append(line)
        if not any(l.strip() not in ("", "- [ ]") for l in new_body):
            new_body.append("- [ ] \n")
        new_today_sections.append((heading, new_body))
        inserted = True
    else:
        new_today_sections.append((heading, body))

if not inserted:
    print("Warning: ⏫ Next Up section not found in today's note — rollover skipped.")
    sys.exit(1)

yesterday_file.write_text(rebuild(new_yesterday_sections), encoding="utf-8")
today_file.write_text(rebuild(new_today_sections), encoding="utf-8")

print(f"Rolled over {len(rollover_tasks)} task(s) from {yesterday_file.name} → {today_file.name}")
for t in rollover_tasks:
    print(f"  {t.rstrip()}")
