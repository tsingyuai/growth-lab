# X local runtime

The repository distributes the read-only Client, tests, and workflow instructions. Python dependencies and the persistent browser profile live outside the repository.

Readiness requires all of the following:

1. repository-local `collect_x.py` and its declared Playwright environment;
2. a real Chrome or Edge executable (`auto` falls back from Chrome to Edge);
3. `--preflight` validating the shared `SOCIAL_PROXY_MODE` route (`auto`, `direct`, `system`, or `explicit`);
4. a repository-external profile with a valid user-completed X login;
5. a loopback-only CDP endpoint on the configured `X_BROWSER_CDP_PORT`;
6. one low-frequency, non-empty read when the intended query has results.

The presence of a profile directory alone never proves login readiness. A reachable local proxy port alone never proves that X is reachable through it. In `system` mode, the normal browser inherits Windows/PAC/domain-routing rules without a browser-specific proxy argument. X must not define a platform-specific proxy secret; it consumes the shared social proxy policy and keeps loopback services outside the proxy. Do not copy another project's authentication files into Growth Lab.
