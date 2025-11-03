#!/usr/bin/env python3
"""
Auto Workflow: Tạo/Start Profile + Auto Login
Cross-platform (Windows/macOS) sử dụng Selenium
"""
import logging
import sys
import time
from proxy_handler import NineProxyHandler
from multilogin import MultiLoginHandler
from proxy_handler import ProxyHandler
from gameseal_auto_login import GameSealAutoLogin
from telegram_handler import TelegramHandler
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main workflow"""
    proxy_handler = NineProxyHandler()
    multilogin_handler = MultiLoginHandler()
    
    logger.info("=" * 70)
    logger.info("AUTO WORKFLOW: CREATE PROFILE + START + AUTO LOGIN")
    logger.info("=" * 70)
    
    # Step 1: Login to Multilogin
    logger.info("\n[STEP 1] Logging in to Multilogin...")
    success, login_result = multilogin_handler.login()
    
    if not success:
        logger.error(f"Failed to login: {login_result.get('error')}")
        return False
    
    logger.info("✓ Logged in successfully")
        
    # Step 2: Get proxy
    logger.info("\n[STEP 2] Getting proxy...")
    success, proxy_result = proxy_handler.get_next_proxy()
    
    if not success:
        logger.error(f"Failed to get proxy: {proxy_result.get('error')}")
        return False
        
    logger.info(f"✓ Got proxy: {proxy_result['host']}:{proxy_result['port']}")
    
    # Step 3: Check existing profile
    logger.info("\n[STEP 3] Checking for existing profile...")
    profile_name = f"AutoBuy_Port_{proxy_result['port']}"
    profile_id = multilogin_handler.find_profile_by_name(profile_name)
    
    if profile_id:
        logger.info(f"✓ Found existing profile: {profile_name} (ID: {profile_id})")
        
        # Stop profile nếu đang chạy để có thể start lại và lấy port
        logger.info("Stopping profile if running...")
        multilogin_handler.stop_profile(profile_id)
        time.sleep(3)
    else:
        logger.info("Creating new profile...")
        success, profile_result = multilogin_handler.create_profile(
            proxy_result, 
            profile_name=profile_name
        )
        
        if not success:
            logger.error(f"Failed to create profile: {profile_result.get('error')}")
            return False
            
        profile_id = profile_result["profile_id"]
        logger.info(f"✓ Created new profile: {profile_name} (ID: {profile_id})")
    
    # Step 4: Start profile và lấy debugging port
    logger.info("\n[STEP 4] Starting profile...")
    success, start_result = multilogin_handler.start_profile(profile_id)
    
    if not success:
        logger.error(f"Failed to start profile: {start_result.get('error')}")
        return False
    
    debug_port = start_result.get("selenium_port")
    
    if not debug_port:
        logger.warning("No debugging port in API response, will try common ports...")
        # Multilogin thường dùng các port này cho debugging
        debug_port = None  # Sẽ thử nhiều port
    else:
        logger.info(f"✓ Got debugging port from API: {debug_port}")
    
    time.sleep(5)  # Đợi browser khởi động hoàn toàn
    
    # Step 5: Auto login với Selenium
    logger.info("\n[STEP 5] Running auto login...")
    
    EMAIL = "bd161120@gmail.com"
    PASSWORD = "Abc@12345"
    
    # Parse data từ input
    # Card: 4217835061254272 08/28 320 | VISA CREDIT CLASSIC | CHIME | US | 75044 | Garland | TX | 209 Coral Ridge Dr | María Esther Serrano Teruel
    user_data = {
        'first_name': 'María Esther',
        'last_name': 'Serrano Teruel',
        'address': '209 Coral Ridge Dr',
        'city': 'Garland',
        'state': 'TX',
        'zip': '75044',
        'country': 'US',
        'phone': '+12108682111',
        'dob_day': '15',  # Mặc định
        'dob_month': '06',  # Mặc định
        'dob_year': '1990'  # Mặc định
    }
    
    card_data = {
        'number': '4217835061254272',
        'exp_date': '08/28',
        'cvv': '320',
        'type': 'VISA',
        'bank': 'CHIME',
        # Billing address từ user_data
        'address': user_data['address'],
        'city': user_data['city'],
        'zip': user_data['zip'],
        'country': 'United States'
    }
    
    automation = GameSealAutoLogin(
        email=EMAIL, 
        password=PASSWORD, 
        debug_port=debug_port
    )
    
    # Kết nối với browser
    if not automation.connect_to_browser():
        logger.error("Failed to connect to browser!")
        return False
    
    # Chạy workflow login
    success = automation.run_login_workflow()
    if not success:
        logger.error("Auto login failed!")
        return False
    
    # Điền thông tin profile
    logger.info("\n[STEP 6] Filling profile information...")
    if not automation.fill_profile_form(user_data):
        logger.warning("Failed to fill profile, continuing...")
    
    # Hoàn tất checkout
    logger.info("\n[STEP 7] Completing checkout...")
    checkout_success = automation.complete_checkout(card_data)
    
    # Initialize Telegram handler
    telegram = TelegramHandler(
        bot_token=config.TELEGRAM_BOT_TOKEN,
        chat_id=config.TELEGRAM_CHAT_ID
    )
    
    # Send notification to Telegram
    logger.info("\n[STEP 8] Sending Telegram notification...")
    telegram.send_order_status(
        success=checkout_success,
        profile_name=profile_name,
        email=EMAIL,
        card_last4=card_data['number'][-4:],
        error_msg=None if checkout_success else "Payment failed or declined"
    )
    
    if not checkout_success:
        logger.error("Checkout failed!")
        return False
    
    logger.info("\n" + "=" * 70)
    logger.info("✓ SUCCESS! Full workflow completed")
    logger.info(f"Profile: {profile_name}")
    logger.info(f"Proxy: {proxy_result['host']}:{proxy_result['port']}")
    logger.info(f"Email: {EMAIL}")
    logger.info(f"User: {user_data['first_name']} {user_data['last_name']}")
    logger.info(f"Card: {card_data['number'][-4:]}")
    logger.info("=" * 70)
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
