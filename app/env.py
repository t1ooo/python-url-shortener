from typing import List
from dotenv import dotenv_values


class Env:
    def __init__(self, path: str = ".env"):
        config = dotenv_values(path)
        self._base_url = str(config["base_url"]).strip()
        self._except_domains = list(
            filter(len, map(str.strip, str(config["except_domains"]).split(",")))
        )
        self._sqlite_db_path = str(config["sqlite_db_path"])

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def except_domains(self) -> List[str]:
        return self._except_domains

    @property
    def sqlite_db_path(self) -> str:
        return self._sqlite_db_path
