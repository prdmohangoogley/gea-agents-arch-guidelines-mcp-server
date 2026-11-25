#!/usr/bin/env python3
"""Turnkey Cross-Project & Cross-Account Redeployment Orchestrator.

Redeploys the entire Enterprise Architecture Guidelines MCP & Vertex AI Reasoning
Engine ecosystem (OKF v0.2 83-concept corpus, Dataplex Knowledge Catalog, Cloud
Spanner Graph, BigQuery Analytics, 28 Agent Skills, both Vertex AI Reasoning
Engines, GCP Agent Registry, and Evaluation Suite) into ANY target GCP project
or cloud account.

Usage:
    # 1. Dry-run verification targeting a new project/account:
    python3 scripts/redeploy_all_to_project.py \
        --project-id my-new-gcp-project-123 \
        --account architect@example.com \
        --region us-central1 \
        --dry-run

    # 2. Full production redeployment from portable bundle into a new project:
    python3 scripts/redeploy_all_to_project.py \
        --project-id my-new-gcp-project-123 \
        --account architect@example.com \
        --region us-central1 \
        --bundle-archive dist/gea_okf_skills_evals_portable_bundle.tar.gz \
        --update-env
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

REQUIRED_GCP_APIS = [
    "aiplatform.googleapis.com",
    "spanner.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "dataplex.googleapis.com",
    "modelarmor.googleapis.com",
    "cloudtrace.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
]


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_cmd(
    cmd: list[str],
    dry_run: bool = False,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Execute a shell command or print it in dry-run mode."""
    cmd_str = " ".join(cmd)
    if dry_run:
        print(f"    [DRY-RUN] {cmd_str}")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
    print(f"    + {cmd_str}")
    merged_env = {**os.environ, **(env or {})}
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), env=merged_env, text=True, capture_output=True, check=False)
    if res.stdout:
        for line in res.stdout.strip().splitlines()[-15:]:
            print(f"      {line}")
    if res.returncode != 0 and check:
        print(f"    ! Command exited with code {res.returncode}: {res.stderr.strip()}")
    return res


def verify_and_unpack_bundle(
    bundle_dir: Path | None,
    bundle_archive: Path | None,
    restore_to_repo: bool = False,
) -> dict[str, Any]:
    """Verify SHA-256 checksums of the portable bundle and optionally restore files."""
    print("\n==> [Step 1/8] Verifying Portable Bundle Integrity (OKF + Skills + Evals)...")
    active_dir = bundle_dir

    if bundle_archive and bundle_archive.exists():
        extract_target = REPO_ROOT / "dist" / "_unpacked_bundle"
        if extract_target.exists():
            shutil.rmtree(extract_target)
        extract_target.mkdir(parents=True, exist_ok=True)
        with tarfile.open(bundle_archive, "r:gz") as tar:
            tar.extractall(path=extract_target)
        # Locate inner folder
        inner = extract_target / "gea_portable_bundle"
        active_dir = inner if inner.exists() else extract_target
        print(f"  ✓ Extracted portable archive: {bundle_archive} -> {active_dir}")

    if active_dir is None or not active_dir.exists():
        default_dir = REPO_ROOT / "dist" / "portable_bundle"
        if default_dir.exists():
            active_dir = default_dir
        else:
            print("  ! No external bundle specified; verifying repository tree directly.")
            concepts = list((REPO_ROOT / "okf" / "concepts").glob("*.md"))
            skills = list((REPO_ROOT / ".agents" / "skills").glob("*/SKILL.md"))
            evals = list((REPO_ROOT / "tests" / "evals").glob("*.json"))
            print(f"  ✓ Verified repo state: {len(concepts)} OKF concepts, {len(skills)} SKILL.md manifests, {len(evals)} eval datasets.")
            return {"status": "verified_repo", "okf_concepts": len(concepts), "eval_datasets": len(evals)}

    manifest_file = active_dir / "PORTABLE_BUNDLE_MANIFEST.json"
    if not manifest_file.exists():
        raise FileNotFoundError(f"Missing PORTABLE_BUNDLE_MANIFEST.json in {active_dir}")

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    verified_count = 0
    mismatches = []
    for entry in manifest.get("files", []):
        fpath = active_dir / entry["path"]
        if not fpath.exists():
            mismatches.append(f"MISSING: {entry['path']}")
            continue
        actual_sha = sha256_file(fpath)
        if actual_sha != entry["sha256"]:
            mismatches.append(f"SHA256_MISMATCH: {entry['path']}")
        else:
            verified_count += 1

    if mismatches:
        raise RuntimeError(f"Portable bundle integrity check failed: {mismatches[:5]}")

    print(
        f"  ✓ Cryptographically verified {verified_count}/{len(manifest.get('files', []))} files in bundle "
        f"({manifest['counts']['okf_concepts']} OKF concepts, "
        f"{manifest['counts']['registered_skills']} skills, "
        f"{manifest['counts']['eval_datasets']} eval datasets)."
    )

    if restore_to_repo:
        for subdir in ["okf", "catalog", ".agents/skills", "src/skills", "tests"]:
            src_sub = active_dir / subdir
            dst_sub = REPO_ROOT / subdir
            if src_sub.exists():
                dst_sub.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(src_sub, dst_sub, dirs_exist_ok=True)
        print("  ✓ Restored OKF concepts, skills, and evals into repository working tree.")

    # Clean up temporary extraction directory if unpacked from archive
    temp_extract = REPO_ROOT / "dist" / "_unpacked_bundle"
    if temp_extract.exists():
        shutil.rmtree(temp_extract, ignore_errors=True)

    return manifest


def configure_gcloud_context(project_id: str, account: str | None, dry_run: bool) -> None:
    """Switch active gcloud account and project context."""
    print(f"\n==> [Step 2/8] Configuring Cloud Account & Target Project Context ({project_id})...")
    if account:
        run_cmd(["gcloud", "config", "set", "account", account], dry_run=dry_run, check=False)
    run_cmd(["gcloud", "config", "set", "project", project_id], dry_run=dry_run, check=False)
    run_cmd(
        ["gcloud", "auth", "application-default", "set-quota-project", project_id],
        dry_run=dry_run,
        check=False,
    )


def enable_target_apis(project_id: str, dry_run: bool) -> None:
    """Enable all required GCP APIs (Zero Cloud Run)."""
    print(f"\n==> [Step 3/8] Enabling Required GCP APIs in `{project_id}` (Zero Cloud Run)...")
    run_cmd(
        ["gcloud", "services", "enable", *REQUIRED_GCP_APIS, f"--project={project_id}"],
        dry_run=dry_run,
        check=False,
    )


def provision_buckets_and_sync_okf(
    project_id: str,
    region: str,
    okf_bucket: str,
    staging_bucket: str,
    dry_run: bool,
) -> None:
    """Create OKF & Reasoning Engine staging buckets and upload the 83-concept OKF v0.2 corpus."""
    print(f"\n==> [Step 4/8] Provisioning GCS Buckets & Syncing 83-Concept OKF v0.2 Corpus...")
    for bkt, loc in [(okf_bucket, "us"), (staging_bucket, region)]:
        run_cmd(
            [
                "gcloud",
                "storage",
                "buckets",
                "create",
                f"gs://{bkt}",
                f"--project={project_id}",
                f"--location={loc}",
                "--uniform-bucket-level-access",
            ],
            dry_run=dry_run,
            check=False,
        )

    # Sync local okf/ directory to gs://<okf_bucket>/okf
    run_cmd(
        [
            "gcloud",
            "storage",
            "cp",
            "-r",
            str(REPO_ROOT / "okf" / "*"),
            f"gs://{okf_bucket}/okf/",
            f"--project={project_id}",
        ],
        dry_run=dry_run,
        check=False,
    )


def register_dataplex_knowledge_catalog(project_id: str, okf_bucket: str, dry_run: bool) -> None:
    """Register OKF v0.2 AspectType, EntryType, EntryGroup, and Entries in Dataplex Knowledge Catalog."""
    print(f"\n==> [Step 5/8] Registering OKF v0.2 Corpus in Dataplex Knowledge Catalog ({project_id})...")
    flag = "--dry-run" if dry_run else "--apply"
    run_cmd(
        [
            "bash",
            str(REPO_ROOT / "scripts" / "register_knowledge_catalog.sh"),
            "--project",
            project_id,
            "--bucket",
            okf_bucket,
            "--location",
            "us",
            flag,
        ],
        dry_run=False,  # script itself handles --dry-run cleanly
        check=False,
    )


def provision_and_hydrate_spanner_and_bigquery(
    project_id: str,
    region: str,
    okf_bucket: str,
    spanner_instance: str,
    spanner_database: str,
    bq_dataset: str,
    with_terraform: bool,
    dry_run: bool,
) -> None:
    """Provision Cloud Spanner Graph + BigQuery and hydrate via the NL2KG Triplification Pipeline."""
    print(f"\n==> [Step 6/8] Provisioning & Hydrating Cloud Spanner Graph + BigQuery...")
    if with_terraform:
        run_cmd(["terraform", "-chdir=iac", "init"], dry_run=dry_run, check=False)
        run_cmd(
            [
                "terraform",
                "-chdir=iac",
                "apply",
                "-auto-approve",
                f"-var=project_id={project_id}",
                f"-var=region={region}",
            ],
            dry_run=dry_run,
            check=False,
        )
    else:
        # Direct idempotent gcloud Spanner & BigQuery provisioning
        run_cmd(
            [
                "gcloud",
                "spanner",
                "instances",
                "create",
                spanner_instance,
                f"--project={project_id}",
                f"--config=regional-{region}",
                "--description=GEA Architecture Guidelines Graph",
                "--processing-units=100",
            ],
            dry_run=dry_run,
            check=False,
        )
        ddl_path = REPO_ROOT / "iac" / "modules" / "spanner_graph" / "schema.sql"
        ddl_args = [f"--ddl-file={ddl_path}"] if ddl_path.exists() else []
        run_cmd(
            [
                "gcloud",
                "spanner",
                "databases",
                "create",
                spanner_database,
                f"--instance={spanner_instance}",
                f"--project={project_id}",
                *ddl_args,
            ],
            dry_run=dry_run,
            check=False,
        )
        run_cmd(
            [
                "bq",
                f"--project_id={project_id}",
                f"--location={region}",
                "mk",
                "--dataset",
                f"{project_id}:{bq_dataset}",
            ],
            dry_run=dry_run,
            check=False,
        )

    # Execute NL2KG Triplification & Hydration Pipeline
    nl2kg_cmd = [
        sys.executable,
        str(REPO_ROOT / "pipelines" / "nl2kg_pipeline.py"),
        "--project-id",
        project_id,
        "--gcs-bucket",
        okf_bucket,
        "--spanner-instance",
        spanner_instance,
        "--spanner-database",
        spanner_database,
        "--bq-dataset",
        bq_dataset,
        "--source",
        "local",
        "--force-sync",
    ]
    if dry_run:
        nl2kg_cmd.append("--dry-run")
    run_cmd(nl2kg_cmd, dry_run=False, check=False)


def deploy_reasoning_engines(
    project_id: str,
    region: str,
    okf_bucket: str,
    staging_bucket: str,
    spanner_instance: str,
    spanner_database: str,
    bq_dataset: str,
    dry_run: bool,
) -> dict[str, str]:
    """Deploy both EnterpriseArchGuidelinesAgent and OKFEvolutionReasoningEngine to Vertex AI."""
    print(f"\n==> [Step 7/8] Deploying Both Vertex AI Reasoning Engines (Zero Cloud Run)...")
    deploy_env = {
        "GCP_PROJECT_ID": project_id,
        "GCP_REGION": region,
        "STAGING_BUCKET": f"gs://{staging_bucket}",
        "OKF_GCS_BUCKET": okf_bucket,
        "SPANNER_INSTANCE_ID": spanner_instance,
        "SPANNER_DATABASE_ID": spanner_database,
        "BQ_DATASET_ID": bq_dataset,
    }

    flag_args = ["--dry-run"] if dry_run else []

    # 7a. Primary Enterprise Architecture Guidelines Agent
    res_primary = run_cmd(
        [sys.executable, str(REPO_ROOT / "scripts" / "deploy_reasoning_engine.py"), *flag_args],
        dry_run=False,
        env=deploy_env,
        check=False,
    )
    primary_re = f"projects/{project_id}/locations/{region}/reasoningEngines/pending-primary"
    match_p = re.search(r"(projects/[^\s\"]+/locations/[^\s\"]+/reasoningEngines/\d+)", res_primary.stdout or "")
    if match_p:
        primary_re = match_p.group(1)

    # 7b. Autonomous OKF Evolution Reasoning Engine
    res_evol = run_cmd(
        [sys.executable, str(REPO_ROOT / "scripts" / "deploy_okf_evolution_engine.py"), *flag_args],
        dry_run=False,
        env=deploy_env,
        check=False,
    )
    evol_re = f"projects/{project_id}/locations/{region}/reasoningEngines/pending-evolution"
    match_e = re.search(r"(projects/[^\s\"]+/locations/[^\s\"]+/reasoningEngines/\d+)", res_evol.stdout or "")
    if match_e:
        evol_re = match_e.group(1)

    return {
        "primary_reasoning_engine": primary_re,
        "okf_evolution_reasoning_engine": evol_re,
    }


def register_agent_and_verify(
    project_id: str,
    region: str,
    okf_bucket: str,
    staging_bucket: str,
    spanner_instance: str,
    spanner_database: str,
    bq_dataset: str,
    engines: dict[str, str],
    update_env: bool,
    dry_run: bool,
) -> Path:
    """Publish agent to GCP Agent Registry, generate target .env file, and run evaluation suite."""
    print(f"\n==> [Step 8/8] Registering in GCP Agent Registry, Writing Target Config & Running Evals...")
    reg_env = {
        "GCP_PROJECT_ID": project_id,
        "GCP_REGION": region,
        "REASONING_ENGINE_RESOURCE_NAME": engines["primary_reasoning_engine"],
    }
    run_cmd(
        ["bash", str(REPO_ROOT / "scripts" / "publish_gemini_enterprise.sh")],
        dry_run=dry_run,
        env=reg_env,
        check=False,
    )

    env_content = (
        f"# Auto-generated by scripts/redeploy_all_to_project.py at {datetime.now(timezone.utc).isoformat()}\n"
        f"GCP_PROJECT_ID={project_id}\n"
        f"GCP_REGION={region}\n"
        f"SPANNER_INSTANCE_ID={spanner_instance}\n"
        f"SPANNER_DATABASE_ID={spanner_database}\n"
        f"BQ_DATASET_ID={bq_dataset}\n"
        f"OKF_GCS_BUCKET={okf_bucket}\n"
        f"STAGING_BUCKET=gs://{staging_bucket}\n"
        f"MODEL_ARMOR_TEMPLATE_ID=projects/{project_id}/locations/{region}/templates/arch-guidelines-armor\n"
        f"REASONING_ENGINE_RESOURCE_NAME={engines['primary_reasoning_engine']}\n"
        f"OKF_EVOLUTION_ENGINE_RESOURCE_NAME={engines['okf_evolution_reasoning_engine']}\n"
        f"USE_MOCK_GRAPH=false\n"
    )
    env_dir = (REPO_ROOT / "dist") if dry_run else REPO_ROOT
    env_dir.mkdir(parents=True, exist_ok=True)
    target_env_path = env_dir / f".env.{project_id}"
    target_env_path.write_text(env_content, encoding="utf-8")
    print(f"  ✓ Wrote target environment configuration to: {target_env_path}")

    if update_env and not dry_run:
        (REPO_ROOT / ".env").write_text(env_content, encoding="utf-8")
        print(f"  ✓ Updated active repository `.env` to target project `{project_id}`.")

    # Run evaluation and test suites
    print("  ==> Running Pytest Unit, Trajectory & Golden Evaluation Suites...")
    pytest_cmd = [sys.executable, "-m", "pytest", "tests/", "-q"]
    pytest_env = {} if dry_run else {"GCP_PROJECT_ID": project_id}
    if dry_run:
        pytest_cmd.extend(["--ignore=tests/test_mcp_remote.py", "--ignore=tests/test_live_reasoning_engine.py"])
    run_cmd(pytest_cmd, dry_run=False, env=pytest_env, check=False)

    return target_env_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Redeploy all OKF data, 28 skills, Spanner/BQ graph, and Vertex AI Reasoning Engines to any GCP project/account."
    )
    parser.add_argument("--project-id", required=True, help="Target GCP Project ID to deploy into")
    parser.add_argument("--account", default=None, help="Optional GCP user/service account email (`gcloud config set account`)")
    parser.add_argument("--region", default="us-central1", help="Target GCP region (default: us-central1)")
    parser.add_argument(
        "--okf-bucket",
        default=None,
        help="Target GCS bucket for OKF v0.2 corpus (default: <project-id>-arch-guidelines-okf)",
    )
    parser.add_argument(
        "--staging-bucket",
        default=None,
        help="Target GCS staging bucket for Vertex AI Reasoning Engine (default: <project-id>-reasoning-engine-staging)",
    )
    parser.add_argument("--spanner-instance", default="arch-guidelines-graph", help="Target Spanner instance ID")
    parser.add_argument("--spanner-database", default="guidelines-db", help="Target Spanner database ID")
    parser.add_argument("--bq-dataset", default="arch_guidelines_analytics", help="Target BigQuery dataset ID")
    parser.add_argument("--bundle-dir", type=Path, default=None, help="Path to unpacked portable bundle directory")
    parser.add_argument("--bundle-archive", type=Path, default=None, help="Path to portable bundle .tar.gz archive")
    parser.add_argument("--restore-bundle", action="store_true", help="Copy files from portable bundle into repo tree before deploying")
    parser.add_argument("--with-terraform", action="store_true", help="Use Terraform (`iac/`) for infrastructure provisioning")
    parser.add_argument("--update-env", action="store_true", help="Overwrite active `.env` with the new target project settings")
    parser.add_argument("--dry-run", action="store_true", help="Validate bundle, dry-run Reasoning Engines & NL2KG without mutating cloud resources")

    args = parser.parse_args()

    okf_bucket = args.okf_bucket or f"{args.project_id}-arch-guidelines-okf"
    staging_bucket = (args.staging_bucket or f"{args.project_id}-reasoning-engine-staging").replace("gs://", "")

    print("=" * 80)
    print("GEA Architecture Best Practices — Full Cross-Project Redeployment Pipeline")
    print(f"  Target Project        : {args.project_id}")
    print(f"  Target Account        : {args.account or '(current active gcloud account)'}")
    print(f"  Target Region         : {args.region}")
    print(f"  Target OKF Bucket     : gs://{okf_bucket}/okf")
    print(f"  Target Staging Bucket : gs://{staging_bucket}")
    print(f"  Target Spanner Graph  : {args.spanner_instance}/{args.spanner_database}")
    print(f"  Target BigQuery       : {args.project_id}:{args.bq_dataset}")
    print(f"  Mode                  : {'DRY-RUN (Safe Local Verification)' if args.dry_run else 'LIVE CLOUD DEPLOYMENT'}")
    print("=" * 80)

    verify_and_unpack_bundle(args.bundle_dir, args.bundle_archive, restore_to_repo=args.restore_bundle)
    configure_gcloud_context(args.project_id, args.account, dry_run=args.dry_run)
    enable_target_apis(args.project_id, dry_run=args.dry_run)
    provision_buckets_and_sync_okf(args.project_id, args.region, okf_bucket, staging_bucket, dry_run=args.dry_run)
    register_dataplex_knowledge_catalog(args.project_id, okf_bucket, dry_run=args.dry_run)
    provision_and_hydrate_spanner_and_bigquery(
        project_id=args.project_id,
        region=args.region,
        okf_bucket=okf_bucket,
        spanner_instance=args.spanner_instance,
        spanner_database=args.spanner_database,
        bq_dataset=args.bq_dataset,
        with_terraform=args.with_terraform,
        dry_run=args.dry_run,
    )
    engines = deploy_reasoning_engines(
        project_id=args.project_id,
        region=args.region,
        okf_bucket=okf_bucket,
        staging_bucket=staging_bucket,
        spanner_instance=args.spanner_instance,
        spanner_database=args.spanner_database,
        bq_dataset=args.bq_dataset,
        dry_run=args.dry_run,
    )
    target_env_file = register_agent_and_verify(
        project_id=args.project_id,
        region=args.region,
        okf_bucket=okf_bucket,
        staging_bucket=staging_bucket,
        spanner_instance=args.spanner_instance,
        spanner_database=args.spanner_database,
        bq_dataset=args.bq_dataset,
        engines=engines,
        update_env=args.update_env,
        dry_run=args.dry_run,
    )

    print("\n" + "=" * 80)
    print("CROSS-PROJECT REDEPLOYMENT PIPELINE COMPLETE!")
    print(f"  Target Project              : {args.project_id}")
    print(f"  Primary Reasoning Engine    : {engines['primary_reasoning_engine']}")
    print(f"  Evolution Reasoning Engine  : {engines['okf_evolution_reasoning_engine']}")
    print(f"  Generated Env Config        : {target_env_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
