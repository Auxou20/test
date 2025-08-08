from __future__ import annotations
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTabWidget, QTextEdit, QPushButton, QFileDialog, QLabel, QLineEdit, QHBoxLayout
)
from PySide6.QtCore import Qt
import sys
from pathlib import Path

from ..core.rag import ingest_path, answer_with_citations
from ..core.adversary import critique
from ..core.docgen import generate_markdown, generate_docx
from ..core.predictive import nearest_cases, probability, strategic_reco
from ..core.alerts import start_alerts, stop_alerts, notifier

def _row(label: str, widget):
    row = QHBoxLayout()
    row.addWidget(QLabel(label))
    row.addWidget(widget)
    return row

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LEXIS – Assistant IA Juridique (local)")
        self.resize(1100, 700)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._tab_qa(), "Q&A Sourcé")
        self.tabs.addTab(self._tab_adversaire(), "Adversaire IA")
        self.tabs.addTab(self._tab_docs(), "Génération docs")
        self.tabs.addTab(self._tab_predictif(), "Prédictif")
        self.tabs.addTab(self._tab_veille(), "Veille")

        lay = QVBoxLayout()
        lay.addWidget(self.tabs)
        self.setLayout(lay)

    # --- Q&A ---
    def _tab_qa(self):
        w = QWidget()
        lay = QVBoxLayout(w)

        self.qa_question = QTextEdit()
        self.qa_answer = QTextEdit(); self.qa_answer.setReadOnly(True)

        btn_box = QHBoxLayout()
        btn_ingest = QPushButton("Importer PDF…")
        btn_ask = QPushButton("Poser la question")
        btn_box.addWidget(btn_ingest); btn_box.addWidget(btn_ask)

        btn_ingest.clicked.connect(self._ingest_pdf)
        btn_ask.clicked.connect(self._ask_qa)

        lay.addWidget(QLabel("Question juridique:"))
        lay.addWidget(self.qa_question)
        lay.addLayout(btn_box)
        lay.addWidget(QLabel("Réponse (avec citations):"))
        lay.addWidget(self.qa_answer)
        return w

    def _ingest_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir un PDF", "", "PDF Files (*.pdf)")
        if path:
            ingest_path(Path(path))
            self.qa_answer.setText(f"Ingestion terminée: {path}")

    def _ask_qa(self):
        q = self.qa_question.toPlainText().strip()
        if not q:
            return
        res = answer_with_citations(q, k=6)
        self.qa_answer.setText(res["answer"])

    # --- Adversaire IA ---
    def _tab_adversaire(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        self.adv_args = QTextEdit()
        self.adv_report = QTextEdit(); self.adv_report.setReadOnly(True)
        btn = QPushButton("Analyser (Avocat du Diable)")
        btn.clicked.connect(self._run_adv)
        lay.addWidget(QLabel("Arguments à tester:"))
        lay.addWidget(self.adv_args)
        lay.addWidget(btn)
        lay.addWidget(QLabel("Rapport:"))
        lay.addWidget(self.adv_report)
        return w

    def _run_adv(self):
        args = self.adv_args.toPlainText().strip()
        if not args: return
        rep = critique(args)
        self.adv_report.setText(rep["report"])

    # --- Génération docs ---
    def _tab_docs(self):
        w = QWidget()
        lay = QVBoxLayout(w)

        self.doc_ton = QLineEdit("Offensif")
        self.doc_juridiction = QLineEdit("TJ Paris")
        self.doc_objet = QLineEdit("Référé provision")
        self.doc_faits = QTextEdit("Faits…")
        self.doc_moyens = QTextEdit("Moyens…")
        self.doc_concl = QTextEdit("Conclusions…")
        btn_gen_md = QPushButton("Générer (markdown)")
        btn_gen_docx = QPushButton("Générer .docx")

        btn_gen_md.clicked.connect(self._gen_md)
        btn_gen_docx.clicked.connect(self._gen_docx)

        lay.addLayout(_row("Ton:", self.doc_ton))
        lay.addLayout(_row("Juridiction:", self.doc_juridiction))
        lay.addLayout(_row("Objet:", self.doc_objet))
        lay.addWidget(QLabel("Faits:")); lay.addWidget(self.doc_faits)
        lay.addWidget(QLabel("Moyens:")); lay.addWidget(self.doc_moyens)
        lay.addWidget(QLabel("Conclusions:")); lay.addWidget(self.doc_concl)
        lay.addWidget(btn_gen_md); lay.addWidget(btn_gen_docx)

        self.doc_preview = QTextEdit(); self.doc_preview.setReadOnly(True)
        lay.addWidget(QLabel("Aperçu:"))
        lay.addWidget(self.doc_preview)
        return w

    def _gen_md(self):
        ctx = {
            "ton": self.doc_ton.text(),
            "juridiction": self.doc_juridiction.text(),
            "objet": self.doc_objet.text(),
            "faits": self.doc_faits.toPlainText(),
            "moyens": self.doc_moyens.toPlainText(),
            "conclusions": self.doc_concl.toPlainText()
        }
        md = generate_markdown(ctx)
        self.doc_preview.setText(md)

    def _gen_docx(self):
        ctx = {
            "ton": self.doc_ton.text(),
            "juridiction": self.doc_juridiction.text(),
            "objet": self.doc_objet.text(),
            "faits": self.doc_faits.toPlainText(),
            "moyens": self.doc_moyens.toPlainText(),
            "conclusions": self.doc_concl.toPlainText()
        }
        path, _ = QFileDialog.getSaveFileName(self, "Enregistrer", "projet.docx", "Docx (*.docx)")
        if path:
            generate_docx(path, ctx)
            self.doc_preview.setText(f"Document enregistré: {path}")

    # --- Prédictif ---
    def _tab_predictif(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        self.pred_summary = QTextEdit("Résumé factuel et juridique du cas…")
        self.pred_out = QTextEdit(); self.pred_out.setReadOnly(True)
        self.pred_success = QLineEdit("0.6")
        self.pred_court = QLineEdit("0.5")
        self.pred_quality = QLineEdit("0.7")
        self.pred_context = QLineEdit("0.5")
        btn_sim = QPushButton("Cas similaires")
        btn_prob = QPushButton("Probabilité")
        btn_reco = QPushButton("Recommandations")

        btn_sim.clicked.connect(self._pred_sim)
        btn_prob.clicked.connect(self._pred_prob)
        btn_reco.clicked.connect(self._pred_reco)

        lay.addWidget(QLabel("Résumé du cas:")); lay.addWidget(self.pred_summary)
        lay.addLayout(_row("poids_jurisprudence_similaire (0-1):", self.pred_success))
        lay.addLayout(_row("poids_tendance_tribunal (0-1):", self.pred_court))
        lay.addLayout(_row("poids_qualité_arguments (0-1):", self.pred_quality))
        lay.addLayout(_row("poids_facteurs_contextuels (0-1):", self.pred_context))
        lay.addWidget(btn_sim); lay.addWidget(btn_prob); lay.addWidget(btn_reco)
        lay.addWidget(QLabel("Sortie:")); lay.addWidget(self.pred_out)
        return w

    def _pred_sim(self):
        res = nearest_cases(self.pred_summary.toPlainText(), k=5)
        txt = "\n\n".join([f"- {r['metadata'].get('source','local')} p.{r['metadata'].get('page','?')} — score={r.get('score')}" for r in res])
        self.pred_out.setText(txt or "Aucun similaire (ingérez d'abord des décisions).")

    def _pred_prob(self):
        vals = [float(self.pred_success.text()), float(self.pred_court.text()),
                float(self.pred_quality.text()), float(self.pred_context.text())]
        prob = probability(*vals)
        self.pred_out.setText(f"Probabilité de succès estimée: {prob*100:.1f}%")

    def _pred_reco(self):
        txt = strategic_reco(self.pred_summary.toPlainText())
        self.pred_out.setText(txt)

    # --- Veille ---
    def _tab_veille(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        self.veille_log = QTextEdit(); self.veille_log.setReadOnly(True)
        btn_start = QPushButton("Démarrer (toutes les 6h)")
        btn_stop = QPushButton("Arrêter")
        btn_refresh = QPushButton("Rafraîchir journaux")

        btn_start.clicked.connect(lambda: start_alerts(self._job, minutes=360))
        btn_stop.clicked.connect(lambda: (stop_alerts(), self._refresh_log()))
        btn_refresh.clicked.connect(self._refresh_log)

        lay.addWidget(QLabel("Veille juridique (démo)"))
        lay.addWidget(btn_start); lay.addWidget(btn_stop); lay.addWidget(btn_refresh)
        lay.addWidget(self.veille_log)
        return w

    def _job(self):
        from ..core.alerts import sample_watch_job
        sample_watch_job()

    def _refresh_log(self):
        lines = [f"{t:%Y-%m-%d %H:%M} — {title}: {msg}" for t,title,msg in notifier.events[-100:]]
        self.veille_log.setText("\n".join(lines))

def run_app():
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
