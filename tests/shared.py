import os
from app.url_shortener.url_storage import SqliteUrlStorage


_TEST_DIR = "tests/test_data"
_URL_STORAGE_PATH = _TEST_DIR + "/url_storage.sqlite"


def create_test_dir():
    os.makedirs(_TEST_DIR, exist_ok=True)


def clear_test_dir():
    for file in os.listdir(_TEST_DIR):
        os.remove(_TEST_DIR + "/" + file)


async def create_sqlite_url_storage():
    # NOTES: doesn't work with in memory database
    return await SqliteUrlStorage.create(_URL_STORAGE_PATH)
