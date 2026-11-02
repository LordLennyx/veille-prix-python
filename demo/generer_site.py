"""Génère trois boutiques fictives (structures HTML différentes) pour tester le robot sans solliciter de vrai site.

    python demo/generer_site.py --jour 3     # état du catalogue au jour 3
"""
import argparse, random, pathlib, html

RACINE = pathlib.Path(__file__).parent / "site"
PRODUITS = [
    ("Tecno Spark 20 Pro 256 Go", 149), ("Infinix Hot 40i 128 Go", 109), ("Samsung Galaxy A15 128 Go", 179),
    ("itel A70 64 Go", 79), ("Xiaomi Redmi 13C 128 Go", 119), ("Tecno Camon 30 256 Go", 249),
    ("Samsung Galaxy A25 5G", 269), ("Infinix Note 40 256 Go", 219), ("Oraimo FreePods 4", 29),
    ("Power bank Oraimo 20 000 mAh", 25), ("Climatiseur Nasco 1,5 CV", 429), ("Réfrigérateur Hisense 205 L", 349),
    ("Téléviseur TCL 43 pouces 4K", 299), ("Congélateur Innova 200 L", 329), ("Ventilateur Binatone 18 pouces", 39),
    ("Groupe électrogène Tiger 3 kVA", 599), ("Ordinateur HP 250 G9 i5", 649), ("Imprimante Canon Pixma G2410", 169),
    ("Routeur 4G Huawei B311", 69), ("Fer à repasser Philips", 24),
]
BOUTIQUES = {"kiosque": "Kiosque Akwa", "marche-digital": "Marché Digital", "bon-plan": "BonPlan237"}


def euros(n):
    return f"{n:,}".replace(",", " ")


def etat(boutique, jour):
    """Prix et stock déterministes pour une boutique et un jour donnés."""
    rng = random.Random(f"{boutique}-{jour}")
    base = random.Random(boutique)
    out = []
    for i, (nom, prix) in enumerate(PRODUITS):
        if base.random() < .18:      # chaque boutique ne vend pas tout
            continue
        marge = 1 + base.uniform(-.06, .1)
        evt = random.Random(f"{boutique}-{i}")           # un seul changement de prix durable par produit
        jour_promo, ampleur = evt.randint(2, 11), evt.choice([-.12, -.08, -.05, .04, .06])
        derive = 1 + ampleur if jour >= jour_promo else 1
        p = max(5, int(round(prix * marge * derive / 5) * 5) - 1)   # prix psychologiques : 149, 154…
        stock = random.Random(f"{boutique}-{i}-{jour}").random() > .06
        out.append({"ref": f"{boutique[:3].upper()}-{1000 + i}", "nom": nom, "prix": p, "stock": stock})
    return out


def page_kiosque(items, n, total):
    cartes = "".join(f"""
    <article class="produit" data-ref="{p['ref']}">
      <h2 class="produit__titre"><a href="/kiosque/p/{p['ref']}.html">{html.escape(p['nom'])}</a></h2>
      <p class="produit__prix">{euros(p['prix'])},00 €</p>
      <span class="badge {'dispo' if p['stock'] else 'rupture'}">{'En stock' if p['stock'] else 'Rupture'}</span>
    </article>""" for p in items)
    suiv = f'<a rel="next" href="page-{n + 1}.html">Suivant</a>' if n < total else ""
    return f"<!doctype html><html lang=fr><meta charset=utf-8><title>Kiosque Akwa, page {n}</title><main class=grille>{cartes}</main><nav class=pagination>{suiv}</nav></html>"


def page_marche(items, n, total):
    lignes = "".join(f"""<tr class="item"><td class="sku">{p['ref']}</td><td class="designation">{html.escape(p['nom'])}</td>
      <td class="tarif" data-montant="{p['prix']}">{euros(p['prix'])} €</td><td class="dispo">{'oui' if p['stock'] else 'non'}</td></tr>""" for p in items)
    suiv = f'<li class="next"><a href="page-{n + 1}.html">›</a></li>' if n < total else ""
    return f"<!doctype html><html lang=fr><meta charset=utf-8><title>Marché Digital</title><table id=catalogue><tbody>{lignes}</tbody></table><ul class=pages>{suiv}</ul></html>"


def page_bonplan(items, n, total):
    blocs = "".join(f"""<div class="card"><div class="card-body"><span class="name">{html.escape(p['nom'])}</span>
      <div class="price"><b>{euros(p['prix'])}</b> <small>EUR</small></div>{'' if p['stock'] else '<em class="oos">Épuisé</em>'}<input type="hidden" name="sku" value="{p['ref']}"></div></div>""" for p in items)
    suiv = f'<a class="btn-next" href="page-{n + 1}.html">Page suivante</a>' if n < total else ""
    return f"<!doctype html><html lang=fr><meta charset=utf-8><title>BonPlan237</title><section class=listing>{blocs}</section>{suiv}</html>"


GABARITS = {"kiosque": page_kiosque, "marche-digital": page_marche, "bon-plan": page_bonplan}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--jour", type=int, default=1); a = ap.parse_args()
    for b, f in GABARITS.items():
        d = RACINE / b; d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("page-*.html"): old.unlink()
        items = etat(b, a.jour); par = 6; total = (len(items) + par - 1) // par
        for n in range(1, total + 1):
            (d / f"page-{n}.html").write_text(f(items[(n - 1) * par:n * par], n, total), encoding="utf-8")
    (RACINE / "robots.txt").write_text("User-agent: *\nDisallow: /admin/\nCrawl-delay: 1\n", encoding="utf-8")
    print(f"Site de démonstration généré (jour {a.jour}) dans {RACINE}")
