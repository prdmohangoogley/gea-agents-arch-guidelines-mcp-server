#!/usr/bin/env python3
"""From-Scratch End-to-End Deployment & Verification Orchestrator (`deploy_from_scratch.py`).

Deploys the entire Enterprise Architecture Guidelines MCP Server, 92 OKF v0.2 concepts
(L200, L300, L400, and Well-Architected Pillars) from the local gitignored `data/` folder,
Dataplex Universal Catalog Knowledge Base, Cloud Spanner Graph, BigQuery Analytics,
Vertex AI Reasoning Engines, Gemini Enterprise Agent Registry, and runs the complete
MCP + All-38-Skills Runbook + Evaluation test suites into ANY target GCP project and account.

Usage:
    # 1. Dry-run verification targeting a new project and cloud account:
    uv run python scripts/deploy_from_scratch.py \
        --project-id my-argolis-project-id \
        --account admin@my-argolis-domain.com \
        --region us-central1 \
        --dry-run

    # 2. Live full production deployment from scratch into a new project and account:
    uv run python scripts/deploy_from_scratch.py \
        --project-id my-argolis-project-id \
        --account admin@my-argolis-domain.com \
        --region us-central1 \
        --update-env \
        --update-antigravity-config
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
DATA_OKF_DIR = DATA_DIR / "okf"

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
    "discoveryengine.googleapis.com",
]


def run_cmd(
    cmd: list[str],
    dry_run: bool = False,
    env: dict[str, str] | None = None,
    check: bool = False,
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
        for line in res.stdout.strip().splitlines()[-12:]:
            print(f"      {line}")
    if res.returncode != 0 and check:
        raise RuntimeError(f"Command failed ({res.returncode}): {cmd_str}\n{res.stderr}")
    return res


def stage1_verify_local_data_folder() -> dict[str, Any]:
    """Verify that `data/` contains all 92 deduplicated L200, L300, L400, and WAF_Pillars OKFs."""
    print("\n==> [Stage 1/8] Verifying Local `data/` Folder Integrity (L200 + L300 + L400 + WAF Pillars)...")
    if not DATA_OKF_DIR.exists():
        raise FileNotFoundError(
            f"Missing `{DATA_OKF_DIR}`. Ensure the local `data/` folder is present before running deploy_from_scratch.py."
        )

    main_concepts = sorted((DATA_OKF_DIR / "concepts").glob("*.md"))
    waf_concepts = sorted((DATA_OKF_DIR / "pca_waf" / "concepts").glob("*.md"))
    skills_md = sorted((REPO_ROOT / ".agents" / "skills").glob("*/SKILL.md"))

    if len(main_concepts) < 83 or len(waf_concepts) < 9:
        raise RuntimeError(
            f"Expected at least 83 main OKF concepts and 9 WAF concepts in `data/okf/`, found {len(main_concepts)} and {len(waf_concepts)}."
        )

    manifest = json.loads((DATA_OKF_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
    waf_manifest = json.loads((DATA_OKF_DIR / "pca_waf" / "MANIFEST.json").read_text(encoding="utf-8"))

    print(
        f"  ✓ Verified `data/okf/`: {len(main_concepts)} L200/L300/L400 concepts + {len(waf_concepts)} WAF Pillar concepts "
        f"= {len(main_concepts) + len(waf_concepts)} total OKF concepts"
    )
    print(f"  ✓ Version Tag: {manifest.get('version_tag')} | 6-Month Expiry (`stale_after`): {manifest.get('stale_after')}")
    print(f"  ✓ Verified {len(skills_md)} Antigravity `.agents/skills/*/SKILL.md` directories")
    return {"main_manifest": manifest, "waf_manifest": waf_manifest}


def stage2_configure_account_and_project(project_id: str, account: str | None, dry_run: bool) -> None:
    """Switch active gcloud account and project context."""
    print(f"\n==> [Stage 2/8] Configuring Cloud Account & Project Context (`{project_id}`)...")
    if account:
        run_cmd(["gcloud", "config", "set", "account", account], dry_run=dry_run)
    run_cmd(["gcloud", "config", "set", "project", project_id], dry_run=dry_run)
    run_cmd(["gcloud", "auth", "application-default", "set-quota-project", project_id], dry_run=dry_run)


def stage3_enable_gcp_apis(project_id: str, dry_run: bool) -> None:
    """Enable required GCP APIs in the target project."""
    print(f"\n==> [Stage 3/8] Enabling Required GCP APIs in `{project_id}`...")
    run_cmd(["gcloud", "services", "enable", *REQUIRED_GCP_APIS, f"--project={project_id}"], dry_run=dry_run)


def stage4_provision_gcs_and_copy_data(
    project_id: str,
    region: str,
    okf_bucket: str,
    waf_bucket: str,
    staging_bucket: str,
    dry_run: bool,
) -> None:
    """Provision multi-region OKF & WAF buckets + regional staging bucket, and copy `data/` to Cloud Storage."""
    print(f"\n==> [Stage 4/8] Provisioning Cloud Storage Buckets & Copying `data/` to GCS...")
    buckets = [
        (okf_bucket, "us", "corpus=gea_unified_okf,format=okf_v0_2"),
        (waf_bucket, "us", "corpus=geap_waf_pillars,format=okf_v0_2,framework=well-architected"),
        (staging_bucket, region, "purpose=reasoning-engine-staging"),
    ]
    for bkt, loc, labels in buckets:
        run_cmd(
            [
                "gcloud", "storage", "buckets", "create", f"gs://{bkt}",
                f"--project={project_id}",
                f"--location={loc}",
                "--uniform-bucket-level-access",
                "--public-access-prevention",
            ],
            dry_run=dry_run,
        )
        run_cmd(
            [
                "gcloud", "storage", "buckets", "update", f"gs://{bkt}",
                f"--project={project_id}",
                "--versioning",
                "--uniform-bucket-level-access",
                "--public-access-prevention",
                f"--update-labels={labels}",
            ],
            dry_run=dry_run,
        )

    # Sync data/okf and data/{L200,L300,L400,WAF_Pillars} to Cloud Storage
    waf_vtag = "WAF_OKF_2026-11-24_182000"
    sync_pairs = [
        (str(DATA_OKF_DIR), f"gs://{okf_bucket}/okf"),
        (str(DATA_DIR / "L200"), f"gs://{okf_bucket}/tiers/L200"),
        (str(DATA_DIR / "L300"), f"gs://{okf_bucket}/tiers/L300"),
        (str(DATA_DIR / "L400"), f"gs://{okf_bucket}/tiers/L400"),
        (str(DATA_DIR / "WAF_Pillars"), f"gs://{okf_bucket}/tiers/WAF_Pillars"),
        (str(DATA_OKF_DIR / "pca_waf"), f"gs://{waf_bucket}/{waf_vtag}/okf"),
        (str(DATA_OKF_DIR / "pca_waf"), f"gs://{waf_bucket}/okf"),
    ]
    for src_path, dst_uri in sync_pairs:
        if Path(src_path).exists():
            run_cmd(
                ["gcloud", "storage", "rsync", "--recursive", src_path, dst_uri, f"--project={project_id}"],
                dry_run=dry_run,
            )


def _upsert_dataplex_entry_worker(args_tuple: tuple[str, str, str, Path, str, str, str]) -> str:
    """Create or update a single Dataplex entry via gcloud CLI."""
    project_id, eg, entry_id, aspect_file, gcs_uri, display_name, description = args_tuple
    create_cmd = [
        "gcloud", "dataplex", "entries", "create", entry_id,
        f"--project={project_id}",
        "--location=us",
        f"--entry-group={eg}",
        f"--entry-type=projects/{project_id}/locations/us/entryTypes/okf-bundle",
        f"--entry-source-resource={gcs_uri}",
        f"--entry-source-display-name={display_name[:80]}",
        f"--entry-source-description={description[:200]}",
        f"--aspects={aspect_file}",
    ]
    proc = subprocess.run(create_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
    if proc.returncode == 0:
        return f"created:{eg}/{entry_id}"
    if "ALREADY_EXISTS" in proc.stdout or "already exists" in proc.stdout:
        upd_cmd = [
            "gcloud", "dataplex", "entries", "update", entry_id,
            f"--project={project_id}",
            "--location=us",
            f"--entry-group={eg}",
            f"--update-aspects={aspect_file}",
        ]
        uproc = subprocess.run(upd_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
        if uproc.returncode == 0:
            return f"updated:{eg}/{entry_id}"
        return f"error:{eg}/{entry_id}:{uproc.stdout[:120]}"
    return f"error:{eg}/{entry_id}:{proc.stdout[:120]}"


def stage5_propagate_to_dataplex(
    project_id: str,
    okf_bucket: str,
    waf_bucket: str,
    manifests: dict[str, Any],
    dry_run: bool,
) -> None:
    """Create Dataplex AspectType, EntryTypes, EntryGroups, and propagate all 92 OKF concepts."""
    print(f"\n==> [Stage 5/8] Propagating All 92 OKF Concepts from `data/` to Dataplex Universal Catalog (`{project_id}`)...")
    aspect_schema_path = REPO_ROOT / "catalog" / "aspect-type-okf.json"

    run_cmd(
        [
            "gcloud", "dataplex", "aspect-types", "create", "okf",
            f"--project={project_id}",
            "--location=us",
            f"--metadata-template-file-name={aspect_schema_path}",
        ],
        dry_run=dry_run,
    )
    for et_id, et_name in [("okf-bundle", "OKF Bundle Concept"), ("okf-concept", "OKF PCA WAF Concept")]:
        run_cmd(
            [
                "gcloud", "dataplex", "entry-types", "create", et_id,
                f"--project={project_id}",
                "--location=us",
                f"--display-name={et_name}",
                "--description=Open Knowledge Format v0.2 Architectural Concept Document",
            ],
            dry_run=dry_run,
        )
    for eg_id, eg_name in [
        ("geap-architecture-kb", "GEA Agent Development - Unified L200/L300/L400/WAF Architecture KB"),
        ("geap-pca-waf-kb", "Google Cloud PCA & Well-Architected Framework OKF Knowledge Base"),
    ]:
        run_cmd(
            [
                "gcloud", "dataplex", "entry-groups", "create", eg_id,
                f"--project={project_id}",
                "--location=us",
                f"--display-name={eg_name}",
            ],
            dry_run=dry_run,
        )

    if dry_run:
        print("    [DRY-RUN] Would upsert 92 entries in geap-architecture-kb and 9 entries in geap-pca-waf-kb.")
        return

    # Rewrite aspect keys dynamically for target `project_id`
    build_aspects_dir = REPO_ROOT / "build" / f"dataplex-aspects-{project_id}"
    build_aspects_dir.mkdir(parents=True, exist_ok=True)
    target_aspect_key = f"{project_id}.us.okf"

    tasks: list[tuple[str, str, str, Path, str, str, str]] = []
    for doc in manifests["main_manifest"].get("documents", []):
        doc_id = doc["document_id"]
        tier = doc.get("tier", "L200")
        src_cat_file = DATA_OKF_DIR / "catalog-entries" / f"{doc_id}.json"
        raw_cat = json.loads(src_cat_file.read_text(encoding="utf-8"))
        first_val = next(iter(raw_cat.values()))
        data_block = first_val.get("data", {})

        out_aspect = {target_aspect_key: {"data": data_block}}
        out_file = build_aspects_dir / f"{doc_id}.json"
        out_file.write_text(json.dumps(out_aspect, indent=2) + "\n", encoding="utf-8")

        gcs_uri = f"gs://{okf_bucket}/{doc['source_url']}"
        tasks.append((
            project_id,
            "geap-architecture-kb",
            doc_id,
            out_file,
            gcs_uri,
            f"[{tier}] {doc['title']}",
            doc["title"],
        ))

    waf_vtag = manifests["waf_manifest"].get("version_tag", "WAF_OKF_2026-11-24_182000")
    for wc in manifests["waf_manifest"].get("concepts", []):
        slug = wc["slug"]
        cid = wc["id"]
        src_cat_file = DATA_OKF_DIR / "pca_waf" / "catalog-entries" / f"{slug}.json"
        raw_cat = json.loads(src_cat_file.read_text(encoding="utf-8"))
        aspects_map = raw_cat.get("aspects", raw_cat)
        first_val = next(iter(aspects_map.values()))
        data_block = first_val.get("data", {})

        out_aspect = {target_aspect_key: {"data": data_block}}
        out_file = build_aspects_dir / f"waf-{slug}.json"
        out_file.write_text(json.dumps(out_aspect, indent=2) + "\n", encoding="utf-8")

        gcs_uri = f"gs://{waf_bucket}/{waf_vtag}/okf/concepts/{slug}.md"
        tasks.append((
            project_id,
            "geap-architecture-kb",
            f"pca-waf-{slug}",
            out_file,
            gcs_uri,
            f"[WAF] {cid}: {wc['title']}",
            wc["description"],
        ))
        tasks.append((
            project_id,
            "geap-pca-waf-kb",
            slug,
            out_file,
            gcs_uri,
            f"[WAF] {cid}: {wc['title']}",
            wc["description"],
        ))

    created, updated, errors = 0, 0, 0
    with ThreadPoolExecutor(max_workers=10) as pool:
        for fut in as_completed([pool.submit(_upsert_dataplex_entry_worker, t) for t in tasks]):
            r = fut.result()
            if r.startswith("created:"):
                created += 1
            elif r.startswith("updated:"):
                updated += 1
            else:
                errors += 1
    print(f"  ✓ Dataplex Knowledge Base Synced: {created} created, {updated} updated, {errors} errors")


def stage6_provision_and_hydrate_spanner_and_bq(
    project_id: str,
    region: str,
    okf_bucket: str,
    spanner_instance: str,
    spanner_database: str,
    bq_dataset: str,
    manifests: dict[str, Any],
    dry_run: bool,
) -> None:
    """Provision Cloud Spanner Graph + BigQuery and hydrate all 92 OKF concepts, WAF patterns, and anti-patterns."""
    print(f"\n==> [Stage 6/8] Provisioning & Hydrating Cloud Spanner Graph (`{spanner_instance}/{spanner_database}`) & BigQuery...")
    run_cmd(
        [
            "gcloud", "spanner", "instances", "create", spanner_instance,
            f"--project={project_id}",
            f"--config=regional-{region}",
            "--description=GEA Arch Guidelines Graph",
            "--edition=ENTERPRISE",
            "--processing-units=100",
        ],
        dry_run=dry_run,
    )
    ddl_path = REPO_ROOT / "iac" / "modules" / "spanner" / "schema.sql"
    if not ddl_path.exists():
        ddl_path = REPO_ROOT / "iac" / "modules" / "spanner_graph" / "schema.sql"
    ddl_args = [f"--ddl-file={ddl_path}"] if ddl_path.exists() else []
    run_cmd(
        [
            "gcloud", "spanner", "databases", "create", spanner_database,
            f"--instance={spanner_instance}",
            f"--project={project_id}",
            *ddl_args,
        ],
        dry_run=dry_run,
    )
    run_cmd(
        ["bq", f"--project_id={project_id}", f"--location={region}", "mk", "--dataset", f"{project_id}:{bq_dataset}"],
        dry_run=dry_run,
    )

    # Run NL2KG pipeline pointing at `data/okf/concepts`
    nl2kg_cmd = [
        sys.executable,
        str(REPO_ROOT / "pipelines" / "nl2kg_pipeline.py"),
        "--project-id", project_id,
        "--local-dir", str(DATA_OKF_DIR / "concepts"),
        "--gcs-bucket", okf_bucket,
        "--spanner-instance", spanner_instance,
        "--spanner-database", spanner_database,
        "--bq-dataset", bq_dataset,
        "--source", "local",
        "--force-sync",
    ]
    if dry_run:
        nl2kg_cmd.append("--dry-run")
    run_cmd(nl2kg_cmd, dry_run=False)


def stage7_deploy_mcp_and_reasoning_engines(
    project_id: str,
    region: str,
    okf_bucket: str,
    staging_bucket: str,
    spanner_instance: str,
    spanner_database: str,
    bq_dataset: str,
    update_env: bool,
    update_antigravity_config: bool,
    dry_run: bool,
) -> dict[str, str]:
    """Deploy Vertex AI Reasoning Engines, register in Gemini Enterprise Agent Registry, and update MCP configs."""
    print(f"\n==> [Stage 7/8] Deploying Vertex AI Reasoning Engines & Updating MCP Configurations...")
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

    res_p = run_cmd([sys.executable, str(REPO_ROOT / "scripts" / "deploy_reasoning_engine.py"), *flag_args], env=deploy_env)
    primary_re = f"projects/{project_id}/locations/{region}/reasoningEngines/enterprise-arch-agent"
    mp = re.search(r"(projects/[^\s\"]+/locations/[^\s\"]+/reasoningEngines/\d+)", res_p.stdout or "")
    if mp:
        primary_re = mp.group(1)

    res_e = run_cmd([sys.executable, str(REPO_ROOT / "scripts" / "deploy_okf_evolution_engine.py"), *flag_args], env=deploy_env)
    evol_re = f"projects/{project_id}/locations/{region}/reasoningEngines/okf-evolution-agent"
    me = re.search(r"(projects/[^\s\"]+/locations/[^\s\"]+/reasoningEngines/\d+)", res_e.stdout or "")
    if me:
        evol_re = me.group(1)

    # Publish to Gemini Enterprise / Agent Registry
    run_cmd(
        ["bash", str(REPO_ROOT / "scripts" / "publish_gemini_enterprise.sh")],
        dry_run=dry_run,
        env={**deploy_env, "REASONING_ENGINE_RESOURCE_NAME": primary_re},
    )

    env_text = (
        f"# Auto-generated by scripts/deploy_from_scratch.py at {datetime.now(timezone.utc).isoformat()}\n"
        f"GCP_PROJECT_ID={project_id}\n"
        f"GCP_REGION={region}\n"
        f"SPANNER_INSTANCE_ID={spanner_instance}\n"
        f"SPANNER_DATABASE_ID={spanner_database}\n"
        f"BQ_DATASET_ID={bq_dataset}\n"
        f"OKF_GCS_BUCKET={okf_bucket}\n"
        f"STAGING_BUCKET=gs://{staging_bucket}\n"
        f"REASONING_ENGINE_RESOURCE_NAME={primary_re}\n"
        f"OKF_EVOLUTION_ENGINE_RESOURCE_NAME={evol_re}\n"
        f"USE_MOCK_GRAPH=false\n"
    )
    out_env = (REPO_ROOT / "dist" / f".env.{project_id}") if dry_run else (REPO_ROOT / f".env.{project_id}")
    out_env.parent.mkdir(parents=True, exist_ok=True)
    out_env.write_text(env_text, encoding="utf-8")

    if update_env and not dry_run:
        (REPO_ROOT / ".env").write_text(env_text, encoding="utf-8")
        print(f"  ✓ Updated `.env` to point to project `{project_id}`")

    if update_antigravity_config and not dry_run:
        mcp_cfg_path = Path.home() / ".gemini" / "config" / "mcp_config.json"
        if mcp_cfg_path.exists():
            cfg = json.loads(mcp_cfg_path.read_text(encoding="utf-8"))
            for srv in ["arch-guidelines", "gea-arch-guidelines"]:
                if srv in cfg.get("mcpServers", {}):
                    cfg["mcpServers"][srv]["env"].update({
                        "GCP_PROJECT_ID": project_id,
                        "PROJECT_ID": project_id,
                        "SPANNER_INSTANCE_ID": spanner_instance,
                        "SPANNER_DATABASE_ID": spanner_database,
                        "BQ_DATASET_ID": bq_dataset,
                        "CLOUDSDK_CORE_PROJECT": project_id,
                    })
            mcp_cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
            print(f"  ✓ Updated `~/.gemini/config/mcp_config.json` to target project `{project_id}`")

    return {"primary_reasoning_engine": primary_re, "okf_evolution_reasoning_engine": evol_re}


def stage8_run_all_mcp_and_runbook_tests(project_id: str, dry_run: bool) -> None:
    """Run the entire MCP server test suite, including the single All-38-Skills Runbook Test and Evaluations."""
    print("\n==> [Stage 8/8] Running Complete MCP Test Suite + All-38-Skills Runbook Test + Evaluation Suite...")
    pytest_cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_all_38_skills_runbook.py",
        "tests/test_pca_waf_okf_skills.py",
        "tests/test_new_tools.py",
        "tests/test_okf_fde_audit_remediations.py",
        "tests/test_mcp_local.py",
        "tests/test_model_armor.py",
        "tests/test_model_router.py",
        "tests/test_pipeline.py",
        "tests/test_server.py",
        "-v",
    ]
    res = run_cmd(pytest_cmd, dry_run=False, check=True)
    print("  ✓ All MCP server tests and all 38 skills in the runbook test passed!")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deploy the entire Architecture Best Practices MCP Server, `data/` OKF corpus, Dataplex KB, Spanner Graph, and 38 Skills from scratch."
    )
    parser.add_argument("--project-id", required=True, help="Target GCP Project ID (e.g. Argolis project ID)")
    parser.add_argument("--account", default=None, help="Target GCP account email (`gcloud config set account`)")
    parser.add_argument("--region", default="us-central1", help="Target GCP region (default: us-central1)")
    parser.add_argument("--okf-bucket", default=None, help="Target GCS bucket for unified OKF corpus")
    parser.add_argument("--waf-bucket", default=None, help="Target GCS bucket for WAF Pillars OKF corpus")
    parser.add_argument("--staging-bucket", default=None, help="Target GCS staging bucket for Reasoning Engines")
    parser.add_argument("--spanner-instance", default="gea-arch-guidelines-spanner", help="Target Spanner instance ID")
    parser.add_argument("--spanner-database", default="arch_guidelines_graph", help="Target Spanner database ID")
    parser.add_argument("--bq-dataset", default="gea_arch_guidelines_analytics", help="Target BigQuery dataset ID")
    parser.add_argument("--update-env", action="store_true", help="Update repository `.env` with target project")
    parser.add_argument("--update-antigravity-config", action="store_true", help="Update `~/.gemini/config/mcp_config.json` with target project")
    parser.add_argument("--dry-run", action="store_true", help="Verify `data/`, dry-run cloud mutations, and execute the full test suite")

    args = parser.parse_args()

    okf_bucket = args.okf_bucket or (
        "gea_agent_development_architectural_best_practices_1790796607"
        if args.project_id == "fivedaysai-prd-sandbox-317383"
        else f"{args.project_id}-arch-guidelines-okf"
    )
    waf_bucket = args.waf_bucket or (
        "gea_agent_development_architectural_best_practices_pca_waf"
        if args.project_id == "fivedaysai-prd-sandbox-317383"
        else f"{args.project_id}-arch-guidelines-pca-waf"
    )
    staging_bucket = (args.staging_bucket or f"{args.project_id}-reasoning-engine-staging").replace("gs://", "")

    print("=" * 85)
    print("FROM-SCRATCH DEPLOYMENT PIPELINE — GEA Architecture Best Practices MCP & 92 OKFs")
    print(f"  Target GCP Project    : {args.project_id}")
    print(f"  Target Cloud Account  : {args.account or '(current active gcloud account)'}")
    print(f"  Target Region         : {args.region}")
    print(f"  Source Data Directory : {DATA_DIR} (92 deduplicated L200/L300/L400/WAF OKFs)")
    print(f"  Target OKF Bucket     : gs://{okf_bucket}")
    print(f"  Target WAF Bucket     : gs://{waf_bucket}")
    print(f"  Target Spanner Graph  : {args.spanner_instance}/{args.spanner_database}")
    print(f"  Target BigQuery       : {args.project_id}:{args.bq_dataset}")
    print(f"  Execution Mode        : {'DRY-RUN + FULL TEST SUITE' if args.dry_run else 'LIVE CLOUD DEPLOYMENT'}")
    print("=" * 85)

    manifests = stage1_verify_local_data_folder()
    stage2_configure_account_and_project(args.project_id, args.account, dry_run=args.dry_run)
    stage3_enable_gcp_apis(args.project_id, dry_run=args.dry_run)
    stage4_provision_gcs_and_copy_data(
        args.project_id, args.region, okf_bucket, waf_bucket, staging_bucket, dry_run=args.dry_run
    )
    stage5_propagate_to_dataplex(args.project_id, okf_bucket, waf_bucket, manifests, dry_run=args.dry_run)
    stage6_provision_and_hydrate_spanner_and_bq(
        args.project_id,
        args.region,
        okf_bucket,
        args.spanner_instance,
        args.spanner_database,
        args.bq_dataset,
        manifests,
        dry_run=args.dry_run,
    )
    engines = stage7_deploy_mcp_and_reasoning_engines(
        args.project_id,
        args.region,
        okf_bucket,
        staging_bucket,
        args.spanner_instance,
        args.spanner_database,
        args.bq_dataset,
        args.update_env,
        args.update_antigravity_config,
        dry_run=args.dry_run,
    )
    stage8_run_all_mcp_and_runbook_tests(args.project_id, dry_run=args.dry_run)

    print("\n" + "=" * 85)
    print("FROM-SCRATCH DEPLOYMENT & VERIFICATION COMPLETE!")
    print(f"  Project ID                 : {args.project_id}")
    print(f"  Primary Reasoning Engine   : {engines['primary_reasoning_engine']}")
    print(f"  Evolution Reasoning Engine : {engines['okf_evolution_reasoning_engine']}")
    print("=" * 85)


if __name__ == "__main__":
    main()
