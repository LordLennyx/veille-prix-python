"""Ligne de commande.

    python -m veille --base demo/site --jour 2026-11-02
    python -m veille --base https://boutique.exemple.cm/ --sources sources.json
"""
import argparse, json, logging, pathlib, time, datetime
from .collecte import Collecteur
from .extraction import extraire
from .stockage import Base
from .analyse import differences, comparatif
from . import export

log = logging.getLogger("veille")


def collecter(cfg, base):
    p = cfg["parametres"]
    tous, stats = [], []
    for s in cfg["sources"]:
        t0 = time.time()
        col = Collecteur(base, p["agent"], p["delai_secondes"], p["tentatives"])
        page, items, n = s["depart"], [], 0
        while page and n < 50:
            html = col.get(page)
            if html is None:
                break
            lot, suivant = extraire(html, s)
            items += lot
            n += 1
            log.info("%-15s page %d  %2d produits", s["nom"], n, len(lot))
            page = str(pathlib.PurePosixPath(page).parent / suivant) if suivant else None
        tous += items
        stats.append({"source": s["nom"], "pages": n, "produits": len(items), "secondes": round(time.time() - t0, 2), "erreurs": col.stats["erreurs"]})
    return tous, stats


def main():
    ap = argparse.ArgumentParser(prog="veille", description="Veille de prix concurrentielle")
    ap.add_argument("--sources", default="sources.json")
    ap.add_argument("--base", required=True, help="URL du site ou dossier local")
    ap.add_argument("--jour", default=datetime.date.today().isoformat())
    ap.add_argument("--sortie", default="sortie")
    ap.add_argument("--db", default="veille.sqlite")
    ap.add_argument("-q", action="store_true", help="silencieux")
    a = ap.parse_args()
    logging.basicConfig(level=logging.WARNING if a.q else logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
    cfg = json.loads(pathlib.Path(a.sources).read_text(encoding="utf-8"))
    out = pathlib.Path(a.sortie)
    out.mkdir(exist_ok=True)
    items, stats = collecter(cfg, a.base)
    db = Base(a.db)
    jours = [j for j in db.jours() if j < a.jour]
    db.enregistrer(a.jour, items)
    alertes = differences(db.releves(jours[-1]), items) if jours else []
    comp = comparatif(items)
    export.csv_fr(out / f"releve-{a.jour}.csv", items, ["source", "ref", "nom", "prix", "stock"])
    export.xlsx(out / f"veille-{a.jour}.xlsx", comp, alertes, cfg["sources"])
    export.json_tableau(out / "tableau.json", jour=a.jour, sources=cfg["sources"], stats=stats, comparatif=comp, alertes=alertes, historique=db.historique())
    log.info("%d produits, %d alertes, %d produits comparés -> %s", len(items), len(alertes), len(comp), out)
    for al in alertes[:5]:
        log.info("  %-8s %-15s %s %s", al["type"].upper(), al["source"], al["nom"], f"{al['ecart']:+} %" if al.get("ecart") else "")


if __name__ == "__main__":
    main()
