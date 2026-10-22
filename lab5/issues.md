# Issues found in `movie_reviews.py`

Tool versions: Pylint 4.1.3, Bandit 1.9.4, Flake8 7.4.1, Python 3.13.16.
Baseline: Pylint 5.47/10, Bandit 4 findings (1 High, 1 Medium, 2 Low), Flake8 4 findings.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Weak MD5 hash (Bandit B324, High/High) | Security | 46 | `hashlib.md5(...)` is flagged as a weak hash for security use. It is used here only to fingerprint a review, not for security. | Pass `usedforsecurity=False`. This states the real intent and keeps the review id unchanged. |
| Binding to all interfaces (Bandit B104, Medium/Medium) | Security | 4 | `STREAM_HOST = "0.0.0.0"` would expose the stream on every network interface. | Default to loopback `127.0.0.1`, overridable with the `STREAM_HOST` environment variable. |
| Hardcoded password (Bandit B105, Low/Medium) | Security | 6 | `MODERATOR_PASSWORD = "reviews-demo"` is a secret in source. It is never used anywhere. | Delete the unused constant. |
| `random` for selection (Bandit B311, Low/High) | Security | 41 | `random.choice` is not a cryptographic generator. | Use `secrets.choice`. Same behaviour (a uniformly random pick), no suppression comment needed. |
| `import`-time side effect, no main guard (found by manual review) | Bug | 75 | `main()` runs at module level, so importing the module runs the whole demo. | Wrap in `if __name__ == "__main__":`. |
| `pick_featured` crashes on an empty board (found by manual review) | Bug | 41 | `random.choice` on an empty list raises an unhelpful `IndexError`. | Raise a clear `ValueError("No movies to feature")`. |
| Unknown title gives a bare `KeyError` (found by manual review) | Bug | 20, 27 | `rate_movie` and `average_rating` index `movies[title]` directly. | Not fixing: the exception type is reasonable for a missing key and changing it is outside the lab scope. |
| Global statement (Pylint W0603) | Code Quality | 8, 40 | `pick_featured` mutates a module global `featured` that nothing else reads. | Remove the global. The function just returns the choice. |
| camelCase names (Pylint C0103) | Code Quality | 11, 16, 26, 34, 39, 45, 48, 54 | `addMovie`, `rateMovie`, `reviewText` and others break snake_case. | Rename to `add_movie`, `rate_movie`, `review_text`, etc. and update all callers. |
| Missing docstrings (Pylint C0114, C0116) | Maintainability | 1, 11, 16, 26, 34, 39, 45, 48, 54, 58 | No module docstring and no function docstrings. | Add a short docstring to the module and every function. |
| Unnecessary `else` after `return` (Pylint R1705) | Code Quality | 28-31 | `else` branch is redundant after `return`. | Remove the `else` and de-indent. |
| `range(len(...))` loop (Pylint C0200) | Code Quality | 50 | Index loop over a list. | Use `enumerate(titles, start=1)`. |
| Missing whitespace around `=` (Flake8 E225) | Style | 35 | `ranked=sorted(...)` | Add spaces. |
| Missing blank line (Flake8 E302) | Style | 48 | Only one blank line before a top-level def. | Add a second blank line. |
| Inline comment spacing (Flake8 E261) | Style | 70 | Fewer than two spaces before `#`. | Use two spaces. |
| Missing space after comma (Flake8 E231) | Style | 72 | `print("Genres:",sorted(...))` | Add a space after the comma. |

**Severity ordering used:** Bandit findings first, ordered by Bandit's own severity (High, Medium, Low). Then real bugs found by manual review. Then Pylint and Flake8 findings, which carry no severity of their own, ranked by my judgement: design and logic problems, then naming, docstrings and unused code, then whitespace and line length.

**Grouping:** repeated identical findings (eight naming warnings, ten docstring warnings) share one row with all line numbers, because each has the same fix.

**Status:** to be filled in after fixing.
