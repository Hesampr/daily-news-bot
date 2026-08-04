import os
import time
import numpy as np
from pathlib import Path

STORE_PATH = Path(__file__).parent.parent.parent / "data" / "seen_embeddings.npz"


def _ensure_dir():
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_store():
    if not STORE_PATH.exists():
        return np.zeros((0, 0), dtype=float), []
    try:
        with np.load(STORE_PATH, allow_pickle=True) as d:
            embs = d["embeddings"]
            metas = d["meta"].tolist() if "meta" in d else []
            return embs, metas
    except Exception:
        return np.zeros((0, 0), dtype=float), []


def save_store(embeddings: np.ndarray, meta: list):
    _ensure_dir()
    try:
        np.savez_compressed(STORE_PATH, embeddings=embeddings, meta=np.array(meta, dtype=object))
    except Exception as e:
        raise


def find_similar(embedding: np.ndarray, threshold: float, top_k: int = 5) -> bool:
    """Return True if any stored embedding has cosine similarity >= threshold."""
    embs, metas = load_store()
    if embs.size == 0:
        return False
    # normalize
    try:
        a = embedding.astype(float)
        a_norm = a / np.linalg.norm(a)
        embs_norm = embs / np.linalg.norm(embs, axis=1, keepdims=True)
        sims = embs_norm.dot(a_norm)
        if np.any(sims >= threshold):
            return True
    except Exception:
        return False
    return False


def add_embeddings(new_embeddings: np.ndarray, new_meta: list, cap: int = 2000):
    """Append new_embeddings (2D) and meta (list of dicts). Caps total stored rows to `cap` by dropping oldest."""
    if new_embeddings is None or len(new_embeddings) == 0:
        return
    embs, metas = load_store()
    if embs.size == 0:
        embs = np.array(new_embeddings, dtype=float)
        metas = list(new_meta)
    else:
        embs = np.vstack([embs, np.array(new_embeddings, dtype=float)])
        metas = list(metas) + list(new_meta)
    # cap
    if embs.shape[0] > cap:
        keep = embs.shape[0] - cap
        embs = embs[keep:]
        metas = metas[keep:]
    save_store(embs, metas)


def meta_for_article(article: dict) -> dict:
    return {"ts": time.time(), "title": article.get("title"), "source": article.get("source")}
