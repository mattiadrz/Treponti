import streamlit as st
import sqlite3
import re

# --- DB Setup ---

DB_FILE = "tempi_gioco.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS tempi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anno INTEGER NOT NULL,
    gioco TEXT NOT NULL,
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL,
    sesso TEXT NOT NULL,
    tempo TEXT NOT NULL
)
''')
conn.commit()

# --- Funzioni Utils ---

def valida_tempo(t):
    # Accetta hh:mm:ss oppure mm:ss oppure ss
    pattern = r'^(\d{1,2}:)?(\d{1,2}:)?\d{1,2}$'
    return re.match(pattern, t.strip()) is not None

def tempo_to_secondi(t):
    parts = t.strip().split(":")
    parts = [int(p) for p in parts]
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h = 0
        m, s = parts
    else:
        h = 0
        m = 0
        s = parts[0]
    return h*3600 + m*60 + s

# --- DB CRUD ---

def carica_tempi_gioco_db(anno):
    c.execute("SELECT gioco, nome, categoria, sesso, tempo FROM tempi WHERE anno = ?", (anno,))
    rows = c.fetchall()
    tempi = {}
    for gioco, nome, categoria, sesso, tempo in rows:
        if gioco not in tempi:
            tempi[gioco] = []
        tempi[gioco].append({
            "nome": nome,
            "categoria": categoria,
            "sesso": sesso,
            "tempo": tempo
        })
    return tempi

def aggiungi_tempo_db(anno, gioco, nome, categoria, sesso, tempo):
    c.execute('''
        INSERT INTO tempi (anno, gioco, nome, categoria, sesso, tempo)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (anno, gioco, nome, categoria, sesso, tempo))
    conn.commit()

def cancella_tempo_db(anno, gioco, nome, categoria, sesso):
    c.execute('''
        DELETE FROM tempi WHERE anno = ? AND gioco = ? AND nome = ? AND categoria = ? AND sesso = ?
    ''', (anno, gioco, nome, categoria, sesso))
    conn.commit()

# --- Streamlit UI ---

st.title("Palio di Besnate - Gestione Tempi per Gioco")

tab1, tab2, tab3, tab4 = st.tabs(["Tab1", "Tab2", "Tab3", "Tempi per Gioco"])

with tab4:
    st.header("Inserimento Tempo per Gioco")

    anno_gioco = st.number_input("Anno", min_value=1900, max_value=2100, step=1, key="anno_gioco")
    nome_giocatore = st.text_input("Nome Giocatore")
    gioco = st.text_input("Nome Gioco")
    categoria_gioco = st.selectbox("Categoria", ["Materna", "Elementari", "Medie", "Adolescenti", "Adulti"], key="cat_gioco")
    sesso_gioco = st.selectbox("Sesso", ["M", "F", "Altro"], key="sex_gioco")
    tempo_gioco = st.text_input("Tempo (hh:mm:ss o mm:ss o ss)", key="tempo_gioco")

    if st.button("Salva Tempo Gioco"):
        if not (nome_giocatore and gioco and categoria_gioco and sesso_gioco and tempo_gioco):
            st.error("Compila tutti i campi.")
        elif not valida_tempo(tempo_gioco):
            st.error("Formato tempo non valido.")
        else:
            aggiungi_tempo_db(anno_gioco, gioco, nome_giocatore, categoria_gioco, sesso_gioco, tempo_gioco)
            st.success("Tempo salvato!")

    st.header("Tempi Migliori per Gioco")

    anno_vis = st.number_input("Seleziona Anno per Visualizzare", min_value=1900, max_value=2100, step=1, key="anno_vis_tempi")

    tempi_gioco = carica_tempi_gioco_db(anno_vis)
    if not tempi_gioco:
        st.write("Nessun dato disponibile per l'anno selezionato.")
    else:
        for gioco_nome, entries in tempi_gioco.items():
            st.markdown(f"### {gioco_nome}")
            gruppi = {}
            for entry in entries:
                key = (entry["categoria"], entry["sesso"])
                sec = tempo_to_secondi(entry["tempo"])
                if key not in gruppi or sec < gruppi[key][1]:
                    gruppi[key] = (entry, sec)

            for (categoria, sesso), (entry, _) in gruppi.items():
                st.write(f"- **{categoria} | {sesso}** → {entry['tempo']} ({entry['nome']})")

    st.header("Cancella Tempo per Gioco")

    anno_canc = st.number_input("Anno", min_value=1900, max_value=2100, step=1, key="anno_canc")
    gioco_canc = st.text_input("Nome Gioco", key="gioco_canc")
    categoria_canc = st.selectbox("Categoria", ["Materna", "Elementari", "Medie", "Adolescenti", "Adulti"], key="cat_canc_gioco")
    sesso_canc = st.selectbox("Sesso", ["M", "F", "Altro"], key="sex_canc_gioco")
    nome_canc = st.text_input("Nome Giocatore", key="nome_canc_gioco")

    if st.button("Cancella Tempo Gioco"):
        if not (gioco_canc and categoria_canc and sesso_canc and nome_canc):
            st.error("Compila tutti i campi per cancellare.")
        else:
            cancella_tempo_db(anno_canc, gioco_canc, nome_canc, categoria_canc, sesso_canc)
            st.success("Tempo cancellato.")

# --- Close DB connection on script end ---

import atexit
atexit.register(lambda: conn.close())
