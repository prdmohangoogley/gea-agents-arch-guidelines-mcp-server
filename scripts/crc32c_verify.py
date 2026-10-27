#!/usr/bin/env python3
"""CRC32C integrity verification for the uploaded knowledge base.

Cloud Storage always stores a CRC32C (Castagnoli) checksum for every object
and `gcloud storage` validates it during transfer. This script closes the
loop independently: it recomputes CRC32C over the LOCAL bytes and compares
against the checksum Cloud Storage reports for the REMOTE object. If a file
was silently truncated or altered anywhere in the pipeline, this catches it.

Uses the google-crc32c C extension when available and falls back to a
self-contained pure-Python implementation, so it runs on a stock macOS
Python with no pip install required.

Usage:
    crc32c_verify.py --selftest
    crc32c_verify.py --local-root DIR --bucket BUCKET --prefix PREFIX
    crc32c_verify.py --file PATH            # just print the local checksum
"""

import argparse
import base64
import json
import os
import struct
import subprocess
import sys

# --------------------------------------------------------------------------
# CRC32C
# --------------------------------------------------------------------------

try:  # fast path
    import google_crc32c

    def crc32c_bytes(data, crc=0):
        c = google_crc32c.Checksum()
        c.update(data)
        return int.from_bytes(c.digest(), "big")

    IMPL = "google-crc32c (C extension)"
except ImportError:
    # Castagnoli polynomial, reflected form.
    _POLY = 0x82F63B78
    _TABLE = []
    for _i in range(256):
        _c = _i
        for _ in range(8):
            _c = (_c >> 1) ^ (_POLY if _c & 1 else 0)
        _TABLE.append(_c)

    def _crc32c_update(data, crc):
        crc ^= 0xFFFFFFFF
        for b in data:
            crc = _TABLE[(crc ^ b) & 0xFF] ^ (crc >> 8)
        return crc ^ 0xFFFFFFFF

    def crc32c_bytes(data, crc=0):
        return _crc32c_update(data, crc)

    IMPL = "pure-Python fallback"


def crc32c_file(path, chunk=1 << 20):
    """Streaming CRC32C of a file; returns the 32-bit integer."""
    crc = 0
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            crc = crc32c_bytes(block, crc)
    return crc


def to_gcs_b64(value):
    """Cloud Storage reports crc32c as base64 of the big-endian 4 bytes."""
    return base64.b64encode(struct.pack(">I", value)).decode("ascii")


# --------------------------------------------------------------------------
# self test - guards the pure-Python path against silent breakage
# --------------------------------------------------------------------------

def selftest():
    # Canonical CRC32C check value for the string "123456789".
    vectors = [
        (b"123456789", 0xE3069283),   # canonical CRC32C check value
        (b"", 0x00000000),
        (b"a", 0xC1D04330),
        (b"The quick brown fox jumps over the lazy dog", 0x22620404),
    ]
    ok = True
    for data, expected in vectors:
        got = crc32c_bytes(data)
        status = "ok " if got == expected else "FAIL"
        if got != expected:
            ok = False
        print("  %s %-12r expected=%08X got=%08X" % (status, data, expected, got))
    print("\nimplementation: %s" % IMPL)
    print("base64 of CRC32C('123456789') = %s" % to_gcs_b64(crc32c_bytes(b"123456789")))
    return 0 if ok else 1


# --------------------------------------------------------------------------
# remote comparison
# --------------------------------------------------------------------------

# gcloud has spelled the checksum field differently across versions and
# surfaces (`crc32c_hash` in gcloud storage, `crc32c` in the JSON API).
# Projecting a name that does not exist yields null rather than an error, so
# probe for whichever key is actually present instead of assuming one.
CRC_KEYS = ("crc32c_hash", "crc32c", "crc32cHash", "crc32CHash")
SIZE_KEYS = ("size", "Size", "content_length", "bytes")


def _first_key(item, keys):
    for k in keys:
        if item.get(k) not in (None, ""):
            return item[k]
    return None


def remote_checksums(bucket, prefix):
    """Return {object_name: (crc32c_b64, size)} for everything under prefix."""
    uri = "gs://%s/%s" % (bucket, prefix.strip("/"))
    # Ask for the full resource, not a projection, so we can find the
    # checksum whatever this gcloud version calls it.
    cmd = ["gcloud", "storage", "objects", "list", uri + "/**", "--format=json"]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        sys.stderr.write("failed to list objects:\n%s\n" % out.stderr)
        sys.exit(2)

    items = json.loads(out.stdout or "[]")
    result = {}
    for item in items:
        name = item.get("name") or item.get("storage_url") or ""
        # some versions return a full gs:// URL rather than the object name
        if name.startswith("gs://"):
            name = name.split("/", 3)[3] if name.count("/") >= 3 else name
        crc = _first_key(item, CRC_KEYS)
        size = _first_key(item, SIZE_KEYS)
        try:
            size = int(size) if size is not None else None
        except (TypeError, ValueError):
            size = None
        result[name] = (crc, size)

    # Fail loudly and unambiguously if we could not read checksums at all,
    # rather than reporting every object as a mismatch.
    if items and all(v[0] is None for v in result.values()):
        sample = sorted(items[0].keys())
        sys.stderr.write(
            "\nCould not find a CRC32C field in this gcloud's output.\n"
            "Tried: %s\n"
            "Fields actually returned: %s\n\n"
            "This is a tooling/compatibility problem, NOT a data problem -\n"
            "the objects themselves may be perfectly fine. Re-run with\n"
            "--debug-fields to dump one object, or verify manually:\n"
            "  gcloud storage objects describe gs://%s/<object>\n"
            % (", ".join(CRC_KEYS), ", ".join(sample), bucket))
        sys.exit(3)

    return result


def verify(local_root, bucket, prefix):
    remote = remote_checksums(bucket, prefix)
    prefix_clean = prefix.strip("/")

    local_files = []
    for dirpath, _dirs, files in os.walk(local_root):
        for fn in sorted(files):
            if fn.startswith("."):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, local_root).replace(os.sep, "/")
            local_files.append((rel, full))
    local_files.sort()

    print("implementation : %s" % IMPL)
    print("local root     : %s" % local_root)
    print("remote         : gs://%s/%s" % (bucket, prefix_clean))
    print("local files    : %d" % len(local_files))
    print("remote objects : %d\n" % len(remote))

    problems = []
    checked = 0
    for rel, full in local_files:
        obj = "%s/%s" % (prefix_clean, rel) if prefix_clean else rel
        entry = remote.get(obj)
        if entry is None:
            problems.append("MISSING REMOTE  %s" % obj)
            continue
        remote_crc, remote_size = entry
        local_size = os.path.getsize(full)
        local_crc = to_gcs_b64(crc32c_file(full))

        if local_size != remote_size:
            problems.append("SIZE MISMATCH   %s (local %d, remote %d)"
                            % (obj, local_size, remote_size))
        elif local_crc != remote_crc:
            problems.append("CRC32C MISMATCH %s (local %s, remote %s)"
                            % (obj, local_crc, remote_crc))
        else:
            checked += 1

    extra = set(remote) - {
        ("%s/%s" % (prefix_clean, rel) if prefix_clean else rel)
        for rel, _ in local_files
    }
    for obj in sorted(extra):
        problems.append("EXTRA REMOTE    %s" % obj)

    print("verified OK    : %d" % checked)
    if problems:
        print("problems       : %d\n" % len(problems))
        for p in problems:
            print("  %s" % p)
        return 1
    print("\nAll objects match on size and CRC32C.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--file")
    ap.add_argument("--local-root")
    ap.add_argument("--bucket")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--debug-fields", action="store_true",
                    help="dump the raw field names gcloud returns for one "
                         "object, to diagnose checksum-field naming")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if args.debug_fields:
        if not args.bucket:
            sys.exit("--debug-fields needs --bucket")
        uri = "gs://%s/%s" % (args.bucket, args.prefix.strip("/"))
        out = subprocess.run(
            ["gcloud", "storage", "objects", "list", uri + "/**",
             "--limit=1", "--format=json"],
            capture_output=True, text=True)
        if out.returncode != 0:
            sys.exit(out.stderr)
        items = json.loads(out.stdout or "[]")
        if not items:
            sys.exit("no objects found under %s" % uri)
        print("fields returned by this gcloud for one object:\n")
        for k in sorted(items[0]):
            v = str(items[0][k])
            print("  %-28s %s" % (k, (v[:60] + "...") if len(v) > 60 else v))
        return 0
    if args.file:
        print("%s  %s" % (to_gcs_b64(crc32c_file(args.file)), args.file))
        return 0
    if args.local_root and args.bucket:
        return verify(args.local_root, args.bucket, args.prefix)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
