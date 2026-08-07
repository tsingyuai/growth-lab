# Cross-platform orchestration

## Supported combinations

| Research | Distribution | Behavior |
|---|---|---|
| multi-source | single target | synthesize evidence into one brief, then generate one native package |
| multi-source | multi-target | synthesize evidence once, then generate independent native packages |
| single source | same target | learn only approved dimensions and generate a native package |
| single source | other target(s) | preserve evidence and abstract structure, then rewrite for each target |
| user-provided only | single target | use only the supplied evidence and approved learning scope |
| user-provided only | multi-target | generate independent packages from the same approved evidence |

## Files and transitions

```text
research-plan.json
  -> research/<source evidence>
  -> canonical-brief.json
  -> packages/<platform>/copy.md
  -> packages/<platform>/source-boundary.md
  -> packages/<platform>/publish-manifest.json
  -> packages/<platform>/video/video-manifest.json  (only when formats includes video)
```

Run `validate_orchestration.py` at three transitions:

- `plan`: before collection; allows read-only research without lifecycle content consent.
- `generation`: before generating or transforming publishable content; requires full `content_governance` and an approved brief linked to the exact plan hash.
- `packages`: after all target variants; requires one package per target, exact brief hashes, native constraints, source boundaries, existing files, and publishing disabled. A target requesting `video` must also contain a rendered-not-published video manifest and an existing final video file.
- A video route first resolves visual input: reuse one current reviewed card pack when eligible; otherwise generate a video-only card pack through `render-social-card-pack`. Imported cards and the copied source visual manifest stay inside `packages/<platform>/video/`; a video-only card pack does not create another platform publishing target.

The canonical brief is not publishable copy. It contains shared facts, audience, objective, core message, evidence-backed insights, and target-specific message jobs. A target package may have one primary reference anchor. `close-replication` may map that anchor's full card order and relative layout only after explicit risk confirmation; supporting sources remain evidence and must not be blended into the replicated map.
