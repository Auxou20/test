from __future__ import annotations
from typing import List, Dict
from pathlib import Path
import json
import numpy as np

from app.core.config import CHROMA_DIR  # on réutilise ce dossier pour stocker l'index
from app.core.llm import ollama

INDEX_DIR = Path(CHROMA_DIR)
INDEX_DIR.mkdir(parents=True, exist_ok=True)
INDEX_PATH = INDEX_DIR / "index.json"

# Structure JSON:
# {
#   "ids": [str, ...],
#   "texts": [str, ...],
#   "metadatas": [dict, ...],
#   "embeddings": [[float, ...], ...]
# }

def _load_index():
    if not INDEX_PATH.exists():
        return {"ids": [], "texts": [], "metadatas": [], "embeddings": []}
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_index(idx):
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False)

def add_documents(docs: List[Dict]):
    """
    docs: liste de {id, text, metadata}
    """
    if not docs:
        return
    idx = _load_index()
    texts = [d["text"] for d in docs]
    embeds = ollama.embed(texts)  # -> List[List[float]]
    for d, e in zip(docs, embeds):
        idx["ids"].append(d["id"])
        idx["texts"].append(d["text"])
        idx["metadatas"].append(d.get("metadata", {}))
        idx["embeddings"].append(e)
    _save_index(idx)

def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

def query(text: str, k: int = 5):
    """
    Retourne: List[ {id, text, score, metadata} ] triée par score décroissant (cosine).
    """
    idx = _load_index()
    if not idx["ids"]:
        return []

    q_emb = np.array(ollama.embed([text])[0], dtype=np.float32)
    embs = np.array(idx["embeddings"], dtype=np.float32)

    # calcul cosine pour tous
    # normalise
    qn = q_emb / (np.linalg.norm(q_emb) + 1e-12)
    en = embs / (np.linalg.norm(embs, axis=1, keepdims=True) + 1e-12)
    sims = en @ qn  # produits scalaires => cosines

    order = np.argsort(-sims)[:k]
    out = []
    for i in order:
        out.append({
            "id": idx["ids"][i],
            "text": idx["texts"][i],
            "score": float(sims[i]),
            "metadata": idx["metadatas"][i],
        })
    return out
