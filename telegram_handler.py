import requests
import logging

logger = logging.getLogger(__name__)

class TelegramHandler:
    def __init__(self, bot_token, chat_id):
        """
        Initialize Telegram handler
        
        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat/channel ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message, parse_mode="HTML"):
        """
        Send message to Telegram channel
        
        Args:
            message: Message text
            parse_mode: Parse mode (HTML, Markdown, etc.)
        
        Returns:
            bool: True if success, False otherwise
        """
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("✓ Message sent to Telegram successfully")
                return True
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")
            return False
    
    def send_order_status(self, success, profile_name, email, card_last4=None, error_msg=None):
        """
        Send order status notification
        
        Args:
            success: True if order successful, False otherwise
            profile_name: Multilogin profile name
            email: Account email
            card_last4: Last 4 digits of card (optional)
            error_msg: Error message if failed (optional)
        
        Returns:
            bool: True if message sent successfully
        """
        status_emoji = "✅" if success else "❌"
        status_text = "THÀNH CÔNG" if success else "THẤT BẠI"
        
        message = f"""
🤖 <b>Bot Auto Buy - GameSeal</b>

{status_emoji} <b>Trạng thái:</b> {status_text}

📋 <b>Thông tin:</b>
• Profile: <code>{profile_name}</code>
• Email: <code>{email}</code>
"""
        
        if card_last4:
            message += f"• Card: ****{card_last4}\n"
        
        if not success and error_msg:
            message += f"\n⚠️ <b>Lỗi:</b> {error_msg}\n"
        
        return self.send_message(message)
