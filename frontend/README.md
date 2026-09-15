# monistats frontend

Reads live signal data from the same Postgres database the Python backend writes to,
and shows it as a menu-style dashboard: pick an asset class (Crypto / Forex / Stocks),
see the latest triggered signals.

## Local development

```bash
npm install
cp .env.local.example .env.local   # fill in DATABASE_URL — same one the backend uses
npm run dev
```

Open http://localhost:3000

## Deploying to Vercel

1. Push this `frontend/` folder (as part of the monistats repo) to GitHub if not already there.
2. Go to vercel.com, sign in with GitHub, "Add New Project", import the monistats repo.
3. When it asks for the Root Directory, set it to `frontend` (important — this is a
   subfolder of the repo, not the repo root).
4. Under Environment Variables, add `DATABASE_URL` with the same Postgres connection
   string your backend's `.env` uses.
5. Deploy. Vercel gives you a live URL immediately.

## Notes

- Only Crypto will show data until the backend also fetches forex/stocks (see the
  main README's roadmap) — Forex and Stocks tabs will show the empty state until then.
- The API route (`app/api/signals/route.ts`) only reads from the database — it never
  writes, so there's no risk of the frontend interfering with the backend's signals.
