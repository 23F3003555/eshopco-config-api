# eShopCo Config API

## Run locally
```bash
python -m pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://127.0.0.1:8000/effective-config`.

Test CLI-style overrides:
```bash
curl "http://127.0.0.1:8000/effective-config?set=port%3D9000&set=debug%3Dtrue"
```

## Deploy to Render
1. Push all files in this folder to a GitHub repository.
2. In Render, create **New + → Web Service** and connect that repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables `APP_ENV=development` and `APP_WORKERS=13`.
6. Deploy. Use `https://YOUR-SERVICE.onrender.com/effective-config` as the grader URL.

The `.env` file is included for the assignment's specified layer. For a public deployment, avoid committing real secrets; this exercise masks `api_key` in the response.
