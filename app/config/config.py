import os
import pytz
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações de timezone
TIMEZONE = pytz.timezone("America/Sao_Paulo")

# Configurações de autenticação
SECRET_KEY = os.environ.get("SECRET_KEY")
CAPTCHA_API_KEY = os.environ.get("CAPTCHA_API_KEY")

# Configurações de servidor
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 5000))
RELOAD = os.environ.get("RELOAD", "False").lower() == "true"
HEADLESS = os.environ.get("HEADLESS", "False").lower() == "true"

# Configurações do Playwright
PLAYWRIGHT_ARGS = [
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-infobars",
]

# Configurações de cidades por UF
UFCITY = {"SC": ["florianopolis", "blumenau", "timbo", "braco do norte"]}

# Validações obrigatórias
if not all([SECRET_KEY, CAPTCHA_API_KEY]):
    raise Exception(
        "SECRET_KEY and CAPTCHA_API_KEY are required in environment variables"
    )

__all__ = [
    "TIMEZONE",
    "SECRET_KEY",
    "CAPTCHA_API_KEY",
    "HOST",
    "PORT",
    "RELOAD",
    "HEADLESS",
    "PLAYWRIGHT_ARGS",
    "UFCITY"
]


