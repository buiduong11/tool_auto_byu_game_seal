#!/usr/bin/env python3
"""
Test script để test click button Continue trên GameSeal register form
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
    logger.info("TEST: GameSeal Register Button Click")
    logger.info("="*70)
    
    # Khởi tạo undetected Chrome browser để bypass bot detection
    logger.info("Starting undetected Chrome browser...")
    
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = uc.Chrome(options=options, version_main=None)
    driver.maximize_window()
    
    try:
        # Mở trang GameSeal register
        logger.info("Opening GameSeal register page...")
        driver.get("https://gameseal.com/account/register")
        time.sleep(3)
        
        # Điền form
        logger.info("\n[STEP 1] Filling registration form...")
        
        # Email - dùng random email
        import random
        random_email = f"test_{random.randint(10000, 99999)}@outlook.com"
        
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_input.clear()
        email_input.send_keys(random_email)
        logger.info(f"✓ Email filled: {random_email}")
        time.sleep(1)
        
        # Password
        password_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        if len(password_inputs) >= 2:
            password_inputs[0].clear()
            password_inputs[0].send_keys("Abcdn@12345")
            logger.info("✓ Password filled")
            time.sleep(1)
            
            password_inputs[1].clear()
            password_inputs[1].send_keys("Abcdn@12345")
            logger.info("✓ Repeat password filled")
            time.sleep(1)
        
        # Check newsletter checkbox - QUAN TRỌNG!
        logger.info("Checking newsletter checkbox...")
        try:
            # Scroll đến checkbox
            checkbox_container = driver.find_element(By.XPATH, "//label[contains(text(), 'Save 10%')]")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox_container)
            time.sleep(1)
            
            # Click vào label thay vì input (dễ click hơn)
            checkbox_container.click()
            logger.info("✓ Newsletter checkbox clicked")
            time.sleep(1)
            
            # Verify checkbox đã checked
            checkbox_input = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
            if checkbox_input.is_selected():
                logger.info("✓ Checkbox is now checked!")
            else:
                logger.warning("⚠️ Checkbox still not checked, trying input directly...")
                checkbox_input.click()
                time.sleep(0.5)
        except Exception as e:
            logger.error(f"Failed to check newsletter checkbox: {str(e)}")
        
        # Tìm button Continue
        logger.info("\n[STEP 2] Finding Continue button...")
        
        # Thử nhiều selector - dựa trên inspector
        selectors = [
            ('CSS', 'button.btn.btn-primary.is-big.w-100.has-no-shadow.text-uppercase'),
            ('CSS', 'button.btn-primary.is-big'),
            ('CSS', 'button.has-no-shadow'),
            ('XPATH', '//button[@role="button" and contains(@class, "btn-primary")]'),
            ('XPATH', '//button[contains(text(), "CONTINUE")]'),
            ('CSS', 'div.register-submit > button'),
            ('CSS', 'form.register-form button[type="submit"]')
        ]
        
        button_found = None
        for method, selector in selectors:
            try:
                logger.info(f"Trying {method}: {selector}")
                if method == 'CSS':
                    button = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                else:
                    button = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                
                if button:
                    logger.info(f"✓ Found button with {method}: {selector}")
                    logger.info(f"  Button text: {button.text}")
                    logger.info(f"  Button is displayed: {button.is_displayed()}")
                    logger.info(f"  Button is enabled: {button.is_enabled()}")
                    button_found = button
                    break
            except Exception as e:
                logger.info(f"  Failed: {str(e)[:50]}")
                continue
        
        if not button_found:
            logger.error("❌ Could not find Continue button with any selector!")
            logger.info("\nPage source preview:")
            logger.info(driver.page_source[:2000])
            return False
        
        # Debug: Check form state trước khi click
        logger.info("\n[DEBUG] Checking form state before clicking...")
        
        # Check email value
        email_value = driver.execute_script("return document.querySelector('input[type=\"email\"]').value;")
        logger.info(f"Email value: {email_value}")
        
        # Check password values
        password_values = driver.execute_script("return Array.from(document.querySelectorAll('input[type=\"password\"]')).map(p => p.value);")
        logger.info(f"Password values: {password_values}")
        
        # Check checkbox state
        checkbox_checked = driver.execute_script("return document.querySelector('input[type=\"checkbox\"]').checked;")
        logger.info(f"Checkbox checked: {checkbox_checked}")
        
        # Check button text
        button_text = button_found.text
        logger.info(f"Button text: '{button_text}'")
        
        # Check if button is really the Continue button
        button_html = driver.execute_script("return arguments[0].outerHTML;", button_found)
        logger.info(f"Button HTML: {button_html[:200]}")
        
        # Get reCAPTCHA token trước khi submit
        logger.info("\n[STEP 3] Getting reCAPTCHA token...")
        
        # Đợi reCAPTCHA load
        time.sleep(3)
        
        # Lấy reCAPTCHA token từ page
        recaptcha_token = None
        try:
            # reCAPTCHA v3 thường lưu token trong textarea
            recaptcha_token = driver.execute_script("""
                var token = document.querySelector('[name="g-recaptcha-response"]');
                return token ? token.value : null;
            """)
            
            if recaptcha_token:
                logger.info(f"✓ Got reCAPTCHA token: {recaptcha_token[:50]}...")
            else:
                logger.warning("⚠️ No reCAPTCHA token found, trying to trigger it...")
                
                # Trigger reCAPTCHA bằng cách execute grecaptcha
                driver.execute_script("""
                    if (typeof grecaptcha !== 'undefined') {
                        grecaptcha.ready(function() {
                            grecaptcha.execute();
                        });
                    }
                """)
                time.sleep(3)
                
                recaptcha_token = driver.execute_script("""
                    var token = document.querySelector('[name="g-recaptcha-response"]');
                    return token ? token.value : null;
                """)
                
                if recaptcha_token:
                    logger.info(f"✓ Got reCAPTCHA token after trigger: {recaptcha_token[:50]}...")
        except Exception as e:
            logger.error(f"Failed to get reCAPTCHA token: {str(e)}")
        
        # Click button
        logger.info("\n[STEP 4] Submitting form...")
        
        # Scroll đến button
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_found)
        time.sleep(1)
        
        # Thử submit form
        click_methods = [
            ("Normal click", lambda b: b.click()),
            ("JavaScript click", lambda b: driver.execute_script("arguments[0].click();", b))
        ]
        
        for method_name, click_func in click_methods:
            try:
                logger.info(f"Trying: {method_name}")
                click_func(button_found)
                logger.info(f"✓ Clicked with {method_name}")
                
                # Đợi lâu hơn - có thể đang xử lý captcha hoặc validation
                logger.info("Waiting for response...")
                time.sleep(5)
                
                # Check URL sau khi click
                current_url = driver.current_url
                logger.info(f"Current URL after click: {current_url}")
                
                # Check for captcha
                try:
                    captcha_frames = driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha'], iframe[src*='captcha']")
                    if captcha_frames:
                        logger.warning(f"⚠️ Found {len(captcha_frames)} captcha iframe(s)!")
                except:
                    pass
                
                # Check console errors
                try:
                    logs = driver.get_log('browser')
                    for log in logs:
                        if log['level'] == 'SEVERE':
                            logger.error(f"Browser error: {log['message']}")
                except:
                    pass
                
                # Check for error messages
                try:
                    error_elements = driver.find_elements(By.CSS_SELECTOR, ".error, .alert, .invalid-feedback, [class*='error']")
                    if error_elements:
                        for err in error_elements:
                            if err.is_displayed() and err.text:
                                logger.error(f"Error message: {err.text}")
                except:
                    pass
                
                if current_url != "https://gameseal.com/account/register":
                    logger.info(f"✅ SUCCESS! URL changed to: {current_url}")
                    break
                else:
                    logger.warning(f"⚠️ URL still at register page")
            except Exception as e:
                logger.error(f"Failed with {method_name}: {str(e)}")
                continue
        
        # Đợi để user có thể xem kết quả
        logger.info("\n" + "="*70)
        logger.info("Test completed. Browser will stay open for 30 seconds...")
        logger.info("="*70)
        time.sleep(30)
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        logger.info("Closing browser...")
        driver.quit()

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
