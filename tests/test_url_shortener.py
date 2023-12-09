import pytest
from app.url_shortener.id_generator import (
    TimeIdGenerator,
)
from app.url_shortener.url_shortener import UrlShortener, is_valid_alias
from tests.shared import clear_test_dir, create_sqlite_url_storage, create_test_dir


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    create_test_dir()
    yield
    clear_test_dir()


async def test_url_shortener():
    generator = TimeIdGenerator()
    storage = await create_sqlite_url_storage()
    except_domains = ["example.com", "127.0.0.1"]
    service = UrlShortener(generator, storage, except_domains)

    n = 1000
    urls = [f"http://{n}.com" for n in range(n)]
    aliases = [await service.shorten(url) for url in urls]

    # should generate unique aliases
    assert len(set(aliases)) == n

    # should return the same alias for the given url
    assert aliases == [await service.shorten(url) for url in urls]

    # should return valid aliases
    assert all(map(is_valid_alias, aliases)) == True

    # should return the correct url for the given alias
    urls_lengthen = [await service.lengthen(alias) for alias in aliases]
    assert urls_lengthen == urls

    # should raise an ValueException for except_domain
    for d in except_domains:
        with pytest.raises(ValueError, match="bad url"):
            await service.shorten(f"http://{d}/123")

    await storage.close()
