#!/usr/bin/env python3
"""
Simple test để verify email GameSeal
Chạy script này khi:
- Đã có tab Outlook mở với mail browser
- Đã có tab Multilogin mở
"""
import time
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_verify_workflow():
    """Test verify email workflow với browser mới"""
    logger.info("="*70)
    logger.info("TEST: VERIFY GAMESEAL EMAIL WORKFLOW")
    logger.info("="*70)
    
    # Email đang test
    outlook_email = input("Enter Outlook email: ").strip()
    
    try:
        # Mở browser mới
        logger.info("Opening browser...")
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options, version_main=None)
        driver.maximize_window()
        
        # STEP 1: Mở Outlook
        logger.info("\n[STEP 1] Opening Outlook...")
        driver.get("https://outlook.live.com/mail/")
        
        input("\n⏸️  Press ENTER after you logged in to Outlook...")
        
        # STEP 2: Đợi mail load
        logger.info("\n[STEP 2] Waiting for inbox to load...")
        time.sleep(8)
        
        # STEP 3: Click vào email đầu tiên
        logger.info("\n[STEP 3] Looking for GameSeal email...")
        time.sleep(5)
        
        email_selectors = [
            (By.CSS_SELECTOR, "div[role='listitem']:first-child"),
            (By.CSS_SELECTOR, "div[role='option']:first-child"),
            (By.XPATH, "(//div[@role='listitem'])[1]"),
            (By.CSS_SELECTOR, "div.customScrollBar > div:first-child")
        ]
        
        clicked = False
        for by, selector in email_selectors:
            try:
                logger.info(f"Trying: {selector}")
                first_email = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by, selector))
                )
                first_email.click()
                logger.info("✓ Clicked first email")
                clicked = True
                time.sleep(3)
                break
            except:
                continue
        
        if not clicked:
            logger.error("✗ Could not click email automatically")
            input("⏸️  Please click the GameSeal email manually, then press ENTER...")
        
        # STEP 4: Tìm verification link
        logger.info("\n[STEP 4] Looking for verification link...")
        time.sleep(3)
        
        link_selectors = [
            (By.PARTIAL_LINK_TEXT, "ACTIVATE NOW"),
            (By.PARTIAL_LINK_TEXT, "Activate"),
            (By.PARTIAL_LINK_TEXT, "verify"),
            (By.PARTIAL_LINK_TEXT, "Verify"),
            (By.XPATH, "//a[contains(@href, 'verify')]"),
            (By.XPATH, "//a[contains(@href, 'activate')]"),
            (By.CSS_SELECTOR, "a[href*='gameseal.com']")
        ]
        
        verification_link = None
        for by, selector in link_selectors:
            try:
                logger.info(f"Trying: {selector}")
                link_element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((by, selector))
                )
                verification_link = link_element.get_attribute('href')
                logger.info(f"✓ Found link: {verification_link}")
                break
            except:
                continue
        
        if not verification_link:
            logger.error("✗ Could not find verification link automatically")
            logger.info("\nTrying to show all links...")
            try:
                all_links = driver.find_elements(By.TAG_NAME, "a")
                logger.info(f"Found {len(all_links)} links in email:")
                for i, link in enumerate(all_links[:15]):
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    if href and 'gameseal' in href.lower():
                        logger.info(f"  [{i}] {text}: {href}")
                        if not verification_link:
                            verification_link = href
            except:
                pass
            
            if not verification_link:
                verification_link = input("\n⏸️  Please paste the verification link here: ").strip()
        
        # STEP 5: Mở tab mới và navigate
        logger.info("\n[STEP 5] Opening verification link in new tab...")
        driver.switch_to.new_window('tab')
        time.sleep(2)
        
        logger.info(f"Navigating to: {verification_link}")
        driver.get(verification_link)
        time.sleep(5)
        
        logger.info("\n" + "="*70)
        logger.info("✓ VERIFICATION COMPLETED!")
        logger.info("="*70)
        logger.info(f"Current URL: {driver.current_url}")
        
        input("\n⏸️  Press ENTER to close browser...")
        driver.quit()
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_verify_workflow()
