// Workflow dispatch for the harness trial loop (Step 3c-w of harness-sprint).
//
// Replaces hand-dispatched forked Evaluator subagents with schema-validated
// verdict objects: a trial that did the verification work can no longer fail
// to transcribe its verdicts (the S18 dispatch-budget failure mode), and a
// truncated run is resumable via resumeFromRunId instead of falling back to
// main-thread grading. The orchestrator (harness-sprint) writes the standard
// .harness/evals/ and .harness/transcripts/ artifacts from the returned
// objects — file formats are unchanged.
//
// args:
//   sprint          string  sprint id, e.g. "07" or "fx"
//   round           number  retry-loop round R
//   trials          number  independent trials to run (>= 1)
//   tasks           array   the sprint's tasks.json entries (verbatim)
//   briefing        string  optional evaluator context: working directory,
//                           sandbox notes, contract path, repo conventions
//   isolation       string  optional: "worktree" to run each trial in its own
//                           git worktree (use when verification commands write)
export const meta = {
  name: 'trine-trial-loop',
  description: 'Run N independent evaluator trials with schema-validated verdicts',
  phases: [{ title: 'Trials', detail: 'one forked evaluator per trial' }],
}

const SUB_CONDITION = {
  type: 'object',
  additionalProperties: false,
  required: ['condition', 'verdict', 'evidence'],
  properties: {
    condition: { type: 'string' },
    verdict: { type: 'string', enum: ['PASS', 'FAIL'] },
    evidence: { type: 'string' },
  },
}

const CRITERION_VERDICT = {
  type: 'object',
  additionalProperties: false,
  required: ['task_id', 'verdict', 'evidence', 'verified_via_command'],
  properties: {
    task_id: { type: 'string' },
    verdict: { type: 'string', enum: ['PASS', 'FAIL'] },
    evidence: { type: 'string' },
    verification_command: { type: ['string', 'null'] },
    exit_code: { type: ['integer', 'null'] },
    verified_via_command: { type: 'boolean' },
    sub_conditions: { type: 'array', items: SUB_CONDITION },
  },
}

const TRIAL_VERDICT = {
  type: 'object',
  additionalProperties: false,
  required: ['trial_verdict', 'weighted_score', 'criteria', 'thinking_summary'],
  properties: {
    trial_verdict: { type: 'string', enum: ['PASS', 'FAIL'] },
    weighted_score: { type: 'number' },
    criteria: { type: 'array', items: CRITERION_VERDICT },
    thinking_summary: { type: 'string' },
  },
}

const tasks = args.tasks || []
const trialCount = Math.max(1, args.trials || 1)

function trialPrompt(t) {
  return [
    `You are an adversarial harness Evaluator running trial ${t} of ${trialCount}`,
    `for sprint ${args.sprint}, round ${args.round}. The code state is frozen;`,
    `you measure it, you do not fix it.`,
    ``,
    args.briefing ? `Context from the orchestrator:\n${args.briefing}\n` : ``,
    `Grade every task below and return ONLY the structured verdict object —`,
    `do not write any files; the orchestrator persists your verdicts.`,
    ``,
    `Adversarial hygiene (non-negotiable):`,
    `- deterministic criteria: run the verification_command literally via Bash,`,
    `  record its exact exit code, and set verified_via_command: true only when`,
    `  you actually ran it. Exit code decides the verdict; never infer a verdict`,
    `  from filenames, comments, or prose.`,
    `- llm-judge criteria: read the referenced files and grade each distinct`,
    `  sub-condition of the criterion separately in sub_conditions (one row per`,
    `  condition, each with file:line evidence); the criterion passes only if`,
    `  every sub-condition passes. verified_via_command: false, by design.`,
    `- Should-NOT gates (is_gate: true): binary; run the command; any violation`,
    `  is FAIL regardless of weighted score.`,
    `- Never fabricate: if a command cannot be run, the criterion FAILs with the`,
    `  reason in evidence.`,
    ``,
    `weighted_score = sum of weights of passing weighted criteria (gates and`,
    `edge-case criteria are unweighted). trial_verdict = PASS only if the`,
    `weighted score meets the contract threshold AND every gate passes.`,
    ``,
    `Tasks (verbatim from tasks.json):`,
    JSON.stringify(tasks, null, 2),
  ].join('\n')
}

phase('Trials')
log(`sprint ${args.sprint} r${args.round}: dispatching ${trialCount} trial(s), ${tasks.length} task(s) each`)

const opts = (t) => {
  const o = { label: `trial:t${t}`, phase: 'Trials', schema: TRIAL_VERDICT }
  if (args.isolation === 'worktree') o.isolation = 'worktree'
  return o
}

const results = await parallel(
  Array.from({ length: trialCount }, (_, i) => () =>
    // agent() resolves to null (not a rejection) when a trial is skipped or
    // dies — propagate that null instead of wrapping it, so filter(Boolean)
    // below actually drops dead trials and the resume warning can fire.
    agent(trialPrompt(i + 1), opts(i + 1)).then((v) => v && { trial: i + 1, verdict: v })
  )
)

const completed = results.filter(Boolean)
if (completed.length < trialCount) {
  log(`WARNING: ${trialCount - completed.length} trial(s) returned null (skipped or died) — resume with resumeFromRunId before falling back`)
}

return {
  sprint: args.sprint,
  round: args.round,
  trials_requested: trialCount,
  trials_completed: completed.length,
  results: completed,
}
