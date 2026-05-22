#!/usr/bin/env python3
"""
daily_arrivals.py
Invia su Telegram gli arrivi del giorno corrente.
"""
import sys, json, urllib.request, urllib.parse, os
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sofia_auth import auth_headers

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or (
    Path.home() / ".hermes/profiles/palazzopinto/.telegram_token"
).read_text().strip() if (Path.home() / ".hermes/profiles/palazzopinto/.telegram_token").exists() else None

TELEGRAM_CHAT_ID = 2006873328

# Leggo token dal config yaml se non trovato altrove
if not TELEGRAM_BOT_TOKEN:
    import yaml
    cfg = Path.home() / ".hermes/profiles/palazzopinto/config.yaml"
    data = yaml.safe_load(cfg.read_text())
    TELEGRAM_BOT_TOKEN = data.get("telegram", {}).get("bot_token", "")

ROOMS = {
    "69d91a44ec7b7de2eba0c3af": "Fuocorosa",
    "69d91a43ec7b7de2eba0c3ac": "Aleatico",
    "69d91a43ec7b7de2eba0c396": "Malvasia",
    "69d91a43ec7b7de2eba0c391": "Verdeca",
}


def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def fetch_arrivals_for_room(room_id: str, today_str: str, headers: dict) -> list:
    """Fetch arrivals for a room via /calendar/:hotelId — includes Booking.com imported events."""
    month = today_str[:7]  # YYYY-MM
    url = f"https://api.palazzopintobnb.com/api/bookings/calendar/{room_id}?month={month}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())

    arrivals = []
    for b in data.get("bookings", []):
        check_in = b.get("checkIn", "")[:10]
        status = b.get("status", "")
        # Include confirmed/pending/arrived/Imported that check-in today
        if check_in == today_str and status in ("confirmed", "pending", "arrived", "Imported", "imported"):
            b["_roomId"] = room_id
            arrivals.append(b)
    return arrivals


def main():
    today = datetime.now(timezone.utc).date()
    today_str = today.isoformat()

    headers = auth_headers()

    # Fetch arrivals from all rooms via calendar endpoint (captures Booking.com imported events)
    all_arrivals = []
    for room_id in ROOMS:
        try:
            all_arrivals.extend(fetch_arrivals_for_room(room_id, today_str, headers))
        except Exception as e:
            pass  # skip room on error, don't crash the whole script

    date_fmt = today.strftime("%-d %B %Y")

    if not all_arrivals:
        msg = f"🏨 <b>Arrivi del {date_fmt}</b>\n\nNessun arrivo previsto oggi."
    else:
        lines = [f"🏨 <b>Arrivi del {date_fmt}</b> — {len(all_arrivals)} ospite/i\n"]
        for b in all_arrivals:
            room = ROOMS.get(b.get("_roomId", ""), b.get("_roomId", "?"))
            name = f"{b.get('firstName', '')} {b.get('lastName', '')}".strip() or "N/D"
            checkout = b.get("checkOut", "")[:10]
            adults = b.get("adultCount", 0)
            children = b.get("childCount", 0)
            arrival_time = b.get("arrivalTime", "")
            status = b.get("status", "")
            res_num = b.get("reservationNumber", "")
            pax = f"{adults} adulti" + (f" + {children} bambini" if children else "")
            is_booking_com = "@booking.com" in res_num or b.get("isImported", False)
            source = "Booking.com" if is_booking_com else "diretto"

            line = (
                f"👤 <b>{name}</b>\n"
                f"   🛏 {room}  |  check-out: {checkout}\n"
                f"   👥 {pax}  |  arrivo: {arrival_time or 'n/d'}\n"
                f"   📋 {res_num or 'n/d'} ({source}, {status})"
            )
            lines.append(line)

        msg = "\n\n".join(lines)

    send_telegram(msg)
    print(msg)


if __name__ == "__main__":
    main()
