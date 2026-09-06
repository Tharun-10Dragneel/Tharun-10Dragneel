# Bounded workflow repair design

## Scope
Repair `today.py` and `.github/workflows/build.yaml`. Do not edit SVG files.

## Changes
- Make API calls use a short connect/read timeout.
- Treat GraphQL `errors` and malformed success data as failures.
- Paginate owned repository stars and return the complete total.
- Keep authored commit counts from the existing cache.
- Preserve missing data as an error. Do not convert API failures to zero.
- Make import safe when workflow environment variables are absent.
- Add `workflow_dispatch` and use a supported Python version.
- Make commit and push failures fail the workflow.
- Keep the existing SVG IDs and static SVG content unchanged.

## Checks
- Mock HTTP responses for timeout, HTTP error, GraphQL error, malformed data, and star pagination.
- Check cache commit semantics and import without secrets.
- Check SVG overwrite changes only dynamic text and dynamic dot IDs.
- Validate YAML syntax and run the focused test suite.
- Do not run the full live-history query without valid access and explicit approval.
