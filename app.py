import streamlit as st
import json
import os

DATABASE_FILE = "gare_database.json"

def carica_database():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salva_database(db):
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

database = carica_database()

st.title("Database Gare Borgo Treponti")

anno = st.number_input("Anno", min_value=1900, max_value=2100, value=2023)
nome = st.text_input("Nome Gara")
categoria = st.selectbox("Categoria", ["Materna", "Elementari", "Medie", "Adolescenti", "Adulti"])
sesso = st.selectbox("Sesso", ["M", "F", "Altro"])
tempo = st.text_input("Tempo (hh:mm:ss o mm:ss o ss)")

if st.button("Aggiungi Gara"):
    if anno not in database:
        database[str(anno)] = []
    database[str(anno)].append({"nome": nome, "categoria": categoria, "sesso": sesso, "tempo": tempo})
    salva_database(database)
    st.success("Gara aggiunta!")

if st.button("Mostra Gare"):
    if str(anno) in database:
        st.write(f"Gare per l'anno {anno}:")
        for g in database[str(anno)]:
            st.write(f"- {g['nome']} | {g['categoria']} | {g['sesso']} | {g['tempo']}")
    else:
        st.write("Nessuna gara per questo anno.")
