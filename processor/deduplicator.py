import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from config import SIMILARITY_THRESHOLD

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def deduplicate_and_merge(articles: list) -> tuple:
    errors = []

    if not articles:
        return [], errors

    try:
        model = _get_model()
        titles = [a["title"] for a in articles]
        embeddings = model.encode(titles, convert_to_numpy=True)
        sim_matrix = cosine_similarity(embeddings)

        visited = set()
        merged = []

        for i in range(len(articles)):
            if i in visited:
                continue

            group = [i]
            for j in range(i + 1, len(articles)):
                if j not in visited and sim_matrix[i][j] >= SIMILARITY_THRESHOLD:
                    group.append(j)
                    visited.add(j)
            visited.add(i)

            base = articles[i].copy()
            if len(group) > 1:
                sources = list({articles[k]["source"] for k in group})
                links = list({articles[k]["link"] for k in group})
                best_desc = max([articles[k]["description"] for k in group], key=len)
                base["source"] = sources
                base["link"] = links
                base["description"] = best_desc
            else:
                base["source"] = [base["source"]]
                base["link"] = [base["link"]]

            merged.append(base)

        return merged, errors

    except Exception as e:
        errors.append(f"Semantic deduplication failed, using title-based fallback: {str(e)}")
        return _title_based_dedup(articles), errors


def _title_based_dedup(articles: list) -> list:
    seen_titles = set()
    result = []
    for a in articles:
        t = a["title"].lower().strip()
        if t not in seen_titles:
            seen_titles.add(t)
            a["source"] = [a["source"]]
            a["link"] = [a["link"]]
            result.append(a)
    return result
