import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import datetime
import os
import getpass

# Variabile globale per i dati
data = pd.DataFrame()  # Inizializza la variabile data

# Funzione per eseguire l'analisi delle azioni
def analyze_stock():
    global data  # Dichiara data come globale
    clear_previous_analysis()  # Pulisci l'analisi precedente

    symbol = symbol_entry.get()
    
    # Ottieni la data dal campo e converti in formato datetime
    start_date_str = start_date_entry.get()
    end_date_str = end_date_entry.get()
    
    try:
        # Converte le stringhe di data in oggetti datetime
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Errore", "Formato della data non valido. Usa il formato YYYY-MM-DD.")
        return

    if not symbol:
        messagebox.showerror("Errore", "Inserisci un simbolo di azione valido.")
        return

    data = yf.download(symbol, start=start_date, end=end_date)  # Salva i dati nella variabile globale

    if data.empty:
        messagebox.showerror("Errore", "Nessun dato trovato per il simbolo inserito.")
        return

    # Mostra gli ultimi dati
    result_text.delete(1.0, tk.END)  # Pulisce il campo testo
    result_text.insert(tk.END, data.tail().to_string())  # Aggiunge i dati

    # Calcola la variazione percentuale giornaliera
    data['Percent Change'] = data['Close'].pct_change() * 100
    last_percent_change = data['Percent Change'].iloc[-1]
    percent_change_label.config(text=f"Variazione Giornaliera: {last_percent_change:.2f}%")

    # Calcola la variazione percentuale rispetto all'intervallo
    if not data.empty:
        start_price = data['Close'].iloc[0]
        end_price = data['Close'].iloc[-1]
        interval_change = ((end_price - start_price) / start_price) * 100
        interval_change_label.config(text=f"Variazione Intervallo: {interval_change:.2f}%")

        # Calcola il volume totale degli scambi nell'intervallo
        total_volume = data['Volume'].sum()
        total_volume_label.config(text=f"Volume Totale: {total_volume:,}")  # Formatta con le virgole

        # Salva la cronologia delle ricerche
        save_search_history(symbol, start_date, end_date)

    # Mostra i grafici
    show_candle_chart(data, symbol)
    show_close_chart(data, symbol)

# Funzione per pulire l'analisi precedente
def clear_previous_analysis():
    result_text.delete(1.0, tk.END)  # Pulisce il campo testo
    percent_change_label.config(text="Variazione Giornaliera: --")  # Resetta l'etichetta della variazione percentuale
    interval_change_label.config(text="Variazione Intervallo: --")  # Resetta l'etichetta della variazione intervallo
    total_volume_label.config(text="Volume Totale: --")  # Resetta l'etichetta del volume totale

    # Rimuove i grafici precedenti
    for widget in candle_chart_frame.winfo_children():
        widget.destroy()
    for widget in close_chart_frame.winfo_children():
        widget.destroy()

# Funzione per visualizzare il grafico a candele
def show_candle_chart(data, symbol):
    fig, ax = plt.subplots()
    ax.plot(data.index, data['Close'], label="Prezzo di Chiusura")
    ax.set_title(f'Prezzo di Chiusura di {symbol}')
    ax.set_xlabel('Data')
    ax.set_ylabel('Prezzo')

    # Aggiorna il grafico nella finestra Tkinter
    canvas = FigureCanvasTkAgg(fig, master=candle_chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Funzione per visualizzare il grafico dei prezzi di chiusura
def show_close_chart(data, symbol):
    fig, ax = plt.subplots()
    ax.plot(data.index, data['Close'], label="Prezzo di Chiusura")
    ax.set_title(f'Prezzo di Chiusura di {symbol}')
    ax.set_xlabel('Data')
    ax.set_ylabel('Prezzo')

    # Aggiorna il grafico nella finestra Tkinter
    canvas = FigureCanvasTkAgg(fig, master=close_chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Funzione per salvare la cronologia delle ricerche
def save_search_history(symbol, start_date, end_date):
    username = getpass.getuser()  # Ottiene il nome utente del PC
    history_entry = f"Utente: {username}, Simbolo: {symbol}, Data Inizio: {start_date.date()}, Data Fine: {end_date.date()}\n"
    
    with open("registro.txt", "a") as file:
        file.write(history_entry)

# Funzione per esportare i dati in CSV
def export_to_csv(data):
    if data.empty:
        messagebox.showerror("Errore", "Nessun dato da esportare.")
        return
    
    # Chiede all'utente dove salvare il file
    filename = f"{symbol_entry.get()}_data.csv"
    data.to_csv(filename)
    messagebox.showinfo("Successo", f"Dati esportati in {filename}")

# Configura la finestra principale
root = tk.Tk()
root.title("Analisi delle Azioni Finanziarie")
root.geometry("1000x600")

# Simbolo dell'azione
ttk.Label(root, text="Inserisci il simbolo dell'azione:").pack()
symbol_entry = ttk.Entry(root)
symbol_entry.pack()

# Intervallo di date
ttk.Label(root, text="Data di inizio:").pack()
start_date_entry = ttk.Entry(root)
start_date_entry.pack()
start_date_entry.insert(0, "2020-01-01")

ttk.Label(root, text="Data di fine:").pack()
end_date_entry = ttk.Entry(root)
end_date_entry.pack()
end_date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

# Bottone per avviare l'analisi
analyze_button = ttk.Button(root, text="Analizza", command=analyze_stock)
analyze_button.pack(pady=10)

# Bottone per esportare i dati in CSV
export_button = ttk.Button(root, text="Esporta in CSV", command=lambda: export_to_csv(data))
export_button.pack(pady=10)

# Sezione per mostrare i risultati
result_text = tk.Text(root, height=10, width=80)
result_text.pack()

# Variazione percentuale giornaliera
percent_change_label = ttk.Label(root, text="Variazione Giornaliera: --")
percent_change_label.pack()

# Variazione percentuale rispetto all'intervallo
interval_change_label = ttk.Label(root, text="Variazione Intervallo: --")
interval_change_label.pack()

# Volume totale degli scambi
total_volume_label = ttk.Label(root, text="Volume Totale: --")
total_volume_label.pack()

# Grafico a candele
ttk.Label(root, text="Grafico a Candele:").pack()
candle_chart_frame = ttk.Frame(root)
candle_chart_frame.pack(fill=tk.BOTH, expand=True)

# Grafico dei prezzi di chiusura
ttk.Label(root, text="Grafico dei Prezzi di Chiusura:").pack()
close_chart_frame = ttk.Frame(root)
close_chart_frame.pack(fill=tk.BOTH, expand=True)

# Avvia l'interfaccia grafica
root.mainloop()
