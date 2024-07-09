from rapidfuzz import fuzz, process
import pandas as pd

# Datenvorbereitung
df = pd.read_pickle("data/export.pkl")
df["ingredients"] = df["ingredients"].apply(lambda arr: [obj["name"] for obj in arr])
df = df.reset_index()["ingredients"]
df = df.explode('ingredients').reset_index(drop=True)
zutaten = list(set(df.tolist()))

# Funktion zur Suche und Rückgabe der besten K Zutaten
def finde_passende_zutaten(suchanfrage, k=5):
    ergebnisse = process.extract(suchanfrage, zutaten, limit=k, scorer=fuzz.ratio)
    vorgeschlagene_zutaten = [result[0] for result in ergebnisse]
    return vorgeschlagene_zutaten