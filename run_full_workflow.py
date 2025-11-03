#!/usr/bin/env python3
"""
Full Workflow: Create Profile + Start + Auto Login
Tích hợp tạo proxy, tạo profile, start profile và auto login
"""
import logging
import sys
import time
from proxy_handler import NineProxyHandler
from multilogin import MultiLoginHandler
from gameseal_auto_login import GameSealAutoLogin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main workflow"""
    proxy_handler = NineProxyHandler()
    multilogin_handler = MultiLoginHandler()
    
    # Step 1: Login to Multilogin
    logger.info("=" * 70)
    logger.info("FULL WORKFLOW: PROXY + PROFILE + AUTO LOGIN")
    logger.info("=" * 70)
    
    logger.info("\nStep 1: Logging in to Multilogin...")
    success, login_result = multilogin_handler.login()
    
    if not success:
        logger.error(f"Failed to login to Multilogin: {login_result.get('error')}")
        return False
    
    logger.info("✓ Logged in successfully")
        
    # Step 2: Get proxy
    logger.info("\nStep 2: Getting proxy...")
    success, proxy_result = proxy_handler.get_next_proxy()
    
    if not success:
        logger.error(f"Failed to get proxy: {proxy_result.get('error')}")
        return False
        
    logger.info(f"✓ Got proxy: {proxy_result['host']}:{proxy_result['port']}")
    
    # Step 3: Check existing profile or create new
    logger.info("\nStep 3: Checking for existing profile...")
    profile_name = f"AutoBuy_Port_{proxy_result['port']}"
    profile_id = multilogin_handler.find_profile_by_name(profile_name)
    
    if profile_id:
        logger.info(f"✓ Reusing existing profile: {profile_name} (ID: {profile_id})")
    else:
        logger.info("Creating new Multilogin profile...")
        success, profile_result = multilogin_handler.create_profile(
            proxy_result, 
            profile_name=profile_name
        )
        
        if not success:
            logger.error(f"Failed to create profile: {profile_result.get('error')}")
            return False
            
        profile_id = profile_result["profile_id"]
        logger.info(f"✓ Created new profile: {profile_name} (ID: {profile_id})")
    
    # Step 4: Start profile
    logger.info("\nStep 4: Starting Multilogin profile...")
    success, start_result = multilogin_handler.start_profile(profile_id)
    
    debug_port = None
    if success and start_result.get("selenium_port"):
        debug_port = start_result["selenium_port"]
        logger.info(f"✓ Profile started on port {debug_port}")
        time.sleep(3)
    else:
        error_msg = start_result.get("error", "")
        if "ALREADY_RUNNING" in error_msg or "already running" in error_msg.lower():
            logger.info("✓ Profile is already running")
            # Không có port, sẽ dùng cách khác
        else:
            logger.warning(f"Could not start profile: {error_msg}")
            logger.info("Please make sure profile is running manually")
        time.sleep(3)
    
    # Step 5: Auto login với Selenium
    logger.info("\nStep 5: Running auto login workflow...")
    
    # Thông tin đăng nhập
    EMAIL = "jacki2egthome@outlook.sg"
    PASSWORD = "Abc@12345"
    
    automation = GameSealAutoLogin(email=EMAIL, password=PASSWORD, debug_port=debug_port)
    
    # Kết nối với browser
    if not automation.connect_to_browser():
        logger.error("Cannot connect to browser!")
        logger.info("Trying alternative method...")
        # Thử không dùng debugging port
        automation.debug_port = None
        if not automation.connect_to_browser():
            logger.error("Failed to connect. Please ensure Multilogin browser is running.")
            return False
    
    # Chạy workflow login
    success = automation.run_login_workflow()
    
    if not success:
        logger.error("Auto login failed")
        return False
    
    logger.info("\n" + "=" * 70)
    logger.info("✓ SUCCESS! Full workflow completed")
    logger.info(f"Profile: {profile_name}")
    logger.info(f"Proxy: {proxy_result['host']}:{proxy_result['port']}")
    logger.info(f"Email: {EMAIL}")
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
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
