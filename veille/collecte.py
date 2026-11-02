"""Téléchargement poli : robots.txt respecté, délai entre requêtes, nouvelles tentatives avec attente croissante."""
import time, logging, pathlib
from urllib import robotparser
from urllib.parse import urljoin, urlparse
import requests

log = logging.getLogger("veille")


class Collecteur:
    def __init__(self, base, agent, delai=1.0, tentatives=3):
        self.base, self.agent, self.delai, self.tentatives = str(base), agent, delai, tentatives
        self.local = not self.base.startswith("http")
        self.http = requests.Session()
        self.http.headers["User-Agent"] = agent
        self.robots = robotparser.RobotFileParser()
        self._dernier = 0.0
        self.stats = {"pages": 0, "erreurs": 0, "octets": 0}
        try:
            self.robots.parse(self._brut("robots.txt").splitlines())
        except Exception:
            self.robots.parse([])
        cd = self.robots.crawl_delay(agent)
        if cd and not self.local:
            self.delai = max(self.delai, float(cd))

    def _brut(self, chemin):
        if self.local:
            return (pathlib.Path(self.base) / chemin).read_text(encoding="utf-8")
        r = self.http.get(urljoin(self.base, chemin), timeout=15)
        r.raise_for_status()
        return r.text

    def autorise(self, chemin):
        chemin_url = "/" + chemin.lstrip("/") if self.local else urlparse(urljoin(self.base, chemin)).path
        return self.robots.can_fetch(self.agent, chemin_url)

    def get(self, chemin):
        if not self.autorise(chemin):
            log.warning("Interdit par robots.txt : %s", chemin)
            return None
        for essai in range(1, self.tentatives + 1):
            attente = self.delai - (time.time() - self._dernier)
            if attente > 0:
                time.sleep(attente)
            self._dernier = time.time()
            try:
                txt = self._brut(chemin)
                self.stats["pages"] += 1
                self.stats["octets"] += len(txt.encode())
                return txt
            except Exception as e:
                self.stats["erreurs"] += 1
                log.warning("Échec %s (essai %d/%d) : %s", chemin, essai, self.tentatives, e)
                time.sleep(min(8, 2 ** essai * .5))
        return None
