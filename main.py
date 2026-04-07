import requests
from datetime import datetime, timedelta
import os

API_KEY = os.environ.get("API_FOOTBALL_KEY", "")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

LIGAS = {
    140: "🇪🇸 LaLiga",
    39:  "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League",
    135: "🇮🇹 Serie A",
    61:  "🇫🇷 Ligue 1",
    78:  "🇩🇪 Bundesliga",
    2:   "🏆 Champions League",
    1:   "🌍 Mundial",
    141: "🇪🇸 Segunda División",
    40:  "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship (2ª inglesa)",
}

HEADERS = {"x-apisports-key": API_KEY}

def get_yesterday():
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def get_fixtures(league_id, date):
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"league": league_id, "date": date, "season": 2024}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json().get("response", [])

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
    else:
        return f"  {home} {home_goals} - {away_goals} {away} ({status})"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"})

def main():
    date = get_yesterday()
    mensaje = f"⚽ <b>Resultados del {date}</b>\n"
    hay_partidos = False
    for league_id, league_name in LIGAS.items():
        fixtures = get_fixtures(league_id, date)
        if fixtures:
            hay_partidos = True
            mensaje += f"\n<b>{league_name}</b>\n"
            for fixture in fixtures:
                mensaje += format_fixture(fixture) + "\n"
    if not hay_partidos:
        mensaje += "\nNo hubo partidos ayer."
    send_telegram(mensaje)
    print(mensaje)

if __name__ == "__main__":
    main()
