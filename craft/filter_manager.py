def normalize_glob_patterns(patterns):
    """Normalise les patterns pour un matching cross-platform cohérent."""
    if not patterns:
        return []
    normalized = []
    for pattern in patterns:
        if not pattern:
            continue
        cleaned = pattern.strip()
        if not cleaned:
            continue
        normalized.append(cleaned.replace('\\', '/'))
    return normalized
