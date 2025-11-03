#!/usr/bin/env python3
"""
Test freecaptcha với GameSeal
"""
import time
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import freecaptcha

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("="*70)
    logger.info("TEST: GameSeal with freecaptcha")
    logger.info("="*70)
    
    # Start browser
    logger.info("Starting browser...")
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options, version_main=None)
    driver.maximize_window()
    
    try:
        # Open GameSeal register page
        logger.info("Opening GameSeal register page...")
        driver.get("https://gameseal.com/account/register")
        time.sleep(3)
        
        # Get reCAPTCHA site key
        logger.info("\n[STEP 1] Finding reCAPTCHA site key...")
        site_key = driver.execute_script("""
            // Tìm site key trong iframe hoặc script
            var iframes = document.querySelectorAll('iframe[src*="recaptcha"]');
            for (var i = 0; i < iframes.length; i++) {
                var src = iframes[i].src;
                var match = src.match(/[?&]k=([^&]+)/);
                if (match) return match[1];
            }
            
            // Tìm trong scripts
            var scripts = document.querySelectorAll('script');
            for (var i = 0; i < scripts.length; i++) {
                var content = scripts[i].textContent;
                var match = content.match(/sitekey['"\\s:]+['"]([^'"]+)['"]/i);
                if (match) return match[1];
            }
            
            return null;
        """)
        
        if site_key:
            logger.info(f"✓ Found site key: {site_key}")
        else:
            logger.error("✗ Could not find reCAPTCHA site key!")
            return False
        
        # Build anchor URL
        anchor_url = f"https://www.google.com/recaptcha/api2/anchor?ar=1&k={site_key}&co=aHR0cHM6Ly9nYW1lc2VhbC5jb206NDQz&hl=en&v=hbAq-YhJxOnlU-7cpgBoAJHb&size=invisible&cb=freecaptcha"
        
        logger.info(f"\n[STEP 2] Solving reCAPTCHA with freecaptcha...")
        logger.info(f"Anchor URL: {anchor_url[:100]}...")
        
        # Solve captcha
        token = freecaptcha.solve(anchor_url)
        
        if token:
            logger.info(f"✓ Got reCAPTCHA token: {token[:50]}...")
        else:
            logger.error("✗ Failed to get reCAPTCHA token!")
            return False
        
        # Fill form
        logger.info("\n[STEP 3] Filling registration form...")
        
        import random
        email = f"test_{random.randint(10000, 99999)}@outlook.com"
        password = "Abcdn@12345"
        
        # Email
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_input.clear()
        email_input.send_keys(email)
        logger.info(f"✓ Email: {email}")
        time.sleep(1)
        
        # Passwords
        password_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        password_inputs[0].clear()
        password_inputs[0].send_keys(password)
        password_inputs[1].clear()
        password_inputs[1].send_keys(password)
        logger.info("✓ Passwords filled")
        time.sleep(1)
        
        # Checkbox
        try:
            checkbox_label = driver.find_element(By.XPATH, "//label[contains(text(), 'Save 10%')]")
            checkbox_label.click()
            logger.info("✓ Checkbox checked")
            time.sleep(1)
        except:
            pass
        
        # Inject reCAPTCHA token
        logger.info("\n[STEP 4] Injecting reCAPTCHA token...")
        driver.execute_script(f"""
            var textarea = document.querySelector('[name="g-recaptcha-response"]');
            if (textarea) {{
                textarea.value = "{token}";
                textarea.innerHTML = "{token}";
            }}
        """)
        logger.info("✓ Token injected")
        
        # Submit form
        logger.info("\n[STEP 5] Submitting form...")
        
        # Trigger form validation và submit
        driver.execute_script(f"""
            // Set token
            var textarea = document.querySelector('[name="g-recaptcha-response"]');
            if (textarea) {{
                textarea.value = "{token}";
            }}
            
            // Enable button
            var button = document.querySelector('button.btn-primary.is-big');
            if (button) {{
                button.removeAttribute('disabled');
            }}
            
            // Submit form
            var form = document.querySelector('form.register-form');
            if (form) {{
                form.submit();
            }}
        """)
        
        # Wait for response
        logger.info("Waiting for response...")
        time.sleep(5)
        
        current_url = driver.current_url
        logger.info(f"Current URL: {current_url}")
        
        if current_url != "https://gameseal.com/account/register":
            logger.info(f"✅ SUCCESS! Redirected to: {current_url}")
        else:
            logger.warning("⚠️ Still at register page")
            
            # Check for errors
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR, ".error, .alert")
                for err in error_elements:
                    if err.is_displayed() and err.text:
                        logger.error(f"Error: {err.text}")
            except:
                pass
        
        # Keep browser open
        logger.info("\nBrowser will stay open for 30 seconds...")
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
        logger.info("\n⚠️  Interrupted")
        exit(1)
