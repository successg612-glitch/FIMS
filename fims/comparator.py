import os

from fims.hashing import rehash_file


def compare(baseline, filepath):
    """Return "created", "modified", "deleted", or None by comparing a live
    rehash of filepath against the stored baseline dict."""
    exists = os.path.exists(filepath)
    known = filepath in baseline

    if known and exists:
        current_hash = rehash_file(filepath)
        return "modified" if current_hash != baseline[filepath] else None
    if not known and exists:
        return "created"
    if known and not exists:
        return "deleted"
    return None
