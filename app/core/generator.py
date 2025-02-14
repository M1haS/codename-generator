"""
Codename Generation Engine

Supports:
- Single word (noun only)
- Double word (adj + noun) — default
- Triple word (adj + adj + noun)
- Custom separator (space, dash, underscore, dot)
- Collision-aware generation via existing_names set
"""

import random
import string
from typing import Optional, Set
from app.core.wordlists import WORDLISTS, WORDLISTS_RU, SUPPORTED_STYLES
from app.config import settings


SEPARATORS = {
    "space": " ",
    "dash": "-",
    "underscore": "_",
    "dot": ".",
}


class CodenameExhaustedError(Exception):
    """Raised when no unique codename can be generated within retry limit."""


def _get_wordlist(style: str, lang: str = "en") -> dict:
    if lang == "ru":
        return WORDLISTS_RU.get(style, WORDLISTS.get(style, WORDLISTS["military"]))
    return WORDLISTS.get(style, WORDLISTS["military"])


def _generate_one(
    style: str,
    lang: str,
    word_count: int,
    separator: str,
) -> str:
    wl = _get_wordlist(style, lang)
    adj_pool = wl["adjectives"]
    noun_pool = wl["nouns"]
    sep = SEPARATORS.get(separator, " ")

    if word_count == 1:
        return random.choice(noun_pool)
    elif word_count == 2:
        return sep.join([random.choice(adj_pool), random.choice(noun_pool)])
    else:  # 3+
        adjs = random.choices(adj_pool, k=word_count - 1)
        return sep.join(adjs + [random.choice(noun_pool)])


def generate_unique(
    style: str = "military",
    lang: str = "en",
    word_count: int = 2,
    separator: str = "space",
    existing_names: Optional[Set[str]] = None,
) -> str:
    """
    Generate a single unique codename not in existing_names.
    Raises CodenameExhaustedError if max retries exceeded.
    """
    existing = existing_names or set()
    for attempt in range(settings.max_retries_on_collision):
        candidate = _generate_one(style, lang, word_count, separator)
        if candidate not in existing:
            return candidate
    raise CodenameExhaustedError(
        f"Could not generate unique codename after {settings.max_retries_on_collision} attempts. "
        f"Namespace may be saturated for style='{style}' lang='{lang}'."
    )


def generate_batch(
    count: int,
    style: str = "military",
    lang: str = "en",
    word_count: int = 2,
    separator: str = "space",
    existing_names: Optional[Set[str]] = None,
) -> list[str]:
    """Generate multiple unique codenames in one call."""
    if count > settings.max_generate_batch:
        raise ValueError(f"Batch size {count} exceeds limit {settings.max_generate_batch}")
    existing = set(existing_names or [])
    results = []
    for _ in range(count):
        name = generate_unique(style, lang, word_count, separator, existing)
        results.append(name)
        existing.add(name)
    return results


def pool_size(style: str, lang: str = "en", word_count: int = 2) -> int:
    """Calculate theoretical pool size for given parameters."""
    wl = _get_wordlist(style, lang)
    adj_count = len(wl["adjectives"])
    noun_count = len(wl["nouns"])
    if word_count == 1:
        return noun_count
    elif word_count == 2:
        return adj_count * noun_count
    else:
        return (adj_count ** (word_count - 1)) * noun_count
