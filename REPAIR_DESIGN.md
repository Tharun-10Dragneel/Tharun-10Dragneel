# Bounded workflow repair design

## Scope
Repair transient GitHub failures in `today.py`. Do not edit SVG files.

## Evidence
The live workflow failed after five minutes with HTTP 503 from `recursive_loc`. The current code alternates recursive calls between `recursive_loc` and `loc_counter_one_repo` for each history page.

## Changes
- Retry only transient HTTP 502, 503, 504, 429, and network timeout/connection errors.
- Use a small fixed retry limit and bounded backoff. Fail after exhaustion.
- Replace inner history recursion with an iterative cursor loop.
- Filter inner history by the authenticated owner ID while retaining the local author-ID guard.
- Keep the outer unfiltered history `totalCount` for cache invalidation.
- Preserve fail-fast behavior for authentication and other API errors.

## Checks
- Mock more than 100 history entries and mixed primary authors, foreign authors, and null authors.
- Check empty repositories and empty filtered matches.
- Check cursor progress guards.
- Check transient retry success and exhaustion.
- Check fail-fast authentication errors.
- Run the real `__main__` harness with mocked HTTP and both SVG copies.
- Run formatter, lint, compile, and the focused test suite.
