#!/usr/bin/env python3
"""
Test payment status check và Telegram notification
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram_handler import TelegramHandler
import config
import time

def test_payment_status(debug_port=9222):
    """Test check payment status và gửi Telegram"""
    print(f"Connecting to browser on port {debug_port}...")
    
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
    
    try:
        driver = webdriver.Chrome(options=options)
        print("✓ Connected to browser")
        
        # Đợi 2 giây
        time.sleep(2)
        
        # Check button Buy Now
        print("\nChecking for Buy Now button...")
        try:
            buy_now_btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    "#productDetailPageBuyProductForm > div > div.col-8 > button"))
            )
            print("✓ Found Buy Now button")
            payment_success = False
            status_msg = "Payment FAILED - Buy Now button still visible"
        except:
            print("✓ Buy Now button NOT found")
            payment_success = True
            status_msg = "Payment SUCCESS - Buy Now button disappeared"
        
        print(f"\n{status_msg}")
        
        # Gửi Telegram notification
        print("\nSending Telegram notification...")
        telegram = TelegramHandler(
            bot_token=config.TELEGRAM_BOT_TOKEN,
            chat_id=config.TELEGRAM_CHAT_ID
        )
        
        result = telegram.send_order_status(
            success=payment_success,
            profile_name="AutoBuy_Port_60005",
            email="bd161120@gmail.com",
            card_last4="4272",
            error_msg=None if payment_success else "Button Buy Now still visible"
        )
        
        if result:
            print("✓ Telegram notification sent!")
        else:
            print("✗ Failed to send Telegram notification")
        
        return payment_success
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    
    print("=" * 70)
    print("TEST PAYMENT STATUS & TELEGRAM")
    print("=" * 70)
    
    # Lấy port từ argument hoặc dùng mặc định
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9222
    print(f"\nUsing port: {port}")
    
    test_payment_status(port)
