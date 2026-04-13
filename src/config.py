import os

import yaml

_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "configs")
_ENV = os.environ.get("ENV", "prod")

with open(os.path.join(_CONFIG_DIR, f"{_ENV}.yml")) as f:
    _cfg = yaml.safe_load(f)

_cfg_db_path: str = _cfg["database"]["sqlite_path"]
if os.path.exists(_cfg_db_path):
    DB_PATH = _cfg_db_path
else:
    DB_PATH = os.path.join(os.environ["DATA_DIR"], "tg_bot_messages.db")

BOT_USERNAME: str = _cfg["bot"]["username"]
MODEL_NAME: str = _cfg["model"]["name"]
