#!/usr/bin/env python3
"""
Test login wmhotmail bằng Selenium
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_wmhotmail_login(debug_port, email, code):
    """
    Test login wmhotmail
    
    Args:
        debug_port: Port của browser
        email: Email wmhotmail
        code: Code để login
    """
    try:
        logger.info(f"Connecting to browser on port {debug_port}...")
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
        
        driver = webdriver.Chrome(options=options)
        logger.info("✓ Connected to browser")
        
        # Mở wmhotmail
        logger.info("\nOpening wmhotmail.com...")
        driver.get("http://mail.wmhotmail.com")
        time.sleep(3)
        
        # Nhập email
        logger.info(f"Entering email: {email}")
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "rcmloginuser"))
        )
        email_input.clear()
        email_input.send_keys(email)
        time.sleep(1)
        
        # Nhập code
        logger.info(f"Entering code: {code}")
        code_input = driver.find_element(By.ID, "rcmloginpwd")
        code_input.clear()
        code_input.send_keys(code)
        time.sleep(1)
        
        # Click login
        logger.info("Clicking login button...")
        login_btn = driver.find_element(By.ID, "rcmloginsubmit")
        login_btn.click()
        time.sleep(5)
        
        # Check login success
        current_url = driver.current_url
        logger.info(f"Current URL: {current_url}")
        
        if "task=mail" in current_url:
            logger.info("✓ Login successful!")
            
            # Đợi inbox load
            time.sleep(3)
            
            # Lấy danh sách email
            logger.info("\nGetting email list...")
            try:
                # Tìm email rows
                email_rows = driver.find_elements(By.CSS_SELECTOR, "table.messagelist tbody tr")
                logger.info(f"Found {len(email_rows)} emails")
                
                if len(email_rows) > 0:
                    # Click vào email đầu tiên
                    logger.info("Clicking first email...")
                    email_rows[0].click()
                    time.sleep(3)
                    
                    # Đọc nội dung email
                    logger.info("Reading email content...")
                    email_body = driver.find_element(By.ID, "messagebody")
                    content = email_body.text
                    logger.info(f"Email content:\n{content[:200]}...")
                    
                    # Tìm verification code (thường là 6 số)
                    import re
                    codes = re.findall(r'\b\d{6}\b', content)
                    if codes:
                        logger.info(f"✓ Found verification code: {codes[0]}")
                        return codes[0]
                    else:
                        logger.warning("No verification code found")
                        
            except Exception as e:
                logger.error(f"Error reading emails: {str(e)}")
            
            return True
        else:
            logger.error("✗ Login failed!")
            return False
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    
    print("=" * 70)
    print("TEST WMHOTMAIL LOGIN")
    print("=" * 70)
    
    # Test data
    EMAIL = "cjlu8s@wmhotmail.com"
    CODE = "552714"
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9222
    
    print(f"\nEmail: {EMAIL}")
    print(f"Code: {CODE}")
    print(f"Port: {PORT}")
    
    test_wmhotmail_login(PORT, EMAIL, CODE)
