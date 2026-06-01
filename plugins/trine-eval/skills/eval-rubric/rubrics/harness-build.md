# Harness Build Evaluation Rubric

Rubric for evaluating agent runtime harnesses against the "Playbook for Building Agent Harnesses" stages. This rubric assesses whether a harness correctly implements the foundational infrastructure layers that govern how an autonomous agent operates: its control plane and agentic loop, tool registry and sandboxing, projection and planning subsystem, skills and instruction execution, observation and monitoring, external affordances, and governance with human oversight.

Each dimension maps to one or more playbook stages. A harness that scores well on weighted dimensions but fails any of the three hard-threshold gates (loop termination, sandboxing, governance placement) receives an automatic sprint FAIL regardless of its weighted score. The gates are non-negotiable preconditions for safe agentic operation — no amount of strong dimension scores can compensate for their absence.

## Dimensions and Weights

### Control Plane & Agentic Loop (20%)

Assesses whether the harness defines a coherent control plane that governs the agentic loop — including how the loop is initiated, how state transitions are managed between steps, and whether the loop has documented termination conditions and numeric bounds.

| Score | Description |
|-------|-------------|
| 5 | Control plane is explicitly documented with a defined start/stop protocol. The agentic loop has a clearly enforced maximum step count AND a maximum token or time budget. State transitions between steps are modeled (e.g., idle → planning → acting → reflecting → done). Loop termination is guaranteed by the harness, not assumed from model behavior. Retry/recovery paths are defined for tool failures. |
| 4 | Loop has a documented max-step or max-token bound. State transitions are described at a high level. Termination is enforced by the harness. Missing one of: formal start/stop protocol, retry/recovery paths, or dual bound (step + token). |
| 3 | A max-step or max-token bound is declared somewhere in the harness documentation. The loop structure is described but state transitions are implicit. No formal retry/recovery for tool failures beyond basic error handling. |
| 2 | The loop structure is referenced but bounds are informal ("the loop stops when the agent is done"). No numeric limit is enforced. State transitions are not modeled. |
| 1 | No agentic loop documentation. The harness runs until the model stops producing output. No termination guarantee. |

### Tool Registry & Sandboxing (18%)

Assesses the harness's tool registration system — how tools are defined, how their side-effects and permissions are declared — and whether tool execution is sandboxed with explicit isolation from the host environment.

| Score | Description |
|-------|-------------|
| 5 | All tools are registered in a structured registry with declared name, description, input schema, output schema, and side-effect classification (read-only / write / external). Code execution tools are sandboxed with explicit filesystem, network, and process isolation declared. Sandbox configuration (allowed paths, blocked hosts, resource limits) is versioned alongside the harness. Dangerous tools require explicit capability declaration before use. |
| 4 | Tool registry exists with name, description, and side-effect classification. Code execution is sandboxed with at least two isolation dimensions declared (e.g., filesystem + network). Missing one of: output schema, resource limits, or versioned sandbox config. |
| 3 | Tools are documented but the registry is informal (e.g., a markdown list). Code execution sandboxing is declared but the scope of isolation is underspecified (e.g., "runs in a container" without stating what is blocked). No side-effect classification. |
| 2 | Some tools are documented. Sandboxing is mentioned but not defined — no isolation dimensions are stated. No registry structure. |
| 1 | No tool registry. No sandboxing declaration. Tools are invoked without any documented isolation or side-effect policy. |

### Projection & Planning (12%)

Assesses whether the harness supports a planning or projection subsystem that decomposes goals into steps before the agentic loop executes them, and whether plan state is tracked between loop iterations.

| Score | Description |
|-------|-------------|
| 5 | Dedicated planning phase precedes execution. The planner produces a structured plan (ordered steps, dependencies, estimated cost/token budget). Plan state is persisted (e.g., in a JSON state file) so the harness can resume from interruption. Replanning is triggered when execution diverges from the plan. |
| 4 | Planning phase exists and produces a structured plan. Plan state is tracked but not necessarily persisted across restarts. Replanning is described but may be manual. |
| 3 | The harness documents a planning step but its output is informal (prose notes rather than structured data). Plan state is not persisted. No replanning mechanism. |
| 2 | Planning is ad-hoc — the agent plans inline during execution with no separate phase. No plan state persistence. |
| 1 | No planning subsystem. The harness provides the goal directly to the agentic loop with no decomposition step. |

### Skills & Instruction Execution (15%)

Assesses the quality of the harness's skill definitions — the prompt engineering, instruction format, and execution contracts that govern how the agent interprets and carries out individual skill invocations.

| Score | Description |
|-------|-------------|
| 5 | Each skill is defined with: (a) a frontmatter manifest (name, description, allowed-tools, constraints), (b) step-by-step instructions written for the model (not the developer), (c) explicit scope annotations limiting what context is read at each step, (d) a defined output contract (what the skill must produce). Skills are composable — one skill can invoke another via a sub-agent. Instruction quality follows ACI best practices (concise, unambiguous, example-grounded). |
| 4 | Skills have frontmatter manifests and step-by-step instructions. Context scope annotations are present for most steps. Output contracts are described. Missing one of: composability, ACI best-practice compliance, or example grounding. |
| 3 | Skills have frontmatter manifests and prose instructions. Context scope annotations are absent or present only on some steps. No explicit output contract — the skill's success condition is implied. |
| 2 | Skills are defined as markdown files but lack frontmatter manifests or structured instructions. Instructions are written for the developer, not the model. |
| 1 | No structured skill definitions. Agent behavior is controlled by a monolithic system prompt with no modular skill decomposition. |

### Observation & Monitoring (12%)

Assesses whether the harness captures execution transcripts, emits structured events, and provides hooks that allow an evaluator or human operator to observe what the agent did and why at each step.

| Score | Description |
|-------|-------------|
| 5 | Execution transcripts are captured per-sprint in a structured format (timestamped, tool-call-level granularity). Structured events are emitted at key lifecycle points (loop start, tool invocation, tool result, loop end). A pre-eval and post-eval hook allows the evaluator to read transcripts before scoring. Transcript review is part of the workflow (grader quality is checked against transcripts). |
| 4 | Transcripts are captured at sprint level. Key lifecycle events are emitted. Pre-eval hook exists. Missing one of: tool-call granularity, post-eval hook, or transcript review in workflow. |
| 3 | Progress logging exists (e.g., progress.md, sprint-state.json) but it is not transcript-level — the evaluator cannot see individual tool calls. No lifecycle event hooks. |
| 2 | Minimal logging. Sprint-level pass/fail status is recorded but execution detail is absent. No hooks. |
| 1 | No structured observation. Agent output is ephemeral — there is no record of what the agent did during a sprint. |

### External Affordances (8%)

Assesses whether the harness correctly declares and manages outbound integrations — API calls, data retrieval, file I/O, and other external side effects that the agent may produce — and whether these affordances are enumerated and bounded.

| Score | Description |
|-------|-------------|
| 5 | All outbound integrations are declared in a manifest or config (API endpoints, data sources, writable directories). Each external affordance has a declared rate limit or budget. Network calls are proxied or logged. The harness can run in "dry-run" mode that simulates external calls without executing them. |
| 4 | Outbound integrations are declared. Rate limits or budgets exist for most affordances. Network calls are logged. Missing dry-run mode or one undeclared affordance. |
| 3 | External affordances are described in documentation but not declared in a machine-readable manifest. No rate limits. No dry-run mode. |
| 2 | Some external calls are documented, but the list is incomplete. No budgets or rate limits. No logging of external calls. |
| 1 | External affordances are undeclared. The harness makes external calls without any enumeration, logging, or budget. |

### Governance & Human Oversight (15%)

Assesses whether the harness documents an escalation path for irreversible or high-stakes agentic decisions — requiring human review or out-of-band approval before the agent proceeds with destructive operations, money movement, external side effects, or other actions that cannot be undone.

| Score | Description |
|-------|-------------|
| 5 | A formal escalation policy is documented: specific action categories that require human review are listed (e.g., file deletion, API writes, financial transactions, deployment). The harness enforces a pause-and-wait mechanism — the agent cannot proceed past these action categories without an approval signal. Approval paths are documented (human in the loop, async approval queue, or explicit `/approve` command). Audit trail of escalated decisions is maintained. |
| 4 | Escalation policy is documented with listed action categories. Pause-and-wait is described. Missing one of: enforcement mechanism, audit trail, or async approval path. |
| 3 | Governance is acknowledged — the harness documentation notes that irreversible actions should involve human review — but the escalation path is not formally specified. No enforcement mechanism. |
| 2 | Human oversight is mentioned in passing but no escalation categories are defined and no approval mechanism exists. |
| 1 | No governance documentation. The agent can perform irreversible or high-stakes actions without any human review checkpoint. |

## Hard Thresholds

The following three gates are UNCONDITIONAL. Failing any gate causes **automatic sprint FAIL**
regardless of the weighted dimension score. No score-based waiver applies.

- **Loop Termination & Bounds (UNCONDITIONAL):** The harness under evaluation MUST have a
  documented maximum step count OR maximum token budget on its agentic loop. A harness with
  no documented loop bound causes automatic FAIL for this gate. A verbal claim that "the loop
  always terminates" without an enforced numeric limit does not satisfy this gate.

- **Sandboxing (UNCONDITIONAL):** The harness MUST declare that code execution is sandboxed —
  with explicit filesystem, network, or process isolation. Absence of any sandboxing declaration
  causes automatic FAIL. A harness that executes arbitrary tool calls in the host environment
  without isolation does not satisfy this gate.

- **Governance Placement (UNCONDITIONAL):** The harness MUST document a human-review or
  out-of-band approval path for agentic decisions that escalate (irreversible actions, external
  side effects, money movement, or destructive operations). Absence of any documented escalation
  path causes automatic FAIL for this gate.

These three gates cannot be waived by compensating dimension scores. A harness that scores 5/5
on every dimension but lacks a documented loop bound, sandboxing declaration, or governance
escalation path still receives an automatic FAIL. The gates verify documentation presence and
policy existence, not implementation quality.

## Testing Methods

- **File structure verification:** Confirm the harness repository contains expected artifacts — control plane config, tool registry manifest, skill definition files, observation hooks, governance policy document
- **Loop bound grep:** Search harness documentation and config for numeric max-step or max-token values; flag harnesses where only prose claims exist without numeric enforcement
- **Sandbox declaration check:** Inspect the tool registry and any execution config for explicit isolation declarations (allowed-paths, blocked-hosts, container spec, resource limits); report which isolation dimensions are declared vs. absent
- **Governance policy audit:** Read the escalation policy document (or equivalent section); verify that specific action categories are enumerated and that an approval mechanism is described
- **Skill manifest inspection:** Check each skill definition for frontmatter (name, description, allowed-tools) and step-level context scope annotations; count skills with and without manifests
- **Observation hook tracing:** Walk the sprint workflow to verify transcript capture, lifecycle event emission, and evaluator hook invocations are documented at each stage
- **Cross-reference playbook stages:** Map each of the nine playbook stages to one or more harness artifacts; flag stages with no corresponding artifact as gaps
