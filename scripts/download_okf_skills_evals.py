#!/usr/bin/env python3
"""Download and Package All OKF v0.2 Data, 28 Agent Skills, and Evaluation Suites Locally.

Creates a self-contained, cryptographically checksummed portable bundle
(`dist/portable_bundle/` and `dist/gea_okf_skills_evals_portable_bundle.tar.gz`)
that can be moved to any machine and redeployed into any GCP project or account
using `scripts/redeploy_all_to_project.py`.

Usage:
    # 1. Package local OKF + Skills + Evals + Graph Triples snapshot:
    python3 scripts/download_okf_skills_evals.py

    # 2. Pull latest OKF objects from live GCS bucket first, then package:
    python3 scripts/download_okf_skills_evals.py --pull-from-gcs \
        --source-project fivedaysai-prd-sandbox-317383 \
        --gcs-bucket gea_agent_development_architectural_best_practices_1790796607
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def pull_okf_from_gcs(project_id: str, bucket_name: str, target_okf_dir: Path) -> dict[str, Any]:
    """Download live OKF bundle from GCS (gs://<bucket>/okf) into target_okf_dir."""
    gcs_uri = f"gs://{bucket_name}/okf"
    print(f"==> Pulling live OKF data from {gcs_uri} (project: {project_id})...")
    target_okf_dir.mkdir(parents=True, exist_ok=True)

    # First try google-cloud-storage SDK, fallback to gcloud storage cp
    downloaded_count = 0
    try:
        from google.cloud import storage

        client = storage.Client(project=project_id)
        bucket = client.bucket(bucket_name)
        blobs = list(bucket.list_blobs(prefix="okf/"))
        for blob in blobs:
            if blob.name.endswith("/"):
                continue
            rel_path = blob.name[len("okf/") :]
            if not rel_path:
                continue
            dest = target_okf_dir / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            blob.download_to_filename(str(dest))
            downloaded_count += 1
        print(f"  ✓ Downloaded {downloaded_count} objects from {gcs_uri} via Cloud Storage SDK.")
        return {"status": "success", "method": "python_sdk", "downloaded_files": downloaded_count}
    except Exception as sdk_err:
        print(f"  ! SDK download fallback ({sdk_err}); attempting `gcloud storage cp`...")
        cmd = [
            "gcloud",
            "storage",
            "cp",
            "-r",
            f"{gcs_uri}/*",
            str(target_okf_dir),
            f"--project={project_id}",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode == 0:
            print(f"  ✓ Downloaded live OKF corpus from {gcs_uri} via gcloud CLI.")
            return {"status": "success", "method": "gcloud_cli"}
        print(f"  ! Could not reach GCS ({res.stderr.strip()}); using local repository OKF files.")
        return {"status": "fallback_local", "reason": res.stderr.strip()}


def copy_tree_filtered(src: Path, dst: Path) -> list[Path]:
    """Copy directory tree excluding __pycache__, .pyc, and .DS_Store files."""
    copied: list[Path] = []
    if not src.exists():
        return copied
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".pytest_cache", ".git", ".terraform"}]
        rel_root = Path(root).relative_to(src)
        target_root = dst / rel_root
        target_root.mkdir(parents=True, exist_ok=True)
        for fname in files:
            if fname in {".DS_Store"} or fname.endswith((".pyc", ".pyo", ".tfstate", ".tfstate.backup")):
                continue
            src_file = Path(root) / fname
            dst_file = target_root / fname
            shutil.copy2(src_file, dst_file)
            copied.append(dst_file)
    return copied


def export_skills_catalog_snapshot(bundle_dir: Path) -> dict[str, Any]:
    """Export the 28 discovered skills (Tier-1 catalog + Tier-2 full manifests) to JSON."""
    from src.registry.skills_registry import SkillsRegistry

    registry = SkillsRegistry()
    catalog = registry.list_catalog()
    full_manifests = {}
    for item in catalog:
        sid = item.get("id") or item.get("skill_id")
        if not sid:
            continue
        manifest = registry.get_manifest(sid)
        if manifest:
            full_manifests[sid] = manifest.model_dump() if hasattr(manifest, "model_dump") else manifest

    snapshot = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "total_skills": len(catalog),
        "tier1_catalog": catalog,
        "tier2_manifests": full_manifests,
    }
    out_file = bundle_dir / "skills" / "skills_registry_snapshot.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return {"total_skills": len(catalog), "snapshot_path": str(out_file.relative_to(bundle_dir))}


def export_nl2kg_graph_snapshot(bundle_dir: Path) -> dict[str, Any]:
    """Run offline NL2KG extraction over all OKF concepts so graph triples are bundled."""
    try:
        from pipelines.nl2kg_pipeline import run_pipeline

        checkpoint_tmp = bundle_dir / "okf" / ".nl2kg_bundle_checkpoint.json"
        graph = run_pipeline(
            gcs_bucket_name="local-bundle-export",
            local_dir=bundle_dir / "okf" / "concepts",
            source="local",
            project_id="portable-bundle",
            spanner_instance_id="arch-guidelines-graph",
            spanner_database_name="guidelines-db",
            bq_dataset_id="arch_guidelines_analytics",
            checkpoint_file=checkpoint_tmp,
            dry_run=True,
            force_sync=True,
        )
        if checkpoint_tmp.exists():
            checkpoint_tmp.unlink()

        graph_file = bundle_dir / "okf" / "nl2kg_graph_triples_snapshot.json"
        graph_file.write_text(graph.model_dump_json(indent=2), encoding="utf-8")
        return {
            "guidelines_count": len(graph.guidelines),
            "fde_rubric_items_count": len(graph.fde_rubric_items),
            "patterns_count": len(graph.patterns),
            "antipatterns_count": len(graph.antipatterns),
            "tradeoffs_count": len(graph.tradeoffs),
            "edges_count": len(graph.edges) + len(graph.enforces_rubric_edges),
            "snapshot_file": str(graph_file.relative_to(bundle_dir)),
        }
    except Exception as exc:
        print(f"  ! Warning: NL2KG graph snapshot skipped: {exc}")
        return {"status": "skipped", "reason": str(exc)}


def build_portable_bundle(
    output_dir: Path,
    archive_path: Path,
    pull_from_gcs: bool = False,
    source_project: str = "fivedaysai-prd-sandbox-317383",
    gcs_bucket: str = "gea_agent_development_architectural_best_practices_1790796607",
) -> dict[str, Any]:
    """Assemble and checksum the complete portable bundle."""
    print("=" * 78)
    print("GEA Architecture Best Practices — Portable OKF, Skills & Evals Exporter")
    print("=" * 78)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy local OKF directory (concepts, bundle.json, MANIFEST.json, catalog-entries, img)
    print("==> [1/6] Packaging OKF v0.2 Corpus (concepts, schemas, catalog entries)...")
    copy_tree_filtered(REPO_ROOT / "okf", output_dir / "okf")
    copy_tree_filtered(REPO_ROOT / "catalog", output_dir / "catalog")

    gcs_sync_result = {"status": "skipped_local_only"}
    if pull_from_gcs:
        gcs_sync_result = pull_okf_from_gcs(source_project, gcs_bucket, output_dir / "okf")

    concept_files = sorted((output_dir / "okf" / "concepts").glob("*.md"))
    print(f"  ✓ Packaged {len(concept_files)} OKF v0.2 concept markdown files.")

    # 2. Package all Agent Skills (.agents/skills + src/skills + src/registry)
    print("==> [2/6] Packaging Agent Skills (.agents/skills, src/skills, SkillsRegistry)...")
    copy_tree_filtered(REPO_ROOT / ".agents" / "skills", output_dir / ".agents" / "skills")
    copy_tree_filtered(REPO_ROOT / "src" / "skills", output_dir / "src" / "skills")
    copy_tree_filtered(REPO_ROOT / "src" / "registry", output_dir / "src" / "registry")
    skills_meta = export_skills_catalog_snapshot(output_dir)
    print(
        f"  ✓ Packaged {skills_meta['total_skills']} registered skills "
        f"(16 SKILL.md folders + 12 Python skill plugins + full JSON snapshot)."
    )

    # 3. Package all Evals & Test Suites (tests/evals + tests/)
    print("==> [3/6] Packaging Golden Datasets, Trajectory Evals & Test Suites...")
    copy_tree_filtered(REPO_ROOT / "tests", output_dir / "tests")
    eval_datasets = sorted((output_dir / "tests" / "evals").glob("*.json"))
    eval_tests = sorted((output_dir / "tests").rglob("test_*.py"))
    print(f"  ✓ Packaged {len(eval_datasets)} golden/trajectory JSON datasets and {len(eval_tests)} test suites.")

    # 4. Package Source Code, NL2KG Pipelines, IaC, and Deployment Scripts
    print("==> [4/6] Packaging Server Source, NL2KG Pipelines, Terraform IaC & Scripts...")
    copy_tree_filtered(REPO_ROOT / "src", output_dir / "src")
    copy_tree_filtered(REPO_ROOT / "pipelines", output_dir / "pipelines")
    copy_tree_filtered(REPO_ROOT / "iac", output_dir / "iac")
    copy_tree_filtered(REPO_ROOT / "scripts", output_dir / "scripts")
    for root_file in ["pyproject.toml", "README.md", ".env"]:
        rf = REPO_ROOT / root_file
        if rf.exists():
            shutil.copy2(rf, output_dir / root_file)

    # 5. Export offline NL2KG Knowledge Graph Triples Snapshot
    print("==> [5/6] Generating Offline NL2KG Knowledge Graph Triples Snapshot...")
    graph_meta = export_nl2kg_graph_snapshot(output_dir)
    print(
        f"  ✓ Snapshot generated: {graph_meta.get('guidelines_count', 0)} Guidelines, "
        f"{graph_meta.get('fde_rubric_items_count', 0)} Rubric Items, "
        f"{graph_meta.get('edges_count', 0)} Graph Edges."
    )

    # 6. Compute SHA-256 Checksum Manifest & Create Tarball Archive
    print("==> [6/6] Computing SHA-256 Manifest and Creating Portable Archive...")
    all_files = sorted(p for p in output_dir.rglob("*") if p.is_file())
    file_entries = []
    for fpath in all_files:
        rel = str(fpath.relative_to(output_dir))
        if rel == "PORTABLE_BUNDLE_MANIFEST.json":
            continue
        file_entries.append(
            {
                "path": rel,
                "size_bytes": fpath.stat().st_size,
                "sha256": sha256_file(fpath),
            }
        )

    manifest = {
        "bundle_format_version": "1.0.0",
        "okf_version": "0.2",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_project_id": source_project,
        "source_gcs_bucket": gcs_bucket,
        "gcs_pull_status": gcs_sync_result,
        "counts": {
            "okf_concepts": len(concept_files),
            "registered_skills": skills_meta["total_skills"],
            "eval_datasets": len(eval_datasets),
            "test_files": len(eval_tests),
            "total_bundled_files": len(file_entries),
        },
        "nl2kg_graph_snapshot": graph_meta,
        "files": file_entries,
    }

    manifest_path = output_dir / "PORTABLE_BUNDLE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(output_dir, arcname="gea_portable_bundle")

    archive_size_mb = archive_path.stat().st_size / (1024 * 1024)
    print("=" * 78)
    print("PORTABLE BUNDLE EXPORT COMPLETE!")
    print(f"  Directory : {output_dir}")
    print(f"  Archive   : {archive_path} ({archive_size_mb:.2f} MB)")
    print(f"  Concepts  : {len(concept_files)} OKF v0.2 files")
    print(f"  Skills    : {skills_meta['total_skills']} skills (Tier-1 + Tier-2 + plugins)")
    print(f"  Evals     : {len(eval_datasets)} golden datasets + {len(eval_tests)} pytest suites")
    print(f"  Manifest  : {manifest_path} ({len(file_entries)} SHA-256 verified files)")
    print("=" * 78)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and package all OKF v0.2 data, 28 skills, and evals into a portable bundle."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "dist" / "portable_bundle",
        help="Target directory for unpacked portable bundle (default: dist/portable_bundle)",
    )
    parser.add_argument(
        "--archive",
        type=Path,
        default=REPO_ROOT / "dist" / "gea_okf_skills_evals_portable_bundle.tar.gz",
        help="Target .tar.gz archive path (default: dist/gea_okf_skills_evals_portable_bundle.tar.gz)",
    )
    parser.add_argument(
        "--pull-from-gcs",
        action="store_true",
        help="Pull latest OKF files from live GCS bucket before creating bundle",
    )
    parser.add_argument(
        "--source-project",
        default=os.getenv("GCP_PROJECT_ID", "fivedaysai-prd-sandbox-317383"),
        help="Source GCP Project ID when using --pull-from-gcs",
    )
    parser.add_argument(
        "--gcs-bucket",
        default=os.getenv("OKF_GCS_BUCKET", "gea_agent_development_architectural_best_practices_1790796607"),
        help="Source GCS bucket name containing /okf corpus",
    )
    args = parser.parse_args()

    build_portable_bundle(
        output_dir=args.output_dir,
        archive_path=args.archive,
        pull_from_gcs=args.pull_from_gcs,
        source_project=args.source_project,
        gcs_bucket=args.gcs_bucket,
    )


if __name__ == "__main__":
    main()
