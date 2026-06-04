#!/usr/bin/env python3
"""Capture a successful session into the raw material for spec extraction.

Two modes (see SKILL.md Phase 1):
  - in-session: the skill already holds the live conversation/artifacts; this
    helper is a thin assembler.
  - transcript: ingest an exported markdown/JSONL transcript for offline use.

Usage:
    python capture.py --transcript <path>     # offline mode
    python capture.py --in-session            # assemble from live context

Gathers: input files/sources used, the user's stated requirements, the approved
output, and the relevant session steps/tool calls (ignoring dead ends/retries).

Status: Milestone-1 stub. Transcript ingest lands in Milestone 2 once the
transcript format is confirmed with the user.
"""
import sys

print("capture.py is a Milestone-1 stub; transcript ingest arrives in M2.", file=sys.stderr)
sys.exit(64)
