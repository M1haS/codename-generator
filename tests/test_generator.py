import pytest

from app.core.generator import (
    CodenameExhaustedError,
    generate_batch,
    generate_unique,
    pool_size,
)


def test_generate_returns_string():
    name = generate_unique()
    assert isinstance(name, str)
    assert len(name) > 0


def test_generate_two_words():
    name = generate_unique(word_count=2, separator="space")
    assert len(name.split(" ")) == 2


def test_generate_dash_separator():
    name = generate_unique(separator="dash", word_count=2)
    assert "-" in name


def test_generate_unique_avoids_existing():
    existing = set()
    for _ in range(20):
        name = generate_unique(existing_names=existing)
        assert name not in existing
        existing.add(name)


def test_batch_all_unique():
    names = generate_batch(count=10, style="nature")
    assert len(names) == len(set(names))


def test_batch_respects_existing():
    existing = {"AMBER FOX", "DRIFT OAK"}
    names = generate_batch(count=5, style="nature", existing_names=existing)
    for name in names:
        assert name not in existing


def test_pool_size_single_word():
    size = pool_size("military", word_count=1)
    assert size > 0


def test_pool_size_double_word():
    double = pool_size("military", word_count=2)
    single = pool_size("military", word_count=1)
    assert double > single


def test_exhausted_raises():
    from app.core.wordlists import WORDLISTS
    # Fill existing with entire noun pool to force exhaustion on word_count=1
    all_nouns = set(WORDLISTS["military"]["nouns"])
    with pytest.raises(CodenameExhaustedError):
        generate_unique(word_count=1, existing_names=all_nouns)


def test_all_styles_generate():
    for style in ["military", "nature", "abstract", "cosmic"]:
        name = generate_unique(style=style)
        assert isinstance(name, str)


def test_batch_size_limit():
    with pytest.raises(ValueError):
        generate_batch(count=999)
