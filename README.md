# AI Booking Assistant

A conversational booking assistant that lets customers chat their way through
scheduling an appointment (or table, class, room, ticket — any service),
while also answering questions from PDF documents you upload (menus,
policies, brochures). Includes a mandatory admin dashboard to review, search,
and export bookings.

Built as a **FastAPI backend + a plain HTML/CSS/JS frontend** — no Streamlit —
so it can be deployed to any container-friendly host (Render, Railway,
Fly.io, etc).

```
"I'd like to book a haircut for Saturday at 3pm"
   -> assistant collects name / email / phone / date / time
   -> summarizes and asks you to confirm
   -> saves to the database and emails a confirmation
   -> "You're all set! Your booking is confirmed with ID #14."
```

---

## 1. Architecture

```
┌─────────────────────┐        HTTP/JSON        ┌──────────────────────────┐
│   Frontend (static)  │  ───────────────────▶  │      FastAPI Backend     │
│  index.html (chat)   │  ◀───────────────────  │        app/main.py       │
│  admin.html (dash)   │                        └───────────┬──────────────┘
└──────────────────────┘                                    │
                                                              ▼
                        ┌──────────────────────────────────────────────────┐
                        │                 chat_logic.py                    │
                        │   session memory (last N messages) + routing     │
                        └───────┬───────────────────────────┬──────────────┘
                                │                            │
                     booking intent?                   general / doc question
                                │                            │
                                ▼                            ▼
                    ┌────────────────────┐        ┌───────────────────────┐
                    │  booking_flow.py   │        │   rag_pipeline.py     │
                    │  slot filling,     │        │  PDF → chunks → TF-IDF│
                    │  validation,       │        │  vector store →       │
                    │  confirmation      │        │  retrieve → blend LLM │
                    └─────────┬──────────┘        └───────────┬───────────┘
                              │                                │
                              ▼                                ▼
                    ┌───────────────────┐            ┌──────────────────┐
                    │     tools.py      │            │      llm.py      │
                    │ • booking persist │            │ Groq / OpenAI /  │
                    │ • email tool      │            │ Gemini (LangChain)│
                    └─────────┬─────────┘            └──────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   database.py /   │
                    │    models.py      │
                    │ SQLite / Postgres │
                    └───────────────────┘
```

### Booking flow

1. Detect booking intent (keywords, or an already-active booking session).
2. Extract any details already given (LLM JSON extraction + regex for
   email/phone) and merge into the in-progress draft.
3. Ask only for whatever's still missing — one thing at a time.
4. Once all fields are present, summarize and ask for explicit confirmation.
5. On "yes": validate, save to the database, send a confirmation email,
   and reply with the booking ID. On "no": let the user correct a field.

### RAG pipeline

PDFs are extracted with `pypdf`, split into ~800-character overlapping
chunks, and indexed in an in-memory **TF-IDF vector store** (scikit-learn).
This is a deliberate choice over a heavy embeddings model: it keeps the
container small enough to run on a free-tier host with no GPU and no
embedding API cost, while still satisfying "chunk → embed → store → retrieve
→ blend with LLM output." If you need semantic (not just keyword-level)
retrieval, swap `VectorStore` in `app/rag_pipeline.py` for FAISS +
sentence-transformers or an OpenAI/Gemini embeddings call.

### Tools

| Tool | Input | Output |
|---|---|---|
| RAG Tool | a question | retrieved chunks blended into an LLM answer |
| Booking Persistence Tool | structured booking payload | `{success, booking_id}` |
| Email Tool | to / subject / body | `{success, message}` |

---

## 2. Project structure

```
app/
  main.py            FastAPI app, all routes, serves the frontend
  config.py           environment configuration
  database.py          SQLAlchemy engine/session
  models.py            Customer / Booking ORM models
  schemas.py            Pydantic request/response models
  llm.py                 multi-provider LLM wrapper (Groq/OpenAI/Gemini)
  rag_pipeline.py         PDF ingestion + TF-IDF vector store + RAG tool
  chat_logic.py            session memory + intent routing
  booking_flow.py           slot filling, validation, confirmation
  tools.py                  booking persistence tool, email tool
  email_utils.py             SMTP sending
frontend/
  index.html            chat UI + PDF upload
  admin.html             admin dashboard
  static/css/style.css
  static/js/chat.js
  static/js/admin.js
data/uploads/           uploaded PDFs land here (gitignored)
Dockerfile
render.yaml            Render.com blueprint
Procfile                 Railway / Heroku-style entrypoint
fly.toml                   Fly.io config
requirements.txt
.env.example
```

---

## 3. Local setup

**Requirements:** Python 3.11+

```bash
git clone <your-repo-url>
cd <repo>
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: add at least one LLM API key (Groq/OpenAI/Gemini), an ADMIN_KEY,
# and SMTP credentials if you want real confirmation emails

uvicorn app.main:app --reload
```

Then open:
- **Chat:** http://localhost:8000/
- **Admin dashboard:** http://localhost:8000/admin (enter the `ADMIN_KEY` from your `.env`)
- **API docs:** http://localhost:8000/docs

### Getting API keys

- **Groq** (fast, generous free tier): https://console.groq.com/keys
- **OpenAI**: https://platform.openai.com/api-keys
- **Google Gemini**: https://aistudio.google.com/app/apikey

Only one is required. Set `LLM_PROVIDER` in `.env` to your preference; the
app automatically falls back to whichever other key is present.

### Email setup (optional but recommended)

For Gmail: turn on 2-Step Verification, then create an **App Password**
(Google Account → Security → App passwords) — do not use your normal Gmail
password. Put that app password in `SMTP_PASSWORD`. If email isn't
configured, bookings still save successfully; the chatbot just tells the
user the email couldn't be sent.

---

## 4. Deployment (no Streamlit)

This app ships as a single Docker container serving both the API and the
static frontend, so it deploys cleanly to any container host.

### Option A — Render.com (recommended, has a free tier)

1. Push this repo to GitHub.
2. On [Render](https://dashboard.render.com), choose **New → Blueprint**,
   and point it at your repo — it will read `render.yaml` automatically.
3. Fill in the secret environment variables it prompts for (`GROQ_API_KEY`,
   `SMTP_USER`, `SMTP_PASSWORD`, `ADMIN_KEY`, etc).
4. Deploy. Your public URL will look like
   `https://ai-booking-assistant.onrender.com`.

   > Render's free tier filesystem is ephemeral — SQLite data resets on
   > redeploy/restart. For real persistence, create a free
   > [Supabase](https://supabase.com) Postgres database and set
   > `DATABASE_URL=postgresql://...` as an env var instead.

### Option B — Railway.app

1. Push to GitHub, then on [Railway](https://railway.app) choose
   **New Project → Deploy from GitHub repo**.
2. Railway auto-detects the `Dockerfile` (or uses the `Procfile`). Add the
   same environment variables from `.env.example` in the Railway dashboard.
3. Deploy — Railway gives you a public `*.up.railway.app` URL.

### Option C — Fly.io

```bash
fly launch     # detects the Dockerfile, creates fly.toml (already provided)
fly secrets set GROQ_API_KEY=... SMTP_USER=... SMTP_PASSWORD=... ADMIN_KEY=...
fly deploy
```

### Manual Docker (any VPS)

```bash
docker build -t ai-booking-assistant .
docker run -p 8000:8000 --env-file .env ai-booking-assistant
```

---

## 5. API reference

| Method | Path | Description |
|---|---|---|
| POST | `/api/chat` | `{session_id, message}` → chat reply |
| POST | `/api/upload` | multipart PDF upload → indexes into RAG store |
| GET | `/api/bookings` | admin: list bookings (`?search=&date=`), requires `X-Admin-Key` header |
| GET | `/api/bookings/export` | admin: download all bookings as CSV |
| DELETE | `/api/bookings/{id}` | admin: cancel a booking |
| GET | `/api/health` | status check (active LLM provider, docs indexed) |

Interactive docs are auto-generated at `/docs`.

---

## 6. Use cases

The booking domain is intentionally generic — `BOOKING_DOMAIN` and
`BUSINESS_NAME` in `.env` just change the copy the bot uses. The same flow
works for:

- Doctor / clinic appointments
- Salon and spa slots
- Hotel room reservations
- Event sign-ups and ticketed bookings
- Class and workshop enrollment
- Restaurant tables and gym sessions

---

## 7. Known limitations & possible improvements

- **Short-term memory is in-process** (a Python dict keyed by session ID) —
  simple and fast, but it resets if the server restarts. For a
  multi-instance deployment, move `_SESSIONS` in `app/chat_logic.py` into
  Redis or the database.
- **TF-IDF retrieval is lexical, not semantic** — great for exact terms
  from the document, weaker on paraphrased questions. Upgrading to
  embeddings (FAISS + sentence-transformers, or an API embeddings call) is
  a drop-in change in `app/rag_pipeline.py`.
- **No speech-to-text/text-to-speech** (listed as a bonus in the brief) —
  not implemented.
- **Single shared knowledge base** — all uploaded PDFs go into one pool
  rather than being scoped per user/session. Fine for a demo; for
  multi-tenant use, key the vector store by session or account.
- **SQLite by default** resets on redeploy on most free hosting tiers —
  switch `DATABASE_URL` to Postgres/Supabase for real persistence.

---

## 8. License

Built for demonstration/assignment purposes.
