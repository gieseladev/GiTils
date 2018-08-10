from gitils import GiTilsError


class RegistrationError(GiTilsError):
    CODE = 1000


class TokenError(GiTilsError):
    CODE = 2000


class LoginError(GiTilsError):
    CODE = 3000
