from __future__ import annotations
from typing import List, Dict
from app.core.vectorstore import query as vs_query
from app.core.llm import ollama

def nearest_cases(summary: str, k: int=10) -> List[Dict]:
    return vs_query(summary, k=k)

def probability(success_weight: float, court_trend: float, argument_quality: float, context_factors: float) -> float:
    return max(0.0, min(1.0, 0.4*success_weight + 0.3*court_trend + 0.2*argument_quality + 0.1*context_factors))

def strategic_reco(summary: str) -> str:
    sys = {"role": "system", "content": "Analyste jurisprudentiel sobre. Donne des recommandations synthétiques chiffrées."}
    user = {"role": "user", "content": f"Cas: {summary}\nFormate: puces 'Dans X% des cas similaires...' + 'Attention: revirement récent...'"}
    return ollama.chat([sys, user])

