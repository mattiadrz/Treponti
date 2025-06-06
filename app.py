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

def insert_record_db2(nome, time_value, game_name, category, year):
    conn = sqlite3.connect("database2.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO results_kids (nome, time, game_name, category, year) VALUES (?, ?, ?, ?, ?)",
        (nome, time_value, game_name, category, year)
    )
    conn.commit()
    conn.close()

def get_records_db2():
    conn = sqlite3.connect("database2.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM results_kids")
    records = cursor.fetchall()
    conn.close()
    return records

def update_record_db2(record_id, nome, new_time, new_game_name, new_category, new_year):
    conn = sqlite3.connect("database2.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE results_kids SET nome=?, time=?, game_name=?, category=?, year=? WHERE id=?",
        (nome, new_time, new_game_name, new_category, new_year, record_id)
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
    if year_filter and year_filter != "Tutti":
        cursor.execute(
            """
            SELECT game_name, category, MIN(time) as min_time
            FROM results_kids
            WHERE year=?
            GROUP BY game_name, category
            """, (year_filter,)
        )
    else:
        cursor.execute(
            """
            SELECT game_name, category, MIN(time) as min_time
            FROM results_kids
            GROUP BY game_name, category
            """
        )
    results = cursor.fetchall()
    conn.close()
    return results

# --- Definizione dell'app Streamlit con le 4 Tab ---

def main():
    st.title("Gestione Tempi con SQLite e Streamlit")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Inserisci Tempi",
        "Modifica/Cancella Tempi",
        "Visualizza Tempi",
        "Gestione Ragazzi e Visualizza Minimi"
    ])

    # ----- TAB 1: Inserimento Record in database1.db -----
    with tab1:
        st.header("Inserisci Nuovo Tempo (DB 1)")
        col1, col2 = st.columns(2)
        with col1:
            time_value = st.number_input("Tempo (es. in secondi)", value=0.0, format="%.2f", key="db1_time_input")
            game_name = st.text_input("Nome del Gioco", key="db1_game_input")
            category = st.selectbox("Categoria", options=["materna", "medie", "adolescenti", "adulti", "donne"])
            year = st.number_input("Anno", value=2025, step=1, key="db1_year_input")
        with col2:
            if category in ["medie", "adolescenti"]:
                gender = st.selectbox("Sesso", options=["maschi", "femmine"])
            else:
                gender = "NA"
        if st.button("Inserisci Record", key="db1_insert_button"):
            insert_record_db1(time_value, game_name, category, gender, year)
            st.success("Record inserito correttamente nei tempi.")

    # ----- TAB 2: Modifica/Cancellazione Record in database1.db -----
    with tab2:
        st.header("Modifica o Cancella Record (DB 1)")
        records = get_records_db1()
        if records:
            df = pd.DataFrame(records, columns=["ID", "Tempo", "Gioco", "Categoria", "Sesso", "Anno"])
            st.dataframe(df)
            
            record_ids = df["ID"].tolist()
            selected_id = st.selectbox("Seleziona ID del record", record_ids, key="db1_select_record")
            action = st.selectbox("Scegli azione", ["Modifica", "Elimina"], key="db1_action_select")
            
            selected_record = df[df["ID"] == selected_id].iloc[0]
            
            if action == "Modifica":
                new_time = st.number_input(
                    "Nuovo Tempo", 
                    value=float(selected_record["Tempo"]), 
                    format="%.2f", 
                    key=f"update_db1_time_{selected_id}"
                )
                new_game_name = st.text_input(
                    "Nuovo Nome del Gioco", 
                    value=selected_record["Gioco"], 
                    key=f"update_db1_game_{selected_id}"
                )
                new_category = st.selectbox(
                    "Nuova Categoria", 
                    options=["materna", "medie", "adolescenti", "adulti", "donne"],
                    index=["materna", "medie", "adolescenti", "adulti", "donne"].index(selected_record["Categoria"]),
                    key=f"update_db1_category_{selected_id}"
                )
                new_year = st.number_input(
                    "Nuovo Anno", 
                    value=int(selected_record["Anno"]), 
                    step=1, 
                    key=f"update_db1_year_{selected_id}"
                )
                if new_category in ["medie", "adolescenti"]:
                    default_gender = selected_record["Sesso"] if selected_record["Sesso"] in ["maschi", "femmine"] else "maschi"
                    new_gender = st.selectbox(
                        "Nuovo Sesso", 
                        options=["maschi", "femmine"],
                        index=(0 if default_gender == "maschi" else 1),
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
        st.header("Visualizza Record con Filtri (DB 1)")
        st.write("Filtra per:")
        filter_options = ["Tutti", "Anno", "Categoria", "Sesso", "Nome del Gioco"]
        filter_choice = st.selectbox("Seleziona filtro", filter_options, key="db1_filter_choice")
        filter_value = None

        if filter_choice == "Anno":
            filter_value = st.number_input("Inserisci Anno", value=2025, step=1, key="filter_year_input")
        elif filter_choice == "Categoria":
            filter_value = st.selectbox("Seleziona Categoria", options=["materna", "medie", "adolescenti", "adulti", "donne"], key="filter_category_input")
        elif filter_choice == "Sesso":
            filter_value = st.selectbox("Seleziona Sesso", options=["maschi", "femmine"], key="filter_gender_input")
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
            st.dataframe(df_filtered)
        else:
            st.info("Nessun record trovato con i filtri applicati.")

    # ----- TAB 4: Gestione Tempi Ragazzi (DB 2) -----
    with tab4:
        st.header("Gestione Tempi Ragazzi e Visualizzazione Minimi (DB 2)")
        option_tab4 = st.radio("Seleziona Azione", ["Inserisci Nuovo Tempo", "Modifica/Cancella Tempo", "Visualizza Minimo per Gioco e Categoria"], key="db2_action_radio")
        
        # --- Sezione Inserimento record in database2.db ---
        if option_tab4 == "Inserisci Nuovo Tempo":
            st.subheader("Inserisci Nuovo Tempo per Ragazzi")
            nome = st.text_input("Nome Ragazzo", key="db2_nome_input")
            time_value = st.number_input("Tempo (es. in secondi)", value=0.0, format="%.2f", key="db2_time_input")
            game_name = st.text_input("Nome del Gioco", key="db2_game_input")
            category = st.selectbox("Categoria", options=["materna", "medie", "adolescenti", "adulti", "donne"], key="db2_category_input")
            year = st.number_input("Anno", value=2025, step=1, key="db2_year_input")
            if st.button("Inserisci Record", key="db2_insert_record"):
                insert_record_db2(nome, time_value, game_name, category, year)
                st.success("Record inserito correttamente per il ragazzo.")
        
        # --- Sezione Modifica/Cancellazione record in database2.db ---
        elif option_tab4 == "Modifica/Cancella Tempo":
            st.subheader("Modifica o Cancella Record per Ragazzi")
            records = get_records_db2()
            if records:
                df = pd.DataFrame(records, columns=["ID", "Nome", "Tempo", "Gioco", "Categoria", "Anno"])
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
                    new_time = st.number_input(
                        "Nuovo Tempo", 
                        value=float(selected_record["Tempo"]), 
                        format="%.2f", 
                        key=f"update_db2_time_{selected_id}"
                    )
                    new_game_name = st.text_input(
                        "Nuovo Nome del Gioco", 
                        value=selected_record["Gioco"], 
                        key=f"update_db2_game_{selected_id}"
                    )
                    new_category = st.selectbox(
                        "Nuova Categoria", 
                        options=["materna", "medie", "adolescenti", "adulti", "donne"],
                        index=["materna", "medie", "adolescenti", "adulti", "donne"].index(selected_record["Categoria"]),
                        key=f"update_db2_category_{selected_id}"
                    )
                    new_year = st.number_input(
                        "Nuovo Anno", 
                        value=int(selected_record["Anno"]), 
                        step=1,
                        key=f"update_db2_year_{selected_id}"
                    )
                    if st.button("Conferma Modifica", key=f"db2_confirm_update_{selected_id}"):
                        update_record_db2(selected_id, new_nome, new_time, new_game_name, new_category, new_year)
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
            filtro_anno = st.selectbox("Seleziona Anno (oppure 'Tutti')", options=["Tutti", "2031", "2030", "2029", "2028", "2027", "2026", "2025", "2024", "2023"], key="db2_filter_year")
            min_results = get_min_times(filtro_anno)
            if min_results:
                df_min = pd.DataFrame(min_results, columns=["Gioco", "Categoria", "Tempo Minimo"])
                st.dataframe(df_min)
            else:
                st.info("Nessun dato disponibile per i criteri di ricerca.")

if __name__ == '__main__':
    main()
