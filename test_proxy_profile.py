#!/usr/bin/env python3
"""
Test: Get proxy + Create profile + Start profile
"""
import logging
from proxy_handler import NineProxyHandler
from multilogin import MultiLoginHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("="*70)
    logger.info("TEST: PROXY + CREATE PROFILE + START")
    logger.info("="*70)
    
    # Step 1: Get proxy
    logger.info("\n[STEP 1] Getting proxy from 9Proxy...")
    proxy_handler = NineProxyHandler()
    success, proxy_info = proxy_handler.get_next_proxy()
    
    if not success:
        logger.error(f"Failed to get proxy: {proxy_info.get('error')}")
        return False
    
    logger.info(f"✓ Got proxy: {proxy_info['host']}:{proxy_info['port']}")
    logger.info(f"  Type: {proxy_info['type']}")
    logger.info(f"  Country: {proxy_info.get('country', 'N/A')}")
    
    # Step 2: Login Multilogin
    logger.info("\n[STEP 2] Logging in to Multilogin...")
    multilogin_handler = MultiLoginHandler()
    login_success, login_result = multilogin_handler.login()
    
    if not login_success:
        logger.error(f"Failed to login: {login_result.get('error')}")
        return False
    
    logger.info("✓ Logged in to Multilogin")
    
    # Step 3: Create profile with proxy
    logger.info("\n[STEP 3] Creating new profile with proxy...")
    profile_name = f"Test_Proxy_{proxy_info['port']}"
    
    create_success, create_result = multilogin_handler.create_profile(
        proxy_info=proxy_info,
        profile_name=profile_name
    )
    
    if not create_success:
        logger.error(f"Failed to create profile: {create_result.get('error')}")
        return False
    
    profile_id = create_result.get("profile_id")
    logger.info(f"✓ Created profile: {profile_name}")
    logger.info(f"  Profile ID: {profile_id}")
    
    # Step 4: Start profile
    logger.info("\n[STEP 4] Starting profile...")
    success, start_result = multilogin_handler.start_profile(profile_id)
    
    if not success:
        logger.error(f"Failed to start profile: {start_result.get('error')}")
        return False
    
    debug_port = start_result.get("selenium_port")
    logger.info(f"✓ Profile started successfully!")
    logger.info(f"  Debug port: {debug_port}")
    
    # Step 5: Test connection
    logger.info("\n[STEP 5] Testing browser connection...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chromium.options import ChromiumOptions
        
        driver = webdriver.Remote(
            command_executor=f"http://127.0.0.1:{debug_port}",
            options=ChromiumOptions()
        )
        
        logger.info("✓ Connected to browser")
        
        # Navigate to IP check site
        logger.info("Navigating to IP check site...")
        driver.get("https://api.ipify.org?format=json")
        import time
        time.sleep(3)
        
        # Get page source
        page_source = driver.page_source
        logger.info(f"Page content: {page_source[:200]}")
        
        logger.info("\n✅ TEST SUCCESSFUL!")
        logger.info(f"Profile {profile_name} is working with proxy {proxy_info['host']}:{proxy_info['port']}")
        
        # Keep browser open
        input("\nPress Enter to close browser and stop profile...")
        
        driver.quit()
        
    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 6: Stop profile
    logger.info("\n[STEP 6] Stopping profile...")
    multilogin_handler.stop_profile(profile_id)
    logger.info("✓ Profile stopped")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
