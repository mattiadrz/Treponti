import streamlit as st
import json
import os
import pandas as pd
import matplotlib.pyplot as plt

DATABASE_FILE = "gare_database.json"
TEMPI_FILE = "tempi_gioco.json"

tempi_gioco = {}
database = {}


def carica_tempi_gioco():
    global tempi_gioco
    if os.path.exists(TEMPI_FILE):
        with open(TEMPI_FILE, "r", encoding="utf-8") as f:
            dati = json.load(f)
            tempi_gioco.update({int(anno): giochi for anno, giochi in dati.items()})

def salva_tempi_gioco():
    with open(TEMPI_FILE, "w", encoding="utf-8") as f:
        json.dump(tempi_gioco, f, indent=2, ensure_ascii=False)

carica_tempi_gioco()

def carica_database():
    global database
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            database.update({int(k): v for k, v in data.items()})

def salva_database():
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)

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

def filtra_e_ordina_gare(anno, filtro_nome):
    if anno not in database:
        return []
    gare = database[anno]
    if filtro_nome:
        gare = [g for g in gare if filtro_nome.lower() in g["nome"].lower()]
    gare = sorted(gare, key=lambda g: tempo_to_secondi(g["tempo"]))
    return gare

carica_database()

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
            if anno not in database:
                database[anno] = []

            esiste = False
            for gara in database[anno]:
                if gara["nome"].lower() == nome.lower() and gara["categoria"] == categoria and gara["sesso"] == sesso:
                    esiste = True
                    if gara["tempo"] == tempo:
                        st.info("Gara già presente con lo stesso tempo!")
                    else:
                        if st.confirm("La gara esiste con tempo diverso. Sovrascrivere?"):
                            gara["tempo"] = tempo
                            salva_database()
                            st.success("Tempo sovrascritto.")
                    break
            if not esiste:
                nuova_gara = {"nome": nome, "categoria": categoria, "sesso": sesso, "tempo": tempo}
                database[anno].append(nuova_gara)
                salva_database()
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
            if anno_stampa not in database:
                st.info("Anno non presente nel database.")
            else:
                gare = database[anno_stampa]
                gara_trovata = False
                for i, gara in enumerate(gare):
                    if gara["nome"].lower() == nome_cancella.lower() and gara["categoria"] == categoria_cancella and gara["sesso"] == sesso_cancella:
                        del gare[i]
                        gara_trovata = True
                        break
                if gara_trovata:
                    if not database[anno_stampa]:
                        del database[anno_stampa]
                    salva_database()
                    st.success("Gara cancellata.")
                else:
                    st.info("Gara non trovata.")

with tab[2]:
    st.header("Statistiche")
    anni = sorted(database.keys())
    if not anni:
        st.write("Nessun dato presente.")
    else:
        totale_gare = 0
        count_sesso = {"M": 0, "F": 0, "Altro": 0}
        tempi_secondi = []

        for anno in anni:
            gare = database[anno]
            totale_gare += len(gare)
            for gara in gare:
                sesso = gara["sesso"]
                if sesso in count_sesso:
                    count_sesso[sesso] += 1
                tempi_secondi.append(tempo_to_secondi(gara["tempo"]))

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
        if anno_export not in database or not database[anno_export]:
            st.info("Nessuna gara presente per l'anno selezionato.")
        else:
            gare = database[anno_export]
            if formato == "CSV":
                df = pd.DataFrame(gare)
                csv = df.to_csv(index=False)
                st.download_button(label="Scarica CSV", data=csv, file_name=f"gare_{anno_export}.csv", mime="text/csv")
            else:
                testo = f"Gare anno {anno_export}:\n\n"
                for gara in gare:
                    testo += f"{gara['nome']} | {gara['categoria']} | {gara['sesso']} | Tempo: {gara['tempo']}\n"
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
            if anno_gioco not in tempi_gioco:
                tempi_gioco[anno_gioco] = {}
            if gioco not in tempi_gioco[anno_gioco]:
                tempi_gioco[anno_gioco][gioco] = []

            nuova_entrata = {
                "nome": nome_giocatore,
                "categoria": categoria_gioco,
                "sesso": sesso_gioco,
                "tempo": tempo_gioco
            }
            tempi_gioco[anno_gioco][gioco].append(nuova_entrata)
            salva_tempi_gioco()
            st.success("Tempo salvato!")

    st.subheader("Tempi Migliori per Gioco")
    anno_vis = st.number_input("Seleziona Anno per Visualizzare", min_value=1900, max_value=2100, step=1, key="anno_vis_tempi")

    if anno_vis not in tempi_gioco or not tempi_gioco[anno_vis]:
        st.write("Nessun dato disponibile per l'anno selezionato.")
    else:
        for gioco, entries in tempi_gioco[anno_vis].items():
            st.markdown(f"### {gioco}")
            gruppi = {}
            for entry in entries:
                key = (entry["categoria"], entry["sesso"])
                sec = tempo_to_secondi(entry["tempo"])
                if key not in gruppi or sec < gruppi[key][1]:
                    gruppi[key] = (entry, sec)

            for (categoria, sesso), (entry, _) in gruppi.items():
                st.write(f"- **{categoria} | {sesso}** → {entry['tempo']} ({entry['nome']})")

        st.subheader("Cancella Tempo per Gioco")

    anno_canc = st.number_input("Anno", min_value=1900, max_value=2100, step=1, key="anno_canc")
    gioco_canc = st.text_input("Nome Gioco", key="gioco_canc")
    categoria_canc = st.selectbox("Categoria", ["Materna", "Elementari", "Medie", "Adolescenti", "Adulti"], key="cat_canc_gioco")
    sesso_canc = st.selectbox("Sesso", ["M", "F", "Altro"], key="sex_canc_gioco")
    nome_canc = st.text_input("Nome Giocatore", key="nome_canc_gioco")

    if st.button("Cancella Tempo Gioco"):
        if not (gioco_canc and categoria_canc and sesso_canc and nome_canc):
            st.error("Compila tutti i campi per cancellare.")
        elif anno_canc not in tempi_gioco or gioco_canc not in tempi_gioco[anno_canc]:
            st.info("Anno o gioco non trovato.")
        else:
            entries = tempi_gioco[anno_canc][gioco_canc]
            nuova_lista = [e for e in entries if not (
                e["nome"].lower() == nome_canc.lower() and 
                e["categoria"] == categoria_canc and 
                e["sesso"] == sesso_canc)]

            if len(nuova_lista) < len(entries):
                tempi_gioco[anno_canc][gioco_canc] = nuova_lista
                # Rimuove il gioco se vuoto
                if not tempi_gioco[anno_canc][gioco_canc]:
                    del tempi_gioco[anno_canc][gioco_canc]
                # Rimuove l'anno se vuoto
                if not tempi_gioco[anno_canc]:
                    del tempi_gioco[anno_canc]
                salva_tempi_gioco()
                st.success("Tempo cancellato.")
            else:
                st.info("Tempo non trovato.")