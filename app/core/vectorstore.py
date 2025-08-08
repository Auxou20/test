from __future__ import annotations
import chromadb
from chromadb.config import Settings
from typing import List, Dict
from app.core.config import CHROMA_DIR
from app.core.llm import ollama

_client = chromadb.Client(Settings(persist_directory=str(CHROMA_DIR)))
_collection = _client.get_or_create_collection("legal_docs")

def add_documents(docs: List[Dict]):
    ids = [d["id"] for d in docs]
    texts = [d["text"] for d in docs]
    metadatas = [d.get("metadata", {}) for d in docs]
    embeddings = ollama.embed(texts)
    _collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
    _client.persist()

def query(text: str, k: int=5):
    emb = ollama.embed([text])[0]
    res = _collection.query(query_embeddings=[emb], n_results=k)
    out = []
    for i in range(len(res["ids"][0])):
        out.append({
            "id": res["ids"][0][i],
            "text": res["documents"][0][i],
            "score": res["distances"][0][i] if "distances" in res else None,
            "metadata": res["metadatas"][0][i]
        })
    return out

