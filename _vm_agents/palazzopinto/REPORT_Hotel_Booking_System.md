# REPORT: Hotel Booking Management System - React MERN FullStack
Repository: https://github.com/antoniogatti/Hotel-Booking-Management-System--React-MERN-FullStack
Data analisi: 21 maggio 2026

---

## 1. STRUTTURA DEL PROGETTO

Il progetto e' una applicazione full-stack MERN (MongoDB, Express, React, Node.js) per
la gestione delle prenotazioni di un B&B (Palazzo Pinto, Puglia). E' strutturato in
tre cartelle principali piu' directory di supporto:

### Struttura radice

```
/
├── hotel-booking-backend/     # Server Node.js/Express/TypeScript
├── hotel-booking-frontend/    # Client React/Vite/TypeScript
├── e2e-tests/                 # Test end-to-end con Playwright
├── shared/                    # Tipi e catalogo stanze condivisi
├── data/                      # Immagini hotel e dati di test (JSON)
├── infra/                     # Infrastruttura Azure (Bicep, PowerShell)
├── .github/workflows/         # CI/CD GitHub Actions
└── docs: README.md, VERSION_HISTORY.md, DEPLOYMENT_CONFIGURATION.md, ...
```

### Backend (hotel-booking-backend/)

```
src/
├── index.ts                   # Entry point, configurazione Express, MongoDB
├── swagger.ts                 # Configurazione Swagger/OpenAPI
├── routes/
│   ├── auth.ts                # Autenticazione (Microsoft OAuth, login locale)
│   ├── users.ts               # Gestione utenti
│   ├── hotels.ts              # Ricerca stanze pubbliche
│   ├── my-hotels.ts           # CRUD hotel/stanze (hotel_owner)
│   ├── bookings.ts            # Gestione prenotazioni (admin/hotel_owner)
│   ├── my-bookings.ts         # Prenotazioni dell'utente loggato
│   ├── contact.ts             # Form di contatto
│   ├── health.ts              # Health check
│   ├── business-insights.ts   # Analytics e dashboard
│   ├── booking-com-sync.ts    # Integrazione Booking.com iCal
│   ├── onenote.ts             # Integrazione Microsoft OneNote
│   └── scheduler-monitor.ts   # Monitoraggio scheduler
├── models/                    # Modelli Mongoose
│   ├── user.ts
│   ├── hotel.ts
│   ├── booking.ts
│   ├── booking-day-status.ts
│   ├── external-calendar-event.ts
│   ├── audit-log.ts
│   └── scheduler-run-log.ts
├── middleware/
│   ├── auth.ts                # Verifica JWT (cookie session_id)
│   └── requireRole.ts         # Controllo ruoli
├── lib/
│   ├── booking-com-ical.ts    # Sync iCal Booking.com
│   ├── booking-enrichment-scheduler.ts
│   ├── azure-openai-booking-extractor.ts  # Estrazione AI con Azure OpenAI
│   ├── onenote-booking-sync.ts
│   ├── microsoft-graph-auth.ts
│   ├── contact-mail.ts
│   ├── excel-booking-sync.ts
│   ├── audit-log.ts
│   ├── user-role.ts
│   └── logger.ts
└── scripts/                   # Script di manutenzione e seed DB
```

### Frontend (hotel-booking-frontend/)

```
src/
├── App.tsx                    # Routing principale
├── api-client.ts / lib/api-client.ts  # Client HTTP (fetch/axios)
├── pages/
│   ├── Home.tsx               # Homepage con slideshow
│   ├── Search.tsx             # Ricerca stanze
│   ├── Detail.tsx             # Dettaglio stanza
│   ├── RoomLanding.tsx        # Landing page stanza specifica
│   ├── Booking.tsx            # Flusso prenotazione
│   ├── Checkout.tsx           # Pagamento Stripe
│   ├── BookingDetails.tsx     # Dettaglio prenotazione utente
│   ├── BookingDashboard.tsx   # Dashboard prenotazioni (admin)
│   ├── VacancyDashboard.tsx   # Dashboard disponibilita'
│   ├── AdminPortal.tsx        # Portale admin
│   ├── AdminPortalCheckIns.tsx
│   ├── BookingCheckIn.tsx
│   ├── AnalyticsDashboard.tsx
│   ├── ManageBookings.tsx
│   ├── MyHotels.tsx
│   ├── AddHotel.tsx
│   ├── EditHotel.tsx
│   ├── SignIn.tsx
│   ├── AuthCallback.tsx
│   ├── BookingComSyncAdmin.tsx
│   ├── SchedulerMonitor.tsx
│   ├── ContactUs.tsx
│   ├── ApiDocs.tsx
│   ├── ApiStatus.tsx
│   └── ...
├── components/                # Componenti riutilizzabili
├── forms/                     # Form gestionali (ManageHotelForm, GuestInfoForm)
├── contexts/                  # AppContext, SearchContext
├── hooks/                     # Custom hooks
├── config/                    # Configurazione sito e opzioni hotel
└── layouts/                   # Layout e AuthLayout
```

---

## 2. API ENDPOINTS

Base URL: http://localhost:5000 (sviluppo) / https://palazzopinto-api-xxxx.azurewebsites.net (prod)
Documentazione Swagger disponibile: GET /api-docs

### Autenticazione (/api/auth)

| Metodo | Path                          | Auth      | Descrizione                          |
|--------|-------------------------------|-----------|--------------------------------------|
| GET    | /api/auth/google              | No        | OAuth Google (DISABILITATO, 410)     |
| GET    | /api/auth/microsoft           | No        | Avvia OAuth Microsoft Entra          |
| GET    | /api/auth/callback/google     | No        | Callback OAuth Google (DISABILITATO) |
| GET    | /api/auth/callback/microsoft  | No        | Callback OAuth Microsoft             |
| POST   | /api/auth/login               | No        | Login locale (solo sviluppo)         |
| GET    | /api/auth/validate-token      | JWT       | Valida token sessione corrente       |
| POST   | /api/auth/logout              | No        | Logout (cancella cookie)             |

### Utenti (/api/users)

| Metodo | Path              | Auth | Descrizione                    |
|--------|-------------------|------|--------------------------------|
| GET    | /api/users/me     | JWT  | Profilo utente corrente        |
| POST   | /api/users/register | No | Registrazione nuovo utente     |

### Stanze/Hotel pubblici (/api/rooms)

| Metodo | Path                              | Auth     | Descrizione                        |
|--------|-----------------------------------|----------|------------------------------------|
| GET    | /api/rooms/search                 | No       | Ricerca stanze (query params: destination, checkIn, checkOut, adultCount, childCount, page, maxPrice, facilities, types, sortOption) |
| GET    | /api/rooms/                       | No       | Lista tutte le stanze              |
| GET    | /api/rooms/:id                    | No       | Dettaglio stanza per ID            |
| GET    | /api/rooms/:hotelId/availability  | No       | Disponibilita' stanza per date     |
| POST   | /api/rooms/:hotelId/booking-request | JWT    | Richiesta prenotazione diretta     |
| POST   | /api/rooms/:hotelId/bookings      | JWT      | Crea prenotazione (con Stripe)     |

### Gestione miei hotel (/api/my-hotels)

| Metodo | Path                  | Auth               | Descrizione                  |
|--------|-----------------------|--------------------|------------------------------|
| POST   | /api/my-hotels/       | JWT, hotel_owner   | Crea nuovo hotel/stanza      |
| GET    | /api/my-hotels/       | JWT, hotel_owner   | Lista miei hotel             |
| GET    | /api/my-hotels/:id    | JWT, hotel_owner   | Dettaglio mio hotel          |
| PUT    | /api/my-hotels/:hotelId | JWT, hotel_owner | Aggiorna hotel               |

### Prenotazioni personali (/api/my-bookings)

| Metodo | Path              | Auth | Descrizione                        |
|--------|-------------------|------|------------------------------------|
| GET    | /api/my-bookings/ | JWT  | Lista prenotazioni utente corrente |

### Gestione prenotazioni (/api/bookings)

| Metodo | Path                               | Auth                    | Descrizione                           |
|--------|------------------------------------|-------------------------|---------------------------------------|
| GET    | /api/bookings/rooms                | JWT, hotel_owner/admin  | Lista stanze gestite                  |
| GET    | /api/bookings/calendar/:hotelId    | JWT, hotel_owner/admin  | Calendario prenotazioni stanza        |
| POST   | /api/bookings/calendar/:hotelId/day-status | JWT, hotel_owner/admin | Imposta stato giorno (chiuso/aperto)|
| POST   | /api/bookings/:id/decision         | JWT, hotel_owner/admin  | Approva/rifiuta prenotazione          |
| GET    | /api/bookings/                     | JWT, admin              | Lista tutte le prenotazioni           |
| GET    | /api/bookings/hotel/:hotelId       | JWT, hotel_owner/admin  | Prenotazioni per hotel                |
| GET    | /api/bookings/:id                  | JWT, hotel_owner/admin  | Dettaglio prenotazione                |
| POST   | /api/bookings/:id/sync-excel       | JWT, hotel_owner/admin  | Sync con Excel via Microsoft Graph    |
| POST   | /api/bookings/:id/sync-onenote     | JWT, hotel_owner/admin  | Sync con OneNote                      |
| PUT    | /api/bookings/:id                  | JWT, hotel_owner/admin  | Aggiorna prenotazione                 |
| PATCH  | /api/bookings/:id/status           | JWT, hotel_owner/admin  | Aggiorna stato prenotazione           |
| DELETE | /api/bookings/:id                  | JWT, admin              | Elimina prenotazione                  |
| POST   | /api/bookings/:id/check-in         | JWT, hotel_owner/admin  | Registra check-in                     |
| GET    | /api/bookings/dashboard/summary    | JWT, hotel_owner/admin  | Riepilogo dashboard                   |
| GET    | /api/bookings/dashboard/upcoming-check-ins | JWT, hotel_owner/admin | Prossimi check-in            |
| PATCH  | /api/bookings/:id/close            | JWT, hotel_owner/admin  | Chiudi giorno/stanza                  |
| PATCH  | /api/bookings/:id/open             | JWT, hotel_owner/admin  | Apri giorno/stanza                    |

### Business Insights (/api/business-insights)

| Metodo | Path                            | Auth        | Descrizione               |
|--------|---------------------------------|-------------|---------------------------|
| GET    | /api/business-insights/dashboard | JWT, admin | Dashboard analitica       |
| GET    | /api/business-insights/forecast  | JWT, admin | Forecast prenotazioni     |
| GET    | /api/business-insights/system-stats | JWT, admin | Metriche di sistema    |

### Integrazione Booking.com (/api/integrations/booking-com)

| Metodo | Path                                              | Auth                   | Descrizione                              |
|--------|---------------------------------------------------|------------------------|------------------------------------------|
| GET    | /api/integrations/booking-com/export/:hotelId/:token.ics | No        | Feed iCal pubblico per Booking.com       |
| PUT    | /api/integrations/booking-com/rooms/:hotelId/config | JWT, hotel_owner/admin | Configura sync Booking.com             |
| POST   | /api/integrations/booking-com/rooms/:hotelId/export-token/regenerate | JWT, hotel_owner/admin | Rigenera token export |
| POST   | /api/integrations/booking-com/sync             | JWT, hotel_owner/admin | Avvia sync manuale iCal                  |

### Integrazione OneNote (/api/onenote) - solo admin

| Metodo | Path                               | Auth  | Descrizione                                   |
|--------|------------------------------------|-------|-----------------------------------------------|
| GET    | /api/onenote/notebooks             | JWT, admin | Lista notebook Microsoft OneNote        |
| GET    | /api/onenote/sections              | JWT, admin | Lista sezioni (query: notebookId)       |
| GET    | /api/onenote/pages                 | JWT, admin | Lista pagine (query: sectionId)         |
| GET    | /api/onenote/prenotazioni/bookings | JWT, admin | Prenotazioni dalla sezione "Prenotazioni"|
| GET    | /api/onenote/pages/:pageId         | JWT, admin | Dettaglio pagina OneNote                |
| GET    | /api/onenote/pages/:pageId/content | JWT, admin | Contenuto HTML pagina OneNote           |
| POST   | /api/onenote/ai/extract-booking    | JWT, admin | Estrai dati prenotazione con Azure OpenAI|

### Scheduler Monitor (/api/scheduler-monitor)

| Metodo | Path                                 | Auth        | Descrizione                        |
|--------|--------------------------------------|-------------|------------------------------------|
| GET    | /api/scheduler-monitor/enrichment/runs | JWT, admin | Log esecuzioni scheduler (query: date YYYY-MM-DD)|

### Contatto (/api/contact)

| Metodo | Path          | Auth | Descrizione                              |
|--------|---------------|------|------------------------------------------|
| POST   | /api/contact/ | No   | Invia form contatto (email via MS Graph) |

### Health Check (/api/health)

| Metodo | Path                  | Auth | Descrizione                    |
|--------|-----------------------|------|--------------------------------|
| GET    | /api/health/          | No   | Stato base del servizio        |
| GET    | /api/health/detailed  | No   | Stato dettagliato (DB, memoria)|

### Meccanismo di autenticazione

- JWT firmato (HS256) con scadenza 1 giorno
- Trasmesso via cookie HTTP-only "session_id"
- Ruoli: "user", "hotel_owner", "admin"
- In sviluppo con FORCE_LOCAL_ADMIN_ROLE=true (default), tutti gli utenti diventano admin
- OAuth: solo Microsoft Entra (Google e' disabilitato con 410)

---

## 3. TECNOLOGIE USATE

### Backend
- Runtime: Node.js 20+
- Framework: Express.js 4.18
- Linguaggio: TypeScript 5.2
- Database: MongoDB con Mongoose 8
- Autenticazione: JWT (jsonwebtoken), bcryptjs, OAuth Microsoft Entra
- Validazione: express-validator
- Pagamenti: Stripe
- Sicurezza: helmet, cors, express-rate-limit
- Logging: morgan (JSON), logger personalizzato
- Compressione: compression
- API docs: swagger-ui-express, swagger-jsdoc
- Email: Microsoft Graph API (sendMail)
- Calendario: node-ical (sync Booking.com iCal)
- AI: Azure OpenAI (GPT-4/mini) per estrazione dati prenotazione
- Integrazione Microsoft: Microsoft Graph (OneNote, Excel, Outlook)
- Dev: nodemon, ts-node, mongodb-memory-server
- CI/CD: GitHub Actions, Docker, Azure Web Apps

### Frontend
- Framework: React 18
- Build tool: Vite 7
- Linguaggio: TypeScript 5
- Routing: react-router-dom 6
- State/fetching: react-query 3
- Form: react-hook-form 7
- UI components: Radix UI (dialog, dropdown, toast, label, separator)
- Stili: Tailwind CSS 3
- Icone: lucide-react, react-icons
- Grafici: recharts
- Galleria immagini: @fancyapps/ui (Fancybox)
- Calendario: react-datepicker
- Cookie consent: vanilla-cookieconsent
- HTTP client: axios
- Cookie: js-cookie

### Infrastruttura
- Cloud: Microsoft Azure (Azure Web Apps, Azure Container Registry)
- IaC: Bicep + PowerShell
- Deploy: GitHub Actions CI/CD
- E2E Tests: Playwright

---

## 4. AVVIO IN LOCALE

### Prerequisiti
- Node.js 20+
- npm
- MongoDB locale oppure MongoDB Atlas (o usare la modalita' in-memory)

### Backend

```bash
cd hotel-booking-backend

# Copia il file di configurazione
cp .env.development.example .env.development

# Installa dipendenze
npm install

# Avvio in modalita' sviluppo (con .env.development)
npm run dev:local

# OPPURE con MongoDB in-memory (nessun DB esterno richiesto):
# Imposta USE_IN_MEMORY_MONGO=true nel .env e lancia:
npm run dev
```
Il backend parte sulla porta 5000. Swagger disponibile su http://localhost:5000/api-docs

### Frontend

```bash
cd hotel-booking-frontend

# Installa dipendenze
npm install

# Avvio sviluppo
npm run dev
# Oppure: npm run dev -- --port 5174
```
Il frontend parte sulla porta 5174. URL: http://localhost:5174

### Ordine di avvio consigliato
1. Avviare prima il backend (porta 5000)
2. Avviare poi il frontend (porta 5174)

### E2E Tests (opzionale)

```bash
cd e2e-tests
npm install
npx playwright install
npx playwright test
```

---

## 5. VARIABILI D'AMBIENTE (.env)

### Backend - Obbligatorie

```ini
# Server
PORT=5000
NODE_ENV=development

# Database MongoDB
MONGODB_CONNECTION_STRING=mongodb+srv://user:pass@cluster.mongodb.net/dbname

# JWT (generare con: openssl rand -base64 512)
JWT_SECRET_KEY=your_strong_jwt_secret

# CORS - URL del frontend
FRONTEND_URL=http://localhost:5174
```

### Backend - OAuth Microsoft (per login e funzioni Graph)

```ini
MS_ENTRA_CLIENT_ID=your_microsoft_app_client_id
MS_ENTRA_CLIENT_SECRET=your_microsoft_app_client_secret
MS_ENTRA_TENANT_ID=common    # oppure il tenant specifico
BACKEND_URL=http://localhost:5000  # Necessario per il callback OAuth
```

### Backend - Pagamenti Stripe

```ini
STRIPE_API_KEY=sk_test_...   # Test key per sviluppo
```

### Backend - Email via Microsoft Graph

```ini
CONTACT_MAIL_SENDER=info@palazzopintobnb.com
CONTACT_MAIL_INBOX=info@palazzopintobnb.com
CONTACT_MAIL_SUBJECT_PREFIX=[PalazzoPinto][ContactForm]
CONTACT_MAIL_CONFIRMATION_SUBJECT=Message Sent - Confirmation
```

### Backend - Azure OpenAI (per estrazione dati da OneNote)

```ini
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### Backend - Opzioni sviluppo

```ini
USE_IN_MEMORY_MONGO=true         # Usa MongoDB in-memory (no DB esterno)
ENABLE_LOCAL_PASSWORD_LOGIN=true # Abilita login con password locale
FORCE_LOCAL_ADMIN_ROLE=true      # Forza ruolo admin per tutti gli utenti locali
ENABLE_SWAGGER=true              # Abilita Swagger anche in produzione
```

### Frontend

Non esiste un file .env.example per il frontend nel repository.
La configurazione avviene tramite vite.config.ts.
L'URL del backend e' configurato nell'api-client e punta a http://localhost:5000
in sviluppo e alla variabile VITE_API_BASE_URL se definita.

### File di configurazione aggiuntivi backend

Il repository include tre template di .env:
- hotel-booking-backend/.env.example              (template generale)
- hotel-booking-backend/.env.development.example  (sviluppo locale)
- hotel-booking-backend/.env.production.example   (produzione)

---

## NOTE AGGIUNTIVE

- Il progetto e' operativo come applicazione reale per "Palazzo Pinto B&B" in Puglia
- Include integrazione completa con Booking.com tramite feed iCal bidirezionale
- Supporta sincronizzazione con Microsoft OneNote per importare prenotazioni manuali
- Supporta sincronizzazione con Microsoft Excel via Graph API
- Include uno scheduler automatico per arricchimento dati prenotazioni
- Il sistema di ruoli prevede 3 livelli: user, hotel_owner, admin
- In produzione il deploy avviene su Azure Web Apps via GitHub Actions CI/CD
- La documentazione Swagger e' disponibile su /api-docs (abilitata di default in sviluppo)
- Include audit log completo di tutte le operazioni sensibili

