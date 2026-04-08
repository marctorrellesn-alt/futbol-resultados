import requests
from datetime import datetime, timedelta, timezone
import os

API_KEY = os.environ.get("API_FOOTBALL_KEY", "")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

HEADERS = {"X-Auth-Token": API_KEY}

LIGAS = [
    {"id": "PL",  "nombre": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League"},
    {"id": "PD",  "nombre": "🇪🇸 LaLiga"},
    {"id": "SA",  "nombre": "🇮🇹 Serie A"},
    {"id": "BL1", "nombre": "🇩🇪 Bundesliga"},
    {"id": "FL1", "nombre": "🇫🇷 Ligue 1"},
    {"id": "CL",  "nombre": "🏆 Champions League"},
]

def get_yesterday():
    now_utc = datetime.now(timezone.utc)
    offset = timedelta(hours=5)
    now_local = now_utc - offset
    yesterday = now_local - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def get_fixtures(league_id, date):
    url = f"https://api.football-data.org/v4/competitions/{league_id}/matches"
    params = {"dateFrom": date, "dateTo": date}
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        data = response.json()
        return data.get("matches", [])
    except Exception:
        return []

def format_fixture(match):
    home = match["homeTeam"]["name"]
    away = match["awayTeam"]["name"]
    status = match["status"]
    if status == "FINISHED":
        home_goals = match["score"]["fullTime"]["home"]
        away_goals = match["score"]["fullTime"]["away"]
        return f"  {home} {home_goals} - {away_goals} {away}"
    elif status == "IN_PLAY" or status == "PAUSED":
        home_goals = match["score"]["fullTime"]["home"] or 0
        away_goals = match["score"]["fullTime"]["away"] or 0
        return f"  🔴 {home} {home_goals} - {away_goals} {away} (en juego)"
    elif status == "POSTPONED":
        return f"  {home} vs {away} (aplazado)"
    elif status == "CANCELLED":
        return f"  {home} vs {away} (cancelado)"
    else:
        hora = match["utcDate"][11:16]
        return f"  {home} vs {away} ({hora})"

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
        matches = get_fixtures(liga["id"], date)
        if matches:
            hay_partidos = True
            mensaje += f"\n<b>{liga['nombre']}</b>\n"
            for match in matches:
                mensaje += format_fixture(match) + "\n"
    if not hay_partidos:
        mensaje += "\nNo hubo partidos ayer en las competiciones seleccionadas."
    send_telegram(mensaje)
    print(mensaje)

if __name__ == "__main__":
    main()
