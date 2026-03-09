import re
import math
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from config import MONGO_URI, DB_NAME, RESULTS_PER_PAGE

# ---------------------------------------------------------------------------
# Client & collections
# ---------------------------------------------------------------------------

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

files_col = db["files"]
users_col = db["users"]


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

async def create_indexes():
    """Create MongoDB indexes. Called once on bot startup."""
    # Uniqueness: one document per (message_id, channel_id) pair
    await files_col.create_index(
        [("message_id", 1), ("channel_id", 1)],
        unique=True,
        name="unique_message",
    )
    # Speed up regex searches on file_name
    await files_col.create_index([("file_name", 1)], name="file_name_idx")


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------

async def save_file(file_data: dict) -> bool:
    """
    Insert a file document. Returns True on success, False if duplicate.

    Expected keys in file_data:
        file_name   : str   – original file name
        file_id     : str   – Telegram file_id (stable enough for copy_message)
        file_type   : str   – document | video | audio | photo | animation | voice
        file_size   : int   – bytes (0 if unknown)
        message_id  : int   – message ID inside DB_CHANNEL
        channel_id  : int   – DB_CHANNEL_ID (stored for safety)
        caption     : str   – caption text (may be empty)
    """
    try:
        await files_col.insert_one(file_data)
        return True
    except DuplicateKeyError:
        return False


async def search_files(query: str, page: int = 1) -> tuple:
    """
    Fuzzy search: split query into words, require ALL words to appear in
    file_name (case-insensitive, any order).

    Returns:
        (results: list[dict], total_count: int, total_pages: int, current_page: int)
    """
    words = query.strip().split()
    if not words:
        return [], 0, 1, 1

    # Lookahead for each word so all must match, regardless of order
    pattern = "".join(f"(?=.*{re.escape(w)})" for w in words)
    filter_q = {"file_name": {"$regex": pattern, "$options": "i"}}

    total_count = await files_col.count_documents(filter_q)
    total_pages = max(1, math.ceil(total_count / RESULTS_PER_PAGE))
    page = max(1, min(page, total_pages))
    skip = (page - 1) * RESULTS_PER_PAGE

    cursor = files_col.find(filter_q).skip(skip).limit(RESULTS_PER_PAGE)
    results = await cursor.to_list(length=RESULTS_PER_PAGE)

    return results, total_count, total_pages, page


async def get_file_by_msg_id(message_id: int, channel_id: int) -> dict | None:
    """Fetch a single file doc by its Telegram message_id inside the DB channel."""
    return await files_col.find_one(
        {"message_id": message_id, "channel_id": channel_id}
    )


async def get_total_files() -> int:
    return await files_col.count_documents({})


async def delete_all_files() -> int:
    result = await files_col.delete_many({})
    return result.deleted_count


# ---------------------------------------------------------------------------
# User tracking (for /stats)
# ---------------------------------------------------------------------------

async def add_user(user_id: int):
    await users_col.update_one(
        {"_id": user_id},
        {"$setOnInsert": {"_id": user_id}},
        upsert=True,
    )


async def get_total_users() -> int:
    return await users_col.count_documents({})
