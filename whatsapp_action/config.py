from dotenv import load_dotenv
import os


def get_env(ENV_KEY: str):
    load_dotenv()
    if os.getenv(ENV_KEY) is not None:
        return str(os.getenv(ENV_KEY))
    else:
        raise KeyError("Cannot find this key in the environment variables")


WHATSAPP_API_BASE_URL = get_env("WHATSAPP_API_BASE_URL")
WEBHOOKS_URL = get_env("WEBHOOKS_URL")
