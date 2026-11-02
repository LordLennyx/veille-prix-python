"""Exports : CSV (Excel FR), classeur XLSX mis en forme, JSON pour le tableau de bord."""
import csv, json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

F_CFA = '# ##0 "F"'


def csv_fr(chemin, lignes, colonnes):
    with open(chemin, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, colonnes, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(lignes)


def xlsx(chemin, comparatif, alertes, sources):
    wb = Workbook()
    ws = wb.active
    ws.title = "Comparatif"
    ids = [s["id"] for s in sources]
    ws.append(["Produit", *[s["nom"] for s in sources], "Meilleur prix", "Écart"])
    for l in comparatif:
        ws.append([l["nom"], *[l["prix"].get(i) for i in ids], l["min"], l["ecart"] / 100])
    entete(ws)
    vert = PatternFill("solid", fgColor="DCFCE7")
    for r, l in enumerate(comparatif, start=2):
        for c, i in enumerate(ids, start=2):
            ws.cell(r, c).number_format = F_CFA
            if l["prix"].get(i) == l["min"]:
                ws.cell(r, c).fill = vert
                ws.cell(r, c).font = Font(bold=True)
        ws.cell(r, len(ids) + 2).number_format = F_CFA
        ws.cell(r, len(ids) + 3).number_format = "0.0%"
    wa = wb.create_sheet("Alertes")
    wa.append(["Type", "Boutique", "Produit", "Ancien prix", "Nouveau prix", "Écart"])
    for a in alertes:
        wa.append([a["type"], a["source"], a["nom"], a.get("ancien"), a.get("prix"), (a["ecart"] / 100) if a.get("ecart") else None])
    entete(wa)
    for row in wa.iter_rows(min_row=2):
        row[3].number_format = row[4].number_format = F_CFA
        row[5].number_format = "+0.0%;-0.0%"
    wb.save(chemin)


def entete(ws):
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F2937")
        c.alignment = Alignment(vertical="center")
    ws.freeze_panes = "B2"
    ws.row_dimensions[1].height = 22
    for i, col in enumerate(ws.columns, start=1):
        ws.column_dimensions[get_column_letter(i)].width = max(12, min(42, max(len(str(c.value or "")) for c in col) + 3))
    ws.auto_filter.ref = ws.dimensions


def json_tableau(chemin, **donnees):
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=1)
