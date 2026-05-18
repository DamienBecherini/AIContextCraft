import subprocess


def get_git_diff(repo_path, ref_a, ref_b):
    """Return the raw Git diff between two revisions."""
    try:
        subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
    except FileNotFoundError as e:
        raise RuntimeError("Git is not installed or not available on PATH.") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Path '{repo_path}' is not a valid Git repository.") from e

    try:
        result = subprocess.run(
            ['git', 'diff', ref_a, ref_b],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        message = stderr if stderr else f"Unable to compute diff between '{ref_a}' and '{ref_b}'."
        raise RuntimeError(message) from e
