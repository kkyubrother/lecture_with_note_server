import configparser


def load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read("config.ini", "utf-8")
    return config


def load_database_url() -> str:
    return load_config()["DATABASE"]["URL"]


def load_google_api_key() -> str:
    return load_config()["GOOGLE"]["API_KEY"]


def load_secret_key() -> str:
    return load_config()["SECURITY"]["SECRET"]
