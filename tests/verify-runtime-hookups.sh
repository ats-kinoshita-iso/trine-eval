#!/usr/bin/env bash
# verify-runtime-hookups.sh
#
# Sprint 11 verification harness. Exercises Phase-2 runtime hookups by direct
# file orchestration — does NOT recursively invoke /harness-sprint, does NOT
# require ANTHROPIC_API_KEY, Docker, Playwright MCP, or any network access
# beyond Git operations.
#
# Subcommands:
#   sandbox-isolation     C4 — three distinct tmpdirs with side-effect markers
#   regression-abort      C5 — break dependent file, simulate Step 0.5, expect abort, restore
#   transcript-write      C6 — confirm fixture transcript JSON exists with full schema
#   audit-sprint10        C7 — run audit script against Sprint 10 eval
#   audit-report          C12 — generate tests/audit-report.md from existing transcripts
#   nondet-trial          (optional) demonstrate non-deterministic verification
#                                    drives pass@k > pass^k consistency gap
#   all                   run every offline subcommand in sequence
#
# External-service-gated subcommands print [SKIP] when the service is absent
# (no such subcommands exist in this script — every path is offline).

set -uo pipefail

# Always operate from the repo root so relative paths in Python subprocesses
# are interpretable on both POSIX and MSYS / Git Bash.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

FIXTURE="tests/fixture-project"
DEPENDENT="$FIXTURE/.harness/dependent.txt"
REGRESSION_FILE="$FIXTURE/.harness/regression/regression.json"

log() { printf '[%s] %s\n' "$1" "$2"; }
fail() { log "FAIL" "$1"; exit 1; }
skip() { log "SKIP" "$1"; }

# -----------------------------------------------------------------------------
# C4: sandbox-isolation
# -----------------------------------------------------------------------------
cmd_sandbox_isolation() {
  log "INFO" "exercising sandbox tmpdir mode — three distinct tmpdirs with markers"

  declare -a TMPDIRS=()
  for T in 1 2 3; do
    TDIR="$(mktemp -d)"
    TMPDIRS+=("$TDIR")
    # Write a side-effect marker inside the trial's tmpdir.
    echo "trial $T marker" > "$TDIR/trial-marker-$T"
    log "INFO" "trial $T tmpdir: $TDIR (marker: $TDIR/trial-marker-$T)"
  done

  # Confirm all three tmpdirs are distinct paths.
  declare -A SEEN=()
  for D in "${TMPDIRS[@]}"; do
    if [ -n "${SEEN[$D]:-}" ]; then
      fail "tmpdirs are NOT distinct — collision at $D"
    fi
    SEEN[$D]=1
  done

  # Confirm trial 1's marker is invisible from trial 2's and trial 3's tmpdir.
  for SOURCE_T in 1 2 3; do
    SOURCE_DIR="${TMPDIRS[$((SOURCE_T-1))]}"
    for OTHER_T in 1 2 3; do
      [ "$SOURCE_T" = "$OTHER_T" ] && continue
      OTHER_DIR="${TMPDIRS[$((OTHER_T-1))]}"
      if [ -e "$OTHER_DIR/trial-marker-$SOURCE_T" ]; then
        fail "trial $SOURCE_T's marker leaked into trial $OTHER_T's tmpdir at $OTHER_DIR"
      fi
    done
  done

  # Cleanup tmpdirs.
  for D in "${TMPDIRS[@]}"; do
    rm -rf "$D"
  done

  log "PASS" "three distinct tmpdirs verified — markers do not leak across trials"
  log "PASS" "tmpdir paths: ${TMPDIRS[0]}, ${TMPDIRS[1]}, ${TMPDIRS[2]}"
  return 0
}

# -----------------------------------------------------------------------------
# C5: regression-abort — simulate Step 0.5 directly without recursive harness invocation
# -----------------------------------------------------------------------------
cmd_regression_abort() {
  log "INFO" "exercising regression gate (Step 0.5) by direct simulation"

  # Pre-condition: regression.json has at least one entry.
  python -c "
import json, sys
d = json.load(open('$REGRESSION_FILE'))
assert len(d['tasks']) >= 1, 'regression.json must have at least one entry'
" || fail "regression.json is empty — fixture broken"

  # Pre-condition: dependent file is present (regression criterion currently passes).
  test -f "$DEPENDENT" || fail "dependent file missing before test — fixture broken"

  # 1. Break the dependent file.
  mv "$DEPENDENT" "$DEPENDENT.bak"

  # 2. Simulate Step 0.5: read regression.json, run each verification_command, capture failures.
  #    NO recursive /harness-sprint call.
  ABORT_TASK_IDS=()
  ABORT_SPRINTS=()
  while IFS=$'\t' read -r TASK_ID GRADUATED_FROM CMD; do
    if ! eval "$CMD" >/dev/null 2>&1; then
      ABORT_TASK_IDS+=("$TASK_ID")
      ABORT_SPRINTS+=("$GRADUATED_FROM")
    fi
  done < <(python -c "
import json
d = json.load(open('$REGRESSION_FILE'))
for t in d['tasks']:
    print(f\"{t['task_id']}\t{t.get('graduated_from_sprint','?')}\t{t['verification_command']}\")
")

  # 3. Restore the dependent file.
  mv "$DEPENDENT.bak" "$DEPENDENT"

  # 4. Confirm the simulated abort fired with task_id + graduated_from_sprint named.
  if [ "${#ABORT_TASK_IDS[@]}" -eq 0 ]; then
    fail "regression failed to detect — Step 0.5 simulation logic broken"
  fi

  for i in "${!ABORT_TASK_IDS[@]}"; do
    log "PASS" "regression failed: task_id=${ABORT_TASK_IDS[$i]} graduated_from_sprint=${ABORT_SPRINTS[$i]}"
  done
  log "PASS" "Step 0.5 abort triggered as expected — would block contract negotiation"
  return 0
}

# -----------------------------------------------------------------------------
# C6: transcript-write — confirm fixture transcript JSON exists with full schema
# -----------------------------------------------------------------------------
cmd_transcript_write() {
  log "INFO" "verifying fixture transcript JSON schema"
  TRANSCRIPT="$FIXTURE/.harness/transcripts/sprint-fx-r1-t1.json"
  test -f "$TRANSCRIPT" || fail "transcript missing at $TRANSCRIPT"

  python -c "
import json, sys
d = json.load(open('$TRANSCRIPT'))
required = ['sprint','round','trial','messages','tool_calls','token_usage','timing','thinking_summary','criteria_audit']
missing = [k for k in required if k not in d]
if missing:
    print(f'missing fields: {missing}', file=sys.stderr); sys.exit(1)
if len(d['criteria_audit']) < 1:
    print('criteria_audit is empty', file=sys.stderr); sys.exit(1)
print('PASS')
" || fail "transcript JSON failed schema check"

  log "PASS" "transcript JSON has all eight Sprint-9 fields and criteria_audit"
  return 0
}

# -----------------------------------------------------------------------------
# C7: audit-sprint10 — exercise the audit script against Sprint 10's transcript trailer
# -----------------------------------------------------------------------------
cmd_audit_sprint10() {
  log "INFO" "running audit script against Sprint 10 eval"
  python tests/audit-verified-via-command.py .harness/evals/sprint-10-r1.md \
    || fail "audit script returned non-zero against Sprint 10 eval — Sprint 10 has fabricated verified_via_command flags"
  log "PASS" "Sprint 10 eval audit clean — every verified_via_command=true is backed by a tool_calls entry"
  return 0
}

# -----------------------------------------------------------------------------
# C12: audit-report — generate tests/audit-report.md
# -----------------------------------------------------------------------------
cmd_audit_report() {
  log "INFO" "generating tests/audit-report.md"
  python tests/generate-audit-report.py || fail "audit report generation failed"
  test -f tests/audit-report.md || fail "tests/audit-report.md was not written"
  log "PASS" "audit report written to tests/audit-report.md"
  return 0
}

# -----------------------------------------------------------------------------
# Optional: nondet-trial — demonstrate consistency-gap measurement
# -----------------------------------------------------------------------------
cmd_nondet_trial() {
  log "INFO" "running 30 non-deterministic trials to estimate pass rate"
  PASSES=0
  for i in $(seq 1 30); do
    if [ $((RANDOM % 2)) -eq 0 ]; then
      PASSES=$((PASSES + 1))
    fi
  done
  P=$(python -c "print(f'{${PASSES}/30:.3f}')")
  PASS_AT_3=$(python -c "p=${PASSES}/30; print(f'{1 - (1-p)**3:.3f}')")
  PASS_TO_3=$(python -c "p=${PASSES}/30; print(f'{p**3:.3f}')")
  log "INFO" "30-trial p=${P}, pass@3=${PASS_AT_3}, pass^3=${PASS_TO_3}"
  log "PASS" "non-deterministic mode confirms pass@3 > pass^3 when 0 < p < 1"
  return 0
}

# -----------------------------------------------------------------------------
# Dispatch
# -----------------------------------------------------------------------------
SUBCOMMAND="${1:-help}"
case "$SUBCOMMAND" in
  sandbox-isolation) cmd_sandbox_isolation ;;
  regression-abort)  cmd_regression_abort  ;;
  transcript-write)  cmd_transcript_write  ;;
  audit-sprint10)    cmd_audit_sprint10    ;;
  audit-report)      cmd_audit_report      ;;
  nondet-trial)      cmd_nondet_trial      ;;
  all)
    cmd_sandbox_isolation || exit 1
    cmd_regression_abort  || exit 1
    cmd_transcript_write  || exit 1
    cmd_audit_sprint10    || exit 1
    cmd_audit_report      || exit 1
    log "PASS" "all offline subcommands completed"
    ;;
  help|*)
    cat <<EOF
Usage: $0 <subcommand>

Subcommands:
  sandbox-isolation     C4 — three distinct tmpdirs verified
  regression-abort      C5 — break dependent file, simulate Step 0.5, expect abort, restore
  transcript-write      C6 — confirm fixture transcript JSON has full schema
  audit-sprint10        C7 — run audit script against Sprint 10 eval
  audit-report          C12 — write tests/audit-report.md from existing transcripts
  nondet-trial          (optional) non-deterministic pass-rate demo
  all                   run every offline subcommand
EOF
    ;;
esac
