import re
from difflib import SequenceMatcher
from typing import Iterable

from .file_handler import load_lines, SEEN_TEXTS_FILE
from ..config import SIMILARITY_THRESHOLD


def _normalize(text: str) -> str:
    if not text:
        return ""
    t = re.sub(r"<[^>]+>", "", text)
    t = re.sub(r"\s+", " ", t)
    return t.strip().lower()


def is_semantic_duplicate(candidate: str, seen_texts: Iterable[str] = None, threshold: float = None, lookback: int = 500) -> bool:
    """Lightweight semantic duplicate check.

    Strategy:
    - Normalize candidate (title + description) and compare with recently seen texts
      using difflib.SequenceMatcher ratio. This is a cheap fallback when embedding
      models are unavailable. Returns True if any seen text has ratio >= threshold.

    - If seen_texts is None, loads last `lookback` lines from data/seen_texts.txt.

    Note: threshold defaults to config.SIMILARITY_THRESHOLD.
    """
    if threshold is None:
        threshold = SIMILARITY_THRESHOLD
    cand = _normalize(candidate)
    if not cand:
        return False

    if seen_texts is None:
        seen_texts = load_lines(SEEN_TEXTS_FILE)[-lookback:]

    for s in seen_texts:
        s_norm = _normalize(s)
        if not s_norm:
            continue
        score = SequenceMatcher(None, cand, s_norm).ratio()
        if score >= threshold:
            return True
    return False
