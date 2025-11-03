#!/usr/bin/env python3
"""
Test GameSeal Guest Checkout Flow
Kiểm tra xem khi không login/register thì flow như thế nào
"""
import time
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("="*70)
    logger.info("TEST: GameSeal Guest Checkout Flow")
    logger.info("="*70)
    
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options, version_main=None)
    driver.maximize_window()
    
    try:
        # Step 1: Mở trang game
        logger.info("\n[STEP 1] Opening game page...")
        driver.get("https://gameseal.com/shape-of-dreams-pc-steam-key-global")
        time.sleep(3)
        
        # Step 2: Click "Add to cart" hoặc "Buy now"
        logger.info("\n[STEP 2] Looking for Add to Cart button...")
        try:
            # Tìm button add to cart
            add_to_cart = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.add-to-cart, button[data-action='add-to-cart']"))
            )
            add_to_cart.click()
            logger.info("✓ Clicked Add to Cart")
            time.sleep(2)
        except:
            logger.info("Add to Cart button not found, trying alternative...")
        
        # Step 3: Go to cart/checkout
        logger.info("\n[STEP 3] Going to checkout...")
        driver.get("https://gameseal.com/checkout")
        time.sleep(3)
        
        # Step 4: Check page content
        logger.info("\n[STEP 4] Analyzing checkout page...")
        
        # Check xem có yêu cầu login không
        page_source = driver.page_source
        
        # Check các elements
        checks = {
            "Email input (#personalMail-desktop)": "#personalMail-desktop",
            "Login required": "login required",
            "Register required": "register required",
            "Guest checkout allowed": "guest",
            "Continue to payment": "CONTINUE TO PAYMENT"
        }
        
        for check_name, check_text in checks.items():
            if check_text in page_source.lower():
                logger.info(f"✓ Found: {check_name}")
            else:
                logger.info(f"✗ Not found: {check_name}")
        
        # Check email input
        try:
            email_input = driver.find_element(By.CSS_SELECTOR, "#personalMail-desktop")
            logger.info(f"\n✓ Email input found!")
            logger.info(f"  Placeholder: {email_input.get_attribute('placeholder')}")
            logger.info(f"  Required: {email_input.get_attribute('required')}")
        except:
            logger.info("\n✗ Email input NOT found")
        
        # Check login/register links
        try:
            login_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Login') or contains(text(), 'Sign in')]")
            if login_links:
                logger.info(f"\n⚠️ Found {len(login_links)} login link(s)")
                for link in login_links:
                    logger.info(f"  - {link.text}: {link.get_attribute('href')}")
            else:
                logger.info("\n✓ No login links found - Guest checkout OK")
        except:
            pass
        
        # Check continue button
        try:
            continue_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'CONTINUE')]")
            logger.info(f"\n✓ Continue button found: {continue_btn.text}")
            logger.info(f"  Disabled: {continue_btn.get_attribute('disabled')}")
        except:
            logger.info("\n✗ Continue button NOT found")
        
        # Take screenshot
        driver.save_screenshot("/tmp/gameseal_checkout.png")
        logger.info("\n📸 Screenshot saved to /tmp/gameseal_checkout.png")
        
        # Step 5: Test nhập email
        logger.info("\n[STEP 5] Testing email input...")
        try:
            email_input = driver.find_element(By.CSS_SELECTOR, "#personalMail-desktop")
            email_input.clear()
            email_input.send_keys("test@example.com")
            time.sleep(2)
            
            # Check button state after email
            continue_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'CONTINUE')]")
            is_disabled = continue_btn.get_attribute('disabled')
            logger.info(f"After entering email, button disabled: {is_disabled}")
            
            if not is_disabled:
                logger.info("✅ Button ENABLED - Guest checkout works!")
            else:
                logger.info("⚠️ Button still disabled - May need more info")
        except Exception as e:
            logger.error(f"Error testing email: {str(e)}")
        
        # Keep browser open
        logger.info("\n" + "="*70)
        logger.info("Browser will stay open for 30 seconds...")
        logger.info("="*70)
        time.sleep(30)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted")
