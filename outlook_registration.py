#!/usr/bin/env python3
"""
Outlook Registration Flow:
1. Login wmhotmail (mail phụ)
2. Login Outlook (mail chính) → Outlook gửi code về mail phụ
3. Quay lại wmhotmail → Đọc email mới nhất → Lấy code
4. Quay lại Outlook → Nhập code → Login thành công
5. Đăng ký tài khoản GameSeal với Outlook email
6. Verify tài khoản qua email
"""
import time
import logging
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from gameseal_auto_login import GameSealAutoLogin
from multilogin import MultiLoginHandler
from proxy_handler import NineProxyHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_card_data(card_line):
    """
    Parse card data từ format MỚI:
    5312600162447956|04/29|441|Juan Ramon Ordonez|5048 sw 40TH ave|Fort Lauderdale|Florida|33314|US|9546358909|
    
    Format: card_number|exp_date|cvv|name|address|city|state|zip|country|phone|
    """
    try:
        # Split by |
        parts = [p.strip() for p in card_line.split('|')]
        
        if len(parts) < 8:
            logger.error(f"Invalid card data format: {card_line}")
            return None
        
        # Parse theo format mới
        card_number = parts[0] if len(parts) > 0 else ''
        exp_date = parts[1] if len(parts) > 1 else ''  # Format: 04/29
        cvv = parts[2] if len(parts) > 2 else ''
        name = parts[3] if len(parts) > 3 else ''
        address = parts[4] if len(parts) > 4 else ''
        city = parts[5] if len(parts) > 5 else ''
        state = parts[6] if len(parts) > 6 else ''
        zip_code = parts[7] if len(parts) > 7 else ''
        country = parts[8] if len(parts) > 8 else 'US'
        phone = parts[9] if len(parts) > 9 else ''
        
        return {
            'number': card_number,
            'exp_date': exp_date,
            'cvv': cvv,
            'name': name,
            'address': address,
            'city': city,
            'state': state,
            'zip': zip_code,
            'country': country,
            'phone': phone
        }
    except Exception as e:
        logger.error(f"Error parsing card data: {str(e)}")
        return None

class OutlookRegistrationFlow:
    def __init__(self, outlook_email, outlook_password, wmhotmail_email, wmhotmail_code, 
                 multilogin_profile_id=None):
        """
        Initialize Outlook registration flow
        
        Args:
            outlook_email: Outlook email chính (vd: catalinaart14_01582@outlook.com)
            outlook_password: Outlook password
            wmhotmail_email: WMHotmail email phụ (vd: p77jah@wmhotmail.com)
            wmhotmail_code: WMHotmail code để login
            multilogin_profile_id: Multilogin profile ID (optional)
        """
        self.outlook_email = outlook_email
        self.outlook_password = outlook_password
        self.wmhotmail_email = wmhotmail_email
        self.wmhotmail_code = wmhotmail_code
        self.multilogin_profile_id = multilogin_profile_id
        self.driver = None  # Chrome driver cho mail
        self.gameseal_automation = None  # GameSealAutoLogin instance
        self.wmhotmail_tab = None
        self.outlook_tab = None
    
    def start_browser(self):
        """Mở Chrome browser mới cho mail"""
        try:
            logger.info("Starting Chrome browser for mail...")
            options = webdriver.ChromeOptions()
            # Thêm options để tránh detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.maximize_window()
            logger.info("✓ Mail browser started")
            return True
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}")
            return False
    
    def start_multilogin_profile(self):
        """Start Multilogin profile và kết nối"""
        try:
            if not self.multilogin_profile_id:
                logger.error("No Multilogin profile ID provided!")
                return False
            
            logger.info(f"Starting Multilogin profile: {self.multilogin_profile_id}")
            
            # Dùng MultiLoginHandler để start profile
            multilogin_handler = MultiLoginHandler()
            
            # Login để lấy token
            logger.info("Logging in to Multilogin...")
            login_success, login_result = multilogin_handler.login()
            if not login_success:
                logger.error(f"Failed to login to Multilogin: {login_result.get('error')}")
                return False
            logger.info("✓ Logged in to Multilogin")
            
            # Start profile
            success, start_result = multilogin_handler.start_profile(self.multilogin_profile_id)
            
            if not success:
                logger.error(f"Failed to start profile: {start_result.get('error')}")
                return False
            
            debug_port = start_result.get("selenium_port")
            if not debug_port:
                logger.error("No debug port returned")
                return False
            
            logger.info(f"✓ Profile started on port: {debug_port}")
            
            # Kết nối với Multilogin browser
            self.multilogin_driver = GameSealAutoLogin(
                email=self.outlook_email,
                password=self.outlook_password,
                debug_port=int(debug_port),
                register_email=self.outlook_email,  # Outlook email để đăng ký GameSeal
                register_password=self.outlook_password  # Outlook password để đăng ký
            )
            
            if not self.multilogin_driver.connect_to_browser():
                logger.error("Failed to connect to Multilogin browser")
                return False
            
            logger.info("✓ Connected to Multilogin browser")
            return True
            
        except Exception as e:
            logger.error(f"Error starting Multilogin: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def login_wmhotmail(self):
        """Step 1: Login wmhotmail (mail phụ)"""
        try:
            logger.info("\n" + "="*70)
            logger.info("[STEP 1] Logging in to wmhotmail...")
            logger.info("="*70)
            
            # Mở wmhotmail
            self.driver.get("http://mail.wmhotmail.com")
            time.sleep(3)
            
            # Nhập email
            logger.info(f"Entering email: {self.wmhotmail_email}")
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "rcmloginuser"))
            )
            email_input.clear()
            email_input.send_keys(self.wmhotmail_email)
            time.sleep(1)
            
            # Nhập code
            logger.info(f"Entering code: {self.wmhotmail_code}")
            code_input = self.driver.find_element(By.ID, "rcmloginpwd")
            code_input.clear()
            code_input.send_keys(self.wmhotmail_code)
            time.sleep(1)
            
            # Click login
            logger.info("Clicking login button...")
            login_btn = self.driver.find_element(By.ID, "rcmloginsubmit")
            login_btn.click()
            time.sleep(5)
            
            # Check login success
            if "task=mail" in self.driver.current_url:
                logger.info("✓ WMHotmail login successful!")
                self.wmhotmail_tab = self.driver.current_window_handle
                return True
            else:
                logger.error("✗ WMHotmail login failed!")
                return False
                
        except Exception as e:
            logger.error(f"Error logging in wmhotmail: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def login_outlook(self):
        """Step 2: Mở tab mới và login Outlook (mail chính)"""
        try:
            logger.info("\n" + "="*70)
            logger.info("[STEP 2] Opening Outlook in new tab...")
            logger.info("="*70)
            
            # Mở tab mới
            self.driver.switch_to.new_window('tab')
            self.outlook_tab = self.driver.current_window_handle
            time.sleep(1)
            
            # Mở Outlook login
            self.driver.get("https://login.live.com")
            time.sleep(5)
            
            # Debug: print current URL and take screenshot
            logger.info(f"Current URL: {self.driver.current_url}")
            self.driver.save_screenshot("/tmp/outlook_login_page.png")
            logger.info("Screenshot saved to /tmp/outlook_login_page.png")
            
            # Nhập email - thử nhiều selector
            logger.info(f"Entering Outlook email: {self.outlook_email}")
            
            # Thử tìm element bằng nhiều cách
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
                    email_input = WebDriverWait(self.driver, 5).until(
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
            email_input.send_keys(self.outlook_email)
            time.sleep(1)
            
            # Submit bằng Enter thay vì click button
            logger.info("Submitting email...")
            email_input.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Screenshot trang verify
            self.driver.save_screenshot("/tmp/outlook_verify_page.png")
            logger.info("Screenshot saved to /tmp/outlook_verify_page.png")
            
            # Nhập email phụ (wmhotmail) vào field Email
            logger.info(f"Entering wmhotmail email: {self.wmhotmail_email}")
            
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
                    email_verify_input = WebDriverWait(self.driver, 3).until(
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
            email_verify_input.send_keys(self.wmhotmail_email)
            time.sleep(1)
            
            # Click Send code button
            logger.info("Clicking Send code button...")
            try:
                # Thử tìm button "Send code"
                send_code_btn = WebDriverWait(self.driver, 5).until(
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
            
            return True
            
        except Exception as e:
            logger.error(f"Error logging in Outlook: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_verification_code_from_wmhotmail(self):
        """Step 3: Quay lại wmhotmail, refresh và lấy verification code"""
        try:
            logger.info("\n" + "="*70)
            logger.info("[STEP 3] Getting verification code from wmhotmail...")
            logger.info("="*70)
            
            # Switch về tab wmhotmail
            self.driver.switch_to.window(self.wmhotmail_tab)
            time.sleep(2)
            
            # Refresh inbox
            logger.info("Refreshing inbox...")
            self.driver.refresh()
            time.sleep(5)
            
            # Tìm và click vào email đầu tiên (mới nhất)
            logger.info("Opening latest email from Microsoft...")
            
            # Debug: Save screenshot
            self.driver.save_screenshot("/tmp/wmhotmail_inbox.png")
            logger.info("Screenshot saved to /tmp/wmhotmail_inbox.png")
            
            # Roundcube Webmail selectors
            selectors = [
                "#messagelist tbody tr",  # Roundcube message list
                "table#messagelist tbody tr",
                "tr.message",
                "#rcmrow1",  # Roundcube first row ID
                "tbody tr[id^='rcmrow']",  # Roundcube rows
                "table.records-table tbody tr"
            ]
            
            clicked = False
            for selector in selectors:
                try:
                    emails = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"Trying selector '{selector}': found {len(emails)} elements")
                    if emails:
                        emails[0].click()
                        clicked = True
                        logger.info(f"✓ Clicked first email with selector: {selector}")
                        break
                except Exception as e:
                    logger.info(f"Failed with selector '{selector}': {str(e)}")
                    continue
            
            if not clicked:
                logger.error("Could not click on first email with any selector")
                logger.info("Page source preview:")
                logger.info(self.driver.page_source[:1000])
                return None
            
            time.sleep(3)
            
            # Đọc nội dung email - có thể trong iframe
            logger.info("Reading email content...")
            
            # Thử đọc từ iframe trước
            try:
                iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe#messagecontframe")
                self.driver.switch_to.frame(iframe)
                email_body = self.driver.find_element(By.TAG_NAME, "body")
                content = email_body.text
                self.driver.switch_to.default_content()
            except:
                # Nếu không có iframe, đọc trực tiếp
                email_body = self.driver.find_element(By.ID, "messagebody")
                content = email_body.text
            
            logger.info(f"Email content preview:\n{content[:400]}...")
            
            # Tìm verification code
            # Tìm số 6-8 chữ số, thường sau "安全代码:" hoặc "security code:" hoặc "code:"
            patterns = [
                r'安全代码[:\s]*(\d{6,8})',  # Chinese
                r'security code[:\s]*(\d{6,8})',  # English
                r'code[:\s]*(\d{6,8})',  # Generic
                r'\b(\d{6,8})\b'  # Fallback: any 6-8 digit number
            ]
            
            code = None
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    code = matches[0]
                    break
            
            if code:
                logger.info(f"✓ Found verification code: {code}")
                return code
            else:
                logger.error("✗ Could not find verification code in email")
                return None
                
        except Exception as e:
            logger.error(f"Error getting verification code: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def verify_outlook_with_code(self, code, retry_count=0, max_retries=2):
        """Step 4: Quay lại Outlook và nhập verification code"""
        try:
            logger.info("\n" + "="*70)
            logger.info(f"[STEP 4] Verifying Outlook with code: {code} (Attempt {retry_count + 1}/{max_retries + 1})")
            logger.info("="*70)
            
            # Switch về tab Outlook
            self.driver.switch_to.window(self.outlook_tab)
            time.sleep(2)
            
            # Nhập verification code - thử nhiều selector
            logger.info("Entering verification code...")
            
            code_input_selectors = [
                (By.NAME, "otc"),
                (By.ID, "idTxtBx_SAOTCC_OTC"),
                (By.CSS_SELECTOR, "input[type='tel']"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.CSS_SELECTOR, "input[aria-label*='code']")
            ]
            
            code_input = None
            for by, selector in code_input_selectors:
                try:
                    logger.info(f"Trying code input: {by}={selector}")
                    code_input = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    logger.info(f"✓ Found code input with {by}={selector}")
                    break
                except:
                    continue
            
            if not code_input:
                logger.error("✗ Could not find code input!")
                return False
            
            code_input.clear()
            code_input.send_keys(code)
            time.sleep(2)
            
            # Click verify/submit button thay vì dùng Enter
            logger.info("Submitting verification code...")
            try:
                # Thử tìm submit button
                submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                submit_btn.click()
                logger.info("✓ Clicked submit button")
            except:
                # Nếu không có button, tìm lại input và dùng Enter
                try:
                    code_input_retry = self.driver.find_element(By.CSS_SELECTOR, "input[type='text']")
                    code_input_retry.send_keys(Keys.RETURN)
                    logger.info("✓ Submitted with Enter")
                except:
                    logger.warning("Could not submit code")
            
            time.sleep(5)
            
            # Check xem có error message không (code sai hoặc hết hạn)
            try:
                error_msg = self.driver.find_element(By.CSS_SELECTOR, ".alert-error, .error-message, [role='alert']")
                if error_msg and error_msg.is_displayed():
                    logger.warning(f"⚠️ Error detected: {error_msg.text}")
                    
                    # Nếu còn retry, quay lại wmhotmail lấy code mới
                    if retry_count < max_retries:
                        logger.info("🔄 Retrying... Getting new code from wmhotmail")
                        new_code = self.get_verification_code_from_wmhotmail()
                        if new_code and new_code != code:
                            return self.verify_outlook_with_code(new_code, retry_count + 1, max_retries)
                        else:
                            logger.error("✗ Could not get new code")
                            return False
                    else:
                        logger.error("✗ Max retries reached")
                        return False
            except:
                # Không có error message = success
                pass
            
            time.sleep(5)
            
            # Click button Next sau khi verify
            logger.info("Looking for Next button...")
            try:
                next_btn_selectors = [
                    (By.XPATH, "//button[contains(text(), 'Next')]"),
                    (By.CSS_SELECTOR, "button[type='submit']"),
                    (By.ID, "idSIButton9"),
                    (By.XPATH, "//input[@type='submit']")
                ]
                
                for by, selector in next_btn_selectors:
                    try:
                        logger.info(f"Trying Next button: {by}={selector}")
                        next_btn = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((by, selector))
                        )
                        next_btn.click()
                        logger.info(f"✓ Clicked Next button with {by}={selector}")
                        time.sleep(5)
                        break
                    except:
                        continue
            except Exception as e:
                logger.warning(f"Could not find Next button: {str(e)}")
            
            # Click button OK (A quick note about your Microsoft account)
            logger.info("Looking for OK button...")
            try:
                ok_btn_selectors = [
                    (By.CSS_SELECTOR, "#StickyFooter > button"),
                    (By.XPATH, "//button[contains(text(), 'OK')]"),
                    (By.ID, "idSIButton9"),
                    (By.CSS_SELECTOR, "button[type='submit']")
                ]
                
                for by, selector in ok_btn_selectors:
                    try:
                        logger.info(f"Trying OK button: {by}={selector}")
                        ok_btn = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((by, selector))
                        )
                        ok_btn.click()
                        logger.info(f"✓ Clicked OK button with {by}={selector}")
                        time.sleep(4)
                        break
                    except:
                        continue
            except Exception as e:
                logger.warning(f"Could not find OK button: {str(e)}")
            
            # Click button "Skip for now" (passkey setup)
            logger.info("Looking for 'Skip for now' button...")
            try:
                skip_btn_selectors = [
                    (By.XPATH, "//button[contains(text(), 'Skip for now')]"),
                    (By.XPATH, "//a[contains(text(), 'Skip for now')]"),
                    (By.ID, "iCancel"),
                    (By.CSS_SELECTOR, "button.secondary-button")
                ]
                
                for by, selector in skip_btn_selectors:
                    try:
                        logger.info(f"Trying Skip button: {by}={selector}")
                        skip_btn = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((by, selector))
                        )
                        skip_btn.click()
                        logger.info(f"✓ Clicked Skip button with {by}={selector}")
                        time.sleep(4)
                        break
                    except:
                        continue
            except Exception as e:
                logger.warning(f"Could not find Skip button: {str(e)}")
            
            # Click button "No" (Stay signed in?)
            logger.info("Looking for 'No' button (Stay signed in?)...")
            try:
                no_btn_selectors = [
                    (By.XPATH, "//button[contains(text(), 'No')]"),
                    (By.ID, "idBtn_Back"),
                    (By.CSS_SELECTOR, "button.secondary-button"),
                    (By.XPATH, "//input[@value='No']")
                ]
                
                for by, selector in no_btn_selectors:
                    try:
                        logger.info(f"Trying No button: {by}={selector}")
                        no_btn = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((by, selector))
                        )
                        no_btn.click()
                        logger.info(f"✓ Clicked No button with {by}={selector}")
                        time.sleep(3)
                        break
                    except:
                        continue
            except Exception as e:
                logger.warning(f"Could not find No button: {str(e)}")
            
            # Check if logged in successfully
            current_url = self.driver.current_url
            logger.info(f"Current URL: {current_url}")
            
            if "outlook" in current_url.lower() or "live.com" in current_url:
                logger.info("✓ Outlook login successful!")
                
                # Mở Outlook inbox
                logger.info("Opening Outlook inbox...")
                try:
                    # Navigate to Outlook mail
                    self.driver.get("https://outlook.live.com/mail/0/")
                    time.sleep(5)
                    logger.info("✓ Outlook inbox opened")
                except Exception as e:
                    logger.warning(f"Could not open inbox: {str(e)}")
                
                return True
            else:
                logger.warning("⚠️  Outlook login status unclear, continuing...")
                return True
                
        except Exception as e:
            logger.error(f"Error verifying Outlook: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def register_gameseal_account(self):
        """Step 5: Đăng ký tài khoản GameSeal với Outlook email qua Multilogin"""
        try:
            logger.info("\n" + "="*70)
            logger.info("[STEP 5] Registering GameSeal account...")
            logger.info("="*70)
            
            if not self.multilogin_driver:
                logger.error("Multilogin driver not initialized!")
                return False
            
            # Dùng Multilogin driver thay vì Chrome driver
            driver = self.multilogin_driver.driver
            
            # Mở GameSeal
            logger.info("Opening GameSeal.com...")
            driver.get("https://gameseal.com")
            time.sleep(3)
            
            # Close cookie popup nếu có
            try:
                cookie_btn = self.driver.find_element(By.CSS_SELECTOR, "button.cky-btn.cky-btn-accept")
                cookie_btn.click()
                time.sleep(1)
            except:
                pass
            
            # Click Account button
            logger.info("Clicking Account button...")
            account_btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#accountWidget"))
            )
            account_btn.click()
            time.sleep(2)
            
            # Click Register link
            logger.info("Clicking Register link...")
            register_link = self.driver.find_element(By.CSS_SELECTOR, "a.register-link[href='/account/register']")
            register_link.click()
            time.sleep(3)
            
            # Nhập email
            logger.info(f"Entering email: {self.outlook_email}")
            email_input = self.driver.find_element(By.ID, "registerMail")
            email_input.clear()
            email_input.send_keys(self.outlook_email)
            time.sleep(1)
            
            # Nhập password (dùng password của Outlook)
            logger.info("Entering password...")
            password_input = self.driver.find_element(By.ID, "registerPassword")
            password_input.clear()
            password_input.send_keys(self.outlook_password)
            time.sleep(1)
            
            # Nhập confirm password
            logger.info("Entering confirm password...")
            confirm_input = self.driver.find_element(By.ID, "registerPasswordConfirm")
            confirm_input.clear()
            confirm_input.send_keys(self.outlook_password)
            time.sleep(1)
            
            # Click Register button
            logger.info("Clicking Register button...")
            register_btn = self.driver.find_element(By.CSS_SELECTOR, ".register-submit button.btn-primary")
            register_btn.click()
            time.sleep(5)
            
            logger.info("✓ Registration submitted!")
            logger.info("⏳ Waiting for verification email...")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            logger.error(f"Error registering GameSeal account: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_gameseal_account(self, card_data=None):
        """Verify GameSeal account qua email và chạy purchase workflow"""
        try:
            logger.info("\n" + "="*70)
            logger.info("[STEP 6] Verifying GameSeal account via email...")
            logger.info("="*70)
            
            # Switch về tab Outlook (KHÔNG LOAD LẠI TRANG - sẽ mất mail!)
            logger.info("Switching to Outlook tab...")
            self.driver.switch_to.window(self.outlook_tab)
            time.sleep(2)
            
            # Check xem đã ở inbox chưa
            current_url = self.driver.current_url
            logger.info(f"Current URL: {current_url}")
            
            # CHỈ navigate nếu CHƯA ở inbox
            if "outlook.live.com/mail" not in current_url:
                logger.info("Not at inbox yet, navigating...")
                self.driver.get("https://outlook.live.com/mail/")
                time.sleep(8)
            else:
                logger.info("✓ Already at inbox, NOT reloading page to preserve emails")
                time.sleep(3)
            
            # Xử lý popup privacy/terms nếu có (QUAN TRỌNG: Phải làm TRƯỚC khi click email)
            logger.info("Checking for privacy popup...")
            try:
                # Thử tìm button "Rejeitar" hoặc "Aceitar"
                popup_buttons = [
                    (By.XPATH, "//button[contains(text(), 'Rejeitar')]"),
                    (By.XPATH, "//button[contains(text(), 'Aceitar')]"),
                    (By.XPATH, "//button[contains(text(), 'Reject')]"),
                    (By.XPATH, "//button[contains(text(), 'Accept')]"),
                    (By.CSS_SELECTOR, "button[aria-label*='Reject']"),
                    (By.CSS_SELECTOR, "button[aria-label*='Accept']"),
                    (By.XPATH, "//button[@type='button' and contains(@class, 'ms-Button')]")
                ]
                
                popup_closed = False
                for by, selector in popup_buttons:
                    try:
                        logger.info(f"Trying popup button: {selector}")
                        popup_btn = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((by, selector))
                        )
                        popup_btn.click()
                        logger.info(f"✓ Closed privacy popup with: {selector}")
                        popup_closed = True
                        time.sleep(2)
                        break
                    except:
                        continue
                
                if not popup_closed:
                    logger.info("No privacy popup found (or already closed)")
            except Exception as e:
                logger.info(f"No popup to close: {str(e)[:50]}")
            
            # Đợi thêm sau khi đóng popup
            time.sleep(2)
            
            # Tìm email từ GameSeal (check cả Inbox và Junk Email!)
            logger.info("Looking for GameSeal verification email...")
            try:
                # Đợi inbox load
                time.sleep(3)
                
                # Screenshot để debug
                self.driver.save_screenshot("/tmp/outlook_inbox_before_click.png")
                logger.info("Screenshot saved: /tmp/outlook_inbox_before_click.png")
                
                # Tìm TẤT CẢ emails trong inbox
                email_selectors = [
                    (By.CSS_SELECTOR, "div[role='option']"),
                    (By.CSS_SELECTOR, "div[data-convid]"),
                    (By.CSS_SELECTOR, "div[role='listitem']"),
                ]
                
                all_emails = []
                for by, selector in email_selectors:
                    try:
                        logger.info(f"Trying to find all emails with: {by}={selector}")
                        all_emails = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_all_elements_located((by, selector))
                        )
                        logger.info(f"Found {len(all_emails)} emails in Inbox")
                        if len(all_emails) > 0:
                            break
                    except:
                        continue
                
                # Tìm email từ GameSeal trong Inbox
                gameseal_email = None
                if all_emails:
                    for i, email in enumerate(all_emails):
                        try:
                            # Lấy text của email để check
                            email_text = email.text.lower()
                            logger.info(f"Inbox Email {i}: {email_text[:100]}")
                            
                            # Check xem có phải GameSeal không
                            if "gameseal" in email_text or "activate" in email_text or "verify" in email_text:
                                logger.info(f"✓ Found GameSeal email in Inbox at index {i}")
                                gameseal_email = email
                                break
                        except:
                            continue
                
                # Nếu không tìm thấy trong Inbox → Check Junk Email folder
                if not gameseal_email:
                    logger.info("GameSeal email not found in Inbox, checking Junk Email folder...")
                    try:
                        # Click vào Junk Email folder
                        junk_selectors = [
                            (By.XPATH, "//span[contains(text(), 'Junk Email')]"),
                            (By.XPATH, "//span[contains(text(), 'Junk')]"),
                            (By.CSS_SELECTOR, "[aria-label*='Junk']"),
                            (By.XPATH, "//div[contains(@aria-label, 'Junk')]")
                        ]
                        
                        for by, selector in junk_selectors:
                            try:
                                logger.info(f"Trying to click Junk folder: {selector}")
                                junk_folder = WebDriverWait(self.driver, 3).until(
                                    EC.element_to_be_clickable((by, selector))
                                )
                                junk_folder.click()
                                logger.info("✓ Clicked Junk Email folder")
                                time.sleep(3)
                                break
                            except:
                                continue
                        
                        # Tìm emails trong Junk folder
                        junk_emails = []
                        for by, selector in email_selectors:
                            try:
                                junk_emails = WebDriverWait(self.driver, 5).until(
                                    EC.presence_of_all_elements_located((by, selector))
                                )
                                logger.info(f"Found {len(junk_emails)} emails in Junk folder")
                                if len(junk_emails) > 0:
                                    break
                            except:
                                continue
                        
                        # Tìm GameSeal email trong Junk
                        for i, email in enumerate(junk_emails):
                            try:
                                email_text = email.text.lower()
                                logger.info(f"Junk Email {i}: {email_text[:100]}")
                                
                                if "gameseal" in email_text or "activate" in email_text or "verify" in email_text:
                                    logger.info(f"✓ Found GameSeal email in Junk at index {i}")
                                    gameseal_email = email
                                    break
                            except:
                                continue
                    except Exception as e:
                        logger.warning(f"Could not check Junk folder: {str(e)[:100]}")
                
                if not gameseal_email:
                    logger.error("Could not find GameSeal email in Inbox or Junk folder")
                    return False
                
                # Click vào GameSeal email
                logger.info("Clicking GameSeal email...")
                try:
                    gameseal_email.click()
                    logger.info("✓ Clicked GameSeal email")
                    clicked = True
                    time.sleep(3)
                    
                    # Screenshot sau khi click
                    self.driver.save_screenshot("/tmp/outlook_email_opened.png")
                    logger.info("Screenshot saved: /tmp/outlook_email_opened.png")
                except Exception as e:
                    logger.error(f"Failed to click: {str(e)[:100]}")
                    clicked = False
                
                if not clicked:
                    logger.error("✗ Could not click first email")
                    return False
                
                # Tìm và copy verification link từ email
                logger.info("Looking for verification link...")
                link_selectors = [
                    (By.PARTIAL_LINK_TEXT, "ACTIVATE NOW"),
                    (By.PARTIAL_LINK_TEXT, "Activate"),
                    (By.PARTIAL_LINK_TEXT, "verify"),
                    (By.PARTIAL_LINK_TEXT, "Verify"),
                    (By.PARTIAL_LINK_TEXT, "confirm"),
                    (By.PARTIAL_LINK_TEXT, "Confirm"),
                    (By.XPATH, "//a[contains(@href, 'verify')]"),
                    (By.XPATH, "//a[contains(@href, 'activate')]"),
                    (By.XPATH, "//a[contains(@href, 'gameseal.com')]"),
                    (By.XPATH, "//a[contains(text(), 'ACTIVATE')]"),
                    (By.XPATH, "//a[contains(text(), 'Verify')]"),
                    (By.CSS_SELECTOR, "a[href*='gameseal.com']")
                ]
                
                verification_link = None
                for by, selector in link_selectors:
                    try:
                        logger.info(f"Trying to find link: {by}={selector}")
                        link_element = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((by, selector))
                        )
                        verification_link = link_element.get_attribute('href')
                        logger.info(f"✓ Found verification link: {verification_link}")
                        break
                    except:
                        continue
                
                if not verification_link:
                    logger.error("✗ Could not find verification link with selectors")
                    logger.info("Trying to find all links in email...")
                    try:
                        all_links = self.driver.find_elements(By.TAG_NAME, "a")
                        logger.info(f"Found {len(all_links)} links in email:")
                        for i, link in enumerate(all_links[:20]):  # Show first 20
                            href = link.get_attribute('href')
                            text = link.text.strip()
                            if href and 'gameseal' in href.lower():
                                logger.info(f"  [{i}] GameSeal link: {href}")
                                if not verification_link:
                                    verification_link = href
                                    logger.info(f"✓ Using this link: {verification_link}")
                    except:
                        pass
                    
                    if not verification_link:
                        logger.error("✗ No verification link found at all!")
                        return False
                
                # Dùng Multilogin driver để mở verification link
                logger.info("Opening verification link in Multilogin browser...")
                if not self.gameseal_automation or not self.gameseal_automation.driver:
                    logger.error("✗ Multilogin driver not available")
                    return False
                
                # Mở tab mới trong Multilogin browser bằng switch_to.new_window
                multilogin_driver = self.gameseal_automation.driver
                logger.info("Creating new tab in Multilogin...")
                
                # Lưu window handle hiện tại
                original_window = multilogin_driver.current_window_handle
                
                # Mở tab mới
                multilogin_driver.switch_to.new_window('tab')
                time.sleep(2)
                
                # Navigate đến verification link
                logger.info(f"Navigating to verification link: {verification_link}")
                multilogin_driver.get(verification_link)
                time.sleep(5)
                
                # RELOAD lại trang một lần nữa (QUAN TRỌNG!)
                logger.info("Reloading page to ensure proper activation...")
                multilogin_driver.refresh()
                time.sleep(5)
                
                logger.info("✓ GameSeal account verified and auto-logged in!")
                
                # Sau khi verify, GameSeal tự động login → Chạy flow mua hàng hoàn chỉnh
                logger.info("\n" + "="*70)
                logger.info("[STEP 7] Starting full purchase workflow...")
                logger.info("="*70)
                
                # Chuẩn bị user data
                user_data = {
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'address': '123 Main St',
                    'city': 'New York',
                    'phone': '+1234567890'
                }
                
                # Sử dụng card_data được truyền vào, hoặc dùng default
                if not card_data:
                    card_data = {
                        'number': '4111111111111111',
                        'exp_date': '12/25',
                        'cvv': '123',
                        'zip': '75044',
                        'city': 'Garland',
                        'address': '209 Coral Ridge Dr'
                    }
                
                # Gọi full purchase workflow
                if not self.gameseal_automation.run_full_purchase_workflow(user_data, card_data):
                    logger.error("✗ Failed to run purchase workflow")
                    return False
                
                logger.info("✓ Full purchase workflow completed!")
                return True
                
            except Exception as e:
                logger.error(f"Error during verification: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
            
        except Exception as e:
            logger.error(f"Error verifying GameSeal account: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_full_flow(self, card_data=None):
        """Chạy toàn bộ flow với card data"""
        try:
            logger.info("\n" + "="*70)
            logger.info("OUTLOOK REGISTRATION FLOW")
            logger.info("="*70)
            
            # Start Chrome browser cho mail
            if not self.start_browser():
                return False
            
            # Không cần start Multilogin ở đây - gameseal_auto_login.py sẽ tự làm
            
            # Step 1: Login wmhotmail
            if not self.login_wmhotmail():
                return False
            
            # Step 2: Login Outlook
            if not self.login_outlook():
                return False
            
            # Step 3: Get verification code from wmhotmail
            code = self.get_verification_code_from_wmhotmail()
            if not code:
                return False
            
            # Step 4: Verify Outlook with code
            if not self.verify_outlook_with_code(code):
                return False
            
            # Step 5: Gọi gameseal_auto_login.py để xử lý phần GameSeal
            logger.info("\n" + "="*70)
            logger.info("[STEP 5] Starting GameSeal registration...")
            logger.info("="*70)
            
            try:
                logger.info(f"Registering GameSeal with email: {self.outlook_email}")
                
                # Step 1: Get proxy
                logger.info("Getting proxy from 9Proxy...")
                proxy_handler = NineProxyHandler()
                success, proxy_info = proxy_handler.get_next_proxy()
                if not success:
                    logger.error(f"Failed to get proxy: {proxy_info.get('error')}")
                    return False
                
                logger.info(f"✓ Got proxy: {proxy_info['host']}:{proxy_info['port']}")
                
                # Step 2: Login Multilogin
                multilogin_handler = MultiLoginHandler()
                login_success, login_result = multilogin_handler.login()
                if not login_success:
                    logger.error(f"Failed to login to Multilogin: {login_result.get('error')}")
                    return False
                
                # Step 3: Create new profile with proxy
                logger.info("Creating new Multilogin profile...")
                profile_name = f"GameSeal_{self.outlook_email.split('@')[0]}"
                
                create_success, create_result = multilogin_handler.create_profile(
                    proxy_info=proxy_info,
                    profile_name=profile_name
                )
                if not create_success:
                    logger.error(f"Failed to create profile: {create_result.get('error')}")
                    return False
                
                profile_id = create_result.get("profile_id")
                logger.info(f"✓ Created profile: {profile_name} (ID: {profile_id})")
                
                # Step 4: Start profile
                logger.info("Starting profile...")
                success, start_result = multilogin_handler.start_profile(profile_id)
                if not success:
                    logger.error(f"Failed to start profile: {start_result.get('error')}")
                    return False
                
                debug_port = start_result.get("selenium_port")
                if not debug_port:
                    logger.error("No debug port returned")
                    return False
                
                logger.info(f"✓ Profile started on port: {debug_port}")
                
                # Tạo GameSeal automation instance
                # Dùng mật khẩu cố định cho GameSeal vì mật khẩu mail có thể không đúng format
                GAMESEAL_PASSWORD = "Abcdn@12345"
                
                self.gameseal_automation = GameSealAutoLogin(
                    email=self.outlook_email,
                    password=GAMESEAL_PASSWORD,
                    debug_port=int(debug_port),
                    register_email=self.outlook_email,
                    register_password=GAMESEAL_PASSWORD
                )
                
                # Connect và chạy workflow
                if not self.gameseal_automation.connect_to_browser():
                    logger.error("Failed to connect to Multilogin browser")
                    return False
                
                # Dùng registration workflow - CÓ ĐĂNG KÝ với manual button click
                if not self.gameseal_automation.run_registration_workflow():
                    logger.error("Failed to run GameSeal registration workflow")
                    return False
                
                logger.info("✓ GameSeal registration completed!")
                
            except Exception as e:
                logger.error(f"Error during GameSeal registration: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
            
            # Step 6: Verify GameSeal account (sau khi register xong)
            logger.info("\n" + "="*70)
            logger.info("[STEP 6] Verifying GameSeal account...")
            logger.info("="*70)
            
            # Verify account và chạy purchase workflow với card data
            if not self.verify_gameseal_account(card_data):
                logger.error("Failed to verify GameSeal account")
                return False
            
            logger.info("\n" + "="*70)
            logger.info("✅ FULL FLOW COMPLETED SUCCESSFULLY!")
            logger.info("="*70)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in full flow: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    import os
    import sys
    
    # Đọc data từ file
    data_file = "/Users/mac/Documents/tool_auto_buy/data/data_mail/data_mail.txt"
    card_file = "/Users/mac/Documents/tool_auto_buy/data/data_ci/data_ci.txt"
    index_file = "/Users/mac/Documents/tool_auto_buy/data/data_mail/current_index.txt"
    
    if not os.path.exists(data_file):
        logger.error(f"Data file not found: {data_file}")
        sys.exit(1)
    
    with open(data_file, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    if len(lines) < 4:
        logger.error("Data file must have at least 4 lines")
        sys.exit(1)
    
    # Parse mail data thành các bộ (mỗi bộ 4 dòng)
    mail_sets = []
    for i in range(0, len(lines), 4):
        if i + 3 < len(lines):
            mail_sets.append({
                'outlook_email': lines[i],
                'outlook_password': lines[i + 1],
                'wmhotmail_email': lines[i + 2],
                'wmhotmail_code': lines[i + 3]
            })
    
    logger.info(f"Found {len(mail_sets)} mail set(s) in data file")
    
    # Đọc card data
    card_sets = []
    if os.path.exists(card_file):
        with open(card_file, 'r') as f:
            card_lines = [line.strip() for line in f.readlines() if line.strip()]
        
        for line in card_lines:
            card_data = parse_card_data(line)
            if card_data:
                card_sets.append(card_data)
        
        logger.info(f"Found {len(card_sets)} card(s) in data file")
    else:
        logger.warning(f"Card file not found: {card_file}")
        logger.info("Will use default card data")
    
    # Đọc index hiện tại (bộ mail nào đang xử lý)
    current_index = 0
    if os.path.exists(index_file):
        try:
            with open(index_file, 'r') as f:
                current_index = int(f.read().strip())
        except:
            current_index = 0
    
    # Check xem còn mail để xử lý không
    if current_index >= len(mail_sets):
        logger.info("All mail sets have been processed!")
        logger.info("Resetting index to 0...")
        current_index = 0
    
    # Lấy bộ mail hiện tại
    mail_data = mail_sets[current_index]
    
    # Lấy card data tương ứng (nếu có)
    card_data = None
    if card_sets and current_index < len(card_sets):
        card_data = card_sets[current_index]
        logger.info(f"Using card: {card_data['number'][:4]}...{card_data['number'][-4:]}")
    else:
        logger.warning("No card data available for this index, will use default")
    
    logger.info("\n" + "="*70)
    logger.info(f"PROCESSING MAIL SET {current_index + 1}/{len(mail_sets)}")
    logger.info("="*70)
    logger.info(f"  Outlook: {mail_data['outlook_email']}")
    logger.info(f"  WMHotmail: {mail_data['wmhotmail_email']}")
    
    # Multilogin profile ID (có thể lấy từ config hoặc hardcode)
    # walmart CA 6 - port 60005
    MULTILOGIN_PROFILE_ID = "4e32caab-be06-45e2-8691-aaa66400c776"
    
    logger.info("\n⚠️  IMPORTANT: Make sure Multilogin app is running before starting!")
    logger.info("Waiting 3 seconds...")
    time.sleep(3)
    
    flow = OutlookRegistrationFlow(
        outlook_email=mail_data['outlook_email'],
        outlook_password=mail_data['outlook_password'],
        wmhotmail_email=mail_data['wmhotmail_email'],
        wmhotmail_code=mail_data['wmhotmail_code'],
        multilogin_profile_id=MULTILOGIN_PROFILE_ID
    )
    
    success = flow.run_full_flow(card_data)
    
    logger.info("\n" + "="*70)
    if success:
        logger.info(f"✓ Mail set {current_index + 1} completed successfully!")
        
        # Lưu index tiếp theo
        next_index = current_index + 1
        with open(index_file, 'w') as f:
            f.write(str(next_index))
        logger.info(f"Next run will process mail set {next_index + 1}/{len(mail_sets)}")
        
        # Tự động đóng browsers để chuẩn bị cho lần chạy tiếp theo
        logger.info("\n" + "="*70)
        logger.info("✓ Closing browsers...")
        logger.info("="*70)
        
        if flow.driver:
            try:
                flow.driver.quit()
                logger.info("✓ Chrome browser closed")
            except Exception as e:
                logger.error(f"Error closing Chrome: {str(e)}")
        
        if flow.gameseal_automation and flow.gameseal_automation.driver:
            try:
                flow.gameseal_automation.driver.quit()
                logger.info("✓ Multilogin browser closed")
            except Exception as e:
                logger.error(f"Error closing Multilogin: {str(e)}")
        
        logger.info("✓ Session completed. Ready for next run.")
    else:
        logger.error(f"✗ Mail set {current_index + 1} failed!")
        
        # Đóng browser và skip sang email tiếp theo
        logger.info("Closing browsers and moving to next email...")
        if flow.driver:
            try:
                flow.driver.quit()
            except:
                pass
        if flow.gameseal_automation and flow.gameseal_automation.driver:
            try:
                flow.gameseal_automation.driver.quit()
            except:
                pass
        
        # Skip sang email tiếp theo
        next_index = current_index + 1
        with open(index_file, 'w') as f:
            f.write(str(next_index))
        logger.info(f"✓ Skipped to next mail set {next_index + 1}/{len(mail_sets)}")
        logger.info("Please run the script again to process the next email.")
