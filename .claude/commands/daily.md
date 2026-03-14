You are managing Brent's daily note system inside his Obsidian PARA vault at /Users/brentarnold/Morebrentbrain.

The argument passed to this command is: $ARGUMENTS

---

## Modes

### No argument → Morning Kickoff

1. Get today's date in YYYY-MM-DD format.
2. Check if `Areas/Daily/YYYY-MM-DD.md` already exists.
   - If it exists, read it and tell Brent it's already been created. Show him the current Today and Focus sections and ask if he wants to add anything.
   - If it does not exist, continue below.
3. Find yesterday's daily note (`Areas/Daily/YYYY-MM-DD.md` for yesterday). If it exists:
   - Read it and extract all incomplete tasks (`- [ ]`) from the **Today** and **Quick Capture** sections.
   - List them to Brent and ask: for each item, carry forward, drop, or move to a specific note?
   - Wait for his response before creating today's note.
4. Also read `Inbox/` directory and list any unprocessed notes. Ask if any should become tasks today.
5. Create `Areas/Daily/YYYY-MM-DD.md` using the template below, populating the **Today** section with confirmed carry-forwards.
6. Ask Brent: "What's your focus today?" (1-3 things). Add his answer to the Focus section.
7. Print the final note so he can see it.

---

### `eod` → End of Day Check-in

1. Read today's daily note at `Areas/Daily/YYYY-MM-DD.md`.
2. List all incomplete tasks (`- [ ]`) from the Today and Quick Capture sections.
3. For each incomplete item, ask: done, carry forward tomorrow, or drop?
4. Triage any items in Quick Capture that are not tasks — suggest where they belong (Inbox, a project note, Resources, etc.).
5. Ask: "Any wins worth noting? Anything on your mind?"
6. Update the note:
   - Move completed items to **Done** with `- [x]`
   - Move carry-forwards to **Carry Forward**
   - Move dropped items to **Drop**
   - Add reflection to **Notes**
7. Print the updated End of Day section.

---

### `triage` → Inbox Triage

1. List all files in `Inbox/`.
2. Read each one and suggest where it belongs in the PARA structure:
   - Projects/ (has a clear outcome + deadline)
   - Areas/ (ongoing responsibility)
   - Resources/ (reference material)
   - Archive/ (done or inactive)
   - A daily note Today section (actionable now)
3. Ask Brent to confirm or override each suggestion.
4. Move files accordingly and update their frontmatter `status` field if needed.

---

### `capture` → Quick Add

The remaining text after "capture" is the item to capture.
Append it as a new line under **Quick Capture** in today's daily note.
If today's note doesn't exist yet, create it first (run morning kickoff without the interactive steps).
Confirm the item was added.

---

## Daily Note Template

```
---
title: Daily — {DATE}
date: {DATE}
tags: [daily]
status: active
---

# {DATE}

## Focus
{FOCUS ITEMS}

## Today
{CARRIED FORWARD TASKS}

## Quick Capture

## End of Day
### Done
### Carry Forward
### Drop
### Notes
```

---

## Key paths
- Daily notes: `Areas/Daily/YYYY-MM-DD.md`
- Inbox: `Inbox/`
- Template: `Templates/daily.md`
- Active projects: `Projects/`
- Always use the CLAUDE.md frontmatter convention (title, date, tags, status)
