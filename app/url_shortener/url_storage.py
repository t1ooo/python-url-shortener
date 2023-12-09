from dataclasses import dataclass
import os
from typing import Awaitable, Callable, Dict, Optional, Protocol, TypeVar
import aiosqlite
from app.url_shortener.utils import fmap


@dataclass(frozen=True)
class UrlItem:
    alias: str
    url: str


class UrlStorageException(Exception):
    pass


class UrlStorage(Protocol):
    async def getByUrl(self, url: str) -> Optional[UrlItem]:
        """Return the UrlItem for the given URL if it exists, else None."""
        ...

    async def getByAlias(self, alias: str) -> Optional[UrlItem]:
        """Return the UrlItem for the given alias if it exists, else None."""
        ...

    async def put(self, item: UrlItem):
        """
        Store a UrlItem.
        Raise an UrlStorageException if an item with the same alias already exists.
        """
        ...

    async def close(self):
        ...


class SimpleUrlStorage(UrlStorage):
    def __init__(self):
        self.alias_item: Dict[str, UrlItem] = {}
        self.url_alias: Dict[str, str] = {}

    async def getByUrl(self, url: str) -> Optional[UrlItem]:
        return fmap(self.url_alias.get(url), self.alias_item.get)

    async def getByAlias(self, alias: str) -> Optional[UrlItem]:
        return self.alias_item.get(alias)

    async def put(self, item: UrlItem):
        if item.alias in self.alias_item:
            raise UrlStorageException("already exists")
        self.alias_item[item.alias] = item
        self.url_alias[item.url] = item.alias

    async def close(self):
        # do nothing
        pass


_E = TypeVar("_E")


async def _transaction(
    con: aiosqlite.Connection, fn: Callable[[aiosqlite.Cursor], Awaitable[_E]]
) -> _E:
    cur = await con.cursor()
    await cur.execute("BEGIN")
    try:
        result = await fn(cur)
        await cur.execute("COMMIT")
        return result
    except aiosqlite.Error as e:
        await cur.execute("ROLLBACK")
        raise e
    finally:
        await cur.close()


class SqliteUrlStorage(UrlStorage):
    @classmethod
    async def create(cls, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        con = await aiosqlite.connect(db_path, isolation_level=None)
        obj = cls(con)
        await obj._init_db()
        return obj

    def __init__(self, con: aiosqlite.Connection):
        """Private constructor. Use cls.create instead."""
        self.con = con

    async def close(self):
        await self.con.close()

    async def _init_db(self):
        await self.con.execute("pragma journal_mode=wal")

        async def f(cur: aiosqlite.Cursor):
            await cur.execute(
                """CREATE TABLE IF NOT EXISTS urls(
                alias STRING PRIMARY KEY,
                url   STRING
            )"""
            )
            await cur.execute("CREATE INDEX IF NOT EXISTS urls_url ON urls(url)")

        await _transaction(self.con, f)

    async def getByUrl(self, url: str) -> Optional[UrlItem]:
        cur = await self.con.cursor()
        await cur.execute(
            "SELECT alias, url FROM urls WHERE url=:url LIMIT 1", {"url": url}
        )
        result = fmap(await cur.fetchone(), lambda r: UrlItem(str(r[0]), str(r[1])))
        await cur.close()
        return result

    async def getByAlias(self, alias: str) -> Optional[UrlItem]:
        cur = await self.con.cursor()
        await cur.execute(
            "SELECT alias, url FROM urls WHERE alias=:alias LIMIT 1", {"alias": alias}
        )
        result = fmap(await cur.fetchone(), lambda r: UrlItem(str(r[0]), str(r[1])))
        await cur.close()
        return result

    async def put(self, item: UrlItem):
        async def f(cur: aiosqlite.Cursor):
            await cur.execute("INSERT INTO urls VALUES(:alias, :url)", item.__dict__)

        try:
            await _transaction(self.con, f)
        except aiosqlite.IntegrityError:
            raise UrlStorageException("already exists")
