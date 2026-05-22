#!/usr/bin/env python3
"""
sofia_auth.py — Autenticazione service account Sofia Hermes su api.palazzopintobnb.com

Ottiene un JWT dal backend tramite /api/auth/service e lo cacha in
~/.hermes/profiles/palazzopinto/.sofia_jwt

Il token e' valido 12 ore. Lo script lo rinnova automaticamente se scaduto
o in scadenza entro 30 minuti.

Uso:
    token = get_token()   # restituisce JWT valido, rinnova se necessario
    headers = auth_headers()  # restituisce {"Authorization": "Bearer <token>"}
"""

import json
import os
import time
import urllib.request
import urllib.parse
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────
BACKEND_URL = "https://api.palazzopintobnb.com"
SECRETS_DIR = Path.home() / ".hermes/profiles/palazzopinto"
JWT_CACHE   = SECRETS_DIR / ".sofia_jwt"
SECRET_FILE = SECRETS_DIR / ".sofia_secret"
CREDS_FILE  = SECRETS_DIR / ".sofia_creds"   # JSON: {client_id, client_secret}

# SOFIA_CLIENT_ID e SOFIA_CLIENT_SECRET sono le env var sul backend Azure
# Lato Sofia usiamo lo stesso app_id + secret dell'app Entra
SOFIA_APP_ID = "747f27c4-cd5e-4f70-a7b7-734ca5c0f023"
RENEW_BEFORE_EXPIRY_SECS = 30 * 60  # rinnova se scade entro 30 min
# ──────────────────────────────────────────────────────────────────────────────


def _load_secret() -> str:
    """Legge il client_secret dal file locale."""
    if not SECRET_FILE.exists():
        raise FileNotFoundError(f"Secret non trovato: {SECRET_FILE}")
    return SECRET_FILE.read_text().strip()


def _load_cached_jwt() -> dict | None:
    """Carica il JWT dalla cache. Ritorna None se mancante o malformato."""
    if not JWT_CACHE.exists():
        return None
    try:
        return json.loads(JWT_CACHE.read_text())
    except Exception:
        return None


def _save_jwt(token: str, expires_at: float):
    """Salva il JWT in cache."""
    JWT_CACHE.write_text(json.dumps({"token": token, "expires_at": expires_at}))
    JWT_CACHE.chmod(0o600)


def _fetch_jwt() -> tuple[str, float]:
    """Chiama /api/auth/service e restituisce (token, expires_at_timestamp)."""
    secret = _load_secret()
    payload = json.dumps({
        "client_id": SOFIA_APP_ID,
        "client_secret": secret,
    }).encode()

    req = urllib.request.Request(
        f"{BACKEND_URL}/api/auth/service",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())

    token = data["token"]
    expires_in = data.get("expiresIn", 43200)
    expires_at = time.time() + expires_in
    return token, expires_at


def get_token() -> str:
    """
    Ritorna un JWT valido per le API di Palazzo Pinto.
    Rinnova automaticamente se scaduto o in scadenza entro 30 min.
    """
    cached = _load_cached_jwt()
    if cached:
        remaining = cached["expires_at"] - time.time()
        if remaining > RENEW_BEFORE_EXPIRY_SECS:
            return cached["token"]

    token, expires_at = _fetch_jwt()
    _save_jwt(token, expires_at)
    return token


def auth_headers() -> dict:
    """Ritorna gli header HTTP con il Bearer token."""
    return {"Authorization": f"Bearer {get_token()}"}


if __name__ == "__main__":
    import sys
    try:
        token = get_token()
        print(f"OK — token valido, lunghezza={len(token)}")
        print(f"Primi 40 chars: {token[:40]}...")
    except Exception as e:
        print(f"ERRORE: {e}", file=sys.stderr)
        sys.exit(1)
