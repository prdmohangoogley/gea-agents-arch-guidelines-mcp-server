#!/usr/bin/env bash
#
# Register the OKF bundle with Google Cloud Knowledge Catalog.
#
# Knowledge Catalog is the rebranded Dataplex Universal Catalog, so the CLI
# surface is `gcloud dataplex`. Publishing an OKF bundle means creating:
#
#   EntryGroup   a container for the bundle's entries
#   AspectType   `okf` - the structured metadata carrying OKF frontmatter,
#                including the v0.2 trust signals (status, stale_after,
#                sources, generated, verified)
#   EntryType    `okf-bundle` - the shape of a concept entry
#   Entries      one per concept Markdown file, with the body attached as an
#                overview aspect and frontmatter mapped into the okf aspect
#
# ---------------------------------------------------------------------------
# VERIFIED vs CONFIRM-BEFORE-RUNNING
# ---------------------------------------------------------------------------
# Verified: Knowledge Catalog == Dataplex Universal Catalog, and the command
# groups used below (`gcloud dataplex aspect-types|entry-types|entry-groups|
# entries`) are the correct surface.
#
# Confirm in YOUR project before relying on this end to end: the exact aspect
# schema field spellings and the entry-creation flags have moved between
# Dataplex API versions, and Google also ships a `kcmd` metadata-as-code CLI
# in the knowledge-catalog repo that wraps these calls. If a command below is
# rejected, prefer `kcmd` or check `gcloud dataplex entries create --help`
# rather than hand-patching flags.
#
# This script defaults to --dry-run for exactly that reason. Inspect the
# emitted commands first, then re-run with --apply.
# ---------------------------------------------------------------------------

set -euo pipefail

PROJECT_ID="fivedaysai-prd-sandbox-317383"
BUCKET=""
LOCATION="us"          # Dataplex location (region or multi-region, lowercase)
ENTRY_GROUP="geapl200-architecture-kb"
ASPECT_TYPE="okf"
ENTRY_TYPE="okf-bundle"
APPLY="false"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUNDLE_DIR="${BUNDLE_DIR:-${REPO_ROOT}/okf}"

while [ $# -gt 0 ]; do
  case "$1" in
    --project)     PROJECT_ID="$2"; shift 2 ;;
    --bucket)      BUCKET="$2"; shift 2 ;;
    --location)    LOCATION="$(echo "$2" | tr '[:upper:]' '[:lower:]')"; shift 2 ;;
    --entry-group) ENTRY_GROUP="$2"; shift 2 ;;
    --bundle-dir)  BUNDLE_DIR="$2"; shift 2 ;;
    --apply)       APPLY="true"; shift ;;
    --dry-run)     APPLY="false"; shift ;;
    -h|--help)     sed -n '2,40p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 1 ;;
  esac
done

[ -n "$BUCKET" ] || { echo "--bucket is required" >&2; exit 1; }
[ -d "$BUNDLE_DIR" ] || { echo "bundle not found at $BUNDLE_DIR - run build_okf_bundle.py first" >&2; exit 1; }

run() {
  if [ "$APPLY" = "true" ]; then
    echo "+ $*"
    "$@"
  else
    echo "  [dry-run] $*"
  fi
}

# Create commands that tolerate the resource already existing, so the whole
# registration is re-runnable after a partial failure. Anything else still
# aborts (set -e is intentionally bypassed only for the ALREADY_EXISTS case).
run_create() {
  if [ "$APPLY" != "true" ]; then
    echo "  [dry-run] $*"
    return 0
  fi
  echo "+ $*"
  local out rc=0
  # NOTE: the `|| rc=$?` is load-bearing. Under `set -e` a bare failing
  # assignment (out="$(cmd)") aborts the script instantly, so the error text
  # captured in $out is never printed and the already-exists check below
  # never runs. Putting the assignment in a conditional context suppresses
  # set -e for this one command so we can inspect the result.
  out="$("$@" 2>&1)" || rc=$?
  if [ $rc -eq 0 ]; then
    [ -n "$out" ] && echo "$out"
    return 0
  fi
  if echo "$out" | grep -qiE 'already exists|ALREADY_EXISTS|409'; then
    echo "  (already exists - continuing)"
    return 0
  fi
  echo "$out" >&2
  return $rc
}

BUILD_DIR="${REPO_ROOT}/build"
mkdir -p "$BUILD_DIR"

run_upsert_entry() {
  local entry_id="$1"
  local payload="$2"
  if [ "$APPLY" != "true" ]; then
    echo "  [dry-run] gcloud dataplex entries create $entry_id --project=$PROJECT_ID --location=$LOCATION --entry-group=$ENTRY_GROUP --entry-type=projects/${PROJECT_ID}/locations/${LOCATION}/entryTypes/${ENTRY_TYPE} --entry-source-resource=gs://${BUCKET}/okf/concepts/${entry_id}.md --aspects=$payload"
    return 0
  fi
  echo "+ gcloud dataplex entries create $entry_id"
  local out rc=0
  out="$(gcloud dataplex entries create "$entry_id" \
      --project="$PROJECT_ID" --location="$LOCATION" \
      --entry-group="$ENTRY_GROUP" \
      --entry-type="projects/${PROJECT_ID}/locations/${LOCATION}/entryTypes/${ENTRY_TYPE}" \
      --entry-source-resource="gs://${BUCKET}/okf/concepts/${entry_id}.md" \
      --aspects="$payload" 2>&1)" || rc=$?
  if [ $rc -eq 0 ]; then
    echo "  ✓ created: $entry_id"
    return 0
  fi
  if echo "$out" | grep -qiE 'already exists|ALREADY_EXISTS|409'; then
    echo "  ℹ $entry_id already exists; updating aspects..."
    gcloud dataplex entries update "$entry_id" \
        --project="$PROJECT_ID" --location="$LOCATION" \
        --entry-group="$ENTRY_GROUP" \
        --update-aspects="$payload" >/dev/null
    echo "  ✓ updated: $entry_id"
    return 0
  fi
  echo "$out" >&2
  return $rc
}

echo "==> Knowledge Catalog registration"
echo "    project     ${PROJECT_ID}"
echo "    location    ${LOCATION}"
echo "    entry group ${ENTRY_GROUP}"
echo "    bundle      ${BUNDLE_DIR}"
echo "    mode        $([ "$APPLY" = "true" ] && echo APPLY || echo DRY-RUN)"
echo

# ---------------------------------------------------------------------------
# 1. AspectType `okf` - the OKF v0.2 frontmatter schema, trust signals first
# ---------------------------------------------------------------------------

# The schema is a static artifact, versioned alongside the scripts, rather
# than generated at runtime by a heredoc (heredocs need a writable TMPDIR,
# which is not always available).
OKF_ASPECT_JSON="${SCRIPT_DIR}/../catalog/aspect-type-okf.json"
[ -f "$OKF_ASPECT_JSON" ] || { echo "missing aspect schema: $OKF_ASPECT_JSON" >&2; exit 1; }
python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$OKF_ASPECT_JSON" \
  || { echo "aspect schema is not valid JSON: $OKF_ASPECT_JSON" >&2; exit 1; }

echo "--> AspectType '${ASPECT_TYPE}'"
run_create gcloud dataplex aspect-types create "$ASPECT_TYPE" \
    --project="$PROJECT_ID" --location="$LOCATION" \
    --metadata-template-file-name="$OKF_ASPECT_JSON"

# ---------------------------------------------------------------------------
# 2. EntryType `okf-bundle`
# ---------------------------------------------------------------------------

echo "--> EntryType '${ENTRY_TYPE}'"
run_create gcloud dataplex entry-types create "$ENTRY_TYPE" \
    --project="$PROJECT_ID" --location="$LOCATION" \
    --display-name="OKF Bundle Concept" \
    --description="A single Open Knowledge Format concept document."

# ---------------------------------------------------------------------------
# 3. EntryGroup
# ---------------------------------------------------------------------------

echo "--> EntryGroup '${ENTRY_GROUP}'"
run_create gcloud dataplex entry-groups create "$ENTRY_GROUP" \
    --project="$PROJECT_ID" --location="$LOCATION" \
    --display-name="GEA Agent Development - Architecture Best Practices" \
    --description="OKF knowledge bundle backing the Spanner Graph / BigQuery hybrid knowledge graph and its MCP server."

# ---------------------------------------------------------------------------
# 4. Entries - one per concept, generated from the bundle
# ---------------------------------------------------------------------------

echo "--> Generating per-concept entry payloads"
python3 "${SCRIPT_DIR}/make_catalog_entries.py" \
    --bundle "$BUNDLE_DIR" \
    --bucket "$BUCKET" \
    --out "${BUILD_DIR}/catalog-entries" \
    --entry-group "$ENTRY_GROUP" \
    --entry-type "$ENTRY_TYPE" \
    --aspect-type "$ASPECT_TYPE" \
    --project "$PROJECT_ID" \
    --location "$LOCATION"

ENTRY_COUNT=$(ls "${BUILD_DIR}/catalog-entries"/*.json 2>/dev/null | wc -l | tr -d ' ')
echo "    ${ENTRY_COUNT} entry payloads in ${BUILD_DIR}/catalog-entries"
echo

for payload in "${BUILD_DIR}/catalog-entries"/*.json; do
  [ -e "$payload" ] || continue
  entry_id="$(basename "$payload" .json)"
  run_upsert_entry "$entry_id" "$payload"
done

NOW_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
if [ "$APPLY" = "true" ]; then MODE_WORD="complete"; else MODE_WORD="dry run complete"; fi

printf '\n==> Registration %s\n\n' "$MODE_WORD"
printf '    %-13s%s\n' "Entry group :" "projects/${PROJECT_ID}/locations/${LOCATION}/entryGroups/${ENTRY_GROUP}"
printf '    %-13s%s\n' "Aspect type :" "${ASPECT_TYPE}    (OKF v0.2, trust signals included)"
printf '    %-13s%s\n' "Entry type  :" "${ENTRY_TYPE}"
printf '    %-13s%s\n' "Backing data:" "gs://${BUCKET}/okf"
printf '\n    Staleness queries become possible once entries are live. The search\n'
printf '    query is a POSITIONAL argument, not --query:\n\n'
printf "      gcloud dataplex entries search 'aspect:%s.stale_after<%s' \\\\\n" \
       "${ASPECT_TYPE}" "${NOW_UTC}"
printf '        --project=%s\n' "${PROJECT_ID}"
printf '\n    Confirm the exact syntax for your gcloud version with:\n'
printf '      gcloud dataplex entries search --help\n'
if [ "$APPLY" != "true" ]; then
  printf '\n    Re-run with --apply to execute. Review the emitted commands first.\n'
fi
printf '\n'
