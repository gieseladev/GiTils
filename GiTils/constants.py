import os


class EnvironConst(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        for var, val in vars(cls).items():
            if var.isupper():
                env_key = val or "{}_{}".format(name, var).upper()

                try:
                    env_value = os.environ[env_key]
                except KeyError:
                    raise KeyError("Key \"{}\" missing in the environment variables!".format(env_key)) from None

                setattr(cls, var, env_value)


class Variables(metaclass=EnvironConst):
    GIESELA_IP = ""


class Spotify(metaclass=EnvironConst):
    CLIENT_ID = ""
    CLIENT_SECRET = ""
