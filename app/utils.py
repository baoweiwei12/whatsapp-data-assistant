import os


def get_env(ENV_KEY: str):

    if os.getenv(ENV_KEY) is not None:
        return str(os.getenv(ENV_KEY))
    else:
        raise KeyError("Cannot find this key in the environment variables")
