import subprocess


def get_git_diff(repo_path, ref_a, ref_b):
    """Récupère le diff Git brut entre deux révisions."""
    try:
        subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
    except FileNotFoundError as e:
        raise RuntimeError("Git n'est pas installé ou n'est pas disponible dans le PATH.") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Le chemin '{repo_path}' n'est pas un dépôt Git valide.") from e

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
        message = stderr if stderr else f"Impossible de calculer le diff entre '{ref_a}' et '{ref_b}'."
        raise RuntimeError(message) from e
