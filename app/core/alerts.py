from __future__ import annotations
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from typing import Callable, List

class Notifier:
    def __init__(self):
        self.events = []

    def notify(self, title: str, msg: str):
        self.events.append((datetime.now(), title, msg))

notifier = Notifier()
scheduler = BackgroundScheduler()

def start_alerts(job: Callable, minutes: int=360):
    if not scheduler.running:
        scheduler.start()
    scheduler.add_job(job, "interval", minutes=minutes, id="legal_watch", replace_existing=True)

def stop_alerts():
    if scheduler.running:
        scheduler.remove_job("legal_watch")
        scheduler.shutdown()

def sample_watch_job():
    # Placeholder: ici on appellerait Legifrance/DILA et on filtre par domaines
    notifier.notify("Veille juridique", "Nouveau texte détecté (exemple).")
