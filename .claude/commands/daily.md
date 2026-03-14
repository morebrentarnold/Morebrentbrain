You are helping with a daily review of a Second Brain (PARA method) knowledge management system.

Today's date is $CURRENT_DATE. Perform the following daily review steps:

## 1. Create Today's Daily Note

Create a new file at `Inbox/daily-$CURRENT_DATE.md` with this content:

```markdown
---
title: Daily Note $CURRENT_DATE
date: $CURRENT_DATE
tags: [daily, journal]
status: active
---

# Daily Note — $CURRENT_DATE

## Today's Focus


## Notes & Captures


## Tasks


## Reflections

```

## 2. Summarize Active Projects

Read all `.md` files in the `Projects/` directory (recursively). For each active project (status: active), show:
- Project name and file path
- A one-line summary of what the project is about
- Any notes about whether it seems stale (no recent updates in the file)

## 3. Triage Inbox

List all `.md` files in `Inbox/` (excluding today's daily note you just created). For each:
- Show the filename and title
- Suggest a PARA destination (Projects, Areas, Resources, or Archive) with a brief reason

## 4. Flag Stale Notes

Search across all `Projects/` and `Areas/` notes. Flag any note whose frontmatter `date` field is more than 30 days old and `status` is still `active`.

## Output Format

Present results in clearly labeled sections with headers for each step above. Be concise — one or two lines per item.
