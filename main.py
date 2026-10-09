import os
from pathlib import Path
from typing import Optional

import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

def to_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "on"}

def coerce(key, value):
    if key in {"port", "workers"}:
        return int(value)
    if key == "debug":
        return to_bool(value)
    return str(value)

def normalize_key(key):
    aliases = {
        "NUM_WORKERS": "workers",
        "APP_WORKERS": "workers",
        "APP_PORT": "port",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key",
    }
    return aliases.get(key, key.lower())

def load_config():
    config = dict(DEFAULTS)

    env_name = os.getenv("APP_ENV", "development")
    yaml_path = BASE_DIR / f"config.{env_name}.yaml"
    if yaml_path.exists():
        with yaml_path.open("r", encoding="utf-8") as f:
            yaml_layer = yaml.safe_load(f) or {}
        for key, value in yaml_layer.items():
            config[normalize_key(key)] = value

    dotenv_layer = dotenv_values(BASE_DIR / ".env")
    for key, value in dotenv_layer.items():
        if value is not None:
            config[normalize_key(key)] = value

    # OS environment variables have higher precedence than the .env file.
    for key, value in os.environ.items():
        if key.startswith("APP_"):
            config[normalize_key(key)] = value

    # Coerce all known fields after merging.
    for key in ("port", "workers"):
        config[key] = int(config[key])
    config["debug"] = to_bool(config["debug"])
    config["log_level"] = str(config["log_level"])
    config["api_key"] = str(config["api_key"])
    return config

app = FastAPI(title="eShopCo Configuration Health Check")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/effective-config")
def effective_config(set: Optional[list[str]] = Query(default=None)):
    config = load_config()

    # Each set value is key=value. Split only on the first '=' so values may contain '='.
    for item in set or []:
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        key = key.strip().lower()
        if not key:
            continue
        config[key] = value

    # Enforce required types after CLI overrides, including any additional keys.
    for key in ("port", "workers"):
        if key in config:
            config[key] = int(config[key])
    if "debug" in config:
        config["debug"] = to_bool(config["debug"])
    for key in config:
        if key not in {"port", "workers", "debug"}:
            config[key] = str(config[key])

    # Never reveal the actual API key.
    config["api_key"] = "****"
    return config
