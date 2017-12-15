"""Lyrics object."""
import time


class LyricsOrigin:
    """Represents a place where lyrics come from."""

    __slots__ = ["query", "url", "source_name", "source_url"]

    def __init__(self, query, url, source_name, source_url):
        """Create new origin."""
        self.query = query
        self.url = url
        self.source_name = source_name
        self.source_url = source_url

    def __str__(self):
        """Return string rep."""
        return self.source_name


class Lyrics:
    """Represents lyrics for a song."""

    __slots__ = ["title", "lyrics", "origin", "timestamp"]

    def __init__(self, title, lyrics, origin, *, timestamp=None):
        """Create lyrics."""
        self.title = title
        self.lyrics = lyrics
        self.origin = origin

        self.timestamp = timestamp or time.time()

    def __str__(self):
        """Return string rep."""
        return "<Lyrics for {} from {}>".format(self.title, self.origin)
