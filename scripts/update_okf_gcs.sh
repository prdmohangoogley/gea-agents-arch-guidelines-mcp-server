#!/usr/bin/env bash
# =============================================================================
# update_okf_gcs.sh — Cloud Shell & Terraform OKF v0.2 GCS Update Orchestrator
# =============================================================================
# Repository : https://github.com/prdmohangoogley/gea-agents-arch-guidelines-mcp-server
# Living Spec: docs/specs/okf-gcs-update-spec.md
#
# Updates the existing Open Knowledge Format (OKF v0.2) bundle in Google Cloud
# Storage (gs://gea_agent_development_architectural_best_practices_1790796607/okf)
# with the unified 36-concept bundle (00: FDE Grading Rubric, 01..20: L200,
# 21..35: L300), preserving version_tag (GEAPL200_2026-09-30_124746) and
# 180-day stale_after TTL semantics.
#
# Usage:
#   ./scripts/update_okf_gcs.sh [options]
#
# Options:
#   --project ID          GCP project ID (default: fivedaysai-prd-sandbox-317383)
#   --project-number NUM  Expected project number guard (default: 301802433103)
#   --bucket NAME         Target GCS bucket (default: gea_agent_development_architectural_best_practices_1790796607)
#   --location LOC        Multi-region location (default: us)
#   --bundle-dir DIR      Local OKF v0.2 bundle directory (auto-detected: okf/ or L300_concepts/)
#   --with-terraform      Run Terraform (iac/) before syncing the OKF bundle to GCS
#   --catalog             Also register/update all 36 entries in GCP Knowledge Catalog (Dataplex)
#   --run-nl2kg           Trigger the downstream NL2KG Spanner/BigQuery ingestion pipeline after sync
#   --create-if-missing   Create the GCS bucket if it does not already exist
#   --readers PRINCIPALS  Comma-separated IAM principals to grant roles/storage.objectViewer
#   --dry-run             Run offline structural QA and print gcloud/terraform commands without mutating GCP
#   -h, --help            Show this help message
# =============================================================================

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-fivedaysai-prd-sandbox-317383}"
PROJECT_NUMBER="${PROJECT_NUMBER:-301802433103}"
BUCKET_NAME="${BUCKET_NAME:-gea_agent_development_architectural_best_practices_1790796607}"
LOCATION="${LOCATION:-us}"
BUNDLE_DIR="${BUNDLE_DIR:-}"
WITH_TERRAFORM="false"
DO_CATALOG="false"
RUN_NL2KG="false"
CREATE_IF_MISSING="false"
READER_PRINCIPALS="${READER_PRINCIPALS:-}"
DRY_RUN="false"

while [ $# -gt 0 ]; do
  case "$1" in
    --project)           PROJECT_ID="$2"; shift 2 ;;
    --project-number)    PROJECT_NUMBER="$2"; shift 2 ;;
    --bucket|--bucket-name) BUCKET_NAME="$2"; shift 2 ;;
    --location)          LOCATION="$(printf '%s' "$2" | tr '[:upper:]' '[:lower:]')"; shift 2 ;;
    --bundle-dir)        BUNDLE_DIR="$2"; shift 2 ;;
    --with-terraform)    WITH_TERRAFORM="true"; shift ;;
    --catalog)           DO_CATALOG="true"; shift ;;
    --run-nl2kg)         RUN_NL2KG="true"; shift ;;
    --create-if-missing) CREATE_IF_MISSING="true"; shift ;;
    --readers)           READER_PRINCIPALS="$2"; shift 2 ;;
    --dry-run)           DRY_RUN="true"; shift ;;
    -h|--help)
      sed -n '2,32p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *)
      printf 'ERROR: Unknown option: %s (use --help)\n' "$1" >&2
      exit 2 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Auto-detect the local OKF v0.2 bundle directory
if [ -z "$BUNDLE_DIR" ]; then
  if [ -f "${REPO_ROOT}/okf/bundle.json" ] && [ -d "${REPO_ROOT}/okf/concepts" ]; then
    BUNDLE_DIR="${REPO_ROOT}/okf"
  elif [ -f "${REPO_ROOT}/L300_concepts/bundle.json" ] && [ -d "${REPO_ROOT}/L300_concepts/concepts" ]; then
    BUNDLE_DIR="${REPO_ROOT}/L300_concepts"
  elif [ -f "${REPO_ROOT}/bundle.json" ] && [ -d "${REPO_ROOT}/concepts" ]; then
    BUNDLE_DIR="${REPO_ROOT}"
  else
    printf 'ERROR: Could not auto-detect OKF bundle directory under %s\n' "$REPO_ROOT" >&2
    exit 1
  fi
fi

if [ -t 1 ]; then
  B=$'\033[1m'; G=$'\033[32m'; Y=$'\033[33m'; R=$'\033[31m'; C=$'\033[0m'
else
  B=""; G=""; Y=""; R=""; C=""
fi

say()  { printf "\n%s==> %s%s\n" "$B" "$*" "$C"; }
ok()   { printf "  %s✓%s %s\n" "$G" "$C" "$*"; }
warn() { printf "  %s!%s %s\n" "$Y" "$C" "$*"; }
die()  { printf "\n  %s✗ ERROR:%s %s\n\n" "$R" "$C" "$*" >&2; exit 1; }

run() {
  if [ "$DRY_RUN" = "true" ]; then
    printf "    [dry-run]"
    printf " %q" "$@"
    printf "\n"
    return 0
  fi
  "$@"
}

BUCKET_URI="gs://${BUCKET_NAME}"

# =============================================================================
# Step 1: Offline Structural & FDE Grading Rubric QA Gate (No Heredocs!)
# =============================================================================
say "Step 1: Offline OKF v0.2 Structural & FDE Grading Rubric QA (${BUNDLE_DIR})"

command -v python3 >/dev/null 2>&1 || die "python3 is required for OKF structural QA"

python3 -B -c '
import hashlib, json, os, re, sys

bundle_dir = sys.argv[1]
manifest_path = os.path.join(bundle_dir, "MANIFEST.json")
bundle_path = os.path.join(bundle_dir, "bundle.json")
index_path = os.path.join(bundle_dir, "index.md")
log_path = os.path.join(bundle_dir, "log.md")
concepts_dir = os.path.join(bundle_dir, "concepts")

for req in (manifest_path, bundle_path, index_path, log_path, concepts_dir):
    if not os.path.exists(req):
        sys.exit("Missing required OKF artifact: " + req)

manifest = json.load(open(manifest_path, encoding="utf-8"))
bundle = json.load(open(bundle_path, encoding="utf-8"))

if bundle.get("okf_version") != "0.2":
    sys.exit("Expected okf_version 0.2, got " + str(bundle.get("okf_version")))

version_tag = bundle.get("version_tag")
if version_tag != "GEAPL200_2026-09-30_124746":
    sys.exit("Expected preserved version_tag GEAPL200_2026-09-30_124746, got " + str(version_tag))

concepts = bundle.get("concepts", [])
if len(concepts) < 36:
    sys.exit("Expected at least 36 merged concepts (00..35), found " + str(len(concepts)))

FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n+", re.S)
errors = []

for entry in concepts:
    rel_file = entry["file"]
    c_path = os.path.join(bundle_dir, rel_file)
    fn = os.path.basename(c_path)
    if not os.path.exists(c_path):
        errors.append("Missing concept file: " + rel_file)
        continue
    raw = open(c_path, encoding="utf-8").read()
    m = FRONT_MATTER.match(raw)
    if not m:
        errors.append(fn + ": missing YAML frontmatter")
        continue
    fm = m.group(1)
    body = raw[m.end():]
    actual_sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    if actual_sha != entry.get("sha256"):
        errors.append(fn + ": bundle.json sha256 mismatch")
    if ("content_sha256: \"" + actual_sha + "\"") not in fm:
        errors.append(fn + ": frontmatter content_sha256 mismatch")
    if fn != "00-fde-field-readiness-and-grading-rubric.md":
        if "## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment" not in body:
            errors.append(fn + ": missing FDE Grading Rubric Enforcement section")
        if "/concepts/00-fde-field-readiness-and-grading-rubric.md" not in body:
            errors.append(fn + ": missing cross-reference link to Concept 00")
        if "https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head" not in body:
            errors.append(fn + ": missing Cloud FDE g3doc charter reference")

if errors:
    for e in errors:
        print("  ERROR:", e, file=sys.stderr)
    sys.exit(1)

print("  Verified", len(concepts), "concepts | version_tag=" + version_tag + " | stale_after_days=" + str(bundle.get("stale_after_days")))
' "$BUNDLE_DIR"
ok "All 36 OKF v0.2 concepts, SHA-256 digests, and FDE Grading Rubric sections verified"

# =============================================================================
# Step 2: Cloud Shell / gcloud Preflight & Project Guard
# =============================================================================
say "Step 2: Cloud Shell & GCP Project Preflight"

if [ "$DRY_RUN" != "true" ]; then
  command -v gcloud >/dev/null 2>&1 || die "gcloud CLI not found on PATH"
  ok "gcloud CLI detected"

  ACTIVE_ACCT="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null | head -1)"
  [ -n "$ACTIVE_ACCT" ] || die "No active gcloud credentials. Run: gcloud auth login"
  ok "Authenticated as ${ACTIVE_ACCT}"

  ACTUAL_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)' 2>/dev/null || true)"
  [ -n "$ACTUAL_NUMBER" ] || die "Cannot read project '${PROJECT_ID}'. Check permissions."
  if [ "$ACTUAL_NUMBER" != "$PROJECT_NUMBER" ]; then
    if [ "$PROJECT_ID" = "fivedaysai-prd-sandbox-317383" ] && [ "$ACTUAL_NUMBER" = "301802433103" ]; then
      warn "Project number ${PROJECT_NUMBER} normalized to actual project number ${ACTUAL_NUMBER} for ${PROJECT_ID}"
      PROJECT_NUMBER="301802433103"
    else
      die "Project number mismatch for '${PROJECT_ID}': got ${ACTUAL_NUMBER}, expected ${PROJECT_NUMBER}"
    fi
  fi
  ok "Project ${PROJECT_ID} (${ACTUAL_NUMBER}) verified"
else
  warn "Dry-run mode enabled: skipping live gcloud auth/project lookup"
fi

# =============================================================================
# Step 3: Optional Terraform IaC Execution (--with-terraform)
# =============================================================================
if [ "$WITH_TERRAFORM" = "true" ]; then
  say "Step 3: Applying Terraform Infrastructure as Code"
  if [ "$DRY_RUN" != "true" ]; then
    command -v terraform >/dev/null 2>&1 || die "terraform CLI not found on PATH"
  fi
  if [ -d "${REPO_ROOT}/iac" ]; then
    TF_DIR="${REPO_ROOT}/iac"
    run terraform -chdir="$TF_DIR" init
    run terraform -chdir="$TF_DIR" apply -auto-approve \
      -var="project_id=${PROJECT_ID}" \
      -var="gcs_bucket_name=${BUCKET_NAME}" \
      -var="create_gcs_bucket=${CREATE_IF_MISSING}"
    ok "Terraform applied from ${TF_DIR}"
  elif [ -d "${BUNDLE_DIR}/deploy/terraform" ]; then
    TF_DIR="${BUNDLE_DIR}/deploy/terraform"
    run terraform -chdir="$TF_DIR" init
    run terraform -chdir="$TF_DIR" apply -auto-approve \
      -var="project_id=${PROJECT_ID}" \
      -var="project_number=${PROJECT_NUMBER}" \
      -var="bucket_name=${BUCKET_NAME}"
    ok "Terraform applied from ${TF_DIR}"
  else
    die "No Terraform directory found at ${REPO_ROOT}/iac or ${BUNDLE_DIR}/deploy/terraform"
  fi
fi

# =============================================================================
# Step 4: Verify Existing GCS Bucket & Ensure Object Versioning + Lifecycle
# =============================================================================
say "Step 4: Verifying GCS Bucket (${BUCKET_URI}) & Object Versioning Safety"

run gcloud services enable storage.googleapis.com dataplex.googleapis.com --project "$PROJECT_ID"

if [ "$DRY_RUN" != "true" ]; then
  if gcloud storage buckets describe "$BUCKET_URI" --project="$PROJECT_ID" >/dev/null 2>&1; then
    ok "Existing bucket found: ${BUCKET_URI}"
  elif [ "$CREATE_IF_MISSING" = "true" ]; then
    warn "Bucket ${BUCKET_URI} not found; creating with uniform access & public access prevention..."
    run gcloud storage buckets create "$BUCKET_URI" \
      --project="$PROJECT_ID" \
      --location="$LOCATION" \
      --default-storage-class="STANDARD" \
      --uniform-bucket-level-access \
      --public-access-prevention
    ok "Created ${BUCKET_URI}"
  else
    die "Bucket ${BUCKET_URI} does not exist (pass --create-if-missing to create it)"
  fi

  # Snapshot current remote MANIFEST.json generation number for instant rollback visibility
  PREV_GEN="$(gcloud storage ls -a "${BUCKET_URI}/okf/MANIFEST.json" 2>/dev/null | tail -n 1 || true)"
  if [ -n "$PREV_GEN" ]; then
    ok "Prior remote MANIFEST generation recorded for rollback: ${PREV_GEN}"
  fi
fi

# Ensure Object Versioning and labels are active on the existing bucket so updates preserve prior generations
run gcloud storage buckets update "$BUCKET_URI" --versioning --project="$PROJECT_ID"
run gcloud storage buckets update "$BUCKET_URI" \
  --update-labels=corpus=geapl200,content=architecture-best-practices,format=okf,fde_rubric=enforced,managed_by=update-okf-gcs \
  --project="$PROJECT_ID"
ok "Object versioning ON and governance labels updated on ${BUCKET_URI}"

if [ -n "$READER_PRINCIPALS" ]; then
  OLD_IFS="$IFS"; IFS=','
  for principal in $READER_PRINCIPALS; do
    IFS="$OLD_IFS"
    [ -n "$principal" ] || continue
    run gcloud storage buckets add-iam-policy-binding "$BUCKET_URI" \
      --member="$principal" --role="roles/storage.objectViewer"
    ok "Granted roles/storage.objectViewer -> ${principal}"
    IFS=','
  done
  IFS="$OLD_IFS"
fi

# =============================================================================
# Step 5: Sync Unified 36-Concept OKF v0.2 Bundle Directly to GCS
# =============================================================================
say "Step 5: Synchronizing Unified 36-Concept OKF v0.2 Bundle to ${BUCKET_URI}/okf"

for top_file in index.md log.md bundle.json MANIFEST.json; do
  run gcloud storage cp "${BUNDLE_DIR}/${top_file}" "${BUCKET_URI}/okf/${top_file}" --project="$PROJECT_ID"
done

run gcloud storage rsync "${BUNDLE_DIR}/concepts" "${BUCKET_URI}/okf/concepts" \
  --recursive \
  --delete-unmatched-destination-objects \
  --project="$PROJECT_ID"

if [ -d "${BUNDLE_DIR}/img" ]; then
  run gcloud storage rsync "${BUNDLE_DIR}/img" "${BUCKET_URI}/okf/img" \
    --recursive \
    --delete-unmatched-destination-objects \
    --project="$PROJECT_ID"
fi

if [ -d "${BUNDLE_DIR}/catalog-entries" ]; then
  run gcloud storage rsync "${BUNDLE_DIR}/catalog-entries" "${BUCKET_URI}/okf/catalog-entries" \
    --recursive \
    --delete-unmatched-destination-objects \
    --project="$PROJECT_ID"
fi
ok "Synced 36-concept OKF v0.2 bundle (index.md, log.md, bundle.json, MANIFEST.json, concepts/, img/, catalog-entries/) to ${BUCKET_URI}/okf"

# =============================================================================
# Step 6: Post-Upload CRC32C Integrity Verification
# =============================================================================
say "Step 6: Verifying Remote Object Integrity (CRC32C & Byte Size)"

CRC_SCRIPT=""
if [ -f "${SCRIPT_DIR}/crc32c_verify.py" ]; then
  CRC_SCRIPT="${SCRIPT_DIR}/crc32c_verify.py"
elif [ -f "${BUNDLE_DIR}/deploy/scripts/crc32c_verify.py" ]; then
  CRC_SCRIPT="${BUNDLE_DIR}/deploy/scripts/crc32c_verify.py"
fi

if [ -n "$CRC_SCRIPT" ]; then
  if [ "$DRY_RUN" = "true" ]; then
    printf "    [dry-run] python3 %q --local-root %q --bucket %q --prefix okf\n" \
      "$CRC_SCRIPT" "$BUNDLE_DIR" "$BUCKET_NAME"
  else
    python3 -B "$CRC_SCRIPT" \
      --local-root "$BUNDLE_DIR" \
      --bucket "$BUCKET_NAME" \
      --prefix okf \
      || die "CRC32C verification FAILED against ${BUCKET_URI}/okf"
    ok "Every object under ${BUCKET_URI}/okf matches local size and CRC32C checksum"
  fi
fi

# =============================================================================
# Step 7: Optional GCP Knowledge Catalog (Dataplex) Registration (--catalog)
# =============================================================================
if [ "$DO_CATALOG" = "true" ]; then
  say "Step 7: Registering 36 Concepts in GCP Knowledge Catalog (Dataplex)"
  REG_SCRIPT=""
  if [ -f "${SCRIPT_DIR}/register_knowledge_catalog.sh" ]; then
    REG_SCRIPT="${SCRIPT_DIR}/register_knowledge_catalog.sh"
  elif [ -f "${BUNDLE_DIR}/deploy/scripts/register_knowledge_catalog.sh" ]; then
    REG_SCRIPT="${BUNDLE_DIR}/deploy/scripts/register_knowledge_catalog.sh"
  fi
  [ -n "$REG_SCRIPT" ] || die "register_knowledge_catalog.sh not found"

  if [ "$DRY_RUN" = "true" ]; then
    run bash "$REG_SCRIPT" --project "$PROJECT_ID" --bucket "$BUCKET_NAME" --location "$LOCATION" --bundle-dir "$BUNDLE_DIR" --dry-run
  else
    run bash "$REG_SCRIPT" --project "$PROJECT_ID" --bucket "$BUCKET_NAME" --location "$LOCATION" --bundle-dir "$BUNDLE_DIR" --apply
  fi
  ok "Knowledge Catalog (Dataplex) registration complete"
fi

# =============================================================================
# Step 8: Optional Downstream NL2KG Spanner/BigQuery Sync (--run-nl2kg)
# =============================================================================
if [ "$RUN_NL2KG" = "true" ]; then
  say "Step 8: Running NL2KG Triplification Pipeline (Spanner Graph + BigQuery)"
  if [ -f "${REPO_ROOT}/pipelines/main.py" ]; then
    run python3 -B -m pipelines.main --bucket "$BUCKET_NAME" --prefix "okf/concepts" --project "$PROJECT_ID"
    ok "NL2KG Spanner Graph & BigQuery update completed"
  else
    warn "pipelines/main.py not found in ${REPO_ROOT}; skipping NL2KG run"
  fi
fi

say "Summary"
printf "  %-18s %s/okf\n" "Target GCS URI:" "$BUCKET_URI"
printf "  %-18s %s (%s)\n" "GCP Project:" "$PROJECT_ID" "$PROJECT_NUMBER"
printf "  %-18s %s (preserved)\n" "Version Tag:" "GEAPL200_2026-09-30_124746"
printf "  %-18s %s\n" "Total Concepts:" "36 (00: FDE Rubric, 01..20: L200, 21..35: L300)"
printf "  %-18s %s\n" "Living Spec:" "docs/specs/okf-gcs-update-spec.md"
