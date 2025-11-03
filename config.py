import os
from dotenv import load_dotenv

load_dotenv()

# 9Proxy settings
NINEPROXY_API_URL = "https://panel.9proxy.com"
NINEPROXY_LOCAL_IP = "127.0.0.1"
NINEPROXY_LOCAL_PORT = 60005  # Port bắt đầu cho 9Proxy

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "7554599232:AAG1q4Jw9XaMAweh9GtsjnBc-_iv-xKEofY"
TELEGRAM_CHAT_ID = "-1002919311281"  # Chat ID của channel

# Multilogin settings
MULTILOGIN_API_URL = "https://api.multilogin.com"
MULTILOGIN_LAUNCHER_API = "https://launcher.mlx.yt:45001/api/v1"
MULTILOGIN_LOCAL_API = "https://launcher.mlx.yt:45001/api/v1"
MULTILOGIN_EMAIL = os.getenv("MULTILOGIN_EMAIL", "nguyentai0932888777@gmail.com")
MULTILOGIN_PASSWORD = os.getenv("MULTILOGIN_PASSWORD", "Nguyen123@")

# Profile settings
DEFAULT_FOLDER_ID = os.getenv("MULTILOGIN_FOLDER_ID", "3326adec-7d0c-4f28-b354-94badcbd7a7d")