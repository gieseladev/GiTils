"""Fancy lyrics managment."""

import logging

from .extractor import LyricsExtractor

log = logging.getLogger(__name__)


class LyricsManager:
    """Manage stuff."""

    extractors = []

    @classmethod
    def setup(cls):
        """Load extractors."""
        log.debug("setting up")

        from .extractors import *
        cls.extractors = LyricsExtractor.extractors
        log.info("loaded {} extractors".format(len(cls.extractors)))

    @classmethod
    def extract_lyrics(cls, url, *, cache=True):
        """Extract lyrics from url."""
        for extractor in cls.extractors:
            pass


LyricsManager.setup()
