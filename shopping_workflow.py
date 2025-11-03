#!/usr/bin/env python3
"""Auto shopping workflow - human-like behavior"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HumanBehavior:
    """Simulate human-like interactions"""
    
    @staticmethod
    def random_delay(min_sec=0.5, max_sec=2.0):
        """Random delay between actions"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    @staticmethod
    def human_type(element, text, typing_speed=0.1):
        """Type like a human with delays"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, typing_speed))
    
    @staticmethod
    def move_to_element_human(driver, element):
        """Move mouse to element with smooth curve"""
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        time.sleep(random.uniform(0.2, 0.5))

class GameSealAutomation:
    def __init__(self, selenium_port: str):
        """
        Initialize automation with Selenium
        
        Args:
            selenium_port: Port from Multilogin start_profile
        """
        self.port = selenium_port
        self.driver = None
        self.wait = None
        
    def connect(self):
        """Connect to Multilogin browser"""
        try:
            options = webdriver.ChromeOptions()
            options.debugger_address = f"127.0.0.1:{self.port}"
            
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 15)
            logger.info(f"✓ Connected to browser on port {self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {str(e)}")
            return False
    
    def goto_site(self, url="https://gameseal.com/"):
        """Navigate to website"""
        logger.info(f"Navigating to {url}...")
        self.driver.get(url)
        HumanBehavior.random_delay(2, 4)
    
    def click_account_icon(self):
        """Step 1: Click account icon"""
        try:
            logger.info("Step 1: Clicking account icon...")
            # Find by SVG class or parent element
            account_icon = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg.icon-layout-account, .icon-layout-account'))
            )
            HumanBehavior.move_to_element_human(self.driver, account_icon)
            account_icon.click()
            HumanBehavior.random_delay(1, 2)
            return True
        except Exception as e:
            logger.error(f"Failed to click account icon: {str(e)}")
            return False
    
    def click_register(self):
        """Step 2: Click REGISTER link"""
        try:
            logger.info("Step 2: Clicking REGISTER...")
            register_link = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/account/register"].register-link'))
            )
            HumanBehavior.move_to_element_human(self.driver, register_link)
            register_link.click()
            HumanBehavior.random_delay(1.5, 3)
            return True
        except Exception as e:
            logger.error(f"Failed to click register: {str(e)}")
            return False
    
    def click_login_link(self):
        """Step 3: Click Login link"""
        try:
            logger.info("Step 3: Clicking Login link...")
            login_link = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.card-subtitle-link[href="/account/login"]'))
            )
            HumanBehavior.move_to_element_human(self.driver, login_link)
            login_link.click()
            HumanBehavior.random_delay(1.5, 3)
            return True
        except Exception as e:
            logger.error(f"Failed to click login link: {str(e)}")
            return False
    
    def fill_email(self, email="catalinaart14_01582@outlook.com"):
        """Step 4: Fill email"""
        try:
            logger.info(f"Step 4: Filling email: {email}...")
            email_input = self.wait.until(
                EC.presence_of_element_located((By.ID, 'loginMail'))
            )
            HumanBehavior.move_to_element_human(self.driver, email_input)
            email_input.click()
            HumanBehavior.random_delay(0.3, 0.7)
            HumanBehavior.human_type(email_input, email, typing_speed=0.15)
            HumanBehavior.random_delay(0.5, 1)
            return True
        except Exception as e:
            logger.error(f"Failed to fill email: {str(e)}")
            return False
    
    def fill_password(self, password="Abc@12345"):
        """Step 5: Fill password"""
        try:
            logger.info("Step 5: Filling password...")
            password_input = self.wait.until(
                EC.presence_of_element_located((By.ID, 'loginPassword'))
            )
            HumanBehavior.move_to_element_human(self.driver, password_input)
            password_input.click()
            HumanBehavior.random_delay(0.3, 0.7)
            HumanBehavior.human_type(password_input, password, typing_speed=0.12)
            HumanBehavior.random_delay(0.5, 1)
            return True
        except Exception as e:
            logger.error(f"Failed to fill password: {str(e)}")
            return False
    
    def click_continue(self):
        """Step 6: Click CONTINUE button"""
        try:
            logger.info("Step 6: Clicking CONTINUE...")
            continue_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.login-submit button.btn-primary'))
            )
            HumanBehavior.move_to_element_human(self.driver, continue_btn)
            HumanBehavior.random_delay(0.5, 1)
            continue_btn.click()
            logger.info("✓ Login submitted!")
            HumanBehavior.random_delay(3, 5)
            return True
        except Exception as e:
            logger.error(f"Failed to click continue: {str(e)}")
            return False
    
    def login_workflow(self, email="catalinaart14_01582@outlook.com", password="Abc@12345"):
        """Complete login workflow"""
        steps = [
            ("Navigate to site", lambda: self.goto_site()),
            ("Click account icon", lambda: self.click_account_icon()),
            ("Click register", lambda: self.click_register()),
            ("Click login link", lambda: self.click_login_link()),
            ("Fill email", lambda: self.fill_email(email)),
            ("Fill password", lambda: self.fill_password(password)),
            ("Click continue", lambda: self.click_continue())
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                logger.error(f"Failed at: {step_name}")
                return False
        
        logger.info("=" * 60)
        logger.info("✓ Login workflow completed successfully!")
        logger.info("=" * 60)
        return True
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()

def run_automation(selenium_port: str):
    """Run the full automation"""
    automation = GameSealAutomation(selenium_port)
    
    if not automation.connect():
        return False
    
    try:
        success = automation.login_workflow()
        return success
    except Exception as e:
        logger.error(f"Automation error: {str(e)}")
        return False
    finally:
        # Don't close - keep browser open for user
        logger.info("Browser will remain open for manual interaction")
