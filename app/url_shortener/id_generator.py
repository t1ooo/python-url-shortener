import random
import time
from typing import Protocol


class IdGenerator(Protocol):
    """ "Generate unique id"""

    async def gen(self) -> int:
        """
        Return a unique identifier.
        """
        ...


class SimpleIdGenerator(IdGenerator):
    def __init__(self, start: int, pregenerate: int = 100):
        self.start = start
        self.pregenerate = pregenerate
        self._gen_ids()

    async def gen(self) -> int:
        if len(self.ids) == 0:
            self._gen_ids()
        return self.ids.pop()

    def _gen_ids(self):
        self.ids = list(range(self.start, self.start + self.pregenerate))
        random.shuffle(self.ids)
        self.start += self.pregenerate


class TimeIdGenerator(IdGenerator):
    async def gen(self) -> int:
        return time.time_ns()
