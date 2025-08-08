# LEXIS – Assistant IA Juridique (Windows .exe via PyInstaller)

**Objectif** : Application Windows (GUI) pour avocats, avec modèle IA **local** via [Ollama](https://ollama.com/) (pas d’envoi des dossiers sensibles), RAG (ChromaDB) pour vos documents, connecteurs législatifs (API Légifrance/PISTE), et fonctionnalités avancées : Q&A sourcé, mode *Avocat du Diable*, génération de documents, scoring prédictif, et veille.

## Aperçu des modules
- `app/` : code de l’application (GUI PySide6 et logique).
- `app/core/llm.py` : client Ollama (chat + embeddings) — **nécessite Ollama installé** et un modèle local (ex: `mistral`, `llama3`, ou un modèle juridique si dispo).
- `app/core/vectorstore.py` : stockage Chroma local (./var/chroma).
- `app/core/rag.py` : pipeline RAG (ingestion PDF/DOCX, recherche sémantique, citations).
- `app/core/adversary.py` : critique adverse et scoring (1-10) avec générateur de rapport.
- `app/core/docgen.py` : génération de projets d’actes via templates Jinja2 → Markdown/Docx.
- `app/core/predictive.py` : rapprochement jurisprudentiel (similarité) + probabilité heuristique.
- `app/core/alerts.py` : veille (APScheduler) + connecteurs (Légifrance API/PISTE).
- `app/sources/legifrance_api.py` : **exemple** d’intégration de l’API Légifrance (clé requise).
- `app/ui/` : interface PySide6 (onglets : Q&A, Adversaire, Documents, Prédictif, Veille).
- `.github/workflows/windows-build.yml` : CI GitHub Actions pour générer l’`.exe` Windows.
- `build.bat` : build local de l’exécutable via PyInstaller.

## Prérequis
- **Windows 10/11 (64-bit)**
- **Python 3.10+**
- **Ollama** (installer depuis https://ollama.com/). Puis télécharger un modèle :  
  `ollama pull mistral`  (ou `llama3`, `mixtral`, etc.)  
  Embeddings : `ollama pull nomic-embed-text`
- (**Optionnel**) Clé API **Légifrance/PISTE** si vous voulez la recherche en ligne légale.
- (**Optionnel**) Clé SERP/Brave/Tavily si vous branchez un moteur de recherche généraliste.

## Installation locale (dev)
```bash
python -m venv .venv
. .venv/Scripts/activate  # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env  # puis éditez .env
python -m app  # lance la GUI
```

## Build Windows (.exe)
### Local
```bash
pip install -r requirements.txt
pip install pyinstaller
# Assurez-vous qu'Ollama tourne : 'ollama serve'
# One-file peut être lourd; on-folder est plus simple au début :
pyinstaller --noconfirm --name LEXIS --onefile --windowed app/__main__.py
# L'exécutable est dans dist/LEXIS.exe
```

### GitHub Actions
- Poussez ce repo sur GitHub.
- Le workflow `.github/workflows/windows-build.yml` construira l’exe et publiera un **artifact** téléchargeable dans l’onglet *Actions*.

## Confidentialité & conformité
- **Aucune donnée client envoyée au cloud** si vous utilisez uniquement Ollama + RAG local.
- Pour les sources en ligne (Légifrance/PISTE), vous restez dans les ToS officielles. **Évitez le scraping** de sites payants (Dalloz, Doctrine) : respectez leurs licences.

## Sélection du modèle
Mettez à jour `.env` :
```
OLLAMA_BASE_URL=http://127.0.0.1:11434
LLM_MODEL=mistral
EMBED_MODEL=nomic-embed-text
```
Vous pouvez tester des modèles juridiques (si disponibles sous Ollama) ou charger des GGUF dans Ollama.

## Notes sur les citations
Le RAG renvoie : **[Question] → [Analyse] → [Sources primaires] → [Jurisprudence] → [Doctrine] → [Synthèse] → [Points d’attention]**, avec **citations cliquables** quand l’URL est connue et référence fichier/page quand local.

Bon dev !
