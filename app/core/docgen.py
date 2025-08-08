from __future__ import annotations
from typing import Dict
from jinja2 import Template
from docx import Document

SAMPLE_TEMPLATE = '''
{{ ton|capitalize }} — Projet d'écrit
Juridiction: {{ juridiction }}
Objet: {{ objet }}

Faits résumés:
{{ faits }}

Prétentions & moyens:
{{ moyens }}

Conclusions:
{{ conclusions }}
'''

def generate_markdown(context: Dict) -> str:
    tpl = Template(SAMPLE_TEMPLATE)
    return tpl.render(**context)

def generate_docx(path: str, context: Dict):
    md = generate_markdown(context)
    doc = Document()
    for line in md.splitlines():
        doc.add_paragraph(line)
    doc.save(path)
    return path
