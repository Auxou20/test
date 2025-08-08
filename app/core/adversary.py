from __future__ import annotations
from typing import Dict
from .llm import ollama

TEMPLATE = '''
Mode "Avocat du Diable". Attaque méthodiquement les arguments ci-dessous.
1) Critique formelle (structure, syllogismes) 
2) Critique substantielle (fondements légaux, interprétations alternatives) 
3) Critique stratégique (failles exploitables)
Puis attribue un score 1-10 par argument et propose des renforcements + alternatives si score < 7.
Retourne un rapport concis avec une matrice risque/impact.
Arguments:
{args}
'''

def critique(arguments: str) -> Dict:
    sys = {"role": "system", "content": "Tu es un contre-argumentateur juridique méticuleux."}
    user = {"role": "user", "content": TEMPLATE.format(args=arguments)}
    txt = ollama.chat([sys, user])
    return {"report": txt}
