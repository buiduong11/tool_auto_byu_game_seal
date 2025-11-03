#!/usr/bin/env python3
"""
Test script để verify email GameSeal
Giả sử đã có:
- Tab Outlook đang mở với mail
- Tab Multilogin đang mở
"""
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_verify_email():
    """Test verify email workflow"""
    logger.info("="*70)
    logger.info("TEST: VERIFY GAMESEAL EMAIL")
    logger.info("="*70)
    
    # Kết nối đến Chrome đang chạy (Outlook tab)
    # Giả sử bạn đã mở Chrome với remote debugging
    # chrome --remote-debugging-port=9222
    
    outlook_email = "amy51_gildner@outlook.com"  # Thay bằng email đang test
    
    try:
        # Connect to existing Chrome session
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=chrome_options)
        
        logger.info(f"✓ Connected to Chrome")
        logger.info(f"Current URL: {driver.current_url}")
        
        # Lấy tất cả tabs
        all_windows = driver.window_handles
        logger.info(f"Total tabs: {len(all_windows)}")
        
        # Tìm tab Outlook
        outlook_tab = None
        multilogin_tab = None
        
        for window in all_windows:
            driver.switch_to.window(window)
            current_url = driver.current_url
            logger.info(f"Tab: {current_url}")
            
            if "outlook.live.com" in current_url:
                outlook_tab = window
                logger.info("✓ Found Outlook tab")
            elif "gameseal.com" in current_url:
                multilogin_tab = window
                logger.info("✓ Found Multilogin tab")
        
        if not outlook_tab:
            logger.error("✗ Outlook tab not found! Please open Outlook first.")
            return False
        
        if not multilogin_tab:
            logger.error("✗ Multilogin tab not found! Please open GameSeal first.")
            return False
        
        # STEP 1: Switch to Outlook tab
        logger.info("\n[STEP 1] Switching to Outlook tab...")
        driver.switch_to.window(outlook_tab)
        time.sleep(2)
        
        # STEP 2: Navigate to mail (nếu chưa ở mail)
        if "/mail/" not in driver.current_url:
            logger.info("[STEP 2] Navigating to Outlook mail...")
            driver.get("https://outlook.live.com/mail/")
            time.sleep(8)
        else:
            logger.info("[STEP 2] Already in mail, waiting...")
            time.sleep(5)
        
        # STEP 3: Click vào email đầu tiên (GameSeal)
        logger.info("\n[STEP 3] Looking for GameSeal email...")
        time.sleep(5)
        
        email_selectors = [
            (By.CSS_SELECTOR, "div[role='listitem']:first-child"),
            (By.CSS_SELECTOR, "div[role='option']:first-child"),
            (By.XPATH, "(//div[@role='listitem'])[1]"),
            (By.CSS_SELECTOR, "div.customScrollBar > div:first-child"),
            (By.XPATH, "//div[contains(@class, 'customScrollBar')]//div[@role='listitem'][1]")
        ]
        
        clicked = False
        for by, selector in email_selectors:
            try:
                logger.info(f"Trying selector: {by}={selector}")
                first_email = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by, selector))
                )
                first_email.click()
                logger.info("✓ Clicked first email")
                clicked = True
                time.sleep(3)
                break
            except Exception as e:
                logger.info(f"Failed: {str(e)}")
                continue
        
        if not clicked:
            logger.error("✗ Could not click email")
            return False
        
        # STEP 4: Tìm verification link
        logger.info("\n[STEP 4] Looking for verification link...")
        
        link_selectors = [
            (By.PARTIAL_LINK_TEXT, "ACTIVATE NOW"),
            (By.PARTIAL_LINK_TEXT, "Activate"),
            (By.PARTIAL_LINK_TEXT, "verify"),
            (By.PARTIAL_LINK_TEXT, "Verify"),
            (By.PARTIAL_LINK_TEXT, "confirm"),
            (By.XPATH, "//a[contains(@href, 'verify')]"),
            (By.XPATH, "//a[contains(@href, 'activate')]"),
            (By.XPATH, "//a[contains(text(), 'ACTIVATE')]"),
            (By.CSS_SELECTOR, "a[href*='gameseal.com']")
        ]
        
        verification_link = None
        for by, selector in link_selectors:
            try:
                logger.info(f"Trying to find link: {by}={selector}")
                link_element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((by, selector))
                )
                verification_link = link_element.get_attribute('href')
                logger.info(f"✓ Found verification link: {verification_link}")
                break
            except Exception as e:
                logger.info(f"Not found: {str(e)}")
                continue
        
        if not verification_link:
            logger.error("✗ Could not find verification link")
            logger.info("Trying to get all links in email...")
            try:
                all_links = driver.find_elements(By.TAG_NAME, "a")
                logger.info(f"Found {len(all_links)} links:")
                for link in all_links[:10]:  # Show first 10
                    href = link.get_attribute('href')
                    text = link.text
                    if href:
                        logger.info(f"  - {text}: {href}")
            except:
                pass
            return False
        
        # STEP 5: Switch to Multilogin tab
        logger.info("\n[STEP 5] Switching to Multilogin tab...")
        driver.switch_to.window(multilogin_tab)
        time.sleep(2)
        
        # STEP 6: Mở tab mới và navigate to verification link
        logger.info("\n[STEP 6] Opening new tab in Multilogin...")
        driver.switch_to.new_window('tab')
        time.sleep(2)
        
        logger.info(f"Navigating to: {verification_link}")
        driver.get(verification_link)
        time.sleep(5)
        
        logger.info("\n" + "="*70)
        logger.info("✓ VERIFICATION COMPLETED!")
        logger.info("="*70)
        logger.info(f"Current URL: {driver.current_url}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("\n⚠️  IMPORTANT:")
    logger.info("1. Make sure Chrome is running with: chrome --remote-debugging-port=9222")
    logger.info("2. Make sure you have Outlook tab open with GameSeal email")
    logger.info("3. Make sure you have Multilogin/GameSeal tab open")
    logger.info("\nStarting in 3 seconds...")
    time.sleep(3)
    
    test_verify_email()
