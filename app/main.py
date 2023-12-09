from types import SimpleNamespace
from sanic import Config, Sanic, html, redirect
from sanic.response import json
from sanic.request import Request
from app.env import Env
from app.url_shortener.id_generator import TimeIdGenerator
from app.url_shortener.url_shortener import UrlShortener
from app.url_shortener.url_storage import SqliteUrlStorage

app = Sanic("url_shortener")


@app.before_server_start
async def setup(app: Sanic[Config, SimpleNamespace]):
    if app.test_mode: # TODO: find a better solution?
        return
    env = Env()
    generator = TimeIdGenerator()
    storage = await SqliteUrlStorage.create(env.sqlite_db_path)
    app.ctx.url_shortener = UrlShortener(generator, storage, env.except_domains)
    app.ctx.env = env


@app.before_server_stop
async def stop(app: Sanic[Config, SimpleNamespace]):
    if app.test_mode: # TODO: find a better solution?
        return
    await app.ctx.url_shortener.storage.close()


app.static("/favicon.ico", "static/favicon.ico", name="favicon")
app.static("/", "static/index.html", name="static")


@app.route("/api/shorten", methods=["POST"])
async def shorten(request: Request):  # type: ignore
    env = request.app.ctx.env
    url_shortener = request.app.ctx.url_shortener
    try:
        url = request.json.get("url", "").strip()
        alias = await url_shortener.shorten(url)
        return json(
            {
                "base_url": env.base_url,
                "alias": alias,
                "full_url": env.base_url + "/" + alias,
            }
        )
    except ValueError as e:
        return json({"error": str(e)})


@app.route("/api/lengthen", methods=["POST"])
async def lengthen(request: Request):  # type: ignore
    url_shortener = request.app.ctx.url_shortener
    try:
        alias = request.json.get("alias", "").strip()
        url = await url_shortener.lengthen(alias)
        if url is None:
            return json({"error": "not found"}, status=404)
        else:
            return json({"url": url}, status=404)
    except ValueError as e:
        return json({"error": str(e)})


@app.route("/<alias>", methods=["GET"])
async def lengthen_redirect(request: Request, alias: str):  # type: ignore
    url_shortener = request.app.ctx.url_shortener
    try:
        url = await url_shortener.lengthen(alias)
        if url is None:
            return page_404()
        else:
            return redirect(url, status=301)
    except ValueError as e:
        print(e)
        return page_404()


def page_404():
    html_content = """
    <html>
    <head>
        <title>404 Not Found</title>
    </head>
    <body>
        <h1>404 Not Found</h1>
        <p>The requested page was not found.</p>
    </body>
    </html>
    """
    return html(html_content, status=404)
