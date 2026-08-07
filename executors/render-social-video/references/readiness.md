# Readiness gate

Current status is `generator-ready` for deterministic local rendering. The Seedance adapter is `adapter-ready-not-live-verified`: its offline lifecycle and B-roll integration are implemented, but no real paid task has been created in this repository acceptance cycle. Video publication remains inactive.

## Implementation

- versioned `video-plan` and `video-manifest` schemas;
- deterministic renderer and zero-network fixture;
- optional TTS interface with `none`, `user-audio`, and Windows SAPI paths;
- ffprobe-based validator and representative-frame review;
- video-specific rights, privacy, voice, subtitle, and provenance checks;
- bounded timeouts, idempotent output paths, and no silent retries.
- optional Seedance Ark `check/inspect/run/resume/delete` lifecycle with an ambiguous-create stop marker, signed-URL redaction and generated-B-roll manifest binding;

## Isolation

- a clean clone passes existing tests without video dependencies;
- default onboarding does not request FFmpeg, TTS, GPU, or video API configuration;
- skipping video leaves the canonical brief and every non-video package unchanged;
- all outputs stay under ignored Product Memory;
- removing this directory requires no edits outside its README entry.

## Activation

- add focused automated tests and a minimal 5-10 second fixture;
- validate one 1080x1920 classic render and one 1440x1920 product-demo screenshot/subtitle/audio render; completed mechanically with local acceptance fixtures;
- inspect extracted frames and listen to final audio;
- document external binary and model licenses;
- then add an explicit Model route and `.agents` wrapper in the same activation change.

Activation covers generation only. A real Product run still requires human review of the rendered video and audio. Platform upload/publication must pass a separate Client milestone and authorization.

Seedance moves from `adapter-ready-not-live-verified` to configured readiness only after the user configures an account-owned Ark model endpoint, approves one minimal paid 2–5 second B-roll task, the task is downloaded and decoded, its representative frames pass review, and cleanup behavior is confirmed. Never claim readiness from environment-variable presence alone.
