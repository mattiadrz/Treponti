import streamlit as st
import sqlite3
import pandas as pd

# --- Inizializza i database creando le tabelle se non esistono ---

def init_db1():
    conn = sqlite3.connect("database1.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time REAL,
            game_name TEXT,
            category TEXT,
            gender TEXT,
            year INTEGER
        )
        """
    )
    conn.commit()
    conn.close()

def init_db2():
    conn = sqlite3.connect("database2.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS results_kids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            time REAL,
            game_name TEXT,
            category TEXT,
            gender TEXT,
            year INTEGER
        )
        """
    )
    conn.commit()
    conn.close()

# Inizializza i due database all'avvio
init_db1()
init_db2()

# --- Funzioni di utilità per il database 1 ---

def insert_record_db1(time_value, game_name, category, gender, year):
    conn = sqlite3.connect("database1.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO results (time, game_name, category, gender, year) VALUES (?, ?, ?, ?, ?)",
        (time_value, game_name, category, gender, year)
    )
    conn.commit()
    conn.close()

def get_records_db1():
    conn = sqlite3.connect("database1.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM results")
    records = cursor.fetchall()
    conn.close()
    return records

def update_record_db1(record_id, new_time, new_game_name, new_category, new_gender, new_year):
    conn = sqlite3.connect("database1.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE results SET time=?, game_name=?, category=?, gender=?, year=? WHERE id=?",
        (new_time, new_game_name, new_category, new_gender, new_year, record_id)
    )
    conn.commit()
    conn.close()

def delete_record_db1(record_id):
    conn = sqlite3.connect("database1.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM results WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

# --- Funzioni di utilità per il database 2 (ragazzi) ---

import sqlite3

def insert_record_db2(nome, time_value, game_name, category, year, gender):
    conn = sqlite3.connect("database2.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO results_kids (nome, time, game_name, category, year, gender) VALUES (?, ?, ?, ?, ?, ?)",
        (nome, time_value, game_name, category, year, gender)
    )
    conn.commit()
    conn.close()

def get_records_db2():
    conn = sqlite3.connect("database2.db")
    cursor = conn.cursor()
    # Selezioniamo esplicitamente tutti i campi, inclusa la colonna gender
    cursor.execute("SELECT id, nome, time, game_name, category, gender, year FROM results_kids")
    records = cursor.fetchall()
    conn.close()
    return records

def update_record_db2(record_id, nome, new_time, new_game_name, new_category, new_year, new_gender):
    conn = sqlite3.connect("database2.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE results_kids SET nome=?, time=?, game_name=?, category=?, year=?, gender=? WHERE id=?",
        (nome, new_time, new_game_name, new_category, new_year, new_gender, record_id)
    )
    conn.commit()
    conn.close()

def delete_record_db2(record_id):
    conn = sqlite3.connect("database2.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM results_kids WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

def get_min_times(year_filter=None):
    conn = sqlite3.connect("database2.db")
    cursor = conn.cursor()
    # Utilizziamo una query con subquery e JOIN per estrarre la riga (con il nome e il gender)
    # che possiede il tempo minimo per ogni gruppo (game_name, category, gender).
    if year_filter and year_filter != "Tutti":
        cursor.execute(
            """
            SELECT r.game_name, r.category, r.nome, r.gender, r.time AS min_time
            FROM results_kids r
            INNER JOIN (
                SELECT game_name, category, gender, MIN(time) AS min_time
                FROM results_kids
                WHERE year=?
                GROUP BY game_name, category, gender
            ) m ON r.game_name = m.game_name 
               AND r.category = m.category 
               AND r.gender = m.gender 
               AND r.time = m.min_time
            """, (year_filter,)
        )
    else:
        cursor.execute(
            """
            SELECT r.game_name, r.category, r.nome, r.gender, r.time AS min_time
            FROM results_kids r
            INNER JOIN (
                SELECT game_name, category, gender, MIN(time) AS min_time
                FROM results_kids
                GROUP BY game_name, category, gender
            ) m ON r.game_name = m.game_name 
               AND r.category = m.category 
               AND r.gender = m.gender 
               AND r.time = m.min_time
            """
        )
    results = cursor.fetchall()
    conn.close()
    return results

# --- Definizione dell'app Streamlit con le 4 Tab ---

def main():
    st.title("Gestione Tempi")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Inserisci Tempi",
        "Modifica/Cancella Tempi",
        "Visualizza Tempi",
        "Gestione Ragazzi e Visualizza Minimi"
    ])

    # ----- TAB 1: Inserimento Record in database1.db -----
    with tab1:
        st.header("Inserisci Nuovo Tempo")
        col1, col2 = st.columns(2)
        with col1:
            # Inserimento separato per minuti e secondi
            minutes_value = st.number_input("Minuti", value=0, step=1, key="db1_minutes_input")
            seconds_value = st.number_input("Secondi", value=0.0, format="%.2f", key="db1_seconds_input")
            # Calcola il tempo totale in secondi
            total_time = minutes_value * 60 + seconds_value
            game_name = st.text_input("Nome del Gioco", key="db1_game_input")
            # Categoria aggiornata includendo "elementari"
            category = st.selectbox(
                "Categoria", 
                options=["materna", "elementari", "medie", "adolescenti", "adulti", "donne"],
                key="db1_category_input"
            )
            year = st.number_input("Anno", value=2025, step=1, key="db1_year_input")
        with col2:
            # Se la categoria lo richiede, viene richiesto anche il genere
            if category in ["elementari", "medie", "adolescenti"]:
                gender = st.selectbox("Genere", options=["maschio", "femmina"], key="db1_gender_input")
            else:
                gender = "NA"
        if st.button("Inserisci Record", key="db1_insert_button"):
            insert_record_db1(total_time, game_name, category, gender, year)
            st.success("Record inserito correttamente nei tempi.")

    # ----- TAB 2: Modifica/Cancellazione Record in database1.db -----
    with tab2:
        st.header("Modifica o Cancella Record")
        records = get_records_db1()
        if records:
            df = pd.DataFrame(records, columns=["ID", "Tempo", "Gioco", "Categoria", "Sesso", "Anno"])
            st.dataframe(df)
            
            record_ids = df["ID"].tolist()
            selected_id = st.selectbox("Seleziona ID del record", record_ids, key="db1_select_record")
            action = st.selectbox("Scegli azione", ["Modifica", "Elimina"], key="db1_action_select")
            
            selected_record = df[df["ID"] == selected_id].iloc[0]
            
            if action == "Modifica":
                new_game_name = st.text_input(
                    "Nuovo Nome del Gioco", 
                    value=selected_record["Gioco"], 
                    key=f"update_db1_game_{selected_id}"
                )
                new_category = st.selectbox(
                    "Nuova Categoria", 
                    options=["materna", "elementari", "medie", "adolescenti", "adulti", "donne"],
                    index=["materna", "elementari", "medie", "adolescenti", "adulti", "donne"].index(selected_record["Categoria"]),
                    key=f"update_db1_category_{selected_id}"
                )
                new_year = st.number_input(
                    "Nuovo Anno", 
                    value=int(selected_record["Anno"]), 
                    step=1, 
                    key=f"update_db1_year_{selected_id}"
                )
                # Suddivide il tempo corrente in minuti e secondi
                current_minutes = int(float(selected_record["Tempo"]) // 60)
                current_seconds = float(selected_record["Tempo"]) - current_minutes * 60
                new_minutes = st.number_input(
                    "Nuovi Minuti", 
                    value=current_minutes, 
                    step=1, 
                    key=f"update_db1_minutes_{selected_id}"
                )
                new_seconds = st.number_input(
                    "Nuovi Secondi", 
                    value=current_seconds, 
                    format="%.2f", 
                    key=f"update_db1_seconds_{selected_id}"
                )
                new_time = new_minutes * 60 + new_seconds
                
                if new_category in ["elementari", "medie", "adolescenti"]:
                    # Se il valore salvato per il genere non corrisponde alle opzioni, si usa "maschio" di default
                    default_gender = selected_record["Sesso"] if selected_record["Sesso"] in ["maschio", "femmina"] else "maschio"
                    new_gender = st.selectbox(
                        "Nuovo Genere", 
                        options=["maschio", "femmina"],
                        index=(0 if default_gender == "maschio" else 1),
                        key=f"update_db1_gender_{selected_id}"
                    )
                else:
                    new_gender = "NA"
                    
                if st.button("Conferma Modifica", key=f"db1_confirm_update_{selected_id}"):
                    update_record_db1(selected_id, new_time, new_game_name, new_category, new_gender, new_year)
                    st.success("Record modificato correttamente.")
            elif action == "Elimina":
                if st.button("Conferma Eliminazione", key=f"db1_confirm_delete_{selected_id}"):
                    delete_record_db1(selected_id)
                    st.success("Record eliminato correttamente.")
        else:
            st.info("Nessun record presente nel database.")

    # ----- TAB 3: Visualizzazione Record con Filtri in database1.db -----
    with tab3:
        st.header("Visualizza Record con Filtri")
        st.write("Filtra per:")
        filter_options = ["Tutti", "Anno", "Categoria", "Sesso", "Nome del Gioco"]
        filter_choice = st.selectbox("Seleziona filtro", filter_options, key="db1_filter_choice")
        filter_value = None

        if filter_choice == "Anno":
            filter_value = st.number_input("Inserisci Anno", value=2025, step=1, key="filter_year_input")
        elif filter_choice == "Categoria":
            filter_value = st.selectbox(
                "Seleziona Categoria", 
                options=["materna", "elementari", "medie", "adolescenti", "adulti", "donne"], 
                key="filter_category_input"
            )
        elif filter_choice == "Sesso":
            filter_value = st.selectbox("Seleziona Sesso", options=["maschio", "femmina"], key="filter_gender_input")
        elif filter_choice == "Nome del Gioco":
            filter_value = st.text_input("Inserisci parte del Nome del Gioco", value="", key="filter_game_name_input")

        conn = sqlite3.connect("database1.db")
        cursor = conn.cursor()

        if filter_choice == "Tutti":
            cursor.execute("SELECT * FROM results")
        elif filter_choice == "Anno":
            cursor.execute("SELECT * FROM results WHERE year=?", (filter_value,))
        elif filter_choice == "Categoria":
            cursor.execute("SELECT * FROM results WHERE category=?", (filter_value,))
        elif filter_choice == "Sesso":
            cursor.execute("SELECT * FROM results WHERE gender=?", (filter_value,))
        elif filter_choice == "Nome del Gioco":
            cursor.execute("SELECT * FROM results WHERE game_name LIKE ?", ('%' + filter_value + '%',))
        records_filtered = cursor.fetchall()
        conn.close()

        if records_filtered:
            st.write(f"Record trovati: {len(records_filtered)}")
            df_filtered = pd.DataFrame(records_filtered, columns=["ID", "Tempo", "Gioco", "Categoria", "Sesso", "Anno"])
            # Aggiunge una nuova colonna: tempo formattato in formato mm:ss.ss
            df_filtered["Tempo Formattato"] = df_filtered["Tempo"].apply(
                lambda x: f"{int(x // 60):02d}:{(x - int(x // 60)*60):05.2f}"
            )
            st.dataframe(df_filtered)
        else:
            st.info("Nessun record trovato con i filtri applicati.")

# ----- TAB 4: Gestione Tempi Ragazzi (DB 2) -----
    with tab4:
        st.header("Gestione Tempi Ragazzi e Visualizzazione Minimi")
        option_tab4 = st.radio(
            "Seleziona Azione",
            ["Inserisci Nuovo Tempo", "Modifica/Cancella Tempo", "Visualizza Minimo per Gioco e Categoria"],
            key="db2_action_radio"
        )
        
        # --- Sezione Inserimento record in database2.db ---
        if option_tab4 == "Inserisci Nuovo Tempo":
            st.subheader("Inserisci Nuovo Tempo per Ragazzi")
            nome = st.text_input("Nome Ragazzo", key="db2_nome_input")
            # Input per minuti e secondi
            minutes_value = st.number_input("Minuti", value=0, step=1, key="db2_minutes_input")
            seconds_value = st.number_input("Secondi", value=0.0, format="%.2f", key="db2_seconds_input")
            # Calcolo del tempo totale in secondi
            total_time = minutes_value * 60 + seconds_value
            
            game_name = st.text_input("Nome del Gioco", key="db2_game_input")
            # Menu delle categorie aggiornato, includendo "elementari"
            category = st.selectbox(
                "Categoria",
                options=["materna", "elementari", "medie", "adolescenti", "adulti", "donne"],
                key="db2_category_input"
            )
            # Se la categoria è tra quelle che richiedono di specificare il genere (elementari, medie, adolescenti)
            if category in ["elementari", "medie", "adolescenti"]:
                gender = st.selectbox("Genere", options=["maschio", "femmina"], key="db2_gender_input")
            else:
                gender = "NA"
            year = st.number_input("Anno", value=2025, step=1, key="db2_year_input")
            
            if st.button("Inserisci Record", key="db2_insert_record"):
                # Assicurati che la funzione insert_record_db2 sia definita per accettare anche il parametro "gender"
                insert_record_db2(nome, total_time, game_name, category, year, gender)
                st.success("Record inserito correttamente per il ragazzo.")
        
        # --- Sezione Modifica/Cancellazione record in database2.db ---
        elif option_tab4 == "Modifica/Cancella Tempo":
            st.subheader("Modifica o Cancella Record per Ragazzi")
            records = get_records_db2()
            if records:
                # Assumendo che ora il record contenga anche il campo "Genere"
                df = pd.DataFrame(records, columns=["ID", "Nome", "Tempo", "Gioco", "Categoria", "Genere", "Anno"])
                st.dataframe(df)
                record_ids = df["ID"].tolist()
                selected_id = st.selectbox("Seleziona ID del record", record_ids, key="db2_select_record")
                action = st.selectbox("Scegli azione", ["Modifica", "Elimina"], key="db2_action_select")
                selected_record = df[df["ID"] == selected_id].iloc[0]
                
                if action == "Modifica":
                    new_nome = st.text_input(
                        "Nuovo Nome Ragazzo", 
                        value=selected_record["Nome"], 
                        key=f"update_db2_nome_{selected_id}"
                    )
                    # Calcola minuti e secondi dal tempo attuale
                    current_minutes = int(float(selected_record["Tempo"]) // 60)
                    current_seconds = float(selected_record["Tempo"]) - current_minutes * 60
                    new_minutes = st.number_input(
                        "Nuovi Minuti", 
                        value=current_minutes, 
                        step=1, 
                        key=f"update_db2_minutes_{selected_id}"
                    )
                    new_seconds = st.number_input(
                        "Nuovi Secondi", 
                        value=current_seconds, 
                        format="%.2f", 
                        key=f"update_db2_seconds_{selected_id}"
                    )
                    new_time = new_minutes * 60 + new_seconds
                    
                    new_game_name = st.text_input(
                        "Nuovo Nome del Gioco", 
                        value=selected_record["Gioco"], 
                        key=f"update_db2_game_{selected_id}"
                    )
                    new_category = st.selectbox(
                        "Nuova Categoria", 
                        options=["materna", "elementari", "medie", "adolescenti", "adulti", "donne"],
                        index=["materna", "elementari", "medie", "adolescenti", "adulti", "donne"].index(selected_record["Categoria"]),
                        key=f"update_db2_category_{selected_id}"
                    )
                    if new_category in ["elementari", "medie", "adolescenti"]:
                        new_gender = st.selectbox(
                            "Nuovo Genere", 
                            options=["maschio", "femmina"],
                            index=["maschio", "femmina"].index(selected_record["Genere"]) if selected_record["Genere"] in ["maschio", "femmina"] else 0,
                            key=f"update_db2_gender_{selected_id}"
                        )
                    else:
                        new_gender = None
                    
                    new_year = st.number_input(
                        "Nuovo Anno", 
                        value=int(selected_record["Anno"]), 
                        step=1,
                        key=f"update_db2_year_{selected_id}"
                    )
                    if st.button("Conferma Modifica", key=f"db2_confirm_update_{selected_id}"):
                        update_record_db2(selected_id, new_nome, new_time, new_game_name, new_category, new_year, new_gender)
                        st.success("Record modificato correttamente.")
                elif action == "Elimina":
                    if st.button("Conferma Eliminazione", key=f"db2_confirm_delete_{selected_id}"):
                        delete_record_db2(selected_id)
                        st.success("Record eliminato correttamente.")
            else:
                st.info("Nessun record presente nel database.")
        
        # --- Sezione Visualizzazione minimi per ogni gioco e categoria in database2.db ---
        elif option_tab4 == "Visualizza Minimo per Gioco e Categoria":
            st.subheader("Visualizza Tempo Minimo per Gioco e Categoria")
            filtro_anno = st.selectbox(
                "Seleziona Anno (oppure 'Tutti')", 
                options=["Tutti", "2031", "2030", "2029", "2028", "2027", "2026", "2025", "2024", "2023"],
                key="db2_filter_year"
            )
            min_results = get_min_times(filtro_anno)
            if min_results:
                # Includiamo anche il nome associato al tempo minimo
                df_min = pd.DataFrame(min_results, columns=["Gioco", "Categoria", "Nome","Sesso","Tempo Minimo"])
                st.dataframe(df_min)
            else:
                st.info("Nessun dato disponibile per i criteri di ricerca.")


if __name__ == '__main__':
    main()
