import pytest
from app.url_shortener.id_generator import (
    IdGenerator,
    SimpleIdGenerator,
    TimeIdGenerator,
)


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    # before
    yield
    # after


@pytest.mark.parametrize(
    "generator",
    [SimpleIdGenerator(10), TimeIdGenerator()],
)
async def test_id_generator(generator: IdGenerator):
    n = 10000

    # should generate unique strings
    aliases = [await generator.gen() for _ in range(n)]
    assert len(set(aliases)) == n
