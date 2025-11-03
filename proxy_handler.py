import requests
from typing import Dict, Optional, Tuple
import logging
import json
from config import NINEPROXY_LOCAL_IP, NINEPROXY_LOCAL_PORT, NINEPROXY_API_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NineProxyHandler:
    def __init__(self, local_proxy_ip=NINEPROXY_LOCAL_IP, starting_port=NINEPROXY_LOCAL_PORT, num_ports=20):
        """
        Initialize the 9proxy handler using port forwarding
        
        Args:
            local_proxy_ip: The local IP address where 9proxy is forwarding (default: 127.0.0.1)
            starting_port: Starting port for proxy forwarding (default: 60000)
            num_ports: Number of available ports (default: 20)
        """
        self.proxy_host = local_proxy_ip
        self.starting_port = starting_port
        self.num_ports = num_ports
        self.current_port_index = 0
        self.api_url = NINEPROXY_API_URL
        self.session = requests.Session()
        self.is_logged_in = False
        logger.info(f"9Proxy handler initialized: {self.proxy_host}:{starting_port}-{starting_port + num_ports - 1}")
    
    def login(self, email: str, password: str) -> bool:
        """
        Login to 9proxy panel
        
        Args:
            email: Login email
            password: Login password
            
        Returns:
            bool: True if login successful
        """
        try:
            login_data = {
                "email": email,
                "password": password
            }
            
            response = self.session.post(
                f"{self.api_url}/api/login",
                json=login_data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            if response.status_code == 200:
                self.is_logged_in = True
                logger.info("Successfully logged in to 9proxy")
                return True
            else:
                logger.error(f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False
        
    def get_next_proxy(self) -> Tuple[bool, Dict]:
        """
        Get next proxy using port forwarding from 9Proxy
        Each port (60000-60019) forwards to a different proxy automatically
        
        Returns: (success, result)
            success: bool indicating if proxy info was created successfully
            result: dict containing proxy details
        """
        try:
            # Calculate the port to use
            port = self.starting_port + self.current_port_index
            
            # Move to next port for next call (round-robin)
            self.current_port_index = (self.current_port_index + 1) % self.num_ports
            
            # Create proxy info
            # 9Proxy forwards traffic through these ports to real proxies
            proxy_info = {
                "host": self.proxy_host,
                "port": port,
                "username": "",  # Empty for local forwarding
                "password": "",
                "country": "US",
                "type": "socks5",  # Sử dụng socks5 như trong curl
                "forwarding_port": port
            }
            
            logger.info(f"Using 9Proxy forwarding port: {port}")
            return True, proxy_info
            
        except Exception as e:
            logger.error(f"Error getting proxy: {str(e)}")
            return False, {"error": f"Error getting proxy: {str(e)}"}
    
    def get_us_proxy(self, port=None) -> Tuple[bool, Dict]:
        """
        Alias for get_next_proxy() to maintain backward compatibility
        """
        return self.get_next_proxy()
            
    def reset_port_index(self):
        """
        Reset the port index to start from the beginning
        """
        self.current_port_index = 0
        logger.info("Port index reset to 0")
