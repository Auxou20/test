from __future__ import annotations
from pathlib import Path
from typing import List, Dict
from PyPDF2 import PdfReader

def load_pdf(path: Path) -> List[Dict]:
    reader = PdfReader(str(path))
    docs = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            docs.append({
                "id": f"{path.name}-p{i}",
                "text": text,
                "metadata": {"source": str(path), "page": i, "type": "pdf"}
            })
    return docs
