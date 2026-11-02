"""Historique des relevés dans SQLite (un fichier, aucune installation)."""
import sqlite3

SCHEMA = """
create table if not exists releve (
  jour text, source text, ref text, nom text, cle text, prix integer, stock integer,
  primary key (jour, source, ref)
);
create index if not exists idx_cle on releve(cle);
"""
COLS = ("source", "ref", "nom", "cle", "prix", "stock")


class Base:
    def __init__(self, chemin):
        self.db = sqlite3.connect(chemin)
        self.db.executescript(SCHEMA)

    def enregistrer(self, jour, items):
        self.db.executemany("insert or replace into releve values (?,?,?,?,?,?,?)",
                            [(jour, i["source"], i["ref"], i["nom"], i["cle"], i["prix"], int(i["stock"])) for i in items])
        self.db.commit()

    def jours(self):
        return [r[0] for r in self.db.execute("select distinct jour from releve order by jour")]

    def releves(self, jour):
        cur = self.db.execute("select source, ref, nom, cle, prix, stock from releve where jour=?", (jour,))
        return [dict(zip(COLS, r)) for r in cur]

    def historique(self):
        cur = self.db.execute("select jour, source, cle, prix, stock from releve order by jour")
        return [dict(zip(("jour", "source", "cle", "prix", "stock"), r)) for r in cur]
