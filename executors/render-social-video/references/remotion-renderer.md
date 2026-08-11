# Optional Remotion renderer

## Boundary

The repository-local Pillow/FFmpeg renderer remains the default and requires no Remotion installation. Remotion is an optional repository-external renderer for a reviewed video script that benefits from React-driven motion, designed caption choreography or reusable programmatic scenes.

Remotion is source-available under the separate [Remotion License](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md); it is not covered by Growth Lab's Apache-2.0 license. Growth Lab must not vendor Remotion, its source tree, `node_modules`, browser downloads or caches. A generated video does not need a Remotion watermark or attribution in its publication description.

## First-use gate

Before the first Remotion installation or render, tell the user:

- why Remotion is recommended for the requested effect;
- the exact Remotion version that would be installed;
- that individuals, non-profit organizations and for-profit organizations with up to three employees are eligible for the current free license;
- that other for-profit organizations need a Company License;
- that Growth Lab cannot determine the user's legal eligibility for them;
- that the built-in renderer remains available if they do not want to install Remotion.

Install only after the user explicitly confirms that they reviewed the license boundary and are either eligible for the free license or hold the required Company License. Do not infer eligibility from repository visibility, project size, revenue, prior package installation or a generic authorization to generate video.

Record the confirmation outside the repository, for example at:

```text
~/.growth-lab/clients/remotion/license-acknowledgement.json
```

Use a minimal local record:

```json
{
  "schema_version": 1,
  "remotion_version": "4.0.507",
  "license_url": "https://github.com/remotion-dev/remotion/blob/main/LICENSE.md",
  "eligibility_confirmed": true,
  "confirmed_at": "<RFC3339 timestamp>"
}
```

This record documents that Growth Lab showed the boundary; it is not legal advice or a license issued by Growth Lab. Ask again when the acknowledgement is missing, `eligibility_confirmed` is not true, the installed major version differs, or Remotion materially changes its license.

## External installation

Keep the runtime under `~/.growth-lab/clients/remotion/` or inside ignored run Memory. Pin every Remotion package to the same exact version and retain the generated lockfile beside that external runtime. Do not add Remotion to a repository-root manifest or make non-video workflows install it.

For the currently validated version, an Agent may create an external Node project and install exact packages only after the first-use gate:

```powershell
$runtime = "$HOME\.growth-lab\clients\remotion\runtime-4.0.507"
New-Item -ItemType Directory -Force $runtime | Out-Null
Push-Location $runtime
npm init -y
npm install --save-exact remotion@4.0.507 @remotion/cli@4.0.507 react@19.2.3 react-dom@19.2.3
Pop-Location
```

An existing compatible installation may be reused after its package versions and license acknowledgement are checked. Never silently upgrade it. Review the license again before adopting Remotion 5.x or another major version.

## Run evidence

Keep the composition, downloaded media, rendered output and review frames in ignored Product Memory. The video manifest or adjacent review record should preserve:

- renderer name and exact Remotion version;
- composition entry point and SHA-256;
- package-lock SHA-256;
- license acknowledgement path and confirmation timestamp, without copying personal or organization details;
- output hash, dimensions, frame rate, codecs and decode result.

Remotion installation and rendering do not authorize publication. Publication still follows the owning platform package and its separate final-content authorization.
