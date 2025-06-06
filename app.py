import streamlit as st
import streamlit_authenticator as stauth
import json
import os

# --- LOGIN SETUP ---
names = ['Mattia']
usernames = ['mattia']
passwords = ['borgo2025']  # cambiala per sicurezza

hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    names, usernames, hashed_passwords,
    'borgo_cookie', 'borgo_secret', cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')

# --- SE L'UTENTE È AUTENTICATO ---
if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f"Ciao {name} 👋")

    st.title("Database Gare Borgo Treponti")

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

    anno = st.number_input("Anno", min_value=1900, max_value=2100, value=2023)
    nome = st.text_input("Nome Gara")
    categoria = st.selectbox("Categoria", ["Materna", "Elementari", "Medie", "Adolescenti", "Adulti"])
    sesso = st.selectbox("Sesso", ["M", "F", "Altro"])
    tempo = st.text_input("Tempo (hh:mm:ss o mm:ss o ss)")

    if st.button("Aggiungi Gara"):
        if str(anno) not in database:
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

elif authentication_status is False:
    st.error("Username o password errati.")
elif authentication_status is None:
    st.warning("Inserisci le credenziali per accedere.")
