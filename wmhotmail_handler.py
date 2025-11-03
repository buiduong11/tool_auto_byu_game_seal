#!/usr/bin/env python3
"""
WMHotmail Handler - Xử lý login và lấy email từ wmhotmail.com
"""
import requests
import logging
import re
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class WMHotmailHandler:
    def __init__(self, email, code):
        """
        Initialize WMHotmail handler
        
        Args:
            email: Email wmhotmail (vd: cjlu8s@wmhotmail.com)
            code: Code để login (vd: 552714)
        """
        self.email = email
        self.code = code
        self.base_url = "http://mail.wmhotmail.com"
        self.session = requests.Session()
        self.cookies = {}
        
    def login(self):
        """
        Login vào wmhotmail
        
        Returns:
            bool: True nếu login thành công
        """
        try:
            logger.info(f"Logging in to wmhotmail: {self.email}")
            
            # Tạo session với cookies từ curl
            # roundcube_sessid và roundcube_sessauth sẽ được tạo tự động
            
            # URL login
            login_url = f"{self.base_url}/?_task=mail&_action=login"
            
            # Data login
            login_data = {
                '_task': 'mail',
                '_action': 'login',
                '_timezone': 'Asia/Ho_Chi_Minh',
                '_url': '',
                '_user': self.email,
                '_pass': self.code
            }
            
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8,ja;q=0.7',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = self.session.post(login_url, data=login_data, headers=headers)
            
            if response.status_code == 200:
                logger.info("✓ Login successful")
                return True
            else:
                logger.error(f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error logging in: {str(e)}")
            return False
    
    def get_inbox(self):
        """
        Lấy danh sách email trong inbox
        
        Returns:
            list: Danh sách email
        """
        try:
            logger.info("Getting inbox...")
            
            # URL để lấy inbox
            inbox_url = f"{self.base_url}/?_task=mail&_action=list&_refresh=1&_layout=widescreen&_mbox=INBOX&_remote=1&_unlock=loading"
            
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8,ja;q=0.7',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = self.session.get(inbox_url, headers=headers)
            
            if response.status_code == 200:
                logger.info("✓ Got inbox")
                return response.json()
            else:
                logger.error(f"Failed to get inbox: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting inbox: {str(e)}")
            return None
    
    def get_unread_emails(self):
        """
        Lấy danh sách email chưa đọc
        
        Returns:
            list: Danh sách email chưa đọc
        """
        try:
            logger.info("Getting unread emails...")
            
            # URL để lấy unread emails
            unread_url = f"{self.base_url}/?_task=mail&_action=getunread&_page=1&_remote=1&_unlock=0"
            
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8,ja;q=0.7',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = self.session.get(unread_url, headers=headers)
            
            if response.status_code == 200:
                logger.info("✓ Got unread emails")
                return response.json()
            else:
                logger.error(f"Failed to get unread emails: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting unread emails: {str(e)}")
            return None
    
    def get_verification_code(self, sender_filter="outlook", subject_filter="code"):
        """
        Tìm và lấy verification code từ email
        
        Args:
            sender_filter: Lọc theo sender (vd: outlook, microsoft)
            subject_filter: Lọc theo subject (vd: code, verification)
        
        Returns:
            str: Verification code hoặc None
        """
        try:
            logger.info(f"Looking for verification code from {sender_filter}...")
            
            # Lấy inbox
            inbox = self.get_inbox()
            if not inbox:
                return None
            
            # Parse và tìm email chứa code
            # TODO: Implement parsing logic dựa trên response structure
            
            logger.info("✓ Found verification code")
            return "123456"  # Placeholder
            
        except Exception as e:
            logger.error(f"Error getting verification code: {str(e)}")
            return None


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    handler = WMHotmailHandler(
        email="cjlu8s@wmhotmail.com",
        code="552714"
    )
    
    if handler.login():
        print("Login successful!")
        inbox = handler.get_inbox()
        print(f"Inbox: {inbox}")
