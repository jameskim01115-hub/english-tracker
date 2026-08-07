#!/usr/bin/env python3
"""Hermes english data -> Firestore sync (runs on Hostinger VPS host via cron).

Sources (written by Hermes cron jobs):
  - wanted_phrases.md : Patrick's stuck expressions   -> source=hermes-wanted
  - b2_vocab_log.md   : delivered chunks/words (AM/PM/10AM) -> source=hermes-delivered

These files are the contract. Any English cron job -- existing or newly added --
gets picked up automatically as long as it keeps appending to them. Editing or
creating cron jobs does not require touching this script.

Idempotent: doc id = sha1(source|date|expression). Existing docs are skipped
(POST createDocument returns 409 ALREADY_EXISTS), so review progress made in
the dashboard is never overwritten.

Deployed at: /root/english-sync/sync_english_to_firestore.py (cron hourly, :20)
Local copy:  02_projects/english-tracker/hermes-sync.py -- edit here, then deploy.
"""
import hashlib
import json
import re
import sys
import urllib.request
import urllib.error
from datetime import date, timedelta

BASE = "/docker/hermes-agent-7jge/data/english"
# English Tracker 전용 프로젝트. M Building 프로젝트를 절대 여기에 넣지 말 것.
PROJECT = "english-tracker-cea9f"
API_KEY = "AIzaSyBmHEyQPrTGd1dQ6wD_zlzVz7EQLBjsEx8"
COLLECTION = "english_expressions"
BACKFILL_DAYS = 7  # only sync items learned within this window

FIRESTORE_URL = (
    "https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents/%s"
    % (PROJECT, COLLECTION)
)


def get_id_token():
    """Sign in anonymously. The tracker's Firestore rules require a signed-in
    session, so an unauthenticated write is rejected with 403."""
    url = ("https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=%s"
           % API_KEY)
    body = json.dumps({"returnSecureToken": True}).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)["idToken"]


def today_manila():
    # VPS is UTC; Manila = UTC+8. Good enough for date math without deps.
    from datetime import datetime, timezone
    return (datetime.now(timezone.utc) + timedelta(hours=8)).date()


def doc_id(source, learned, expression):
    key = "%s|%s|%s" % (source, learned, expression)
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:20]


def fs_fields(d):
    out = {}
    for k, v in d.items():
        if isinstance(v, bool):
            out[k] = {"booleanValue": v}
        elif isinstance(v, int):
            out[k] = {"integerValue": str(v)}
        else:
            out[k] = {"stringValue": str(v)}
    return out


def create_doc(did, data, token):
    """Create document; return True if created, False if it already existed."""
    url = "%s?documentId=%s&key=%s" % (FIRESTORE_URL, did, API_KEY)
    body = json.dumps({"fields": fs_fields(data)}).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer %s" % token},
    )
    try:
        urllib.request.urlopen(req, timeout=20)
        return True
    except urllib.error.HTTPError as e:
        if e.code == 409:
            return False
        print("ERROR creating %s: HTTP %s %s" % (did, e.code, e.read()[:200]), file=sys.stderr)
        return False
    except Exception as e:  # network etc.
        print("ERROR creating %s: %s" % (did, e), file=sys.stderr)
        return False


def next_review_for(learned_iso, today):
    """Stage-0 next review = learned+1d; stagger past-due backfill over 5 days."""
    y, m, d = (int(x) for x in learned_iso.split("-"))
    nxt = date(y, m, d) + timedelta(days=1)
    if nxt < today:
        offset = int(hashlib.sha1(learned_iso.encode()).hexdigest(), 16) % 5
        nxt = today + timedelta(days=offset)
    return nxt.isoformat()


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def parse_wanted(text):
    """Yield (date, expression, context) from wanted_phrases.md blocks."""
    for block in re.split(r"^## ", text, flags=re.M):
        m = re.match(r"(\d{4}-\d{2}-\d{2})", block)
        if not m:
            continue
        learned = m.group(1)
        originals = re.findall(r"^- Original[^:]*:\s*(.+)$", block, flags=re.M)
        ctx = re.findall(r"^- Context:\s*(.+)$", block, flags=re.M)
        if originals:
            # multiple Original lines = variants; last one is the preferred form
            yield learned, originals[-1].strip(), (ctx[0].strip() if ctx else "")


def parse_vocab(text):
    """Yield (date, slot, expression, meaning, example) from b2_vocab_log.md."""
    current = None  # (date, slot)
    for line in text.splitlines():
        h = re.match(r"^## (\d{4}-\d{2}-\d{2})\s*\([^)]*\)\s*\[([^\]]+)\]", line)
        if h:
            current = (h.group(1), h.group(2).strip().upper())
            continue
        if current and line.startswith("- "):
            parts = [p.strip() for p in line[2:].split("|")]
            if len(parts) >= 2 and parts[0]:
                example = parts[2] if len(parts) >= 3 else ""
                yield current[0], current[1], parts[0], parts[1], example


def main():
    today = today_manila()
    token = get_id_token()
    cutoff = (today - timedelta(days=BACKFILL_DAYS)).isoformat()
    created = skipped = 0

    for learned, expr, ctx in parse_wanted(read(BASE + "/wanted_phrases.md")):
        if learned < cutoff or not expr:
            continue
        did = doc_id("hermes-wanted", learned, expr)
        data = {
            "expression": expr, "meaning": "", "context": ctx,
            "source": "hermes-wanted", "slot": "", "learnedDate": learned,
            "stage": 0, "nextReview": next_review_for(learned, today),
        }
        if create_doc(did, data, token):
            created += 1
        else:
            skipped += 1

    for learned, slot, expr, meaning, example in parse_vocab(read(BASE + "/b2_vocab_log.md")):
        if learned < cutoff or not expr:
            continue
        did = doc_id("hermes-delivered", learned, expr)
        data = {
            "expression": expr, "meaning": meaning, "context": example,
            "source": "hermes-delivered", "slot": slot, "learnedDate": learned,
            "stage": 0, "nextReview": next_review_for(learned, today),
        }
        if create_doc(did, data, token):
            created += 1
        else:
            skipped += 1

    print("%s sync done: created=%d skipped=%d" % (today.isoformat(), created, skipped))


if __name__ == "__main__":
    main()
