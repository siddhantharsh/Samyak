import random
import datetime
from typing import Protocol

def seeded_rng(seed: int) -> random.Random:
    return random.Random(seed)

class Clock(Protocol):
    def now(self) -> datetime.datetime:
        ...

class FrozenClock:
    def __init__(self, time: datetime.datetime):
        self._time = time

    def now(self) -> datetime.datetime:
        return self._time

class SystemClock:
    def now(self) -> datetime.datetime:
        return datetime.datetime.now()
