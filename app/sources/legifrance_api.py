from __future__ import annotations
from typing import List, Dict, Optional
import httpx, time
from ..core.config import PILOTAGE_API_CLIENT_ID, PILOTAGE_API_CLIENT_SECRET

# NOTE: Exemple simplifié. L’API Légifrance/PISTE requiert l’obtention de jetons OAuth2.
# Référez-vous à leur documentation officielle. Ici, on expose une signature prête à l’emploi.

TOKEN_URL = "https://oauth.piste.gouv.fr/api/oauth/token"
SEARCH_URL = "https://api.piste.gouv.fr/dila/legifrance-beta/lf-engine-app/search"

class LegifranceClient:
    def __init__(self, client_id: str = PILOTAGE_API_CLIENT_ID, client_secret: str = PILOTAGE_API_CLIENT_SECRET):
        self.client_id = client_id
        self.client_secret = client_secret
        self._token = None
        self._token_exp = 0

    def _get_token(self) -> Optional[str]:
        if not self.client_id or not self.client_secret:
            return None
        now = time.time()
        if self._token and now < self._token_exp - 60:
            return self._token
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "openid"
        }
        with httpx.Client(timeout=30.0) as client:
            r = client.post(TOKEN_URL, data=data)
            r.raise_for_status()
            d = r.json()
        self._token = d.get("access_token")
        self._token_exp = now + int(d.get("expires_in", 3600))
        return self._token

    def search(self, query: str, page: int=1) -> List[Dict]:
        token = self._get_token()
        if not token:
            return []
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"query": query, "pageNumber": page}
        with httpx.Client(timeout=30.0) as client:
            r = client.post(SEARCH_URL, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
        # Normalisez la sortie selon vos besoins (titre, url, extrait)
        items = []
        for it in data.get("results", []):
            items.append({
                "title": it.get("title"),
                "url": it.get("url"),
                "snippet": it.get("snippet", ""),
                "source": "legifrance"
            })
        return items

legifrance = LegifranceClient()
