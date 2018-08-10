class GiTilsError(Exception):
    NAME: str
    CODE: int = 0

    msg: str

    def __init__(self, msg: str, *args, name: str = None, code: int = None):
        self.msg = msg
        if code:
            self.CODE += code
        if name:
            self.NAME = name

        super().__init__(*args)

    def __repr__(self) -> str:
        return f"{self.NAME} [{self.CODE}]: {self.msg}"


class General(GiTilsError):
    CODE = 0


class InvalidRequest(GiTilsError):
    CODE = 100
