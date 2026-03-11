#!/bin/bash
set -euo pipefail

TRIAGE_FILE="$CLAUDE_PROJECT_DIR/.claude/last-inbox-triage"
INBOX_DIR="$CLAUDE_PROJECT_DIR/Inbox"
DAYS_THRESHOLD=7

# Count items in Inbox (excluding README)
inbox_count=$(find "$INBOX_DIR" -name "*.md" ! -name "README.md" 2>/dev/null | wc -l | tr -d ' ')

# Check if triage is due
triage_due=false
if [ ! -f "$TRIAGE_FILE" ]; then
  triage_due=true
else
  last_triage=$(cat "$TRIAGE_FILE")
  today=$(date +%Y-%m-%d)
  # Calculate days since last triage
  last_ts=$(date -d "$last_triage" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$last_triage" +%s 2>/dev/null)
  now_ts=$(date +%s)
  days_since=$(( (now_ts - last_ts) / 86400 ))
  if [ "$days_since" -ge "$DAYS_THRESHOLD" ]; then
    triage_due=true
  fi
fi

if [ "$triage_due" = true ]; then
  echo ""
  echo "┌─────────────────────────────────────────────┐"
  echo "│  Inbox Triage Reminder                      │"
  echo "│                                             │"
  if [ "$inbox_count" -gt 0 ]; then
    printf  "│  You have %-3s item(s) in your Inbox.       │\n" "$inbox_count"
  else
    echo "│  Your Inbox is empty — great job!           │"
  fi
  echo "│                                             │"
  echo "│  Run: 'triage inbox' to process items       │"
  echo "│  or ask Claude to help sort them into PARA. │"
  echo "│                                             │"
  echo "│  To mark as done: echo \$(date +%Y-%m-%d) >  │"
  echo "│    .claude/last-inbox-triage                │"
  echo "└─────────────────────────────────────────────┘"
  echo ""
fi
