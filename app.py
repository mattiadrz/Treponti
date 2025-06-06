import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_FILE = "gare_tempi.db"

# Connessione e setup DB
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

# Creazione tabelle se non esistono
c.execute('''
CREATE TABLE IF NOT EXISTS gare (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anno INTEGER,
    nome TEXT,
    categoria TEXT,
    sesso TEXT,
    tempo TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS tempi_giochi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anno INTEGER,
    gioco TEXT,
    nome TEXT,
    categoria TEXT,
    sesso TEXT,
    tempo TEXT
)
''')

conn.commit()

def valida_tempo(tempo_str):
    parti = tempo_str.split(":")
    if len(parti) not in (1, 2, 3):
        return False
    try:
        for p in parti:
            if int(p) < 0:
                return False
    except:
        return False
    return True

def tempo_to_secondi(t):
    parti = t.split(":")
    parti = [int(x) for x in parti]
    if len(parti) == 3:
        return parti[0]*3600 + parti[1]*60 + parti[2]
    elif len(parti) == 2:
        return parti[0]*60 + parti[1]
    elif len(parti) == 1:
        return parti[0]
    else:
        return 0

def secondi_to_tempo(sec):
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"

def aggiungi_gara(anno, nome, categoria, sesso, tempo):
    # Controllo se già esiste gara con stesso nome, categoria, sesso e anno
    c.execute('''
    SELECT id, tempo FROM gare WHERE anno=? AND LOWER(nome)=LOWER(?) AND categoria=? AND sesso=?
    ''', (anno, nome, categoria, sesso))
    row = c.fetchone()
    if row:
        id_gara, tempo_esistente = row
        if tempo_esistente == tempo:
            return "esiste_uguale"
        else:
            # Sovrascrivi tempo
            c.execute('UPDATE gare SET tempo=? WHERE id=?', (tempo, id_gara))
            conn.commit()
            return "sovrascritto"
    else:
        c.execute('INSERT INTO gare (anno, nome, categoria, sesso, tempo) VALUES (?, ?, ?, ?, ?)',
                  (anno, nome, categoria, sesso, tempo))
        conn.commit()
        return "aggiunto"

def filtra_e_ordina_gare(anno, filtro_nome):
    if filtro_nome:
        c.execute('''
        SELECT nome, categoria, sesso, tempo FROM gare WHERE anno=? AND LOWER(nome) LIKE ? ORDER BY tempo
        ''', (anno, f'%{filtro_nome.lower()}%'))
    else:
        c.execute('''
        SELECT nome, categoria, sesso, tempo FROM gare WHERE anno=? ORDER BY tempo
        ''', (anno,))
    risultati = c.fetchall()
    return [{"nome": r[0], "categoria": r[1], "sesso": r[2], "tempo": r[3]} for r in risultati]

def cancella_gara(anno, nome, categoria, sesso):
    c.execute('''
    DELETE FROM gare WHERE anno=? AND LOWER(nome)=LOWER(?) AND categoria=? AND sesso=?
    ''', (anno, nome, categoria, sesso))
    conn.commit()
    return c.rowcount  # numero di righe cancellate

def estrai_anni_presenti():
    c.execute('SELECT DISTINCT anno FROM gare ORDER BY anno')
    return [row[0] for row in c.fetchall()]

def estrai_tutti_gare():
    c.execute('SELECT anno, nome, categoria, sesso, tempo FROM gare')
    return c.fetchall()

def esporta_gare_anno(anno):
    c.execute('SELECT nome, categoria, sesso, tempo FROM gare WHERE anno=?', (anno,))
    return c.fetchall()

# Funzioni gestione tempi_giochi
def aggiungi_tempo_gioco(anno, gioco, nome, categoria, sesso, tempo):
    c.execute('''
    INSERT INTO tempi_giochi (anno, gioco, nome, categoria, sesso, tempo)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (anno, gioco, nome, categoria, sesso, tempo))
    conn.commit()

def get_tempi_gioco_anno(anno):
    c.execute('SELECT gioco, nome, categoria, sesso, tempo FROM tempi_giochi WHERE anno=?', (anno,))
    rows = c.fetchall()
    dati = {}
    for gioco, nome, categoria, sesso, tempo in rows:
        if gioco not in dati:
            dati[gioco] = []
        dati[gioco].append({"nome": nome, "categoria": categoria, "sesso": sesso, "tempo": tempo})
    return dati

def cancella_tempo_gioco(anno, gioco, categoria, sesso, nome):
    c.execute('''
    DELETE FROM tempi_giochi WHERE anno=? AND LOWER(gioco)=LOWER(?) AND categoria=? AND sesso=? AND LOWER(nome)=LOWER(?)
    ''', (anno, gioco, categoria, sesso, nome))
    conn.commit()
    return c.rowcount

### INTERFACCIA STREAMLIT ###

st.title("Database Gare - Borgo Treponti")

tab = st.tabs(["Inserisci Gara", "Visualizza Gare", "Statistiche", "Esporta", "Tempi per Gioco"])

with tab[0]:
    st.header("Inserisci Gara")
    anno = st.number_input("Anno", min_value=1900, max_value=2100, step=1, format="%d")
    nome = st.text_input("Nome Gara")
    categoria = st.selectbox("Categoria", ["Materna", "Elementari", "Medie", "Adolescenti", "Adulti"])
    sesso = st.selectbox("Sesso", ["M", "F", "Altro"])
    tempo = st.text_input("Tempo (hh:mm:ss o mm:ss o ss)")

    if st.button("Aggiungi Gara"):
        if not (nome and categoria and sesso and tempo):
            st.error("Compila tutti i campi.")
        elif not valida_tempo(tempo):
            st.error("Formato tempo non valido. Usa hh:mm:ss o mm:ss o ss.")
        else:
            risultato = aggiungi_gara(anno, nome, categoria, sesso, tempo)
            if risultato == "esiste_uguale":
                st.info("Gara già presente con lo stesso tempo!")
            elif risultato == "sovrascritto":
                st.success("Tempo sovrascritto.")
            else:
                st.success("Gara aggiunta!")

with tab[1]:
    st.header("Visualizza Gare")
    anno_stampa = st.number_input("Anno da visualizzare", min_value=1900, max_value=2100, step=1, key="anno_stampa")
    filtro_nome = st.text_input("Filtro nome (opzionale)", key="filtro_nome")

    if st.button("Mostra Gare"):
        gare_filtrate = filtra_e_ordina_gare(anno_stampa, filtro_nome)
        if not gare_filtrate:
            st.info("Nessuna gara trovata.")
        else:
            df = pd.DataFrame(gare_filtrate)
            df['tempo'] = df['tempo'].astype(str)
            st.dataframe(df)

    st.subheader("Cancella Gara")
    nome_cancella = st.text_input("Nome Gara da cancellare")
    categoria_cancella = st.selectbox("Categoria da cancellare", ["Materna", "Elementari", "Medie", "Adolescenti", "Adulti"], key="cat_cancella")
    sesso_cancella = st.selectbox("Sesso da cancellare", ["M", "F", "Altro"], key="sex_cancella")

    if st.button("Cancella Gara"):
        if not (nome_cancella and categoria_cancella and sesso_cancella):
            st.error("Compila tutti i campi per cancellare.")
        else:
            count = cancella_gara(anno_stampa, nome_cancella, categoria_cancella, sesso_cancella)
            if count > 0:
                st.success("Gara cancellata.")
            else:
                st.info("Gara non trovata.")

with tab[2]:
    st.header("Statistiche")
    anni = estrai_anni_presenti()
    if not anni:
        st.write("Nessun dato presente.")
    else:
        totale_gare = 0
        count_sesso = {"M": 0, "F": 0, "Altro": 0}
        tempi_secondi = []

        for anno in anni:
            c.execute('SELECT sesso, tempo FROM gare WHERE anno=?', (anno,))
            gare = c.fetchall()
            totale_gare += len(gare)
            for sesso, tempo in gare:
                if sesso in count_sesso:
                    count_sesso[sesso] += 1
                tempi_secondi.append(tempo_to_secondi(tempo))

        media_sec = int(sum(tempi_secondi) / len(tempi_secondi)) if tempi_secondi else 0
        media_tempo = secondi_to_tempo(media_sec)

        st.write(f"Anni presenti: {', '.join(map(str, anni))}")
        st.write(f"Totale gare registrate: {totale_gare}")
        st.write("Distribuzione sesso:")
        for sesso, cnt in count_sesso.items():
            st.write(f"- {sesso}: {cnt}")
        st.write(f"Tempo medio gare: {media_tempo}")

        fig, ax = plt.subplots()
        ax.bar(count_sesso.keys(), count_sesso.values(), color=['blue', 'pink', 'gray'])
        ax.set_title("Distribuzione gare per sesso")
        ax.set_ylabel("Numero gare")
        ax.set_xlabel("Sesso")
        st.pyplot(fig)

with tab[3]:
    st.header("Esporta")
    anno_export = st.number_input("Anno da esportare", min_value=1900, max_value=2100, step=1, key="anno_export")
    formato = st.radio("Formato file", ("CSV", "TXT"))

    if st.button("Esporta"):
        gare = esporta_gare_anno(anno_export)
        if not gare:
            st.info("Nessuna gara presente per l'anno selezionato.")
        else:
            if formato == "CSV":
                df = pd.DataFrame([{"nome": g[0], "categoria": g[1], "sesso": g[2], "tempo": g[3]} for g in gare])
                csv = df.to_csv(index=False)
                st.download_button(label="Scarica CSV", data=csv, file_name=f"gare_{anno_export}.csv", mime="text/csv")
            else:
                testo = f"Gare anno {anno_export}:\n\n"
                for g in gare:
                    testo += f"{g[0]} | {g[1]} | {g[2]} | Tempo: {g[3]}\n"
                st.download_button(label="Scarica TXT", data=testo, file_name=f"gare_{anno_export}.txt", mime="text/plain")
with tab[4]:
    st.header("Tempi per Gioco")

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
            aggiungi_tempo_gioco(anno_gioco, gioco, nome_giocatore, categoria_gioco, sesso_gioco, tempo_gioco)
            st.success("Tempo salvato!")

    st.markdown("---")
    st.subheader("Modifica o Elimina Tempo Gioco")

    # Selezione record esistente da modificare/cancellare
    anno_mod = st.number_input("Anno", min_value=1900, max_value=2100, step=1, key="anno_mod")
    gioco_mod = st.text_input("Nome Gioco", key="gioco_mod")
    nome_mod = st.text_input("Nome Giocatore", key="nome_mod")
    categoria_mod = st.selectbox("Categoria", ["Materna", "Elementari", "Medie", "Adolescenti", "Adulti"], key="cat_mod")
    sesso_mod = st.selectbox("Sesso", ["M", "F", "Altro"], key="sex_mod")

    if st.button("Carica Tempo Esistente"):
        c.execute('''
        SELECT tempo FROM tempi_giochi
        WHERE anno=? AND LOWER(gioco)=LOWER(?) AND LOWER(nome)=LOWER(?) AND categoria=? AND sesso=?
        ''', (anno_mod, gioco_mod, nome_mod, categoria_mod, sesso_mod))
        row = c.fetchone()
        if row:
            tempo_esistente = row[0]
            st.session_state["tempo_mod"] = tempo_esistente
            st.success(f"Tempo esistente caricato: {tempo_esistente}")
        else:
            st.error("Record non trovato.")

    tempo_mod = st.text_input("Nuovo Tempo", key="tempo_mod", value=st.session_state.get("tempo_mod", ""))

    if st.button("Modifica Tempo"):
        if not tempo_mod:
            st.error("Inserisci un nuovo tempo.")
        elif not valida_tempo(tempo_mod):
            st.error("Formato tempo non valido.")
        else:
            rows_updated = modifica_tempo_gioco(anno_mod, gioco_mod, nome_mod, categoria_mod, sesso_mod, tempo_mod)
            if rows_updated > 0:
                st.success("Tempo modificato con successo.")
                st.session_state["tempo_mod"] = tempo_mod
            else:
                st.error("Errore: record non trovato o nessuna modifica effettuata.")

    if st.button("Elimina Tempo"):
        rows_deleted = cancella_tempo_gioco(anno_mod, gioco_mod, categoria_mod, sesso_mod, nome_mod)
        if rows_deleted > 0:
            st.success("Record eliminato con successo.")
            st.session_state["tempo_mod"] = ""
        else:
            st.error("Errore: record non trovato.")