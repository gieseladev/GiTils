from gitils import GiTilsError


class TestConnectionError(GiTilsError):
    CODE = 1000


class TokenError(GiTilsError):
    CODE = 2000
