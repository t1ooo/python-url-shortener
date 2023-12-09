import re
from app.env import Env
from app.main import app
from sanic_testing.testing import SanicTestClient
from app.url_shortener.id_generator import TimeIdGenerator
from app.url_shortener.url_shortener import UrlShortener
from app.url_shortener.url_storage import SimpleUrlStorage


def get_test_client():
    env = Env(".env_test")
    generator = TimeIdGenerator()
    storage = SimpleUrlStorage()
    app.ctx.url_shortener = UrlShortener(generator, storage, env.except_domains)
    app.ctx.env = env
    return SanicTestClient(app)


_BASE_URL = ""


def test_api():
    test_client = get_test_client()

    urls = ["https://google.com", "https://amazon.com"]

    for url in urls:
        r = test_client.post(_BASE_URL + "/api/shorten", json={"url": url})[1]

        base_url = r.json.get("base_url")  # type: ignore
        assert base_url == test_client.app.ctx.env.base_url

        alias = r.json.get("alias")  # type: ignore
        assert re.match(r"^[0-9a-zA-Z]+$", alias)
        print(alias)

        full_url = r.json.get("full_url")  # type: ignore
        assert full_url == base_url + "/" + alias

        # should return the same result for the same url
        r_same = test_client.post(_BASE_URL + "/api/shorten", json={"url": url})[1]
        assert r.json == r_same.json  # type: ignore

        # should return the correct url
        r = test_client.post(_BASE_URL + "/api/lengthen", json={"alias": alias})[1]
        r_url = r.json.get("url")  # type: ignore
        assert r_url == url
