@echo off
setlocal
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate
pip install -r requirements.txt pyinstaller
REM Assurez-vous qu'Ollama est lancé: ollama serve
pyinstaller --noconfirm --name LEXIS --onefile --windowed app\__main__.py
echo.
echo Build terminé. Voir dist\LEXIS.exe
