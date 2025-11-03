#!/usr/bin/env python3
"""
GameSeal Auto Login - Automation giống hành động con người
Sử dụng Selenium kết nối với Multilogin browser
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GameSealAutoLogin:
    def __init__(self, email: str, password: str, debug_port: int = None, 
                 register_email: str = None, register_password: str = None):
        """
        Khởi tạo automation
        
        Args:
            email: Email đăng nhập (cũ, để login nếu cần)
            password: Mật khẩu (cũ)
            debug_port: Port debugging của Multilogin browser (nếu có)
            register_email: Email mới để đăng ký (Outlook email)
            register_password: Password mới để đăng ký (Outlook password)
        """
        self.email = email
        self.password = password
        self.debug_port = debug_port
        self.register_email = register_email or email  # Dùng register_email nếu có, không thì dùng email cũ
        self.register_password = register_password or password
        self.driver = None
        self.wait = None
        
    def connect_to_browser(self):
        """Kết nối với Multilogin browser qua Selenium Remote"""
        try:
            if not self.debug_port:
                logger.error("No debug port provided!")
                return False
            
            logger.info(f"Connecting to Multilogin browser on port {self.debug_port}...")
            
            # Dùng webdriver.Remote như trong docs Multilogin
            from selenium.webdriver.chromium.options import ChromiumOptions
            
            self.driver = webdriver.Remote(
                command_executor=f"http://127.0.0.1:{self.debug_port}",
                options=ChromiumOptions()
            )
            self.wait = WebDriverWait(self.driver, 15)
            logger.info(f"✓ Connected to browser on port {self.debug_port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {str(e)}")
            return False
    
    def human_delay(self, min_sec=0.5, max_sec=2.0):
        """Delay ngẫu nhiên giống con người"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def wait_for_element(self, by, selector, timeout=10):
        """Đợi element xuất hiện"""
        try:
            logger.info(f"Waiting for element: {selector}")
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            logger.info(f"✓ Element found: {selector}")
            return element
        except TimeoutException:
            logger.error(f"✗ Element not found: {selector}")
            return None
    
    def click_element(self, element, wait_time=1):
        """Click vào element"""
        try:
            # Scroll vào view nếu cần
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.3)
            
            # Click
            element.click()
            logger.info(f"✓ Clicked element")
            self.human_delay(wait_time, wait_time + 1)
            return True
        except Exception as e:
            logger.error(f"✗ Failed to click: {str(e)}")
            return False
    
    def type_text_human_like(self, element, text):
        """Nhập text giống con người (từng ký tự)"""
        try:
            element.clear()
            time.sleep(0.2)
            
            for char in text:
                element.send_keys(char)
                # Random delay giữa các ký tự (50-150ms)
                time.sleep(random.uniform(0.05, 0.15))
            
            logger.info(f"✓ Typed text")
            self.human_delay(0.5, 1)
            return True
        except Exception as e:
            logger.error(f"✗ Failed to type: {str(e)}")
            return False
    
    def open_url(self, url):
        """Mở URL"""
        try:
            logger.info(f"Opening URL: {url}")
            self.driver.get(url)
            logger.info(f"✓ Opened: {url}")
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"Failed to open URL: {str(e)}")
            return False
    
    def fill_profile_form(self, user_data):
        """Điền form thông tin cá nhân sau khi login"""
        try:
            logger.info("\n" + "=" * 70)
            logger.info("ĐIỀN THÔNG TIN PROFILE")
            logger.info("=" * 70)
            
            # Đợi form load
            time.sleep(3)
            
            # Name
            logger.info("\nFilling name...")
            name_input = self.wait_for_element(By.CSS_SELECTOR, 
                "div.account-content-main-form.personal-data > div:nth-child(3) > input", timeout=10)
            if name_input:
                self.click_element(name_input, wait_time=0.5)
                self.type_text_human_like(name_input, user_data.get('first_name', ''))
            
            # Surname
            logger.info("Filling surname...")
            surname_input = self.wait_for_element(By.CSS_SELECTOR,
                "div.account-content-main-form.personal-data > div:nth-child(4) > input", timeout=5)
            if surname_input:
                self.click_element(surname_input, wait_time=0.5)
                self.type_text_human_like(surname_input, user_data.get('last_name', ''))
            
            # Address
            logger.info("Filling address...")
            address_input = self.wait_for_element(By.CSS_SELECTOR,
                "div.account-content-main-form.personal-data > div:nth-child(5) > input", timeout=5)
            if address_input:
                self.click_element(address_input, wait_time=0.5)
                self.type_text_human_like(address_input, user_data.get('address', ''))
            
            # City
            logger.info("Filling city...")
            city_input = self.wait_for_element(By.CSS_SELECTOR,
                "div.account-content-main-form.personal-data > div:nth-child(7) > input", timeout=5)
            if city_input:
                self.click_element(city_input, wait_time=0.5)
                self.type_text_human_like(city_input, user_data.get('city', ''))
            
            # Country dropdown
            logger.info("Selecting country...")
            country_btn = self.wait_for_element(By.CSS_SELECTOR,
                "div.form-group.country > div > div > div > button > span", timeout=5)
            if country_btn:
                self.click_element(country_btn, wait_time=1)
                # TODO: Select country from dropdown
            
            # Phone number
            logger.info("Filling phone...")
            phone_input = self.wait_for_element(By.CSS_SELECTOR,
                "div.account-content-main-form.personal-data > div:nth-child(9) > input", timeout=5)
            if phone_input:
                self.click_element(phone_input, wait_time=0.5)
                self.type_text_human_like(phone_input, user_data.get('phone', ''))
            
            # Date of birth - Day
            logger.info("Filling birth date...")
            day_btn = self.wait_for_element(By.CSS_SELECTOR,
                "div.form-group.date-of-birth > div:nth-child(2) > div.dropdown-search.is-birthdayDay > div > div > button > span",
                timeout=5)
            if day_btn:
                self.click_element(day_btn, wait_time=1)
                # TODO: Select day
            
            # Month
            month_btn = self.wait_for_element(By.CSS_SELECTOR,
                "div.form-group.date-of-birth > div:nth-child(3) > div.dropdown-search.is-birthdayMonth > div > div > button > span",
                timeout=5)
            if month_btn:
                self.click_element(month_btn, wait_time=1)
                # TODO: Select month
            
            # Year
            year_btn = self.wait_for_element(By.CSS_SELECTOR,
                "div.form-group.date-of-birth > div:nth-child(4) > div.dropdown-search.is-birthdayYear > div > div > button > span > span.dropdown-search-label-value",
                timeout=5)
            if year_btn:
                self.click_element(year_btn, wait_time=1)
                # TODO: Select year
            
            # Region
            logger.info("Selecting region...")
            region_btn = self.wait_for_element(By.CSS_SELECTOR,
                "div.account-content-main-form.generall-data > div.lacu-section-wrapper > div:nth-child(1) > div > div > div > button > span > span.dropdown-search-label-value",
                timeout=5)
            if region_btn:
                self.click_element(region_btn, wait_time=1)
            
            # Submit button
            logger.info("\nSubmitting profile form...")
            submit_btn = self.wait_for_element(By.CSS_SELECTOR,
                "div.account-content-main-form-submit-wrapper > button", timeout=5)
            if submit_btn:
                self.human_delay(1, 2)
                self.click_element(submit_btn, wait_time=3)
                logger.info("✓ Profile form submitted")
                
                # Đợi form submit xong
                time.sleep(2)
                
                # Click logo để về trang chủ
                logger.info("\nClicking logo to go home...")
                logo = self.wait_for_element(By.CSS_SELECTOR,
                    "div.col-12.col-lg-auto.header-logo-col > div.header-logo-main > a", timeout=5)
                if logo:
                    self.click_element(logo, wait_time=2)
                    logger.info("✓ Returned to home page")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error filling profile: {str(e)}")
            return False
    
    def complete_checkout(self, card_data):
        """Hoàn tất checkout với thông tin thẻ"""
        try:
            logger.info("\n" + "=" * 70)
            logger.info("CHECKOUT PROCESS")
            logger.info("=" * 70)
            
            # Click vào ô search
            logger.info("\n[STEP 1] Clicking search box...")
            search_btn = self.wait_for_element(By.CSS_SELECTOR,
                "div.col-12.order-3.d-md-none.header-search-toggle-col > div > button",
                timeout=10)
            if search_btn:
                self.click_element(search_btn, wait_time=1)
            
            # Nhập từ khóa search
            logger.info("\n[STEP 2] Entering search keyword...")
            search_input = self.wait_for_element(By.CSS_SELECTOR,
                "input.form-control.header-search-input", timeout=5)
            if search_input:
                search_keyword = "Binance Gift Card (USDT) 5 USD Key - GLOBAL"
                self.click_element(search_input, wait_time=0.5)
                self.type_text_human_like(search_input, search_keyword)
                logger.info(f"✓ Entered search: {search_keyword}")
                time.sleep(2)  # Đợi search suggest xuất hiện
            
            # Click vào item sản phẩm từ search suggest
            logger.info("\n[STEP 3] Clicking product from search suggest...")
            product_link = self.wait_for_element(By.CSS_SELECTOR,
                "#searchCollapse > div > form > div.search-suggest.js-search-result > ul > li.search-suggest-product.js-result > a",
                timeout=10)
            if product_link:
                self.click_element(product_link, wait_time=2)
            
            # Button buy now
            logger.info("\n[STEP 3] Clicking Buy Now...")
            buy_btn = self.wait_for_element(By.CSS_SELECTOR,
                "#productDetailPageBuyProductForm > div > div.col-8 > button", timeout=10)
            if buy_btn:
                self.click_element(buy_btn, wait_time=3)
                logger.info("✓ Clicked Buy Now, waiting for checkout page...")
                time.sleep(3)  # Đợi trang checkout load
            
            # Xong tới bước này - checkout aside action link
            logger.info("\n[STEP 4] Clicking 'Continue to checkout' link...")
            checkout_link = self.wait_for_element(By.CSS_SELECTOR,
                "div.checkout-aside > div > div.checkout-aside-container > div.checkout-aside-action > a",
                timeout=15)
            if checkout_link:
                self.click_element(checkout_link, wait_time=2)
                logger.info("✓ Clicked checkout link")
            
            # Chọn VISA payment option (div đầu tiên)
            logger.info("\n[STEP 5] Selecting VISA payment option...")
            
            # Thử nhiều selector cho VISA option
            visa_selectors = [
                (By.CSS_SELECTOR, "#changePaymentForm > div > div:nth-child(1) > div > div > label"),
                (By.CSS_SELECTOR, "#changePaymentForm > div > div:nth-child(1)"),
                (By.XPATH, "//label[contains(., 'Credit and debit cards payment')]"),
                (By.XPATH, "//div[contains(@class, 'payment-option')]//img[@alt='Visa']//ancestor::label")
            ]
            
            payment_option = None
            for by, selector in visa_selectors:
                try:
                    logger.info(f"Trying VISA selector: {selector}")
                    payment_option = self.wait_for_element(by, selector, timeout=5)
                    if payment_option:
                        logger.info(f"✓ Found VISA option with: {selector}")
                        break
                except:
                    continue
            
            if payment_option:
                self.click_element(payment_option, wait_time=2)
                logger.info("✓ Selected VISA payment option")
                time.sleep(3)  # Đợi billing form xuất hiện
            else:
                logger.error("Could not find VISA payment option!")
                return False
            
            # Điền thông tin billing address (4 mục)
            logger.info("\n[STEP 5.1] Filling billing address...")
            
            # Street
            logger.info("Filling street...")
            street_input = self.wait_for_element(By.CSS_SELECTOR, "#gs-street", timeout=10)
            if street_input:
                self.click_element(street_input, wait_time=0.5)
                self.type_text_human_like(street_input, card_data.get('address', '209 Coral Ridge Dr'))
            
            # Postcode
            logger.info("Filling postcode...")
            postcode_input = self.wait_for_element(By.CSS_SELECTOR, "#gs-postal-code", timeout=5)
            if postcode_input:
                self.click_element(postcode_input, wait_time=0.5)
                self.type_text_human_like(postcode_input, card_data.get('zip', '75044'))
            
            # City
            logger.info("Filling city...")
            city_input = self.wait_for_element(By.CSS_SELECTOR, "#gs-city", timeout=5)
            if city_input:
                self.click_element(city_input, wait_time=0.5)
                self.type_text_human_like(city_input, card_data.get('city', 'Garland'))
            
            # Country - dropdown
            logger.info("Selecting country...")
            # Click vào dropdown button
            country_btn = self.wait_for_element(By.CSS_SELECTOR,
                "#changePaymentForm > div > div.payment-method.index-2.initialized > div.payment-method-configuration > div.row.payment-method-configuration-row.is-details-billing-address > div.col.card.payment-method-configuration-col.payment-method-billing-address > div.card-content > div > div:nth-child(2) > div:nth-child(2) > div.dropdown-search.is-gs-country > div > div > button > span",
                timeout=10)
            if country_btn:
                self.click_element(country_btn, wait_time=1)
                logger.info("✓ Clicked country dropdown")
                
                # Nhập "united states" vào search input
                country_search = self.wait_for_element(By.CSS_SELECTOR,
                    "div.dropdown-menu-wrapper.dropdown-search-item-dropdown-menu-wrapper > input",
                    timeout=5)
                if country_search:
                    self.type_text_human_like(country_search, "united states")
                    time.sleep(1)
                    
                    # Chọn item "United States"
                    country_item = self.wait_for_element(By.CSS_SELECTOR,
                        "label.dropdown-item.checked",
                        timeout=5)
                    if country_item:
                        self.click_element(country_item, wait_time=1)
                        logger.info("✓ Selected United States")
            
            # Submit billing form
            logger.info("\n[STEP 5.2] Submitting billing form...")
            submit_billing_btn = self.wait_for_element(By.CSS_SELECTOR,
                "#confirmFormSubmit", timeout=10)
            if submit_billing_btn:
                self.click_element(submit_billing_btn, wait_time=2)
                logger.info("✓ Submitted billing form")
                time.sleep(3)  # Đợi form submit và chuyển trang
            
            # Button continue
            logger.info("\n[STEP 6] Clicking continue button...")
            # Thử selector ngắn hơn
            continue_btn = self.wait_for_element(By.CSS_SELECTOR,
                "div.checkout-confirm-summary-sticky-action > button",
                timeout=15)
            if continue_btn:
                self.click_element(continue_btn, wait_time=2)
                logger.info("✓ Clicked continue button")
                time.sleep(3)  # Đợi payment form load
            
            # B9: Nhập mã thẻ
            logger.info("\n[B9] Entering card number...")
            card_input = self.wait_for_element(By.CSS_SELECTOR,
                "#cardNumber", timeout=10)
            if card_input:
                self.click_element(card_input, wait_time=0.5)
                self.type_text_human_like(card_input, card_data.get('number', ''))
            
            # B10: Nhập tháng và năm hết hạn
            logger.info("\n[B10] Entering expiry date...")
            exp_input = self.wait_for_element(By.CSS_SELECTOR,
                "#expDate", timeout=5)
            if exp_input:
                self.click_element(exp_input, wait_time=0.5)
                self.type_text_human_like(exp_input, card_data.get('exp_date', ''))
            
            # B11: Nhập CVV
            logger.info("\n[B11] Entering CVV...")
            cvv_input = self.wait_for_element(By.CSS_SELECTOR,
                "#cvv", timeout=5)
            if cvv_input:
                self.click_element(cvv_input, wait_time=0.5)
                self.type_text_human_like(cvv_input, card_data.get('cvv', ''))
            
            # B12: Click Pay button
            logger.info("\n[B12] Clicking Pay button...")
            pay_btn = self.wait_for_element(By.CSS_SELECTOR,
                "body > app-root > app-select-payment-method > div > div.drawer-container.ng-tns-c2010829045-0 > div > div.payment-details-desktop.mobile-d-none.ng-tns-c2010829045-0 > div.payment-details-body.ng-tns-c2010829045-0 > div.button-section.ng-tns-c2010829045-0 > button > div > span",
                timeout=10)
            if pay_btn:
                self.click_element(pay_btn, wait_time=2)
                logger.info("✓ Payment submitted!")
                
                # Đợi payment process
                time.sleep(5)
                
                # Check payment status
                logger.info("\n[B13] Checking payment status...")
                failed_indicator = self.wait_for_element(By.CSS_SELECTOR,
                    "body > app-root > app-return > div > div > zen-payment-status-loader > div > div.loader-separator > div",
                    timeout=10)
                
                if failed_indicator:
                    logger.error("❌ Payment FAILED!")
                    return False
                else:
                    logger.info("✅ Payment SUCCESS!")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error during checkout: {str(e)}")
            return False
    
    def run_full_purchase_workflow(self, user_data, card_data):
        """
        Flow MUA HÀNG HOÀN CHỈNH sau khi verify (đã auto login)
        B1: Click Account → Profile
        B2: Điền form profile → Submit → Move to home
        B3-B12: Complete checkout (search, buy, payment) - ĐÃ CÓ SẴN trong complete_checkout()
        """
        try:
            logger.info("\n" + "="*70)
            logger.info("FULL PURCHASE WORKFLOW (AFTER VERIFY)")
            logger.info("="*70)
            
            # B1: Click Account button
            logger.info("\n[B1] Clicking Account button...")
            account_btn = self.wait_for_element(By.CSS_SELECTOR, "#accountWidget", timeout=15)
            if not account_btn:
                logger.error("Account button not found!")
                return False
            self.click_element(account_btn, wait_time=2)
            
            # B2: Click Profile
            logger.info("\n[B2] Clicking Profile...")
            # Thử nhiều selector cho Profile link
            profile_selectors = [
                (By.CSS_SELECTOR, "div.list-group.list-group-flush.account-aside-list-group > a:nth-child(3)"),
                (By.XPATH, "//div[contains(@class, 'account-aside-list-group')]//a[contains(text(), 'Profile')]"),
                (By.XPATH, "//a[contains(@href, '/account/profile')]"),
                (By.PARTIAL_LINK_TEXT, "Profile")
            ]
            
            profile_link = None
            for by, selector in profile_selectors:
                try:
                    logger.info(f"Trying Profile selector: {selector}")
                    profile_link = self.wait_for_element(by, selector, timeout=5)
                    if profile_link:
                        logger.info(f"✓ Found Profile with: {selector}")
                        break
                except:
                    continue
            
            if not profile_link:
                logger.error("Profile link not found with any selector!")
                return False
            
            self.click_element(profile_link, wait_time=2)
            
            # B3: Điền form profile
            logger.info("\n[B3] Filling profile form...")
            if not self.fill_profile_form(user_data):
                logger.error("Failed to fill profile")
                return False
            
            # B3: Click move to home (đã có trong fill_profile_form - click logo)
            logger.info("✓ Returned to home")
            
            # B4-B12: Complete checkout (search, product, buy, payment)
            # Method complete_checkout() ĐÃ CÓ ĐẦY ĐỦ:
            # - Search product
            # - Click product từ search result
            # - Buy now
            # - Continue
            # - Payment option
            # - Billing address (street, postcode, city, country)
            # - Card info
            # - Pay button
            logger.info("\n[B4-B12] Running complete checkout flow...")
            if not self.complete_checkout(card_data):
                logger.error("Failed to complete checkout")
                return False
            
            logger.info("\n✅ FULL PURCHASE WORKFLOW COMPLETED!")
            return True
            
        except Exception as e:
            logger.error(f"\n✗ LỖI: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_checkout_workflow(self, game_url: str = None):
        """
        Chạy workflow mua hàng - BỎ QUA đăng ký/đăng nhập
        
        Args:
            game_url: URL của game cần mua (optional, nếu không có thì search)
        """
        try:
            logger.info("\n" + "="*70)
            logger.info("GAMESEAL CHECKOUT WORKFLOW (NO REGISTRATION)")
            logger.info("="*70)
            
            # Bước 1: Mở trang GameSeal
            logger.info("\n[STEP 1] Opening GameSeal homepage...")
            self.driver.get("https://gameseal.com")
            time.sleep(3)  # Đợi trang load
            
            # Bước 1.5: Đóng cookie popup
            logger.info("\n[STEP 1.5] Closing cookie popup...")
            try:
                cookie_btn = self.wait_for_element(By.CSS_SELECTOR, "button.cky-btn.cky-btn-accept", timeout=5)
                if cookie_btn:
                    self.click_element(cookie_btn, wait_time=1)
                    logger.info("✓ Closed cookie popup")
            except:
                logger.info("No cookie popup or already closed")
            
            # Bước 2: Search game hoặc mở URL trực tiếp
            if game_url:
                logger.info(f"\n[STEP 2] Opening game page: {game_url}")
                self.driver.get(game_url)
            else:
                logger.info("\n[STEP 2] Skipping search - going directly to checkout")
            
            time.sleep(2)
            
            # Bước 3: Go to checkout
            logger.info("\n[STEP 3] Going to checkout...")
            self.driver.get("https://gameseal.com/checkout")
            time.sleep(3)
            
            # Bước 4: Nhập email vào #personalMail-desktop
            logger.info("\n[STEP 4] Entering email for checkout...")
            return self.enter_checkout_email()
            
        except Exception as e:
            logger.error(f"\n✗ LỖI: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def enter_checkout_email(self):
        """Nhập email vào checkout page"""
        try:
            # Tìm input email với selector #personalMail-desktop
            logger.info("Finding email input (#personalMail-desktop)...")
            email_input = self.wait_for_element(By.CSS_SELECTOR, "#personalMail-desktop", timeout=10)
            
            if not email_input:
                logger.error("Email input not found!")
                return False
            
            # Click vào input
            self.human_delay(0.5, 1)
            self.click_element(email_input, wait_time=0.5)
            
            # Nhập email
            logger.info(f"Entering email: {self.register_email}")
            self.type_text_human_like(email_input, self.register_email)
            self.human_delay(1, 2)
            
            # Click button "CONTINUE TO PAYMENT SELECTION"
            logger.info("Clicking 'CONTINUE TO PAYMENT SELECTION' button...")
            button = self.wait_for_element(By.XPATH, 
                "//button[contains(text(), 'CONTINUE TO PAYMENT SELECTION')]", 
                timeout=5)
            
            if not button:
                logger.error("Continue button not found!")
                return False
            
            self.human_delay(1, 2)
            if not self.click_element(button, wait_time=3):
                return False
            
            logger.info("✓ Email entered and continue button clicked!")
            return True
            
        except Exception as e:
            logger.error(f"Error entering checkout email: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_registration_workflow(self):
        """Chạy workflow ĐĂNG KÝ với manual button click"""
        try:
            logger.info("\n" + "="*70)
            logger.info("GAMESEAL REGISTRATION WORKFLOW")
            logger.info("="*70)
            
            # Bước 1: Mở trang GameSeal
            logger.info("\n[STEP 1] Opening GameSeal homepage...")
            self.driver.get("https://gameseal.com")
            time.sleep(5)
            
            # Bước 1.5: Đóng cookie popup
            logger.info("\n[STEP 1.5] Closing cookie popup...")
            try:
                cookie_btn = self.wait_for_element(By.CSS_SELECTOR, "button.cky-btn.cky-btn-accept", timeout=5)
                if cookie_btn:
                    self.click_element(cookie_btn, wait_time=1)
                    logger.info("✓ Closed cookie popup")
            except:
                logger.info("No cookie popup or already closed")
            
            # Bước 2: Click Account button
            logger.info("\n[STEP 2] Clicking Account button...")
            account_btn = self.wait_for_element(By.CSS_SELECTOR, "#accountWidget", timeout=15)
            if not account_btn:
                logger.error("Account button not found!")
                return False
            
            self.human_delay(1, 2)
            if not self.click_element(account_btn, wait_time=2):
                return False
            
            # Bước 3: Click REGISTER link
            logger.info("\n[STEP 3] Clicking REGISTER link...")
            register_link = self.wait_for_element(By.CSS_SELECTOR, 'a.register-link[href="/account/register"]', timeout=5)
            if not register_link:
                logger.error("Register link not found!")
                return False
            
            self.human_delay(0.5, 1.5)
            if not self.click_element(register_link, wait_time=2):
                return False
            
            # Bước 4: KHÔNG TỰ ĐỘNG ĐIỀN - CHỜ USER NHẬP
            logger.info("\n[STEP 4] Waiting for registration page to load...")
            
            # Đợi form load
            email_input = self.wait_for_element(By.CSS_SELECTOR, 'input[type="email"]', timeout=10)
            if not email_input:
                logger.error("Registration form not found!")
                return False
            
            # Đợi thêm để trang load hoàn toàn
            time.sleep(2)
            
            # PRINT THÔNG TIN CHO USER
            logger.info("\n" + "="*70)
            logger.info("📝 PLEASE FILL THE REGISTRATION FORM MANUALLY")
            logger.info("="*70)
            logger.info(f"📧 Email:    {self.register_email}")
            logger.info(f"🔑 Password: {self.register_password}")
            logger.info("="*70)
            logger.info("⚠️  IMPORTANT:")
            logger.info("   1. Enter the email above")
            logger.info("   2. Enter the password above (twice)")
            logger.info("   3. Check the newsletter checkbox (optional)")
            logger.info("   4. Click the CONTINUE button")
            logger.info("="*70)
            
            # CHỜ USER CLICK CONTINUE BUTTON
            logger.info("\n" + "="*70)
            logger.info("⏸️  WAITING FOR USER TO CLICK 'CONTINUE' BUTTON")
            logger.info("="*70)
            logger.info("Please click the CONTINUE button manually to proceed...")
            
            # Check button state trước
            try:
                button_check = self.driver.execute_script("""
                    var btn = document.querySelector('button.btn-primary');
                    if (btn) {
                        return {
                            text: btn.textContent.trim(),
                            disabled: btn.disabled,
                            classes: btn.className
                        };
                    }
                    return null;
                """)
                logger.info(f"Button state before click: {button_check}")
            except Exception as e:
                logger.warning(f"Could not check button state: {e}")
            
            # Lưu URL hiện tại
            current_url = self.driver.current_url
            logger.info(f"Current URL: {current_url}")
            
            # Chờ URL thay đổi
            logger.info("Waiting for URL change (checking every 3 seconds)...")
            max_wait_time = 300  # 5 phút
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                time.sleep(3)
                elapsed_time += 3
                
                try:
                    new_url = self.driver.current_url
                    
                    # Check for errors on page
                    if elapsed_time % 9 == 0:  # Mỗi 9 giây
                        errors = self.driver.execute_script("""
                            var errors = [];
                            var errorElems = document.querySelectorAll('.error, .alert, [class*="error"]');
                            errorElems.forEach(function(elem) {
                                if (elem.offsetParent !== null && elem.textContent.trim()) {
                                    errors.push(elem.textContent.trim());
                                }
                            });
                            return errors;
                        """)
                        if errors:
                            logger.error(f"⚠️ Errors on page: {errors}")
                    
                    if new_url != current_url:
                        logger.info(f"\n✓ URL changed! User clicked the button")
                        logger.info(f"New URL: {new_url}")
                        break
                    
                    if elapsed_time % 15 == 0:
                        logger.info(f"Still waiting... ({elapsed_time}s elapsed)")
                        
                except Exception as e:
                    logger.error(f"Error while waiting: {str(e)}")
                    break
            else:
                logger.error(f"\n✗ Timeout after {max_wait_time}s")
                return False
            
            # Đợi registration hoàn tất
            logger.info("\n[STEP 5] Waiting for registration to complete...")
            time.sleep(5)
            
            logger.info("\n" + "=" * 70)
            logger.info("✓ REGISTRATION COMPLETED!")
            logger.info("=" * 70)
            
            return True
            
        except Exception as e:
            logger.error(f"\n✗ LỖI: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def login_to_account(self):
        """Login vào tài khoản GameSeal sau khi verify"""
        try:
            logger.info("Navigating to GameSeal login page...")
            self.driver.get("https://gameseal.com/account/login")
            time.sleep(3)
            
            # Nhập email
            logger.info(f"Entering email: {self.register_email}")
            email_input = self.wait_for_element(By.CSS_SELECTOR, "input[type='email']", timeout=10)
            if not email_input:
                logger.error("Could not find email input")
                return False
            
            email_input.clear()
            email_input.send_keys(self.register_email)
            logger.info("✓ Entered email")
            time.sleep(1)
            
            # Nhập password
            logger.info("Entering password...")
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password_input.clear()
            password_input.send_keys(self.register_password)
            logger.info("✓ Entered password")
            time.sleep(1)
            
            # Click Login button
            logger.info("Clicking LOGIN button...")
            login_btn_selectors = [
                (By.XPATH, "//button[contains(text(), 'LOGIN')]"),
                (By.XPATH, "//button[contains(text(), 'Log in')]"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, ".btn-primary")
            ]
            
            clicked = False
            for by, selector in login_btn_selectors:
                try:
                    login_btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    login_btn.click()
                    logger.info("✓ Clicked LOGIN button")
                    clicked = True
                    break
                except:
                    continue
            
            if not clicked:
                logger.error("Could not find LOGIN button")
                return False
            
            time.sleep(5)
            
            # Check if login successful
            current_url = self.driver.current_url
            logger.info(f"Current URL after login: {current_url}")
            
            if "login" not in current_url.lower():
                logger.info("✓ GameSeal login successful!")
                logger.info("Ready for search and purchase flow...")
                return True
            else:
                logger.warning("Still on login page, login may have failed")
                return False
                
        except Exception as e:
            logger.error(f"Error logging in to GameSeal: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main function để test"""
    from multilogin import MultiLoginHandler
    
    # Thông tin đăng nhập
    EMAIL = "conn6ecrosson655@outlook.com"  # Outlook email
    PASSWORD = "aH6hfAdsRZ35"  # Outlook password
    PROFILE_ID = "4e32caab-be06-45e2-8691-aaa66400c776"  # walmart CA 6
    
    # Start Multilogin profile
    logger.info("Starting Multilogin profile...")
    multilogin_handler = MultiLoginHandler()
    
    # Login
    login_success, login_result = multilogin_handler.login()
    if not login_success:
        logger.error(f"Failed to login to Multilogin: {login_result.get('error')}")
        return False
    
    # Start profile
    success, start_result = multilogin_handler.start_profile(PROFILE_ID)
    if not success:
        logger.error(f"Failed to start profile: {start_result.get('error')}")
        return False
    
    debug_port = start_result.get("selenium_port")
    if not debug_port:
        logger.error("No debug port returned")
        return False
    
    logger.info(f"✓ Profile started on port: {debug_port}")
    
    # Tạo automation instance
    automation = GameSealAutoLogin(
        email=EMAIL,
        password=PASSWORD,
        debug_port=int(debug_port),
        register_email=EMAIL,
        register_password=PASSWORD
    )
    
    # Kết nối với browser
    if not automation.connect_to_browser():
        logger.error("Cannot connect to browser!")
        return False
    
    # Chạy workflow
    success = automation.run_login_workflow()
    
    if success:
        logger.info("\n✅ SUCCESS! Registration workflow completed")
    else:
        logger.error("\n❌ FAILED! Registration workflow failed")
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
