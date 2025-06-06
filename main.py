import json
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DATABASE_FILE = "gare_database.json"
database = {}

def carica_database():
    global database
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            database = json.load(f)
            database = {int(anno): gare for anno, gare in database.items()}

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

def aggiungi_gara():
    try:
        anno = int(entry_anno.get())
    except ValueError:
        messagebox.showerror("Errore", "Inserisci un anno valido (numero intero).")
        return

    nome = entry_nome.get().strip()
    categoria = combo_categoria.get()
    sesso = combo_sesso.get()
    tempo = entry_tempo.get().strip()

    if not (nome and categoria and sesso and tempo):
        messagebox.showerror("Errore", "Compila tutti i campi.")
        return

    if not valida_tempo(tempo):
        messagebox.showerror("Errore", "Formato tempo non valido. Usa hh:mm:ss o mm:ss o ss.")
        return

    if anno not in database:
        database[anno] = []

    for gara in database[anno]:
        if gara["nome"].lower() == nome.lower() and gara["categoria"] == categoria and gara["sesso"] == sesso:
            if gara["tempo"] == tempo:
                messagebox.showinfo("Info", "Gara già presente con lo stesso tempo!")
            else:
                risposta = messagebox.askyesno("Conferma sovrascrittura", "La gara esiste con tempo diverso. Sovrascrivere?")
                if risposta:
                    gara["tempo"] = tempo
                    salva_database()
                    messagebox.showinfo("Successo", "Tempo sovrascritto.")
                else:
                    messagebox.showinfo("Annullato", "Operazione annullata.")
            return

    nuova_gara = {"nome": nome, "categoria": categoria, "sesso": sesso, "tempo": tempo}
    database[anno].append(nuova_gara)
    salva_database()
    messagebox.showinfo("Successo", "Gara aggiunta!")
    pulisci_campi_aggiungi()

def pulisci_campi_aggiungi():
    entry_nome.delete(0, tk.END)
    entry_tempo.delete(0, tk.END)
    combo_categoria.current(0)
    combo_sesso.current(0)

def filtra_e_ordina_gare(anno, filtro_nome):
    if anno not in database:
        return []
    gare = database[anno]
    if filtro_nome:
        gare = [g for g in gare if filtro_nome.lower() in g["nome"].lower()]
    gare = sorted(gare, key=lambda g: tempo_to_secondi(g["tempo"]))
    return gare

def stampa_gare():
    try:
        anno = int(entry_anno_stampa.get())
    except ValueError:
        messagebox.showerror("Errore", "Inserisci un anno valido.")
        return

    filtro_nome = entry_filtro_nome.get().strip()
    gare_filtrate = filtra_e_ordina_gare(anno, filtro_nome)

    output_box.delete('1.0', tk.END)
    if not gare_filtrate:
        output_box.insert(tk.END, "Nessuna gara trovata.\n")
    else:
        output_box.insert(tk.END, f"Gare per l'anno {anno} (filtrate per '{filtro_nome}'):\n\n")
        for gara in gare_filtrate:
            output_box.insert(tk.END, f"- {gara['nome']} | {gara['categoria']} | {gara['sesso']} | Tempo: {gara['tempo']}\n")

def cancella_gara():
    try:
        anno = int(entry_anno_stampa.get())
    except ValueError:
        messagebox.showerror("Errore", "Inserisci un anno valido.")
        return

    nome = entry_nome_cancella.get().strip()
    categoria = combo_categoria_cancella.get()
    sesso = combo_sesso_cancella.get()

    if not (nome and categoria and sesso):
        messagebox.showerror("Errore", "Compila tutti i campi per cancellare.")
        return

    if anno not in database:
        messagebox.showinfo("Info", "Anno non presente nel database.")
        return

    gare = database[anno]
    gara_trovata = False
    for i, gara in enumerate(gare):
        if gara["nome"].lower() == nome.lower() and gara["categoria"] == categoria and gara["sesso"] == sesso:
            del gare[i]
            gara_trovata = True
            break

    if gara_trovata:
        if not database[anno]:  # se la lista gare è vuota, elimino anno dal db
            del database[anno]
        salva_database()
        messagebox.showinfo("Successo", "Gara cancellata.")
        stampa_gare()
        # Pulizia campi cancellazione
        entry_nome_cancella.delete(0, tk.END)
        combo_categoria_cancella.current(0)
        combo_sesso_cancella.current(0)
    else:
        messagebox.showinfo("Info", "Gara non trovata.")

def mostra_statistiche():
    stat_text.delete('1.0', tk.END)
    anni = sorted(database.keys())
    if not anni:
        stat_text.insert(tk.END, "Nessun dato presente.\n")
        return
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

    stat_text.insert(tk.END, f"Anni presenti: {', '.join(map(str, anni))}\n")
    stat_text.insert(tk.END, f"Totale gare registrate: {totale_gare}\n")
    stat_text.insert(tk.END, "Distribuzione sesso:\n")
    for sesso, cnt in count_sesso.items():
        stat_text.insert(tk.END, f"  {sesso}: {cnt}\n")
    stat_text.insert(tk.END, f"Tempo medio gare: {media_tempo}\n")

    # Pulisci figura e disegna nuovo grafico
    fig.clf()  # Pulisce tutta la figura
    ax = fig.add_subplot(111)
    ax.bar(count_sesso.keys(), count_sesso.values(), color=['blue', 'pink', 'gray'])
    ax.set_title("Distribuzione gare per sesso")
    ax.set_ylabel("Numero gare")
    ax.set_xlabel("Sesso")
    canvas.draw_idle()  # Forza il redraw più efficiente

def esporta_file():
    try:
        anno = int(entry_anno_export.get())
    except ValueError:
        messagebox.showerror("Errore", "Inserisci un anno valido.")
        return

    if anno not in database or not database[anno]:
        messagebox.showinfo("Info", "Nessuna gara presente per l'anno selezionato.")
        return

    scelta = file_format_var.get()
    if scelta == "CSV":
        estensione = ".csv"
    else:
        estensione = ".txt"

    percorso = filedialog.asksaveasfilename(defaultextension=estensione,
                                           filetypes=[(f"{scelta} files", f"*{estensione}"), ("All files", "*.*")],
                                           initialfile=f"gare_{anno}{estensione}")

    if not percorso:
        return

    try:
        if scelta == "CSV":
            with open(percorso, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Nome", "Categoria", "Sesso", "Tempo"])
                for gara in database[anno]:
                    writer.writerow([gara["nome"], gara["categoria"], gara["sesso"], gara["tempo"]])
        else:
            with open(percorso, "w", encoding="utf-8") as f:
                f.write(f"Gare anno {anno}:\n\n")
                for gara in database[anno]:
                    f.write(f"{gara['nome']} | {gara['categoria']} | {gara['sesso']} | Tempo: {gara['tempo']}\n")
        messagebox.showinfo("Successo", f"File esportato correttamente:\n{percorso}")
    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante esportazione:\n{e}")

def pulisci_filtro_e_risultati():
    entry_filtro_nome.delete(0, tk.END)
    output_box.delete('1.0', tk.END)

# === GUI ===
root = tk.Tk()
root.title("Database Gare - Borgo Treponti")
root.geometry("800x700")
root.resizable(False, False)
carica_database()

# Notebook con tab
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=10, pady=10)

# --- Tab Inserisci Gara ---
tab_inserisci = ttk.Frame(notebook)
notebook.add(tab_inserisci, text="Inserisci Gara")

ttk.Label(tab_inserisci, text="Anno:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
entry_anno = ttk.Entry(tab_inserisci)
entry_anno.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

ttk.Label(tab_inserisci, text="Nome Gara:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
entry_nome = ttk.Entry(tab_inserisci)
entry_nome.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

ttk.Label(tab_inserisci, text="Categoria:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
combo_categoria = ttk.Combobox(tab_inserisci, values=["Materna", "Elementari", "Medie", "Adolescenti", "Adulti"], state='readonly')
combo_categoria.current(0)
combo_categoria.grid(row=2, column=1, sticky='ew', padx=5, pady=5)

ttk.Label(tab_inserisci, text="Sesso:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
combo_sesso = ttk.Combobox(tab_inserisci, values=["M", "F", "Altro"], state='readonly')
combo_sesso.current(0)
combo_sesso.grid(row=3, column=1, sticky='ew', padx=5, pady=5)

ttk.Label(tab_inserisci, text="Tempo (hh:mm:ss o mm:ss o ss):").grid(row=4, column=0, sticky='w', padx=5, pady=5)
entry_tempo = ttk.Entry(tab_inserisci)
entry_tempo.grid(row=4, column=1, sticky='ew', padx=5, pady=5)

btn_aggiungi = ttk.Button(tab_inserisci, text="Aggiungi Gara", command=aggiungi_gara)
btn_aggiungi.grid(row=5, column=0, columnspan=2, pady=15)

for i in range(2):
    tab_inserisci.columnconfigure(i, weight=1)

# --- Tab Visualizza Gare ---
tab_visualizza = ttk.Frame(notebook)
notebook.add(tab_visualizza, text="Visualizza Gare")

frame_stampa = ttk.Frame(tab_visualizza)
frame_stampa.pack(fill='both', expand=True, padx=10, pady=10)
frame_stampa.columnconfigure(1, weight=1)

ttk.Label(frame_stampa, text="Anno:").grid(row=0, column=0, sticky='w', padx=5, pady=6)
entry_anno_stampa = ttk.Entry(frame_stampa)
entry_anno_stampa.grid(row=0, column=1, sticky='ew', pady=6, padx=5)

ttk.Label(frame_stampa, text="Filtro nome (opzionale):").grid(row=1, column=0, sticky='w', padx=5, pady=6)
entry_filtro_nome = ttk.Entry(frame_stampa)
entry_filtro_nome.grid(row=1, column=1, sticky='ew', pady=6, padx=5)

btn_stampa = ttk.Button(frame_stampa, text="Mostra Gare", command=stampa_gare)
btn_stampa.grid(row=2, column=0, columnspan=2, pady=10)

btn_pulisci = ttk.Button(frame_stampa, text="Pulisci filtro", command=pulisci_filtro_e_risultati)
btn_pulisci.grid(row=3, column=0, columnspan=2, pady=3)

output_box = scrolledtext.ScrolledText(frame_stampa, width=80, height=15)
output_box.grid(row=9, column=0, columnspan=3, pady=10, sticky='nsew')

# Separator
ttk.Separator(frame_stampa, orient='horizontal').grid(row=4, column=0, columnspan=3, sticky='ew', pady=10)

# Campi per cancellare gara
ttk.Label(frame_stampa, text="Nome Gara da cancellare:").grid(row=5, column=0, sticky='w', padx=5, pady=6)
entry_nome_cancella = ttk.Entry(frame_stampa)
entry_nome_cancella.grid(row=5, column=1, sticky='ew', pady=6, padx=5)

ttk.Label(frame_stampa, text="Categoria da cancellare:").grid(row=6, column=0, sticky='w', padx=5, pady=6)
combo_categoria_cancella = ttk.Combobox(frame_stampa, values=["Materna", "Elementari", "Medie", "Adolescenti", "Adulti"], state='readonly')
combo_categoria_cancella.current(0)
combo_categoria_cancella.grid(row=6, column=1, sticky='ew', pady=6, padx=5)

ttk.Label(frame_stampa, text="Sesso da cancellare:").grid(row=7, column=0, sticky='w', padx=5, pady=6)
combo_sesso_cancella = ttk.Combobox(frame_stampa, values=["M", "F", "Altro"], state='readonly')
combo_sesso_cancella.current(0)
combo_sesso_cancella.grid(row=7, column=1, sticky='ew', pady=6, padx=5)

btn_cancella = ttk.Button(frame_stampa, text="Cancella Gara", command=cancella_gara)
btn_cancella.grid(row=8, column=0, columnspan=2, pady=12)

# --- Tab Statistiche ---
tab_statistiche = ttk.Frame(notebook)
notebook.add(tab_statistiche, text="Statistiche")

stat_text = scrolledtext.ScrolledText(tab_statistiche, width=80, height=20)
stat_text.pack(padx=10, pady=10, fill='both', expand=True)

fig = plt.Figure(figsize=(5,3), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=tab_statistiche)
canvas.get_tk_widget().pack(padx=10, pady=10)

btn_stat = ttk.Button(tab_statistiche, text="Mostra Statistiche", command=mostra_statistiche)
btn_stat.pack(pady=5)

# --- Tab Esporta ---
tab_esporta = ttk.Frame(notebook)
notebook.add(tab_esporta, text="Esporta")

ttk.Label(tab_esporta, text="Anno da esportare:").grid(row=0, column=0, sticky='w', padx=5, pady=10)
entry_anno_export = ttk.Entry(tab_esporta)
entry_anno_export.grid(row=0, column=1, sticky='ew', padx=5, pady=10)

file_format_var = tk.StringVar(value="CSV")
ttk.Radiobutton(tab_esporta, text="CSV", variable=file_format_var, value="CSV").grid(row=1, column=0, padx=5, sticky='w')
ttk.Radiobutton(tab_esporta, text="TXT", variable=file_format_var, value="TXT").grid(row=1, column=1, padx=5, sticky='w')

btn_export = ttk.Button(tab_esporta, text="Esporta", command=esporta_file)
btn_export.grid(row=2, column=0, columnspan=2, pady=15)

tab_esporta.columnconfigure(1, weight=1)

root.mainloop()