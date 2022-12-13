"""Util functions for retinal scanner."""
from hashlib import blake2b


def get_hash(data: str, length=8) -> str:
    """Return a blake2b hash hex digest from the specified string."""
    return blake2b(data.encode("utf-8"), digest_size=8).hexdigest()
