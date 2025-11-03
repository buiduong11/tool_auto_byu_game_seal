#!/usr/bin/env python3
"""
Test verify email với Multilogin đang chạy
Sử dụng khi:
- Tab mail browser đang mở (Chrome thường)
- Tab Multilogin đang mở
"""
import sys
import time
import logging
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Email đang test - Mail mới (index 3)
TEST_EMAIL = "c2thrueb102700@outlook.com"
WMHOTMAIL_EMAIL = "w7ko7v@wmhotmail.com"
WMHOTMAIL_CODE = "945518"

# Port Multilogin - THAY ĐỔI PORT NÀY
MULTILOGIN_PORT = "56564"

print(f"Using Multilogin port: {MULTILOGIN_PORT}")

def test_verify_with_multilogin():
    """Test verify email với Multilogin đang chạy"""
    logger.info("="*70)
    logger.info("TEST: VERIFY EMAIL WITH EXISTING MULTILOGIN")
    logger.info("="*70)
    logger.info(f"Email: {TEST_EMAIL}")
    logger.info(f"Multilogin port: {MULTILOGIN_PORT}")
    
    mail_driver = None
    multilogin_driver = None
    
    try:
        # PART 1: Mở browser và login wmhotmail TRƯỚC (copy CHÍNH XÁC từ outlook_registration.py)
        logger.info("\n[PART 1] Opening mail browser...")
        logger.info("Starting Chrome browser for mail...")
        options = webdriver.ChromeOptions()
        # Thêm options để tránh detection (GIỐNG FILE CHÍNH)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        mail_driver = webdriver.Chrome(options=options)
        mail_driver.maximize_window()
        logger.info("✓ Mail browser started")
        time.sleep(2)
        
        # Login wmhotmail TRƯỚC (copy từ outlook_registration.py)
        logger.info("\n[STEP 1] Logging in to wmhotmail FIRST...")
        mail_driver.get("https://www.wmhotmail.com/")
        time.sleep(3)
        
        try:
            # Nhập email
            logger.info(f"Entering email: {WMHOTMAIL_EMAIL}")
            email_input = WebDriverWait(mail_driver, 10).until(
                EC.presence_of_element_located((By.ID, "rcmloginuser"))
            )
            email_input.clear()
            email_input.send_keys(WMHOTMAIL_EMAIL)
            time.sleep(1)
            
            # Nhập code
            logger.info(f"Entering code: {WMHOTMAIL_CODE}")
            code_input = mail_driver.find_element(By.ID, "rcmloginpwd")
            code_input.clear()
            code_input.send_keys(WMHOTMAIL_CODE)
            time.sleep(1)
            
            # Click login
            logger.info("Clicking login button...")
            login_btn = mail_driver.find_element(By.ID, "rcmloginsubmit")
            login_btn.click()
            time.sleep(5)
            
            # Check login success
            if "task=mail" in mail_driver.current_url:
                logger.info("✓ WMHotmail login successful!")
            else:
                logger.error("✗ WMHotmail login failed!")
                return False
        except Exception as e:
            logger.error(f"Failed to login wmhotmail: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        # Lưu tab wmhotmail
        wmhotmail_tab = mail_driver.current_window_handle
        
        # PART 2: Mở tab mới cho Outlook
        logger.info("\n[STEP 2] Opening Outlook in new tab...")
        mail_driver.switch_to.new_window('tab')
        time.sleep(2)
        
        outlook_tab = mail_driver.current_window_handle
        
        # Mở Outlook login page
        logger.info("Opening Outlook login page...")
        mail_driver.get("https://login.live.com/")
        time.sleep(5)
        
        # Save screenshot
        try:
            mail_driver.save_screenshot("/tmp/outlook_test_login.png")
            logger.info("Screenshot saved to /tmp/outlook_test_login.png")
        except:
            pass
        
        # Auto login Outlook (copy từ outlook_registration.py)
        logger.info("\n[STEP 3] Logging in to Outlook...")
        logger.info(f"Outlook email: {TEST_EMAIL}")
        logger.info(f"Current URL: {mail_driver.current_url}")
        
        # Nhập email - thử nhiều selector
        selectors = [
            (By.ID, "i0116"),
            (By.NAME, "loginfmt"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.CSS_SELECTOR, "input[name='loginfmt']")
        ]
        
        email_input = None
        for by, selector in selectors:
            try:
                logger.info(f"Trying selector: {by}={selector}")
                email_input = WebDriverWait(mail_driver, 5).until(
                    EC.presence_of_element_located((by, selector))
                )
                logger.info(f"✓ Found element with {by}={selector}")
                break
            except:
                continue
        
        if not email_input:
            logger.error("✗ Could not find email input with any selector!")
            return False
        
        email_input.clear()
        email_input.send_keys(TEST_EMAIL)
        time.sleep(1)
        
        # Submit bằng Enter thay vì click button
        logger.info("Submitting email...")
        email_input.send_keys(Keys.RETURN)
        time.sleep(5)
        
        # Screenshot trang verify
        mail_driver.save_screenshot("/tmp/outlook_verify_page.png")
        logger.info("Screenshot saved to /tmp/outlook_verify_page.png")
        
        # Nhập email phụ (wmhotmail) vào field Email (copy từ outlook_registration.py)
        logger.info(f"Entering wmhotmail email: {WMHOTMAIL_EMAIL}")
        
        # Tìm input email trên trang verify - thử nhiều selector
        email_verify_selectors = [
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.CSS_SELECTOR, "input[aria-label='Email']"),
            (By.CSS_SELECTOR, "input[name='otc']"),
            (By.XPATH, "//input[@type='text']")
        ]
        
        email_verify_input = None
        for by, selector in email_verify_selectors:
            try:
                logger.info(f"Trying input: {by}={selector}")
                email_verify_input = WebDriverWait(mail_driver, 3).until(
                    EC.presence_of_element_located((by, selector))
                )
                logger.info(f"✓ Found input with {by}={selector}")
                break
            except:
                continue
        
        if not email_verify_input:
            logger.error("✗ Could not find email verify input!")
            return False
        
        email_verify_input.clear()
        email_verify_input.send_keys(WMHOTMAIL_EMAIL)
        time.sleep(1)
        
        # Click Send code button
        logger.info("Clicking Send code button...")
        try:
            # Thử tìm button "Send code"
            send_code_btn = WebDriverWait(mail_driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send code')]"))
            )
            send_code_btn.click()
            logger.info("✓ Clicked Send code button")
        except:
            # Nếu không tìm thấy, dùng Enter
            logger.info("Send code button not found, using Enter...")
            email_verify_input.send_keys(Keys.RETURN)
        
        time.sleep(6)
        
        logger.info("✓ Outlook login submitted")
        logger.info("⏳ Waiting for verification code to be sent to wmhotmail...")
        time.sleep(5)  # Đợi email gửi về wmhotmail
        
        # Quay lại tab wmhotmail để đọc code
        logger.info("\n[STEP 4] Switching back to wmhotmail to read code...")
        mail_driver.switch_to.window(wmhotmail_tab)
        time.sleep(2)
        
        # Refresh inbox
        logger.info("Refreshing wmhotmail inbox...")
        mail_driver.refresh()
        time.sleep(5)
        
        # Đọc email từ Microsoft
        logger.info("Reading email from Microsoft...")
        time.sleep(3)
        
        try:
            # Click vào email đầu tiên
            first_email = WebDriverWait(mail_driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#messagelist tbody tr"))
            )
            first_email.click()
            logger.info("✓ Clicked first email")
            time.sleep(3)
            
            # Đọc nội dung email để lấy code
            email_body = mail_driver.find_element(By.ID, "messagecontainer")
            email_text = email_body.text
            logger.info(f"Email content preview: {email_text[:200]}")
            
            # Extract code (6 digits)
            import re
            code_match = re.search(r'\b\d{6}\b', email_text)
            if code_match:
                verification_code = code_match.group(0)
                logger.info(f"✓ Found verification code: {verification_code}")
            else:
                logger.error("Could not find verification code in email!")
                return False
                
        except Exception as e:
            logger.error(f"Failed to read email: {str(e)}")
            return False
        
        # Quay lại tab Outlook
        logger.info("\n[STEP 5] Switching back to Outlook tab...")
        mail_driver.switch_to.window(outlook_tab)
        time.sleep(2)
        
        # Nhập verification code
        logger.info(f"Entering verification code: {verification_code}")
        try:
            code_input = WebDriverWait(mail_driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='tel'], input[name='otc']"))
            )
            code_input.clear()
            code_input.send_keys(verification_code)
            logger.info("✓ Entered code")
            time.sleep(1)
            
            # Click Verify/Submit
            verify_btn = mail_driver.find_element(By.ID, "idSIButton9")
            verify_btn.click()
            logger.info("✓ Clicked Verify")
            time.sleep(5)
            
            # Handle "Stay signed in?" - click No
            try:
                no_btn = WebDriverWait(mail_driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "idBtn_Back"))
                )
                no_btn.click()
                logger.info("✓ Clicked No (Stay signed in)")
                time.sleep(3)
            except:
                pass
                
        except Exception as e:
            logger.error(f"Failed to enter code: {str(e)}")
            return False
        
        # Navigate to mail
        logger.info("\n[STEP 6] Navigating to Outlook inbox...")
        mail_driver.get("https://outlook.live.com/mail/")
        time.sleep(8)
        
        # Click vào email đầu tiên (GameSeal)
        logger.info("\n[STEP 7] Looking for GameSeal email...")
        time.sleep(5)
        
        email_selectors = [
            (By.CSS_SELECTOR, "div[role='listitem']:first-child"),
            (By.CSS_SELECTOR, "div[role='option']:first-child"),
            (By.XPATH, "(//div[@role='listitem'])[1]")
        ]
        
        clicked = False
        for by, selector in email_selectors:
            try:
                logger.info(f"Trying: {selector}")
                first_email = WebDriverWait(mail_driver, 5).until(
                    EC.element_to_be_clickable((by, selector))
                )
                first_email.click()
                logger.info("✓ Clicked first email")
                clicked = True
                time.sleep(3)
                break
            except Exception as e:
                logger.info(f"Failed: {str(e)[:50]}")
                continue
        
        if not clicked:
            logger.warning("Could not click automatically, waiting for manual click...")
            time.sleep(10)
        
        # Tìm verification link
        logger.info("\n[STEP 2] Looking for verification link...")
        time.sleep(3)
        
        link_selectors = [
            (By.PARTIAL_LINK_TEXT, "ACTIVATE NOW"),
            (By.PARTIAL_LINK_TEXT, "Activate"),
            (By.XPATH, "//a[contains(@href, 'verify')]"),
            (By.XPATH, "//a[contains(@href, 'activate')]"),
            (By.CSS_SELECTOR, "a[href*='gameseal.com']")
        ]
        
        verification_link = None
        for by, selector in link_selectors:
            try:
                logger.info(f"Trying: {selector}")
                link_element = WebDriverWait(mail_driver, 3).until(
                    EC.presence_of_element_located((by, selector))
                )
                verification_link = link_element.get_attribute('href')
                logger.info(f"✓ Found: {verification_link}")
                break
            except:
                continue
        
        if not verification_link:
            logger.error("✗ Could not find link automatically")
            logger.info("Showing all links...")
            try:
                all_links = mail_driver.find_elements(By.TAG_NAME, "a")
                for link in all_links[:20]:
                    href = link.get_attribute('href')
                    if href and 'gameseal' in href.lower():
                        logger.info(f"  Found: {href}")
                        verification_link = href
                        break
            except:
                pass
        
        if not verification_link:
            logger.error("✗ No verification link found!")
            return False
        
        # PART 3: Connect to Multilogin
        logger.info("\n[STEP 8] Connecting to Multilogin...")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{MULTILOGIN_PORT}")
        
        try:
            multilogin_driver = webdriver.Chrome(options=chrome_options)
            logger.info(f"✓ Connected to Multilogin on port {MULTILOGIN_PORT}")
        except Exception as e:
            logger.error(f"✗ Could not connect to Multilogin: {str(e)}")
            logger.error("Make sure Multilogin browser is still running!")
            return False
        
        # Mở tab mới trong Multilogin
        logger.info("\n[STEP 9] Opening new tab in Multilogin...")
        multilogin_driver.switch_to.new_window('tab')
        time.sleep(2)
        
        logger.info(f"Navigating to: {verification_link}")
        multilogin_driver.get(verification_link)
        time.sleep(5)
        
        logger.info("\n" + "="*70)
        logger.info("✓ VERIFICATION COMPLETED!")
        logger.info("="*70)
        logger.info(f"Current URL: {multilogin_driver.current_url}")
        
        logger.info("\nKeeping browsers open for 30 seconds...")
        time.sleep(30)
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if mail_driver:
            try:
                mail_driver.quit()
            except:
                pass

if __name__ == "__main__":
    test_verify_with_multilogin()
