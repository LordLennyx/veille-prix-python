"""Extraction déclarative : chaque champ est un sélecteur CSS, suffixé de @attribut si besoin.
Préfixe « ! » : vrai si l'élément est absent (ex. mention « Épuisé »)."""
import re, unicodedata
from bs4 import BeautifulSoup


def lire(el, regle):
    neg = regle.startswith("!")
    regle = regle.lstrip("!")
    sel, _, attr = regle.partition("@")
    cible = el.select_one(sel) if sel else el
    if neg:
        return cible is None
    if cible is None:
        return None
    return cible.get(attr) if attr else cible.get_text(" ", strip=True)


def prix(txt):
    """'98 000 FCFA', '98.000 F', '98000' -> 98000 ; None si illisible."""
    if txt is None:
        return None
    chiffres = re.sub(r"[^\d]", "", str(txt).split(",")[0])
    return int(chiffres) if chiffres else None


def stock(v):
    """Booléen, ou texte libre : 'oui', 'En stock' -> vrai ; 'non', 'Rupture', vide -> faux."""
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    t = str(v).strip().lower()
    return bool(t) and t not in {"non", "rupture", "épuisé", "0", "false"}


def cle(nom):
    """Clé de rapprochement entre boutiques : minuscules, sans accents ni ponctuation, unités collées."""
    n = unicodedata.normalize("NFD", nom.lower())
    n = "".join(c for c in n if unicodedata.category(c) != "Mn")
    n = re.sub(r"(\d)\s+(go|l|cv|kva|mah)\b", r"\1\2", n)
    return re.sub(r"[^a-z0-9]+", " ", n).strip()


def extraire(html, source):
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for el in soup.select(source["item"]):
        brut = {k: lire(el, r) for k, r in source["champs"].items()}
        if not brut.get("nom"):
            continue
        items.append({"source": source["id"], "ref": brut.get("ref"), "nom": brut["nom"], "cle": cle(brut["nom"]),
                      "prix": prix(brut.get("prix")), "stock": stock(brut.get("stock"))})
    lien = soup.select_one(source["suivant"]) if source.get("suivant") else None
    return items, (lien.get("href") if lien else None)
