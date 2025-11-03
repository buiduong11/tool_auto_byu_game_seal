#!/usr/bin/env python3
"""
Test mở tab mới - kết nối với browser đang chạy và mở tab mới
"""
import logging
import time
from selenium import webdriver
from selenium.webdriver.chromium.options import ChromiumOptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_open_new_tab():
    """Test mở tab mới với browser đang chạy"""
    
    # Thử các port phổ biến của Multilogin
    ports_to_try = [53765, 50332, 49417, 51157, 49373, 54924, 9222, 9223, 9224, 9225, 20000, 20001, 20002]
    
    driver = None
    
    # Tìm port đúng
    for port in ports_to_try:
        try:
            logger.info(f"Trying to connect on port {port}...")
            driver = webdriver.Remote(
                command_executor=f"http://127.0.0.1:{port}",
                options=ChromiumOptions()
            )
            logger.info(f"✓ Connected to browser on port {port}")
            break
        except Exception as e:
            logger.debug(f"Port {port} failed")
            continue
    
    if not driver:
        logger.error("❌ Could not connect to browser on any port!")
        return False
    
    try:
        
        # Lấy URL hiện tại
        current_url = driver.current_url
        logger.info(f"Current URL: {current_url}")
        
        # Lấy số tab hiện tại
        windows_before = driver.window_handles
        logger.info(f"Current tabs: {len(windows_before)}")
        
        # Mở tab mới
        logger.info("\nOpening new tab...")
        home_url = "https://gameseal.com/"
        
        driver.execute_script(f"window.open('{home_url}', '_blank');")
        time.sleep(2)
        
        # Kiểm tra số tab sau khi mở
        windows_after = driver.window_handles
        logger.info(f"Tabs after opening: {len(windows_after)}")
        
        if len(windows_after) > len(windows_before):
            logger.info("✓ New tab opened successfully!")
            
            # Switch sang tab mới
            driver.switch_to.window(windows_after[-1])
            logger.info(f"✓ Switched to new tab")
            
            # Verify URL
            new_tab_url = driver.current_url
            logger.info(f"New tab URL: {new_tab_url}")
            
            time.sleep(2)
            logger.info("\n✅ SUCCESS! New tab opened and switched")
            return True
        else:
            logger.error("❌ Failed to open new tab")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("TEST: OPEN NEW TAB")
    logger.info("=" * 70)
    logger.info("\nMake sure:")
    logger.info("1. Multilogin profile is running")
    logger.info("2. Update DEBUG_PORT in the code with actual port")
    logger.info("\n" + "=" * 70)
    
    success = test_open_new_tab()
    
    if success:
        logger.info("\n✅ Test passed!")
    else:
        logger.info("\n❌ Test failed!")
