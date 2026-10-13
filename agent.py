"""A tiny Git assistant powered by Google Gemini: ask about your repo, get commit messages and change summaries.

Usage: python agent.py [path-to-git-repo]
Try:   "write a commit message for my staged changes"
"""
import os
import subprocess
import sys

from google import genai
from google.genai import types

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
REPO = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")

client = genai.Client()  # reads GEMINI_API_KEY from the environment

SYSTEM = (
    f"You are a Git assistant for the repository at {REPO}. Use your tools to inspect it before answering. "
    "When asked for a commit message, use a short imperative subject line plus a brief body if needed."
)


def git(*args: str) -> str:
    """Run a fixed, read-only git command in the repo and return its output."""
    print(f"  [tool] git {' '.join(args)}")
    result = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, timeout=30)
    return (result.stdout or result.stderr)[:8000] or "(no output)"


# Gemini turns these plain Python functions into tools using their signatures and docstrings.
def git_status() -> str:
    """Show the current branch plus changed, staged and untracked files."""
    return git("status", "--short", "--branch")


def git_diff(staged: bool = False) -> str:
    """Show the diff of changes in the working tree, or of staged changes when staged is true."""
    return git("diff", "--staged") if staged else git("diff")


def git_log(count: int = 10) -> str:
    """Show the most recent commits, one per line (at most 50)."""
    return git("log", f"-{min(count, 50)}", "--oneline", "--decorate")


if __name__ == "__main__":
    # The chat object keeps history, and the SDK runs the function-calling loop automatically.
    chat = client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(system_instruction=SYSTEM, tools=[git_status, git_diff, git_log]),
    )
    print(f"Git assistant for {REPO} (Ctrl+C to quit)")
    while True:
        question = input("\nyou> ").strip()
        if question:
            print("\n" + chat.send_message(question).text)
