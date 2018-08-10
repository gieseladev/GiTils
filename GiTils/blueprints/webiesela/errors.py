from gitils import GiTilsError


class RegistrationError(GiTilsError):
    CODE = 1000


class TokenError(GiTilsError):
    CODE = 2000
