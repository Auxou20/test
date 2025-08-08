from __future__ import annotations
from typing import Dict, List
from pathlib import Path
from .vectorstore import add_documents, query as vs_query
from ..sources.local_loader import load_pdf
from .llm import ollama

def ingest_path(path: Path):
    if path.suffix.lower() == ".pdf":
        docs = load_pdf(path)
        if docs:
            add_documents(docs)

def answer_with_citations(question: str, k: int=6) -> Dict:
    # Retrieve
    hits = vs_query(question, k=k)
    context_blocks = []
    for h in hits:
        meta = h.get("metadata", {})
        src = meta.get("source", "local")
        page = meta.get("page", "?")
        context_blocks.append(f"[{src} p.{page}] {h['text'][:1000]}")

    system = {"role": "system", "content": "Tu es un assistant juridique qui cite systématiquement ses sources. Réponds en français."}
    user = {"role": "user", "content": f"Question: {question}

Contexte (extraits):
" + "
---
".join(context_blocks) + "

Formate la réponse ainsi:
[Question] → [Analyse] → [Sources primaires] → [Jurisprudence] → [Doctrine] → [Synthèse] → [Points d'attention]
Avec puces, et des références entre crochets vers les sources (fichier et page). Termine par une liste 'Citations' qui reprend les références exactes."}
    out = ollama.chat([system, user])
    return {"answer": out, "hits": hits}
