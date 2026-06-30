"""
Run this script once to create the first superadmin account.
Usage: python scripts/seed_admin.py
"""
import asyncio
import uuid
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from auth.utils import hash_password

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "eduflow")

ADMIN_NAME = "Super Admin"
ADMIN_EMAIL = "admin@eduflow.university"
ADMIN_PASSWORD = "Admin@123456"


async def seed():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]

    existing = await db.users.find_one({"email": ADMIN_EMAIL})
    if existing:
        print(f"Admin already exists: {ADMIN_EMAIL}")
        client.close()
        return

    await db.users.insert_one({
        "_id": str(uuid.uuid4()),
        "name": ADMIN_NAME,
        "email": ADMIN_EMAIL,
        "hashed_password": hash_password(ADMIN_PASSWORD),
        "role": "superadmin",
        "created_at": datetime.now(timezone.utc),
        "is_active": True,
    })

    # Indexes
    await db.users.create_index("email", unique=True)
    await db.applications.create_index("thread_id", unique=True)
    await db.applications.create_index("status")
    await db.applications.create_index("created_at")

    print("✓ Superadmin created successfully")
    print(f"  Email:    {ADMIN_EMAIL}")
    print(f"  Password: {ADMIN_PASSWORD}")
    print("  IMPORTANT: Change this password after first login!")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
