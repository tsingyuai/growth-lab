# Credential and data safety

## Configure credentials

Read credentials from the current process environment, a system keychain, or a local environment file excluded by Git. Keep committed `.env.example` files limited to empty variable names and documentation.

Supported variables:

- `BING_WEBMASTER_API_KEY`
- `INDEXNOW_KEY`
- `INDEXNOW_KEY_LOCATION`
- `SITE_URL`
- image Executor variables: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `GEMINI_API_KEY`, and `GOOGLE_GEMINI_BASE_URL`

## Handle secrets

- Check whether a variable exists without printing its value.
- Keep credentials out of source files, Markdown, JSON, generated HTML, screenshots, issue text, commits, shell history, and command arguments.
- Redact query parameters, authorization headers, cookies, and tokens from diagnostic output.
- Avoid saving third-party responses that echo request credentials.
- Rotate a credential immediately when it has been committed or exposed.

## Handle collected data

Store only the evidence needed for the current growth question. Respect platform terms, user consent, privacy obligations, copyright, and retention requirements. Keep sensitive exports in ignored local paths.
