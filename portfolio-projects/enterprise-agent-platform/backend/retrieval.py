"""Local evidence retrieval with normalized TF-IDF + lexical overlap.
No network calls or externally fetched user content.
"""
from __future__ import annotations
import re
from typing import Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def retrieve(query: str, documents: list[dict[str, str]], limit: int = 3) -> list[dict[str, Any]]:
    if not documents or limit < 1:
        return []
    texts = [d['text'] for d in documents]
    safe_query = query.strip() or ' '.join(texts[:1])
    try:
        v = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', max_features=12000)
        matrix = v.fit_transform(texts + [safe_query])
        dense_scores = cosine_similarity(matrix[-1:], matrix[:-1])[0]
    except ValueError:  # Empty vocabulary (e.g. punctuation only)
        dense_scores = [0.0] * len(texts)
    tokens = set(re.findall(r'[a-z0-9]{3,}', safe_query.lower()))
    candidates = []
    for index, doc in enumerate(documents):
        terms = set(re.findall(r'[a-z0-9]{3,}', doc['text'].lower()))
        lexical = len(tokens & terms) / max(1, len(tokens))
        score = .8 * float(dense_scores[index]) + .2 * lexical
        candidates.append({'evidence_id': doc['id'], 'score': round(score, 5), 'excerpt': doc['text'][:240]})
    return sorted((c for c in candidates if c['score'] > 0), key=lambda c: (-c['score'], c['evidence_id']))[:limit]
