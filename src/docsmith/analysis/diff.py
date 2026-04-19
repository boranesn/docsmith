"""Git diff utilities for incremental documentation updates."""

from pathlib import Path


def changed_files_since(repo_path: str | Path, since: str = "HEAD~1") -> set[str]:
    """Return set of source file paths changed since the given git ref."""
    try:
        import git
        repo = git.Repo(str(repo_path))
        diff = repo.git.diff("--name-only", since, "HEAD")
        return {str(Path(repo_path) / f) for f in diff.splitlines() if f.strip()}
    except Exception:
        return set()
