# IDOR Bookstore Labs

A set of tiny, independent Flask apps, all themed as the same fictional bookstore ("Pagebound Books"), each one deliberately built with exactly **one** IDOR failure mode baked in (plus a few combo apps at the end that chain two modes together). No shared code between apps on purpose - read each `app.py`, it's short.

Each app has its own README with a one-line tip (not a walkthrough) on what to go look for.

## Setup

### 1. Install Python

You need Python 3.11+.

- **Windows**: install from [python.org/downloads](https://www.python.org/downloads/) (check "Add python.exe to PATH" during install), or `winget install Python.Python.3.12`.
- **macOS**: `brew install python@3.12`
- **Linux**: use your distro's package manager, e.g. `sudo apt install python3.12`

Verify with:

```
python --version
```

### 2. Install uv

This project uses [uv](https://docs.astral.sh/uv/) for dependency management (faster and simpler than raw pip/venv).

- **Windows (PowerShell)**: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- **macOS/Linux**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Or via pip, on any platform: `pip install uv`

Verify with:

```
uv --version
```

### 3. Install dependencies

From the repo root (where `pyproject.toml` lives):

```
uv sync
```

This creates a `.venv` and installs Flask + graphene into it.

### 4. Run an app

Each app is standalone and runs on its own port (noted in each app's README). From the repo root:

```
uv run 01-sequential-int-url-path/app.py
```

(swap in whichever folder you want to attack - only one app needs to be running at a time, or run several at once in separate terminals since each binds its own port)

## Login (every app)

There's no real auth - visit `/login/alice` or `/login/bob` first to set a session cookie, then explore as that user. Alice and Bob each have their own orders/reviews/wishlist/invoices seeded in memory.

## Apps - individual failure modes

| # | Folder | Failure mode |
|---|--------|--------------|
| 1 | `01-sequential-int-url-path` | Sequential integer ID exposed in the URL path |
| 2 | `02-query-string-param` | ID passed via query string instead of path |
| 3 | `03-body-field-post` | ID hidden in a POST JSON body field |
| 4 | `04-header-based-id` | Client-supplied header takes precedence over the session, with no validation |
| 5 | `05-hidden-form-field` | ID carried in a hidden HTML form field |
| 6 | `06-filename-resource-download` | ID embedded in a downloadable resource's filename |
| 7 | `07-uuid-leaked-elsewhere` | "Unguessable" UUID, but leaked via another endpoint and never ownership-checked |
| 8 | `08-encoded-reversible-id` | ID obscured via trivially reversible encoding |
| 9 | `09-username-as-identifier` | Username/email used directly as the lookup key |
| 10 | `10-composite-id` | Multi-tenant composite ID (org + order) with only half validated |
| 11 | `11-batch-endpoint-array-ids` | Single-object endpoint is safe; the bulk/batch variant isn't |
| 12 | `12-graphql-nested-ids` | A single GraphQL query reaches nested objects by ID, with no ownership check |

## Apps - combos (two failure modes chained)

| # | Folder | Combines |
|---|--------|----------|
| 13 | `13-combo-encoded-id-in-body` | Encoded ID (#8) + body field (#3) |
| 14 | `14-combo-composite-id-header-override` | Composite ID (#10) + header override (#4) |
| 15 | `15-combo-uuid-filename-download` | Leaked UUID (#7) + filename-based download (#6) |
