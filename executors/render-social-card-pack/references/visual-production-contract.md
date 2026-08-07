# Visual Production Contract

## Input contract

The calling Model or Executor must provide persisted paths for:

| Input | Required | Owner |
| --- | --- | --- |
| Platform-specific card copy | yes | social content package |
| Product claim ledger | yes | `run-social-content-loop` Memory |
| Platform research handoff | yes | `run-social-content-loop` Memory |
| Asset inventory with real screenshots | required for Product-promotion packs | Product/social Memory |
| Run-specific visual profile | optional | owning social Memory package; derived from `SOUL.md` and Product-repository evidence |
| Single visual reference selection | required when external visual research is used | current run `visual-reference-selection.json` |
| Publication policy | yes | Model/platform policy |

The Executor may read these inputs but must not copy Product defaults into its own directory.

## Package shape

```text
visual-vN/
├─ visual-manifest.json
├─ visual-quality-review.json
├─ visual-spec.md
├─ effect-review.md
├─ visual-review.md
├─ index.html
├─ prompts/
│  ├─ effects/
│  └─ formal/
├─ effects/
├─ raw/
├─ render/
└─ assets/
   ├─ brand/
   └─ screenshots/
```

`effects/` and `raw/` are internal production evidence. `render/` contains formal candidates only. Reference research screenshots stay outside publishable asset folders.

An external visual direction must resolve to exactly one validated primary reference. Rejected candidates remain research evidence and must not enter prompts, visual specifications, or reference-image arguments. Product-owned logos and screenshots remain factual assets and do not count as additional external learning samples.

## Manifest

Use UTF-8 JSON:

```json
{
  "schema_version": 1,
  "platform": "xiaohongshu",
  "production_mode": "complete-effect",
  "canvas": {
    "width": 1080,
    "height": 1440,
    "format": "png",
    "color_modes": ["RGB", "RGBA"]
  },
  "quality_review": {
    "file": "visual-quality-review.json",
    "sha256": "64-lowercase-hex-characters"
  },
  "cards": [
    {
      "id": "01-cover",
      "role": "cover",
      "output": "render/01-cover.png",
      "copy_source": "xiaohongshu.md#card-01",
      "user_takeaway": "understand the Product's first concrete benefit",
      "evidence_target": "the exact Product UI object or output proving the claim",
      "prompt": "prompts/formal/01-cover.txt",
      "source_mode": "complete-effect",
      "status": "candidate"
    }
  ]
}
```

Rules:

- `schema_version` must be `1`.
- `platform`, `production_mode`, `canvas`, and `cards` are required.
- Card `id` and `output` must be unique.
- Product capability cards must declare `user_takeaway`, `evidence_target`, and the real screenshot source in the package review or manifest.
- `output` must be a relative path inside the package and point to `render/*.png`.
- Card order in the array is publication order.
- `status` may be `candidate`, `revise`, `blocked`, or `approved`.
- Any manifest containing `approved` cards must bind a passed `visual-quality-review.json` by relative path and SHA-256. Every approved card ID must appear in that review.
- Approval in this manifest means content-package approval only; it does not authorize upload or publication.

## Stage transitions

```text
copy locked
  -> visual spec
  -> vertical slice
  -> effect selected or deterministic mode selected
  -> formal candidates
  -> local corrections
  -> mechanical validation
  -> visual review
  -> social-content review
  -> publishing preparation
```

Do not skip directly from an exploratory effect to publishing preparation.

## Product boundary

The package may contain copies of Product-owned assets needed for this run, with provenance. Stable brand facts remain in `SOUL.md`; canonical assets and implementation stay in the Product repository. Timed selections, visual profiles, crops, prompts, effects, renders, and reviews belong to the owning Model Memory package. SEO Memory must contain neither the package nor copied social assets.
