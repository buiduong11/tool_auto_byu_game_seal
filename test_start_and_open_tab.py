#!/usr/bin/env python3
"""
Test: Start profile qua API và test mở tab mới
"""
import logging
import sys
import time
from proxy_handler import NineProxyHandler
from multilogin import MultiLoginHandler
from selenium import webdriver
from selenium.webdriver.chromium.options import ChromiumOptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 70)
    logger.info("TEST: START PROFILE & OPEN NEW TAB")
    logger.info("=" * 70)
    
    proxy_handler = NineProxyHandler()
    multilogin_handler = MultiLoginHandler()
    
    # Step 1: Login
    logger.info("\n[STEP 1] Logging in to Multilogin...")
    success, login_result = multilogin_handler.login()
    if not success:
        logger.error(f"Failed to login: {login_result.get('error')}")
        return False
    logger.info("✓ Logged in")
    
    # Step 2: Get proxy
    logger.info("\n[STEP 2] Getting proxy...")
    success, proxy_result = proxy_handler.get_next_proxy()
    if not success:
        logger.error(f"Failed to get proxy: {proxy_result.get('error')}")
        return False
    logger.info(f"✓ Got proxy: {proxy_result['host']}:{proxy_result['port']}")
    
    # Step 3: Find profile
    logger.info("\n[STEP 3] Finding profile...")
    profile_name = f"AutoBuy_Port_{proxy_result['port']}"
    profile_id = multilogin_handler.find_profile_by_name(profile_name)
    
    if not profile_id:
        logger.error(f"Profile {profile_name} not found!")
        return False
    
    logger.info(f"✓ Found profile: {profile_name} (ID: {profile_id})")
    
    # Step 4: Stop if running
    logger.info("\n[STEP 4] Stopping profile if running...")
    multilogin_handler.stop_profile(profile_id)
    time.sleep(3)
    
    # Step 5: Start profile
    logger.info("\n[STEP 5] Starting profile...")
    success, start_result = multilogin_handler.start_profile(profile_id)
    if not success:
        logger.error(f"Failed to start profile: {start_result.get('error')}")
        return False
    
    debug_port = start_result.get("selenium_port")
    if not debug_port:
        logger.error("No debugging port returned!")
        return False
    
    logger.info(f"✓ Profile started on port: {debug_port}")
    time.sleep(5)
    
    # Step 6: Connect to browser
    logger.info(f"\n[STEP 6] Connecting to browser on port {debug_port}...")
    try:
        driver = webdriver.Remote(
            command_executor=f"http://127.0.0.1:{debug_port}",
            options=ChromiumOptions()
        )
        logger.info("✓ Connected to browser")
    except Exception as e:
        logger.error(f"Failed to connect: {str(e)}")
        return False
    
    # Step 7: Open URL
    logger.info("\n[STEP 7] Opening GameSeal...")
    driver.get("https://gameseal.com/")
    time.sleep(3)
    logger.info(f"Current URL: {driver.current_url}")
    
    # Step 8: Test mở tab mới
    logger.info("\n[STEP 8] Testing open new tab...")
    try:
        windows_before = driver.window_handles
        logger.info(f"Tabs before: {len(windows_before)}")
        
        # Mở tab mới - thử nhiều cách
        home_url = "https://gameseal.com/"
        logger.info(f"Opening new tab with URL: {home_url}")
        
        # Cách 1: Dùng Selenium switch_to.new_window
        logger.info("Method 1: driver.switch_to.new_window...")
        driver.switch_to.new_window('tab')
        time.sleep(1)
        
        # Navigate đến URL
        driver.get(home_url)
        time.sleep(2)
        
        # Check số tab
        windows_after = driver.window_handles
        logger.info(f"Tabs after: {len(windows_after)}")
        
        if len(windows_after) > len(windows_before):
            logger.info("✓ New tab opened!")
            
            # Switch sang tab mới
            driver.switch_to.window(windows_after[-1])
            logger.info("✓ Switched to new tab")
            
            new_tab_url = driver.current_url
            logger.info(f"New tab URL: {new_tab_url}")
            
            time.sleep(2)
            
            logger.info("\n" + "=" * 70)
            logger.info("✅ SUCCESS! New tab opened and switched")
            logger.info("=" * 70)
            return True
        else:
            logger.error("❌ Failed to open new tab")
            return False
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
