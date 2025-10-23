import requests
import logging
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Konfiguration
logging.basicConfig(level=logging.INFO)
LATITUDE = 0.0   # Latitude placeholder
LONGITUDE = 0.0  # Longitude placeholder

# Standarddatum ist heute
DEFAULT_DATE = datetime.now().strftime('%Y-%m-%d')

# Open-Meteo API-Endpunkt für die tägliche Wettervorhersage
API_BASE = "https://api.open-meteo.com/v1/forecast"

# Hilfsfunktion zum Erstellen der API-URL für ein bestimmtes Datum
def build_api_url(date):
    return (
        f"{API_BASE}?latitude={LATITUDE}&longitude={LONGITUDE}"
        f"&start_date={date}&end_date={date}"
        f"&daily=temperature_2m_max,temperature_2m_min,windspeed_10m_max&timezone=Europe%2FBerlin"
    )

def build_api_url_week(start_date):
    end_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=6)).strftime('%Y-%m-%d')
    return (
        f"{API_BASE}?latitude={LATITUDE}&longitude={LONGITUDE}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&daily=temperature_2m_max,temperature_2m_min,windspeed_10m_max&timezone=Europe%2FBerlin"
    )

def fetch_weather(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"API-Anfrage fehlgeschlagen: {e}")
        return None

def show_weather():
    date = date_entry.get()
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        weather_label.config(text="Ungültiges Datum. Format: YYYY-MM-DD")
        return
    url = build_api_url(date)
    data = fetch_weather(url)
    if data and "daily" in data:
        daily = data["daily"]
        temp_max = daily["temperature_2m_max"][0]
        temp_min = daily["temperature_2m_min"][0]
        wind_max = daily["windspeed_10m_max"][0]
        weather_label.config(text=(
            f"Wetter am {date} in der Triftstraße, 13127 Berlin:\n"
            f"Max Temp: {temp_max}°C\nMin Temp: {temp_min}°C\nMax Wind: {wind_max} km/h"
        ))
    else:
        weather_label.config(text="Fehler beim Abrufen der Wetterdaten.")

def plot_week_weather():
    start_date = date_entry.get()
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        weather_label.config(text="Ungültiges Datum. Format: YYYY-MM-DD")
        return
    url = build_api_url_week(start_date)
    data = fetch_weather(url)
    if data and "daily" in data:
        daily = data["daily"]
        dates = daily["time"]
        # Format dates to TT-MM
        dates_short = [datetime.strptime(d, '%Y-%m-%d').strftime('%d-%m') for d in dates]
        temp_max = daily["temperature_2m_max"]
        temp_min = daily["temperature_2m_min"]
        wind_max = daily["windspeed_10m_max"]
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(dates_short, temp_max, label='Max Temp (°C)', marker='o')
        ax.plot(dates_short, temp_min, label='Min Temp (°C)', marker='o')
        ax.plot(dates_short, wind_max, label='Max Wind (km/h)', marker='x')
        ax.set_xlabel('Datum (TT-MM)')
        ax.set_ylabel('Wert')
        ax.set_title('Wettervorhersage für 7 Tage')
        ax.legend()
        ax.grid(True)
        # Remove old canvas if exists
        global canvas
        if 'canvas' in globals() and canvas:
            canvas.get_tk_widget().destroy()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)
    else:
        weather_label.config(text="Fehler beim Abrufen der Wetterdaten.")

# GUI Setup
root = tk.Tk()
root.title("Wetter - Beispiel")
root.geometry("700x700")
root.resizable(False, False)

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

header = ttk.Label(frame, text="Wetterabfrage", font=("Arial", 16, "bold"))
header.pack(pady=(0, 10))

date_label = ttk.Label(frame, text="Datum (MM-DD):", font=("Arial", 12))
date_label.pack()

date_entry = ttk.Entry(frame, font=("Arial", 12))
date_entry.insert(0, DEFAULT_DATE)
date_entry.pack(pady=5)

weather_label = ttk.Label(frame, text="", font=("Arial", 12))
weather_label.pack(pady=10)

refresh_btn = ttk.Button(frame, text="Wetter anzeigen", command=show_weather)
refresh_btn.pack(pady=10)
refresh_btn.focus_set()  # Set focus to the button for visibility

plot_btn = ttk.Button(frame, text="7-Tage-Graf anzeigen", command=plot_week_weather)
plot_btn.pack(pady=10)

show_weather()
root.mainloop()
