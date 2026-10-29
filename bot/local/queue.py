#!/usr/bin/env python3
"""Queue local-Excel receipt writes until the user's computer can take the file.

The queue lives on the bot. The user's computer is only asked to copy files,
and each copy is one local-tool approval. Editing happens on the bot with
openpyxl. A receipt key is stored once. Draining the queue never creates a
second row for that key.

Exit codes from the copy back onto the computer:
- 0: backup written, workbook replaced, receipt file copied
- 2: workbook is locked or open in another app; nothing was replaced
- 3: the workbook changed after it was copied out; nothing was replaced
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from bot.local.bookio import (
    answer_question,
    apply_receipts,
    file_name,
    is_locked,
    receipt_key,
    sha256_bytes,
)

OFFLINE = "offline"
LOCKED = 2
STALE = 3
OK = 0


class Offline(RuntimeError):
    """The registered computer is off or asleep."""


class LocalComputer:
    """A folder that stands in for the user's computer.

    ``status`` does not count as an approval. ``copy_out`` and ``copy_back``
    each count as one approval. When ``online`` is false, neither copy runs.
    """

    def __init__(self, root: Path, online: bool = True):
        self.root = Path(root)
        self.online = online
        self.approvals = 0
        self.before_copy_back = None

    def status(self) -> str:
        return "connected" if self.online else OFFLINE

    def copy_out(self, workbook_name: str) -> bytes:
        if not self.online:
            raise Offline()
        self.approvals += 1
        return (self.root / workbook_name).read_bytes()

    def copy_back(self, workbook_name: str, new_bytes: bytes, expected_hash: str, backup_name: str, files: list[tuple[str, bytes]]) -> dict:
        if not self.online:
            raise Offline()
        self.approvals += 1
        if self.before_copy_back is not None:
            self.before_copy_back(self)
        dest = self.root / workbook_name
        if is_locked(dest):
            return {"code": LOCKED}
        current = dest.read_bytes()
        if sha256_bytes(current) != expected_hash:
            return {"code": STALE}
        backups = self.root / "backups"
        backups.mkdir(parents=True, exist_ok=True)
        backup_path = _unique_backup(backups, backup_name)
        backup_path.write_bytes(current)
        if backup_path.stat().st_size != len(current):
            backup_path.unlink()
            return {"code": LOCKED}
        dest.write_bytes(new_bytes)
        receipts = self.root / "receipts"
        receipts.mkdir(parents=True, exist_ok=True)
        for name, data in files:
            target = receipts / name
            if target.exists() and sha256_bytes(target.read_bytes()) == sha256_bytes(data):
                continue
            if target.exists():
                return {"code": LOCKED}
            target.write_bytes(data)
        return {"code": OK, "backup": str(backup_path)}


def _unique_backup(folder: Path, name: str) -> Path:
    """A backup path that does not exist yet. Never overwrite, and never treat a taken name as a lock."""
    dest = folder / name
    if not dest.exists():
        return dest
    stem = Path(name).stem
    suffix = Path(name).suffix
    number = 2
    while True:
        candidate = folder / f"{stem} - {number}{suffix}"
        if not candidate.exists():
            return candidate
        number += 1


class ReceiptQueue:
    """One row per receipt key. Status is queued, writing, retry, question, or done."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.items: list[dict] = []
        if self.path.exists():
            self.items = json.loads(self.path.read_text(encoding="utf-8")).get("items", [])

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"items": self.items}, indent=2), encoding="utf-8")

    def _key(self, receipt: dict) -> str:
        return receipt_key(receipt.get("store", ""), receipt.get("number", ""), receipt.get("when"), receipt.get("total"))

    def enqueue(self, receipt: dict) -> dict:
        key = self._key(receipt)
        for item in self.items:
            if item["key"] == key:
                return {"key": key, "result": "duplicate", "status": item["status"]}
        stored = dict(receipt)
        body = stored.get("body", "")
        if isinstance(body, bytes):
            stored["body"] = body.decode("utf-8")
        self.items.append({"key": key, "status": "queued", "attempts": 0, "receipt": stored})
        self.save()
        return {"key": key, "result": "queued", "status": "queued"}

    def pending(self) -> list[dict]:
        return [item for item in self.items if item["status"] in {"queued", "retry", "writing"}]

    def mark(self, key: str, status: str) -> None:
        for item in self.items:
            if item["key"] == key:
                item["status"] = status
                if status == "retry":
                    item["attempts"] = int(item.get("attempts") or 0) + 1
        self.save()


def drain(queue: ReceiptQueue, computer: LocalComputer, workbook_name: str, staging: Path, name_prefix: str = "", stamp: str | None = None) -> dict:
    """Copy the book out, apply every pending receipt once, copy the book back.

    Offline: no approvals and no write. Locked: the computer file is unchanged
    and the same queue rows are marked retry. A second drain does not add a
    second amount. The backup stamp defaults to the current time. A name that
    is already used gets a numeric suffix. That collision is not a lock.
    """
    if not stamp:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    pending = queue.pending()
    keys = [item["key"] for item in pending]
    if not pending:
        return {"wrote": [], "skipped": [], "waiting": [], "locked": False, "approvals": computer.approvals}
    if computer.status() != "connected":
        return {"wrote": [], "skipped": [], "waiting": keys, "locked": False, "approvals": computer.approvals}
    for item in pending:
        item["status"] = "writing"
    queue.save()
    try:
        original = computer.copy_out(workbook_name)
    except Offline:
        return {"wrote": [], "skipped": [], "waiting": keys, "locked": False, "approvals": computer.approvals}
    staging.mkdir(parents=True, exist_ok=True)
    staged_book = staging / workbook_name
    staged_receipts = staging / "receipts"
    staged_backups = staging / "backups"
    staged_book.write_bytes(original)
    expected = sha256_bytes(original)
    receipts = [item["receipt"] for item in pending]
    # The staging backup is the bot's own scratch copy. The user's backup is
    # the copy_back into the computer's backups folder.
    applied = apply_receipts(staged_book, receipts, staged_receipts, staged_backups, name_prefix=name_prefix, stamp=stamp)
    if applied["locked"]:
        for item in pending:
            queue.mark(item["key"], "retry")
        return {"wrote": [], "skipped": [], "waiting": keys, "locked": True, "approvals": computer.approvals}
    question_keys = [item["key"] for item in applied.get("questions", [])]
    changed = bool(applied["wrote"] or applied["resumed"] or applied.get("attached") or question_keys)
    files = []
    kept = set(applied["wrote"]) | set(applied["resumed"]) | set(applied.get("attached", [])) | set(question_keys)
    if changed:
        for item in pending:
            if item["key"] not in kept:
                continue
            receipt = item["receipt"]
            body = receipt.get("body", "")
            data = body.encode("utf-8") if isinstance(body, str) else body
            if not data:
                continue
            files.append((
                file_name(receipt.get("when"), receipt.get("store", ""), float(receipt["total"]), receipt.get("ext") or ".txt", prefix=name_prefix),
                data,
            ))
        backup_name = f"{Path(workbook_name).stem} - {stamp}{Path(workbook_name).suffix}"
        result = computer.copy_back(workbook_name, staged_book.read_bytes(), expected, backup_name, files)
        code = result["code"]
        if code == STALE:
            # The computer's file moved. Copy it out once more and apply the
            # same keys. apply_receipts will not add a key that is already there.
            fresh = computer.copy_out(workbook_name)
            staged_book.write_bytes(fresh)
            expected = sha256_bytes(fresh)
            applied = apply_receipts(staged_book, receipts, staged_receipts, staged_backups, name_prefix=name_prefix, stamp=stamp + "-b")
            if applied["wrote"] or applied["resumed"] or applied.get("attached") or applied.get("questions"):
                result = computer.copy_back(workbook_name, staged_book.read_bytes(), expected, backup_name, files)
                code = result["code"]
            else:
                code = OK
        if code == LOCKED:
            for key in keys:
                queue.mark(key, "retry")
            return {"wrote": [], "skipped": applied["skipped"], "attached": [], "questions": [], "waiting": keys, "locked": True, "approvals": computer.approvals}
        if code != OK:
            for key in keys:
                queue.mark(key, "retry")
            return {"wrote": [], "skipped": [], "attached": [], "questions": [], "waiting": keys, "locked": False, "approvals": computer.approvals}
        backup_path = result.get("backup", "")
    else:
        backup_path = ""
    for key in applied["wrote"]:
        queue.mark(key, "done")
    for key in applied["resumed"]:
        queue.mark(key, "done")
    for key in applied.get("attached", []):
        queue.mark(key, "done")
    for key in applied["skipped"]:
        queue.mark(key, "done")
    for item in applied.get("questions", []):
        queue.mark(item["key"], "question")
        for queued in queue.items:
            if queued["key"] == item["key"]:
                queued["text"] = item["text"]
        queue.save()
    return {
        "wrote": applied["wrote"],
        "skipped": applied["skipped"],
        "resumed": applied["resumed"],
        "attached": applied.get("attached", []),
        "questions": applied.get("questions", []),
        "waiting": [],
        "locked": False,
        "approvals": computer.approvals,
        "backup": backup_path,
    }


def resolve_question(queue: ReceiptQueue, computer: LocalComputer, workbook_name: str, staging: Path, key: str, answer: str, name_prefix: str = "", stamp: str | None = None) -> dict:
    """Copy the book out, record one near-match reply, and copy it back.

    ``no`` writes the purchase once. ``yes`` or a date attaches it and clears
    the question. The queue row becomes ``done``. A bare yes with two or more
    candidates leaves the question open and does not replace the file. Offline
    is 0 approvals.
    """
    if not stamp:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    item = next((row for row in queue.items if row["key"] == key), None)
    idle = {"action": "skip", "key": key, "text": "", "locked": False, "approvals": computer.approvals, "backup": ""}
    if item is None or item["status"] != "question":
        return idle
    if computer.status() != "connected":
        return {**idle, "waiting": [key]}
    try:
        original = computer.copy_out(workbook_name)
    except Offline:
        return {**idle, "waiting": [key]}
    staging.mkdir(parents=True, exist_ok=True)
    staged_book = staging / workbook_name
    staged_book.write_bytes(original)
    expected = sha256_bytes(original)
    result = answer_question(
        staged_book,
        key,
        answer,
        staging / "receipts",
        staging / "backups",
        name_prefix=name_prefix,
        stamp=stamp,
    )
    if result["action"] == "ask":
        item["text"] = result.get("text") or item.get("text") or ""
        queue.save()
        return {**result, "locked": False, "approvals": computer.approvals, "backup": ""}
    if result["action"] not in {"wrote", "attached"}:
        return {**result, "approvals": computer.approvals, "backup": ""}
    backup_name = f"{Path(workbook_name).stem} - {stamp}{Path(workbook_name).suffix}"
    copied = computer.copy_back(workbook_name, staged_book.read_bytes(), expected, backup_name, [])
    if copied["code"] != OK:
        return {
            "action": "skip",
            "key": key,
            "text": result.get("text") or "",
            "locked": copied["code"] == LOCKED,
            "approvals": computer.approvals,
            "backup": "",
        }
    queue.mark(key, "done")
    return {
        "action": result["action"],
        "key": key,
        "text": "",
        "locked": False,
        "approvals": computer.approvals,
        "backup": copied.get("backup", ""),
    }
