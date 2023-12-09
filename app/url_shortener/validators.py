import re
from typing import List
from urllib.parse import urlparse


def is_valid_url(url: str, except_domains: List[str] = []) -> bool:
    try:
        r = urlparse(url)
        if r.scheme not in ["http", "https"]:
            return False
        if r.netloc in [""] + except_domains:
            return False
        return True
    except ValueError:
        return False


_re_alias = re.compile(r"^[0-9a-zA-Z]+$")


def is_valid_alias(alias: str) -> bool:
    return _re_alias.match(alias) is not None
