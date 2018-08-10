import asyncio
import random
import string

from vibora.client.websocket import WebsocketClient


async def test_giesela_websocket(host: str, port: int, timeout: float) -> bool:
    client = WebsocketClient(host, port, "/gitils")
    try:
        await asyncio.wait_for(client.connect(), timeout)
    except asyncio.TimeoutError:
        return False
    else:
        # TODO get information and close connection
        return True


_vowels = set("aeiou")
vowels = tuple(_vowels)
consonants = tuple(set(string.ascii_lowercase) - _vowels)

# Measured based on most common words (https://github.com/dwyl/english-words)
switch_chances = {
    # vowels
    "a": .93,
    "e": .89,
    "i": .81,
    "o": .84,
    "u": .90,
    # consonants
    "b": .60,
    "c": .59,
    "d": .75,
    "f": .66,
    "g": .58,
    "h": .76,
    "j": .98,
    "k": .77,
    "l": .67,
    "m": .77,
    "n": .43,
    "p": .51,
    "q": .99,
    "r": .66,
    "s": .39,
    "t": .68,
    "v": .99,
    "w": .72,
    "x": .56,
    "y": .21,
    "z": .90
}


def generate_regtoken(length: int) -> str:
    _str = random.choice(string.ascii_lowercase)
    _last = _str
    _vowel = _last in vowels

    for _ in range(length - 1):
        switch_chance = switch_chances[_last]

        if random.random() < switch_chance:
            _vowel = not _vowel

        _pick_from = vowels if _vowel else consonants
        _last = random.choice(_pick_from)
        _str += _last

    return _str
