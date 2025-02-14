"""
Curated wordlists for codename generation.

Each style has an adjective pool and a noun pool.
Words are chosen for distinctiveness and memorability.
"""

from typing import Dict, List


WORDLISTS: Dict[str, Dict[str, List[str]]] = {
    "military": {
        "adjectives": [
            "IRON", "STEEL", "SILENT", "SWIFT", "SHADOW", "DARK", "CRIMSON",
            "THUNDER", "GHOST", "FROZEN", "HOLLOW", "BROKEN", "BLIND",
            "HIDDEN", "LOST", "FALLEN", "BLACK", "WHITE", "GRAY", "LONE",
            "DEAD", "COLD", "RAPID", "RAZOR", "BURNING", "BLEEDING", "CHROME",
            "NUCLEAR", "DIGITAL", "PHANTOM", "ROGUE", "ABSENT", "SILENT",
        ],
        "nouns": [
            "FALCON", "WOLF", "EAGLE", "RAVEN", "VIPER", "COBRA", "TITAN",
            "SENTINEL", "WARDEN", "HAMMER", "ANVIL", "ARROW", "DAGGER",
            "LANCE", "SHIELD", "BASTION", "FORTRESS", "CITADEL", "GARRISON",
            "BRIGADE", "LEGION", "PHANTOM", "WRAITH", "SPECTER", "HUNTER",
            "STRIKER", "RANGER", "TROOPER", "VICTOR", "ALPHA", "OMEGA",
        ],
    },
    "nature": {
        "adjectives": [
            "AMBER", "EMBER", "DRIFT", "WILD", "DEEP", "HOLLOW", "PALE",
            "STORM", "FROST", "MOSS", "ASHEN", "CRIMSON", "GOLDEN", "SILVER",
            "COPPER", "JADE", "OBSIDIAN", "IVORY", "EBONY", "SCARLET",
            "AZURE", "VIOLET", "TEAL", "OCHRE", "SLATE", "RUSSET", "SAGE",
        ],
        "nouns": [
            "FOX", "OAK", "PINE", "CREEK", "RIDGE", "PEAK", "VALE",
            "MARSH", "GLADE", "GROVE", "STONE", "RIVER", "THORN", "BRIAR",
            "FERN", "BIRCH", "CEDAR", "WILLOW", "ASPEN", "HEMLOCK",
            "FALCON", "CROW", "HAWK", "KITE", "LYNX", "BEAR", "ELK",
            "OTTER", "HERON", "WREN", "SWIFT", "FINCH",
        ],
    },
    "abstract": {
        "adjectives": [
            "VOID", "NULL", "ZERO", "LOST", "BROKEN", "EMPTY", "SILENT",
            "BLIND", "HOLLOW", "ABSENT", "FAINT", "LATENT", "DORMANT",
            "PENDING", "SUSPENDED", "STATIC", "DYNAMIC", "VOLATILE",
            "STABLE", "FRAGILE", "RIGID", "FLUID", "DENSE", "SPARSE",
            "PRIME", "INVERSE", "DUAL", "PARALLEL", "RECURSIVE",
        ],
        "nouns": [
            "SIGNAL", "ECHO", "PULSE", "LOOP", "NODE", "VECTOR", "MATRIX",
            "CIPHER", "TOKEN", "FRAME", "STACK", "QUEUE", "HASH", "INDEX",
            "TRACE", "DELTA", "SIGMA", "LAMBDA", "OMEGA", "AXIOM",
            "THEOREM", "LEMMA", "PROOF", "CLAUSE", "TERM", "SCOPE",
            "BUFFER", "CACHE", "RELAY", "SWITCH",
        ],
    },
    "cosmic": {
        "adjectives": [
            "DARK", "BINARY", "SOLAR", "LUNAR", "STELLAR", "COSMIC",
            "NEBULAR", "QUANTUM", "ORBITAL", "RADIANT", "COLLAPSED",
            "EXPANDING", "FROZEN", "BURNING", "DISTANT", "ANCIENT",
            "PRIMORDIAL", "ETERNAL", "INFINITE", "SINGULAR", "HYPERBOLIC",
        ],
        "nouns": [
            "NEBULA", "PULSAR", "QUASAR", "PHOTON", "PROTON", "NEUTRON",
            "NUCLEUS", "ORBIT", "ECLIPSE", "HORIZON", "ZENITH", "NADIR",
            "APOGEE", "PERIGEE", "TRANSIT", "VOID", "RIFT", "FLUX",
            "CORONA", "AURORA", "HELIX", "VORTEX", "SOLSTICE", "EQUINOX",
            "MERIDIAN", "PARALLAX", "PERIHELION",
        ],
    },
}

# Russian wordlist (transliterated for ASCII compatibility)
WORDLISTS_RU: Dict[str, Dict[str, List[str]]] = {
    "military": {
        "adjectives": [
            "БУРЯ", "ТЕНЬ", "ГРОМ", "ПРИЗРАК", "СТАЛЬ", "ТЁМНЫЙ",
            "БЫСТРЫЙ", "МЁРТВЫЙ", "ХОЛОДНЫЙ", "ПУСТОЙ", "СКРЫТЫЙ",
        ],
        "nouns": [
            "СОКОЛ", "ВОЛК", "ОРЁЛ", "ЩИТ", "МЕЧ", "СТРАЖ",
            "КРЕПОСТЬ", "ОТРЯД", "ПРИЗРАК", "ОХОТНИК", "ВИТЯЗЬ",
        ],
    },
}

SUPPORTED_STYLES = list(WORDLISTS.keys())
SUPPORTED_LANGUAGES = ["en", "ru"]
