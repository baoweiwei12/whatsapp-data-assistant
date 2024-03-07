from app.utils import get_env


SQL_NAME = get_env("SQL_NAME")
SQL_PSWD = get_env("SQL_PSWD")
SQL_HOST = get_env("SQL_HOST")
SQL_DB_NAME = get_env("SQL_DB_NAME")


OPENAI_API_KEY = get_env("OPENAI_API_KEY")
OPENAI_BASE_URL = get_env("OPENAI_BASE_URL")
OPENAI_MODEL = get_env("OPENAI_MODEL")

WHATSAPP_API_BASE_URL = get_env("WHATSAPP_API_BASE_URL")
WEBHOOKS_URL = get_env("WEBHOOKS_URL")

USER_PHONE_NUMBER = get_env("USER_PHONE_NUMBER").split(",")
