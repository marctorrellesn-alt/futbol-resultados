import requests
from datetime import datetime, timedelta, timezone
import os

API_KEY = os.environ.get("API_FOOTBALL_KEY", "")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

HEADERS = {"x-apisports-key": API_KEY}

LIGAS = [
    {"id": 140, "nombre": "🇪🇸 LaLiga",              "season": 2025},
    {"id": 39,  "nombre": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League",     "season": 2025},
    {"id": 135, "nombre": "🇮🇹 Serie A",              "season": 2025},
    {"id": 78,  "nombre": "🇩🇪 Bundesliga",           "season": 2025},
    {"id": 61,  "nombre": "🇫🇷 Ligue 1",              "season": 2025},
    {"id": 141, "nombre": "🇪🇸 Segunda División",      "season": 2025},
    {"id": 40,  "nombre": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship",        "season": 2025},
    {"id": 2,   "nombre": "🏆 Champions League",       "season": 2025},
    {"id": 3,   "nombre": "🟠 Europa League",          "season": 2025},
    {"id": 848, "nombre": "🔵 Conference League",      "season": 2025},
    {"id": 143, "nombre": "🥇 Copa del Rey",           "season": 2025},
    {"id": 48,  "nombre": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Carabao Cup",         "season": 2025},
    {"id": 45,  "nombre": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 FA Cup",              "season": 2025},
    {"id": 1,   "nombre": "🌍 Mundial",                "season": 2026},
]

def get_yesterday():
    return "2025-04-07"

def get_fixtures(league_id, season, date):
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"league": league_id, "date": date, "season": season}
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        return response.json().get("response", [])
    except Exception:
        return []

def format_fixture(fixture):
    home = fixture["teams"]["home"]["name"]
    away = fixture["teams"]["away"]["name"]
    home_goals = fixture["goals"]["home"]
    away_goals = fixture["goals"]["away"]
    status = fixture["fixture"]["status"]["short"]
    if status == "FT":
        return f"  {home} {home_goals} - {away_goals} {away}"
    elif status in ["NS", "TBD"]:
        hora = fixture["fixture"]["date"][11:16]
        return f"  {home} vs {away} ({hora})"
    elif status in ["1H", "2H", "HT", "ET", "P"]:
        return f"  🔴 {home} {home_goals} - {away_goals} {away} (en juego)"
    elif status == "PST":
        return f"  {home} vs {away} (aplazado)"
    elif status == "CANC":
        return f"  {home} vs {away} (cancelado)"
    else:
        return f"  {home} {home_goals} - {away_goals} {away}"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    if len(message) > 4096:
        message = message[:4090] + "\n..."
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    })

def main():
    date = get_yesterday()
    mensaje = f"⚽ <b>Resultados del {date}</b>\n"
    hay_partidos = False
    for liga in LIGAS:
        fixtures = get_fixtures(liga["id"], liga["season"], date)
        if fixtures:
            hay_partidos = True
            mensaje += f"\n<b>{liga['nombre']}</b>\n"
            for fixture in fixtures:
                mensaje += format_fixture(fixture) + "\n"
    if not hay_partidos:
        mensaje += "\nNo hubo partidos ayer en las competiciones seleccionadas."
    send_telegram(mensaje)
    print(mensaje)

if __name__ == "__main__":
    main()
