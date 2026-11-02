from veille.extraction import prix, cle, extraire, stock
from veille.analyse import differences, comparatif


def test_prix():
    assert prix("1 049,00 €") == 1049
    assert prix("149 EUR") == 149
    assert prix("98 000 FCFA") == 98000
    assert prix("98.000 F") == 98000
    assert prix(None) is None and prix("sur devis") is None


def test_cle_rapproche_les_variantes():
    assert cle("Réfrigérateur Hisense 205 L") == cle("refrigerateur  HISENSE 205L")


def test_extraire_attribut_negation_pagination():
    html = ('<div class="card"><span class="name">Fer à repasser</span><div class="price"><b>12 500</b></div>'
            '<input name="sku" value="B-1"></div><a class="btn-next" href="page-2.html">›</a>')
    src = {"id": "b", "item": ".card", "suivant": "a.btn-next",
           "champs": {"ref": "input[name=sku]@value", "nom": ".name", "prix": ".price b", "stock": "!.oos"}}
    items, suivant = extraire(html, src)
    assert items[0]["ref"] == "B-1" and items[0]["prix"] == 12500 and items[0]["stock"] is True
    assert suivant == "page-2.html"


def test_differences_et_comparatif():
    a = [{"source": "x", "ref": "1", "nom": "A", "cle": "a", "prix": 1000, "stock": 1}]
    b = [{"source": "x", "ref": "1", "nom": "A", "cle": "a", "prix": 900, "stock": 0},
         {"source": "y", "ref": "9", "nom": "A", "cle": "a", "prix": 950, "stock": 1}]
    assert [d["type"] for d in differences(a, b)] == ["baisse", "rupture", "nouveau"]
    assert comparatif(b)[0]["meilleur"] == "y"


def test_stock():
    assert stock("oui") and stock(True) and stock("En stock")
    assert not stock("non") and not stock(None) and not stock("")
