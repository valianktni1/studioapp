import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", str(ROOT_DIR / "storage" / "uploads")))
BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", str(ROOT_DIR / "storage" / "backups")))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Subscription plans -> storage limits (bytes)
GB = 1024 ** 3
PLANS = {
    "starter": {"label": "Starter", "storage_limit_bytes": 250 * GB, "price": 19},
    "pro": {"label": "Pro", "storage_limit_bytes": 500 * GB, "price": 39},
    "studio": {"label": "Studio", "storage_limit_bytes": 1024 * GB, "price": 79},
}
