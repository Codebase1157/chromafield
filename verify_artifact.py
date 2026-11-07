#!/usr/bin/env python3
"""Verify a ChromaField run directory against its own MANIFEST.json.

    python verify_artifact.py artifacts/20261107-103638

Recomputes the SHA-256 of every listed file and reports any that differ, are
missing, or are present in the directory but absent from the manifest. Exits
non-zero on any discrepancy, so it can be used as a CI gate.
"""
import hashlib
import json
import sys
from pathlib import Path

SKIP_DIRS = {"__pycache__"}
SKIP_SUFFIX = {".pyc"}
# written by eval/aggregate.py and stats/run_all.py when they are re-run, so
# they legitimately appear after the manifest was sealed
GENERATED = {"predictions/eval_recomputed.json",
             "predictions/stats_recomputed.csv"}


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main(root):
    root = Path(root).resolve()
    manifest_path = root / "MANIFEST.json"
    if not manifest_path.exists():
        print("no MANIFEST.json in %s" % root)
        return 2
    manifest = json.loads(manifest_path.read_text())

    listed, missing, mismatched = set(), [], []
    for entry in manifest["files"]:
        rel = entry["path"]
        listed.add(rel)
        p = root / rel
        if not p.exists():
            missing.append(rel)
            continue
        if sha256_file(p) != entry["sha256"]:
            mismatched.append(rel)

    on_disk = set()
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if SKIP_DIRS & set(p.parts) or p.suffix in SKIP_SUFFIX:
            continue
        rel = str(p.relative_to(root)).replace("\\", "/")
        if rel == "MANIFEST.json":
            continue
        on_disk.add(rel)
    untracked = sorted(on_disk - listed - GENERATED)

    print("run id        : %s" % manifest.get("run_id"))
    print("files listed  : %d" % len(listed))
    print("verified      : %d" % (len(listed) - len(missing) - len(mismatched)))
    print("missing       : %d" % len(missing))
    print("hash mismatch : %d" % len(mismatched))
    print("untracked     : %d" % len(untracked))
    for label, items in (("missing", missing), ("mismatched", mismatched),
                         ("untracked", untracked)):
        for i in items[:20]:
            print("  %-11s %s" % (label, i))
        if len(items) > 20:
            print("  %-11s ... and %d more" % (label, len(items) - 20))

    ok = not (missing or mismatched or untracked)
    print("\n%s" % ("OK: the archive matches its manifest." if ok
                    else "FAILED: the archive does not match its manifest."))
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
