#!/usr/bin/env python3
"""
Test Telegram notification
"""
from telegram_handler import TelegramHandler
import config

def main():
    print("Testing Telegram notification...")
    
    telegram = TelegramHandler(
        bot_token=config.TELEGRAM_BOT_TOKEN,
        chat_id=config.TELEGRAM_CHAT_ID
    )
    
    # Test message
    success = telegram.send_order_status(
        success=True,
        profile_name="AutoBuy_Port_60005",
        email="bd161120@gmail.com",
        card_last4="4272"
    )
    
    if success:
        print("✓ Telegram notification sent successfully!")
    else:
        print("✗ Failed to send Telegram notification")

if __name__ == "__main__":
    main()
