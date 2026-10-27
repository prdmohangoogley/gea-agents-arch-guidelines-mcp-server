#!/usr/bin/env python3
"""Generate Knowledge Catalog (Dataplex) aspect payloads from an OKF bundle.

Reads the concept files produced by build_okf_bundle.py and emits one JSON
aspect payload per concept, mapping OKF v0.2 frontmatter onto the `okf`
aspect type created by register_knowledge_catalog.sh.

Each payload also carries an `overview` aspect holding the Markdown body, so
the concept text is searchable in the catalog rather than only in the bucket.

Usage:
    make_catalog_entries.py --bundle build/okf --bucket BUCKET \
        --out build/catalog-entries --entry-group EG --entry-type ET \
        --aspect-type okf --project PROJECT --location us
"""

import argparse
import json
import os
import re
import sys

FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n+", re.S)


def parse_front_matter(block):
    """Parse the OKF frontmatter subset emitted by build_okf_bundle.py.

    Handles scalars, simple lists, and one level of nested mappings
    (`generated:`) and lists-of-mappings (`verified:`).
    """
    meta = {}
    lines = block.splitlines()
    i = 0

    def unquote(v):
        v = v.strip()
        if v.startswith('"') and v.endswith('"'):
            return v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        return v

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if m and not line.startswith(" "):
            key, val = m.group(1), m.group(2).strip()
            if val:
                meta[key] = unquote(val)
                i += 1
                continue

            # block value: list, list-of-maps, or map
            block_items = []
            block_map = {}
            i += 1
            current = None
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                sub = lines[i]
                if not sub.strip():
                    i += 1
                    continue
                mdash = re.match(r"^  - ([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", sub)
                mplain = re.match(r"^  - (.*)$", sub)
                mkv = re.match(r"^    ([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", sub)
                mmap = re.match(r"^  ([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", sub)
                if mdash:
                    current = {mdash.group(1): unquote(mdash.group(2))}
                    block_items.append(current)
                elif mkv and current is not None:
                    current[mkv.group(1)] = unquote(mkv.group(2))
                elif mplain:
                    block_items.append(unquote(mplain.group(1)))
                    current = None
                elif mmap:
                    block_map[mmap.group(1)] = unquote(mmap.group(2))
                i += 1
            meta[key] = block_items if block_items else block_map
            continue
        i += 1
    return meta


def flatten_verified(v):
    if not v:
        return ""
    out = []
    for ev in v:
        if isinstance(ev, dict):
            out.append("%s @ %s :: %s" % (ev.get("by", "?"), ev.get("at", "?"),
                                          ev.get("scope", "")))
        else:
            out.append(str(ev))
    return "\n".join(out)


def flatten_sources(s):
    if not s:
        return ""
    if isinstance(s, list):
        return "\n".join(str(x) for x in s)
    return str(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--entry-group", required=True)
    ap.add_argument("--entry-type", required=True)
    ap.add_argument("--aspect-type", default="okf")
    ap.add_argument("--project", required=True)
    ap.add_argument("--location", default="us")
    a = ap.parse_args()

    concepts = os.path.join(a.bundle, "concepts")
    if not os.path.isdir(concepts):
        sys.exit("no concepts/ directory under %s" % a.bundle)

    os.makedirs(a.out, exist_ok=True)
    aspect_key = "%s.%s.%s" % (a.project, a.location, a.aspect_type)

    written = 0
    for fn in sorted(os.listdir(concepts)):
        if not fn.endswith(".md"):
            continue
        raw = open(os.path.join(concepts, fn), encoding="utf-8").read()
        m = FRONT_MATTER.match(raw)
        if not m:
            print("  skip (no frontmatter): %s" % fn)
            continue
        meta = parse_front_matter(m.group(1))

        generated = meta.get("generated") or {}
        if not isinstance(generated, dict):
            generated = {}

        payload = {
            aspect_key: {
                "data": {
                    "type": meta.get("type", ""),
                    "title": meta.get("title", ""),
                    "description": meta.get("description", ""),
                    "timestamp": meta.get("timestamp", ""),
                    "status": meta.get("status", "draft"),
                    "stale_after": meta.get("stale_after", ""),
                    "sources": flatten_sources(meta.get("sources")),
                    "generated_by": generated.get("by", ""),
                    "generated_at": generated.get("at", ""),
                    "generated_method": generated.get("method", ""),
                    "verified": flatten_verified(meta.get("verified")),
                    "corpus": meta.get("corpus", ""),
                    "version_tag": meta.get("version_tag", ""),
                    "source_doc_id": meta.get("source_doc_id", ""),
                    "content_sha256": meta.get("content_sha256", ""),
                }
            }
        }

        entry_id = fn[:-3]
        with open(os.path.join(a.out, entry_id + ".json"), "w",
                  encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        written += 1

    print("  wrote %d aspect payloads to %s" % (written, a.out))
    print("  aspect key   : %s" % aspect_key)
    print("  gcs backing  : gs://%s/okf/concepts/" % a.bucket)
    return 0


if __name__ == "__main__":
    sys.exit(main())
