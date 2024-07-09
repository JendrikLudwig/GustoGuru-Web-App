# %%
import os
import pandas as pd
import tempfile
from tqdm import tqdm  # Fortschrittsanzeige
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from scipy.sparse import csr_matrix

# %%
import joblib

input_file = 'data/tfidf_data.json' # path relative to app.py.
with open(input_file, 'r') as f:
    data = json.load(f)

tfidf_data = data['tfidf']
vocabulary = data['vocabulary']
df = pd.DataFrame(data['df'])

tfidf_matrix = csr_matrix((tfidf_data['data'], tfidf_data['indices'], tfidf_data['indptr']), shape=tfidf_data['shape'])


# %%

def findClosestMatch(input_string):
    # Gesamtvokabular erstellen
    vectorizer = TfidfVectorizer()
    vectorizer.fit(df['ing_LT'])
    vocabulary = vectorizer.vocabulary_

    # Schrittweise TF-IDF Vektorisierung und Ähnlichkeitsberechnung
    batch_size = 1000  # Batch-Größe anpassen
    num_batches = (len(df) + batch_size - 1) // batch_size

    # Erstellen eines temporären Verzeichnisses zum Speichern der Zwischenergebnisse
    temp_dir = tempfile.mkdtemp()

    # Initialisieren des TF-IDF-Vektors
    tfidf_matrix_files = []

    # Fortschrittsanzeige für die TF-IDF-Berechnung
    for i in tqdm(range(num_batches), desc="TF-IDF Vektorisierung"):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(df))
        batch_vectorizer = TfidfVectorizer(vocabulary=vocabulary)
        batch_tfidf = batch_vectorizer.fit_transform(df['ing_LT'].iloc[start_idx:end_idx])
        
        # Speichern des Batches auf der Festplatte
        batch_file = os.path.join(temp_dir, f'tfidf_batch_{i}.pkl')
        joblib.dump(batch_tfidf, batch_file)
        tfidf_matrix_files.append(batch_file)

    # Vektorisieren des Beispielstrings
    input_vectorizer = TfidfVectorizer(vocabulary=vocabulary)
    input_vector = input_vectorizer.fit_transform([input_string])

    # Berechnung der Ähnlichkeit stückweise mit Zwischenspeichern
    def compute_similarity_with_input(matrix_file, input_vector):
        matrix = joblib.load(matrix_file)
        sim = cosine_similarity(matrix, input_vector)
        return sim

    # Berechnung der Ähnlichkeit für den Beispielstring mit allen Rezepten
    similarities = []
    for matrix_file in tfidf_matrix_files:
        sim = compute_similarity_with_input(matrix_file, input_vector)
        similarities.append(sim)

    similarities = np.vstack(similarities)

    # Finden der Top-N ähnlichen Rezepte
    def get_top_similar_recipes_to_input(similarities, top_n=1):
        similarities = similarities.flatten()
        similar_recipes_indices = similarities.argsort()[-top_n:][::-1]
        return similar_recipes_indices

    # Top 5 ähnliche Rezepte für den Beispielstring finden
    top_n = 1
    similar_recipes_indices = get_top_similar_recipes_to_input(similarities, top_n)

    # Abrufen der ähnlichen Rezepte
    similar_recipes = df.iloc[similar_recipes_indices]
   

    # Aufräumen: Löschen des temporären Verzeichnisses
    import shutil
    shutil.rmtree(temp_dir)

    return similar_recipes.to_json()
