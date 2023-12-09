import string
import time
from typing import List, Optional
from app.url_shortener.id_generator import IdGenerator
from app.url_shortener.url_storage import UrlItem, UrlStorage, UrlStorageException
from app.url_shortener.utils import fmap
from app.url_shortener.validators import is_valid_alias, is_valid_url


class UrlShortener:
    def __init__(
        self, id_generator: IdGenerator, storage: UrlStorage, except_domains: List[str]
    ):
        self.id_generator = id_generator
        self.storage = storage
        self.except_domains = except_domains

    async def shorten(self, url: str) -> str:
        """
        Return short url(alias) from a given long url.
        Raise an ValueError when passing an invalid URL.
        Raise an Exception when the URL cannot be stored in storage.
        """

        if not is_valid_url(url, self.except_domains):
            raise ValueError("bad url") # TODO: provide more detailed error messages 

        item = await self.storage.getByUrl(url)
        if item is not None:
            return item.alias

        rounds = 5
        delay = 100 / 1000
        for _ in range(rounds):
            try:
                alias = _base62encode(await self.id_generator.gen())
                item = UrlItem(alias, url)
                await self.storage.put(item)
                return alias
            except UrlStorageException:
                time.sleep(delay)

        raise Exception("fail to save url")

    async def lengthen(self, alias: str) -> Optional[str]:
        """
        Return a long url from a given short url(alias).
        Raise an ValueError when passing an invalid alias.
        """
        if not is_valid_alias(alias):
            raise ValueError("bad alias")
        return fmap(await self.storage.getByAlias(alias), lambda item: item.url)


_DICT = string.digits + string.ascii_lowercase + string.ascii_uppercase


def _base62encode(n: int) -> str:
    if n == 0:
        return _DICT[n]

    buf: List[str] = []
    ln = len(_DICT)
    while n > 0:
        buf.append(_DICT[n % ln])
        n //= ln
    return "".join(buf[::-1])
