import requests
import datetime
import os

# ========= إعدادات =========

TELEGRAM_BOT_TOKEN = "8662332213:AAEQ2p3cP7RMHsZC8_RvXTOuCdVbUmRpoMk"
TELEGRAM_CHAT_ID = "@MySeriesAlerts"

STATE_FILE = "sent_today.txt"

# ===========================

TVMAZE_SCHEDULE_URL = "https://api.tvmaze.com/schedule"


def load_sent_ids():
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return set(f.read().splitlines())


def save_sent_ids(sent_ids):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        for eid in sent_ids:
            f.write(eid + "\n")


def get_today_schedule():
    today = datetime.date.today().isoformat()
    params = {"date": today}
    resp = requests.get(TVMAZE_SCHEDULE_URL, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload, timeout=15)


def main():
    sent_ids = load_sent_ids()
    episodes = get_today_schedule()

    for ep in episodes:
        ep_id = str(ep.get("id"))

        if ep_id in sent_ids:
            continue

        show_name = ep["show"]["name"]
        season = ep.get("season")
        number = ep.get("number")
        name = ep.get("name")
        airtime = ep.get("airtime")
        network = ep["show"].get("network")
        network_name = network["name"] if network else "N/A"

        msg = (
            f"🔥 <b>حلقة جديدة صدرت اليوم!</b>\n\n"
            f"📺 <b>{show_name}</b>\n"
            f"📦 الموسم: <b>{season}</b>\n"
            f"🎬 الحلقة: <b>{number}</b> — {name}\n"
            f"🕒 وقت العرض: {airtime}\n"
            f"📡 القناة: {network_name}"
        )

        send_message(msg)
        sent_ids.add(ep_id)

    save_sent_ids(sent_ids)
    print("تم الفحص ✅")


if __name__ == "__main__":
    main()