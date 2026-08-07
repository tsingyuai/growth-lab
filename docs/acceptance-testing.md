# Acceptance testing

Growth Lab acceptance runs are sequential, bounded, and stored under ignored Product workspace data:

```text
workspaces/_acceptance/<run-id>/
```

Run the offline baseline first:

```powershell
python scripts\acceptance\run_acceptance.py --tier offline
```

Run real read-only platform smoke tests only after the corresponding network, Client, and test account are ready:

```powershell
python scripts\acceptance\run_acceptance.py --tier xhs-smoke --limit 3
python scripts\acceptance\run_acceptance.py --tier x-smoke --limit 3
```

Add `--allow-visible-login` only after the user authorizes a visible Xiaohongshu QR window. QR scanning, credential entry, CAPTCHA/risk-control handling, paid API credential setup, and final public publishing approval remain human gates. Search, persistence, cover download, mechanical checks, reporting, and cleanup accounting are automatic.

Before the first provider-backed image, acceptance must exercise the same user gate as production: ask whether API generation is desired, open `.env.local` only after consent, wait for local save, verify provider presence without displaying the key, and then resume the pending image step. Declining configuration must produce a deterministic or no-image result rather than a failure loop.

The X smoke tier performs both a normal query and an exact, locally revalidated query. The second pass downloads media into the ignored acceptance run so file type, size, and persistence can be inspected. Translation is a Model post-processing step: the Agent writes and validates Chinese translations for non-Chinese items while preserving the original text; the Collector never invents a translation field.

Every run contains redacted environment presence, per-step stdout/stderr logs, durations, a machine-readable manifest, and `report.md`. A failed or timed-out step stops the tier. Logs and output are scanned for credential-shaped values before the run can pass.

Visual selection does not ask the user during an autonomous acceptance run when at least one candidate passes. The Agent or an approved visual evaluator writes scores for every candidate using the Xiaohongshu cover rubric. `auto_select_visual_reference.py` applies the hard gate and 75-point threshold, selects exactly one highest-scoring reference, marks it internal-only, and refuses to force a weak batch. When every candidate fails, the user-facing result must state the Agent's rejection judgment and ask whether the user wants to provide a Xiaohongshu note they consider suitable; a new query is the alternative.
