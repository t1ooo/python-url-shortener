import pytest
from app.url_shortener.url_shortener import is_valid_alias, is_valid_url


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    # before
    yield
    # after


def test_is_valid_alias():
    assert is_valid_alias("12323") == True
    assert is_valid_alias("asdfd") == True
    assert is_valid_alias("GFJGK") == True
    assert is_valid_alias("3453adsgSDFF") == True
    assert is_valid_alias("") == False
    assert is_valid_alias(" ") == False
    assert is_valid_alias("+") == False
    assert is_valid_alias("/") == False
    assert is_valid_alias("ы") == False


def test_is_valid_url():
    assert is_valid_url("http://example.com") == True
    assert is_valid_url("https://example.com") == True
    assert is_valid_url("https://1.com") == True
    assert is_valid_url("https://сайт.рф") == True
    assert is_valid_url("http://") == False
    assert is_valid_url("https://") == False
    assert is_valid_url("") == False
    assert is_valid_url("http://127.0.0.1", ["127.0.0.1"]) == False
    assert is_valid_url("http://localhost:3000", ["localhost:3000"]) == False
    assert is_valid_url("ftp://example.com") == False
