"""Comparaison entre deux relevés et rapprochement des produits entre boutiques."""

ORDRE = {"baisse": 0, "rupture": 1, "retour": 2, "hausse": 3, "nouveau": 4, "retire": 5}


def differences(avant, apres, seuil=0.03):
    av = {(i["source"], i["ref"]): i for i in avant}
    alertes = []
    for n in apres:
        a = av.get((n["source"], n["ref"]))
        if a is None:
            alertes.append({"type": "nouveau", **n})
            continue
        if a["prix"] and n["prix"] and abs(n["prix"] - a["prix"]) / a["prix"] >= seuil:
            alertes.append({"type": "baisse" if n["prix"] < a["prix"] else "hausse", "ancien": a["prix"],
                            "ecart": round((n["prix"] - a["prix"]) / a["prix"] * 100, 1), **n})
        if bool(a["stock"]) != bool(n["stock"]):
            alertes.append({"type": "retour" if n["stock"] else "rupture", **n})
    vus = {(i["source"], i["ref"]) for i in apres}
    alertes += [{"type": "retire", **a} for k, a in av.items() if k not in vus]
    return sorted(alertes, key=lambda x: (ORDRE[x["type"]], x.get("ecart", 0)))


def comparatif(releves):
    """Une ligne par produit : prix par boutique (en stock), meilleur prix, écart entre boutiques."""
    par = {}
    for r in releves:
        p = par.setdefault(r["cle"], {"nom": r["nom"], "prix": {}})
        if r["prix"] and r["stock"]:
            p["prix"][r["source"]] = r["prix"]
    lignes = []
    for c, p in par.items():
        if not p["prix"]:
            continue
        mini, maxi = min(p["prix"].values()), max(p["prix"].values())
        lignes.append({"cle": c, "nom": p["nom"], "prix": p["prix"], "meilleur": min(p["prix"], key=p["prix"].get),
                       "min": mini, "ecart": round((maxi - mini) / mini * 100, 1)})
    return sorted(lignes, key=lambda l: -l["ecart"])
