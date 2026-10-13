# Gemini Git Agent

A minimal AI agent powered by Google Gemini that you can chat with about a Git repository. It reads your repo state with tools, then summarizes changes, explains history or drafts commit messages.

```
you> write a commit message for my staged changes
  [tool] git diff --staged

Add retry handling to the HTTP client

Retry failed requests up to 3 times with exponential backoff ...
```

## How it works

Tools are plain Python functions. The `google-genai` SDK reads their signatures and docstrings, passes them to Gemini as tool declarations, and runs the function-calling loop automatically. There is no hand-written loop.

| Tool | Purpose |
|---|---|
| `git_status` | Branch plus changed, staged and untracked files |
| `git_diff` | Working-tree or staged diff |
| `git_log` | Recent commit history |

## Run

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=...   # free key from https://aistudio.google.com/apikey
python agent.py path/to/repo
```

Set `GEMINI_MODEL` to use a different Gemini model (default is `gemini-2.5-flash`).

## Design notes

- Tools are read-only: each one runs a fixed `git` command, and the model can't run arbitrary shell.
- Output is truncated to 8,000 characters so large diffs don't flood the context.
- Chat history persists, so you can follow up with "shorten that" or "what about the previous commit?".
- The only dependency is `google-genai`, so the install is tiny.
