#!/usr/bin/env python3
"""
Azure Cost Dashboard updater.
Fetches current month costs via Cost Management API, generates HTML dashboard,
uploads to Azure Blob Storage static website.
"""
import os
import subprocess, json, calendar, urllib.error
from datetime import date, datetime

SUBSCRIPTION = "927d8895-21e1-452d-a35a-e04253f2c80e"
STORAGE_ACCOUNT = "antdevstorage"
CONTAINER = "$web"
BLOB_PATH = "azure-costs/index.html"
BUDGET = 150.0
LOCAL_HTML_PATH = "/home/azureuser/repo/antoniogatti/Alfred-Hermes/_vm_tools/AzureCostDashboard/index.html"
PAGE_URL = "http://4.232.81.58:8080"
TELEGRAM_BOT_TOKEN = "8762402366:AAERRdcywRFxd6WkNnwGFzdncebn13Xzu6E"
TELEGRAM_CHAT_IDS = [2006873328, 8930593706]  # Ant (@Anttt00), Lucia (Lucifera84)

def get_token():
    cmd = [
        "az", "account", "get-access-token",
        "--resource", "https://management.azure.com",
        "--query", "accessToken", "-o", "tsv"
    ]

    candidates = [None, "/home/azureuser/.azure"]
    errors = []

    for azure_config_dir in candidates:
        env = os.environ.copy()
        if azure_config_dir:
            if not os.path.isdir(azure_config_dir):
                continue
            env["AZURE_CONFIG_DIR"] = azure_config_dir

        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
        token = r.stdout.strip()
        if r.returncode == 0 and token:
            return token

        source = azure_config_dir or env.get("AZURE_CONFIG_DIR", "default")
        stderr = (r.stderr or "").strip() or "unknown error"
        errors.append(f"AZURE_CONFIG_DIR={source}: {stderr}")

    details = " | ".join(errors) if errors else "no Azure CLI profile available"
    raise RuntimeError(
        "Unable to obtain Azure access token. Run 'az login' on a profile with access "
        f"to subscription {SUBSCRIPTION}. Details: {details}"
    )

def fetch_costs(token):
    import urllib.request, time
    url = f"https://management.azure.com/subscriptions/{SUBSCRIPTION}/providers/Microsoft.CostManagement/query?api-version=2023-11-01"
    payload = json.dumps({
        "type": "ActualCost",
        "timeframe": "MonthToDate",
        "dataset": {
            "granularity": "None",
            "aggregation": {"totalCost": {"name": "PreTaxCost", "function": "Sum"}},
            "grouping": [
                {"type": "Dimension", "name": "ResourceGroupName"},
                {"type": "Dimension", "name": "ServiceName"}
            ]
        }
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 30 * (attempt + 1)
                print(f"429 Too Many Requests — attendo {wait}s (tentativo {attempt+1}/5)...")
                time.sleep(wait)
            else:
                raise
    raise Exception("Azure Cost API: troppi tentativi falliti (429)")

def generate_html(rows):
    today = date.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_elapsed = today.day
    days_remaining = days_in_month - days_elapsed

    total_cost = sum(r[0] for r in rows)
    pct = (total_cost / BUDGET) * 100
    projected = (total_cost / days_elapsed) * days_in_month if days_elapsed > 0 else 0

    sorted_rows = sorted(rows, key=lambda x: x[0], reverse=True)

    table_rows_html = ""
    for r in sorted_rows:
        cost, rg, service = r[0], r[1], r[2]
        if cost == 0:
            color = "#6b7280"
        elif cost > 10:
            color = "#ef4444"
        elif cost > 2:
            color = "#f59e0b"
        else:
            color = "#10b981"
        bar_w = min(100, (cost / total_cost * 100)) if total_cost > 0 else 0
        table_rows_html += f"""
        <tr>
          <td>{rg}</td>
          <td>{service}</td>
          <td style="color:{color};font-weight:600">${cost:.4f}</td>
          <td>
            <div style="background:#1f2937;border-radius:4px;height:8px;width:120px">
              <div style="background:{color};height:8px;border-radius:4px;width:{bar_w:.1f}%"></div>
            </div>
          </td>
        </tr>"""

    suggestions = []
    app_svc = next((r for r in rows if r[2] == "Azure App Service" and r[1] == "palazzopintobnb"), None)
    if app_svc and app_svc[0] > 30:
        suggestions.append(("palazzopintobnb / Azure App Service", f"${app_svc[0]:.2f}",
            "Piano App Service molto costoso. Valuta downgrade a B1/B2 o migrazione a Container Apps se il traffico e' basso."))
    vnet_cost = sum(r[0] for r in rows if r[2] == "Virtual Network")
    if vnet_cost > 2:
        suggestions.append(("Virtual Network (totale)", f"${vnet_cost:.2f}",
            "IP pubblici statici costano anche quando non usati (~$3.65/mese cad.). Controlla se ci sono IP non associati a risorse attive."))
    sql = next((r for r in rows if r[2] == "SQL Database"), None)
    if sql and sql[0] > 1:
        suggestions.append(("otto-telemetry / SQL Database", f"${sql[0]:.2f}",
            "Valuta serverless tier o pausa automatica se il DB non e' usato 24/7."))
    if projected > BUDGET:
        suggestions.append(("Proiezione fine mese", f"${projected:.2f}",
            f"Con il ritmo attuale supererai il budget di ${projected - BUDGET:.2f}. Considera di spegnere risorse non critiche."))

    suggestions_html = ""
    for title, cost_str, msg in suggestions:
        suggestions_html += f"""
      <div class="suggestion">
        <div class="sug-header">
          <span class="sug-title">{title}</span>
          <span class="sug-cost">{cost_str}</span>
        </div>
        <p>{msg}</p>
      </div>"""

    if pct >= 100:
        status_color, status_label, bar_color = "#ef4444", "OVER BUDGET", "#ef4444"
    elif pct >= 80:
        status_color, status_label, bar_color = "#f59e0b", "ATTENZIONE", "#f59e0b"
    else:
        status_color, status_label, bar_color = "#10b981", "OK", "#10b981"

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Azure Cost Monitor — Ant Enterprise</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #0f1117; color: #e5e7eb; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; min-height: 100vh; padding: 24px 16px; }}
    .container {{ max-width: 900px; margin: 0 auto; }}
    h1 {{ font-size: 1.4rem; font-weight: 700; color: #f9fafb; margin-bottom: 4px; }}
    .subtitle {{ font-size: 0.85rem; color: #6b7280; margin-bottom: 24px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 28px; }}
    .card {{ background: #1a1d27; border: 1px solid #2d3148; border-radius: 12px; padding: 18px; }}
    .card-label {{ font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }}
    .card-value {{ font-size: 1.6rem; font-weight: 700; }}
    .card-sub {{ font-size: 0.8rem; color: #9ca3af; margin-top: 4px; }}
    .section {{ background: #1a1d27; border: 1px solid #2d3148; border-radius: 12px; padding: 20px; margin-bottom: 24px; }}
    .section-title {{ font-size: 0.9rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 16px; }}
    .budget-bar-bg {{ background: #2d3148; border-radius: 8px; height: 14px; margin-bottom: 10px; overflow: hidden; }}
    .budget-bar-fill {{ height: 14px; border-radius: 8px; background: {bar_color}; width: {min(pct,100):.1f}%; }}
    .budget-info {{ display: flex; justify-content: space-between; font-size: 0.82rem; color: #9ca3af; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
    th {{ text-align: left; color: #6b7280; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; padding: 0 12px 10px 0; border-bottom: 1px solid #2d3148; }}
    td {{ padding: 10px 12px 10px 0; border-bottom: 1px solid #1f2937; vertical-align: middle; }}
    tr:last-child td {{ border-bottom: none; }}
    .suggestion {{ background: #111827; border-left: 3px solid #3b82f6; border-radius: 6px; padding: 14px 16px; margin-bottom: 12px; }}
    .sug-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
    .sug-title {{ font-size: 0.88rem; font-weight: 600; color: #e5e7eb; }}
    .sug-cost {{ font-size: 0.85rem; font-weight: 700; color: #f59e0b; }}
    .suggestion p {{ font-size: 0.82rem; color: #9ca3af; line-height: 1.5; }}
    .status-badge {{ display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; background: {status_color}22; color: {status_color}; border: 1px solid {status_color}55; }}
    .updated {{ font-size: 0.75rem; color: #4b5563; margin-top: 24px; text-align: center; }}
  </style>
</head>
<body>
<div class="container">
  <h1>☁️ Azure Cost Monitor <span class="status-badge">{status_label}</span></h1>
  <p class="subtitle">Subscription: Ant Enterprise &nbsp;·&nbsp; {today.strftime('%d %B %Y')}</p>

  <div class="cards">
    <div class="card">
      <div class="card-label">Speso questo mese</div>
      <div class="card-value" style="color:{status_color}">${total_cost:.2f}</div>
      <div class="card-sub">Budget: $50.00</div>
    </div>
    <div class="card">
      <div class="card-label">% Budget usato</div>
      <div class="card-value" style="color:{status_color}">{pct:.0f}%</div>
      <div class="card-sub">{days_elapsed} giorni su {days_in_month}</div>
    </div>
    <div class="card">
      <div class="card-label">Proiezione fine mese</div>
      <div class="card-value" style="color:{'#ef4444' if projected > BUDGET else '#10b981'}">${projected:.2f}</div>
      <div class="card-sub">{days_remaining} giorni rimanenti</div>
    </div>
    <div class="card">
      <div class="card-label">Sforamento previsto</div>
      <div class="card-value" style="color:#ef4444">${max(0, projected - BUDGET):.2f}</div>
      <div class="card-sub">vs budget $50.00</div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Budget mensile — $50.00</div>
    <div class="budget-bar-bg"><div class="budget-bar-fill"></div></div>
    <div class="budget-info">
      <span>${total_cost:.2f} spesi ({pct:.0f}%)</span>
      <span>${max(0, BUDGET - total_cost):.2f} rimanenti</span>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Consumi per risorsa</div>
    <table>
      <thead><tr><th>Resource Group</th><th>Servizio</th><th>Costo (USD)</th><th>Peso</th></tr></thead>
      <tbody>{table_rows_html}</tbody>
    </table>
  </div>

  <div class="section">
    <div class="section-title">💡 Suggerimenti</div>
    {suggestions_html}
  </div>

  <p class="updated">Ultimo aggiornamento: {datetime.now().strftime('%d/%m/%Y %H:%M')} UTC</p>
</div>
</body>
</html>"""

def upload_html(html_content):
    with open(LOCAL_HTML_PATH, 'w') as f:
        f.write(html_content)
    return True

def build_telegram_summary(rows, total_cost, pct, projected):
    today = date.today()
    import calendar
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_elapsed = today.day
    days_remaining = days_in_month - days_elapsed

    if pct >= 100:
        icon = "🔴"
        status = "OVER BUDGET"
    elif pct >= 80:
        icon = "🟡"
        status = "Attenzione"
    else:
        icon = "🟢"
        status = "OK"

    top3 = sorted(rows, key=lambda x: x[0], reverse=True)[:3]
    top3_lines = "\n".join(f"  • {r[1]} / {r[2]}: ${r[0]:.2f}" for r in top3)

    over = projected - BUDGET
    proj_line = f"📈 Proiezione: ${projected:.2f} (+${over:.2f} sforamento)" if over > 0 else f"📈 Proiezione: ${projected:.2f} (entro budget)"

    daily_avg = total_cost / days_elapsed if days_elapsed > 0 else 0
    days_to_budget = int((BUDGET - total_cost) / daily_avg) if daily_avg > 0 and total_cost < BUDGET else 0
    budget_remaining = BUDGET - total_cost
    overage = projected - BUDGET

    kpi_lines = f"""📊 *KPI del mese*
├ Speso:         *${total_cost:.2f}* / ${BUDGET:.0f}
├ % Budget:      *{pct:.0f}%*
├ Rimanente:     *${budget_remaining:.2f}*
├ Media/giorno:  *${daily_avg:.2f}*
├ Proiezione:    *${projected:.2f}*
└ Sforamento:    *{"$"+f"{overage:.2f}" if overage > 0 else "nessuno ✅"}*"""

    alert = ""
    if overage > 0:
        alert = f"\n⚠️ *Attenzione:* al ritmo attuale sfori di *${overage:.2f}*. Intervieni sulle risorse in alto."
    elif pct >= 80:
        alert = f"\n⚠️ *Attenzione:* hai usato l'80% del budget a {days_elapsed} giorni dall'inizio mese."

    msg = f"""{icon} *Azure Cost Monitor — {today.strftime('%d/%m/%Y')}* {status}
📅 Giorno {days_elapsed} di {days_in_month} ({days_remaining} rimanenti)

{kpi_lines}

🔝 Top 3 spese:
{top3_lines}{alert}

🔗 [Dashboard completa]({PAGE_URL})"""
    return msg

def send_telegram(msg):
    import urllib.request, urllib.parse
    results = []
    for chat_id in TELEGRAM_CHAT_IDS:
        payload = json.dumps({
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
                ok = result.get("ok", False)
                print(f"Telegram chat_id {chat_id}: {'OK' if ok else 'FAILED'}")
                results.append(ok)
        except Exception as e:
            print(f"Telegram chat_id {chat_id}: ERRORE — {e}")
            results.append(False)
    return all(results)

if __name__ == "__main__":
    print("Fetching Azure token...")
    token = get_token()
    print("Fetching costs...")
    data = fetch_costs(token)
    rows = data['properties']['rows']
    total_cost = sum(r[0] for r in rows)
    pct = (total_cost / BUDGET) * 100
    today = date.today()
    import calendar
    days_elapsed = today.day
    projected = (total_cost / days_elapsed) * calendar.monthrange(today.year, today.month)[1]
    print(f"Total: ${total_cost:.2f} ({pct:.0f}% of budget)")
    print("Generating HTML...")
    html = generate_html(rows)
    print("Uploading to Blob Storage...")
    ok = upload_html(html)
    print("Upload OK" if ok else "Upload FAILED")
    msg = build_telegram_summary(rows, total_cost, pct, projected)
    print("Sending Telegram notification...")
    ok = send_telegram(msg)
    print("Telegram OK" if ok else "Telegram FAILED")
