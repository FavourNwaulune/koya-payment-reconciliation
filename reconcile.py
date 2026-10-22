#!/usr/bin/env python3

import json
from decimal import Decimal, InvalidOperation


def parse_amount(value):
    if isinstance(value, bool):
        raise ValueError("bad amount")
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    return Decimal(str(value).replace(",", "").strip())



latest = {}

with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line)
        except ValueError:
            continue  # unreadable line
        if not isinstance(event, dict):
            continue
        txn_id = event.get("txn_id")
        if txn_id is None or txn_id == "":
            continue  # no txn_id
        ts = event.get("ts")
        if txn_id not in latest or ts > latest[txn_id]["ts"]:
            latest[txn_id] = event

total = Decimal(0)
count = 0
for event in latest.values():
    if event.get("status") != "success":
        continue
    try:
        total += parse_amount(event["amount"])
    except (KeyError, ValueError, InvalidOperation):
        continue
    count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
