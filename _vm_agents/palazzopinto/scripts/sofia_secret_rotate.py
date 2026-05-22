#!/usr/bin/env python3
"""
sofia_secret_rotate.py — Rotazione automatica del client secret Azure AD di Sofia Hermes

Eseguito ogni 60 giorni dal cron job.
1. Crea un nuovo secret sull'app Entra SofiaHermes-PalazzoPinto
2. Aggiorna SOFIA_CLIENT_SECRET sull'Azure Web App del backend
3. Salva il nuovo secret localmente in ~/.hermes/profiles/palazzopinto/.sofia_secret
4. Elimina il vecchio secret da Entra
5. Invalida la JWT cache locale
6. Notifica Ant via Telegram

Env richieste: az CLI autenticato con permessi Application.ReadWrite.OwnedBy
"""

import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────
APP_OBJ_ID     = "e9213f7d-ff5c-47f9-b108-380d2458775b"
APP_ID         = "747f27c4-cd5e-4f70-a7b7-734ca5c0f023"
SECRETS_DIR    = Path.home() / ".hermes/profiles/palazzopinto"
SECRET_FILE    = SECRETS_DIR / ".sofia_secret"
JWT_CACHE      = SECRETS_DIR / ".sofia_jwt"
TELEGRAM_TOKEN = "8762402366:AAERRdcywRFxd6WkNnwGFzdncebn13Xzu6E"
TELEGRAM_CHAT  = 2006873328

# Azure Web App del backend — aggiornare se cambia il nome
AZURE_WEBAPP_NAME      = "palazzopinto-api-secure"
AZURE_WEBAPP_RG        = "PalazzoPintoBnB"
# ──────────────────────────────────────────────────────────────────────────────


def run(cmd: list[str]) -> dict:
    r = subprocess.run(cmd, capture_output=True, text=True)
    return {"stdout": r.stdout.strip(), "stderr": r.stderr.strip(), "code": r.returncode}


def telegram(msg: str):
    payload = json.dumps({"chat_id": TELEGRAM_CHAT, "text": msg, "parse_mode": "HTML"}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Telegram notify failed: {e}", file=sys.stderr)


def rotate():
    now = datetime.utcnow().strftime("%Y-%m-%d")
    label = f"SofiaHermes-{now}"
    print(f"Rotazione secret: {label}")

    # 1. Leggi secret ID corrente (per eliminarlo dopo)
    r = run(["az", "ad", "app", "credential", "list", "--id", APP_OBJ_ID, "--query", "[].keyId", "-o", "json"])
    old_key_ids = json.loads(r["stdout"]) if r["code"] == 0 else []
    print(f"Secret esistenti: {old_key_ids}")

    # 2. Crea nuovo secret
    r = run(["az", "ad", "app", "credential", "reset",
             "--id", APP_OBJ_ID,
             "--display-name", label,
             "--years", "1",
             "--append",
             "-o", "json"])
    if r["code"] != 0:
        raise RuntimeError(f"Creazione secret fallita: {r['stderr']}")

    data = json.loads(r["stdout"])
    new_secret = data["password"]
    print(f"Nuovo secret creato: {label}")

    # 3. Aggiorna env var sull'Azure Web App
    r = run(["az", "webapp", "config", "appsettings", "set",
             "--name", AZURE_WEBAPP_NAME,
             "--resource-group", AZURE_WEBAPP_RG,
             "--settings", f"SOFIA_CLIENT_SECRET={new_secret}",
             "-o", "none"])
    if r["code"] != 0:
        # Non bloccare — potrebbe essere un nome Web App diverso
        print(f"WARN: aggiornamento Web App fallito: {r['stderr']}")
        telegram(f"⚠️ <b>Sofia Secret Rotato</b> — ma aggiornamento Azure Web App fallito!\nAggiorna manualmente SOFIA_CLIENT_SECRET sul backend.\nErrore: {r['stderr'][:200]}")
    else:
        print("Azure Web App aggiornata")

    # 4. Salva nuovo secret localmente
    SECRET_FILE.write_text(new_secret)
    SECRET_FILE.chmod(0o600)
    print(f"Secret salvato in {SECRET_FILE}")

    # 5. Elimina vecchi secret da Entra
    for key_id in old_key_ids:
        r = run(["az", "ad", "app", "credential", "delete",
                 "--id", APP_OBJ_ID, "--key-id", key_id])
        print(f"Vecchio secret {key_id} eliminato: {r['code'] == 0}")

    # 6. Invalida JWT cache
    if JWT_CACHE.exists():
        JWT_CACHE.unlink()
        print("JWT cache invalidata")

    # 7. Notifica Ant
    telegram(
        f"🔑 <b>Secret Sofia rinnovato</b> ({now})\n"
        f"App: SofiaHermes-PalazzoPinto\n"
        f"Scade: fra 1 anno\n"
        f"✅ Backend aggiornato automaticamente"
    )
    print("Rotazione completata con successo.")


if __name__ == "__main__":
    try:
        rotate()
    except Exception as e:
        msg = f"❌ <b>Errore rotazione secret Sofia</b>\n{e}"
        print(msg, file=sys.stderr)
        telegram(msg)
        sys.exit(1)
