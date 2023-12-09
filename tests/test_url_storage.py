import pytest
from app.url_shortener.url_storage import (
    SimpleUrlStorage,
    UrlItem,
    UrlStorage,
    UrlStorageException,
)
from tests.shared import clear_test_dir, create_sqlite_url_storage, create_test_dir


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    create_test_dir()
    yield
    clear_test_dir()


async def _test_url_storage(storage: UrlStorage):
    alias = "alias"
    url = "url"

    item = UrlItem(alias, url)
    await storage.put(item)

    # should raise an UrlStorageException if an item with the same alias already exists
    with pytest.raises(UrlStorageException, match="already exists"):
        await storage.put(UrlItem(alias, "other url"))

    # should return the correct item for the given url
    assert await storage.getByUrl(url) == item

    # should return None for non-existent url
    assert await storage.getByUrl("url non-existent") == None

    # should return the correct item for the given alias
    assert await storage.getByAlias(alias) == item

    # should return None for non-existent url
    assert await storage.getByAlias("alias non-existent") == None


async def test_url_storage():
    for storage in [SimpleUrlStorage(), await create_sqlite_url_storage()]:
        await _test_url_storage(storage)
        await storage.close()
