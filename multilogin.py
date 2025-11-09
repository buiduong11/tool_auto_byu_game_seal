import requests
import json
import hashlib
from typing import Dict, Optional, Tuple
import logging
from config import MULTILOGIN_API_URL, MULTILOGIN_LAUNCHER_API, MULTILOGIN_LOCAL_API, MULTILOGIN_EMAIL, MULTILOGIN_PASSWORD, DEFAULT_FOLDER_ID
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiLoginHandler:
    def __init__(self, api_url: str = MULTILOGIN_API_URL, launcher_api: str = MULTILOGIN_LAUNCHER_API, local_api: str = MULTILOGIN_LOCAL_API):
        self.api_url = api_url
        self.launcher_api = launcher_api
        self.local_api = local_api
        self.token = None
        self.base_headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9,vi;q=0.8,ja;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://app.multilogin.com',
            'referer': 'https://app.multilogin.com/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'x-request-origin': 'UI'
        }
    
    def get_headers(self) -> Dict:
        """Get headers with current token"""
        headers = self.base_headers.copy()
        if self.token:
            headers['authorization'] = f'Bearer {self.token}'
        return headers
    
    def login(self, email: str = MULTILOGIN_EMAIL, password: str = MULTILOGIN_PASSWORD) -> Tuple[bool, Dict]:
        """
        Login to Multilogin and get token
        
        Args:
            email: Login email
            password: Login password (plain text, will be hashed to MD5)
            
        Returns:
            (success, result)
        """
        try:
            # Hash password with MD5
            password_hash = hashlib.md5(password.encode()).hexdigest()
            
            login_data = {
                "email": email,
                "password": password_hash
            }
            
            response = requests.post(
                f"{self.api_url}/user/signin",
                json=login_data,
                headers=self.base_headers
            )
            
            if response.status_code != 200:
                logger.error(f"Login failed: {response.status_code} - {response.text}")
                return False, {"error": f"Login failed: {response.status_code}"}
            
            result = response.json()
            self.token = result.get("data", {}).get("token")
            
            if not self.token:
                logger.error(f"No token in response: {result}")
                return False, {"error": "No token in response"}
            
            logger.info("Successfully logged in to Multilogin")
            return True, {"token": self.token}
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False, {"error": f"Login error: {str(e)}"}

    def validate_proxy(self, proxy_info: Dict) -> Tuple[bool, Dict]:
        """
        Validate proxy before creating profile (skip if remote launcher unavailable)
        
        Args:
            proxy_info: Proxy configuration dict
            
        Returns:
            (success, result)
        """
        try:
            proxy_data = {
                "type": proxy_info.get('type', 'socks5').lower(),
                "host": proxy_info['host'],
                "port": proxy_info['port'],
                "username": proxy_info.get('username', ''),
                "password": proxy_info.get('password', '')
            }
            
            response = requests.post(
                f"{self.launcher_api}/proxy/validate",
                json=proxy_data,
                headers=self.get_headers(),
                timeout=5
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('status', {}).get('http_code') != 400:
                logger.info("Proxy validation successful")
                return True, {"status": "valid"}
            else:
                error_msg = result.get('status', {}).get('message', 'Unknown error')
                logger.warning(f"Proxy validation failed: {error_msg}")
                return False, {"error": error_msg}
                
        except Exception as e:
            logger.warning(f"Skipping proxy validation (remote launcher unavailable)")
            return True, {"status": "skipped"}

    def create_profile(self, proxy_info: Dict, folder_id: Optional[str] = None, profile_name: Optional[str] = None) -> Tuple[bool, Dict]:
        """
        Create a new profile with the given proxy settings
        
        Args:
            proxy_info: Proxy configuration dict
            folder_id: Optional folder ID
            profile_name: Optional profile name
            
        Returns:
            (success, result)
        """
        try:
            if not folder_id:
                folder_id = DEFAULT_FOLDER_ID
                
            if not profile_name:
                profile_name = f"Profile_{proxy_info['host']}_{proxy_info['port']}"
            
            profile_data = {
                "name": profile_name,
                "notes": "",
                "tags": [],
                "browser_type": "mimic",
                "folder_id": folder_id,
                "os_type": "macos",
                "parameters": {
                    "fingerprint": {
                        "ports": []
                    },
                    "geolocation": {
                        "mode": "manual",
                        "latitude": 37.7749,  # San Francisco
                        "longitude": -122.4194,
                        "accuracy": 10
                    },
                    "timezone": {
                        "mode": "manual",
                        "value": "America/Los_Angeles"  # US Pacific Time
                    },
                    "flags": {
                        "navigator_masking": "mask",
                        "audio_masking": "natural",
                        "localization_masking": "mask",
                        "geolocation_popup": "prompt",
                        "geolocation_masking": "mask",
                        "timezone_masking": "mask",
                        "graphics_noise": "mask",
                        "graphics_masking": "mask",
                        "webrtc_masking": "mask",
                        "fonts_masking": "mask",
                        "media_devices_masking": "natural",
                        "screen_masking": "mask",
                        "proxy_masking": "custom",
                        "ports_masking": "mask",
                        "canvas_noise": "natural",
                        "startup_behavior": "recover"
                    },
                    "storage": {
                        "is_local": False,  # Cloud storage (không phải Local)
                        "save_service_worker": True
                    },
                    "proxy": {
                        "type": proxy_info.get('type', 'socks5').lower(),
                        "host": proxy_info['host'],
                        "port": proxy_info['port'],
                        "username": proxy_info.get('username', ''),
                        "password": proxy_info.get('password', '')
                    },
                    "custom_start_urls": ["https://whoerip.com/multilogin/"],
                    "extension_ids": None
                }
            }

            response = requests.post(
                f"{self.api_url}/profile/create",
                json=profile_data,
                headers=self.get_headers()
            )

            if response.status_code not in [200, 201]:
                logger.error(f"Failed to create profile: {response.status_code}")
                logger.error(f"Response: {response.text}")
                logger.error(f"Request URL: {self.api_url}/profile/create")
                return False, {"error": f"Failed to create profile: {response.status_code}"}

            result = response.json()
            data = result.get("data", {})
            profile_id = data.get("id") or data.get("uuid") or (data.get("ids", [None])[0] if data.get("ids") else None)
            
            if not profile_id:
                logger.error(f"No profile ID in response: {data}")
                return False, {"error": "No profile ID in response"}

            logger.info(f"Profile created successfully: {profile_id}")
            return True, {"profile_id": profile_id, "name": profile_name}

        except Exception as e:
            logger.error(f"Error creating profile: {str(e)}")
            return False, {"error": f"Error creating profile: {str(e)}"}

    def stop_profile(self, profile_id: str, folder_id: str = DEFAULT_FOLDER_ID) -> Tuple[bool, Dict]:
        """Stop a running profile"""
        try:
            # API endpoint không cần folder_id
            url = f"{self.local_api}/profile/stop/p/{profile_id}"
            response = requests.get(url, headers=self.get_headers(), verify=False, timeout=30)
            
            if response.status_code == 200:
                logger.info("Profile stopped successfully")
                return True, {"status": "stopped"}
            else:
                logger.warning(f"Failed to stop profile: {response.status_code} - {response.text}")
                return False, {"error": f"Failed to stop: {response.status_code}"}
        except Exception as e:
            logger.warning(f"Could not stop profile: {str(e)}")
            return False, {"error": str(e)}
    
    def start_profile(self, profile_id: str, folder_id: str = DEFAULT_FOLDER_ID) -> Tuple[bool, Dict]:
        """
        Start a browser profile using local launcher API
        
        Args:
            profile_id: The profile ID to start
            folder_id: The folder ID
            
        Returns:
            (success, result)
        """
        try:
            # Multilogin X dùng API V2 với parameter automation_type=selenium
            # Endpoint: /api/v2/profile/f/{folder_id}/p/{profile_id}/start?automation_type=selenium
            launcher_v2_base = "https://launcher.mlx.yt:45001/api/v2"
            url = f"{launcher_v2_base}/profile/f/{folder_id}/p/{profile_id}/start?automation_type=selenium"
            logger.info(f"Using Multilogin X API V2...")
            
            response = requests.get(
                url,
                headers=self.get_headers(),
                verify=False,  # Local SSL
                timeout=30
            )

            # Handle profile already running
            if response.status_code == 400:
                data = response.json()
                if "PROFILE_ALREADY_RUNNING" in data.get("status", {}).get("error_code", ""):
                    logger.warning("Profile already running, stopping and restarting...")
                    self.stop_profile(profile_id, folder_id)
                    import time
                    time.sleep(5)  # Đợi lâu hơn để profile stop hoàn toàn
                    # Try again
                    logger.info("Restarting profile...")
                    response = requests.get(url, headers=self.get_headers(), verify=False, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Failed to start profile: {response.status_code} - {response.text}")
                return False, {"error": f"Failed to start profile: {response.status_code}"}

            data = response.json()
            logger.info(f"Start profile response: {data}")
            
            # Multilogin X API V2 trả về port trong data.port
            selenium_port = data.get("data", {}).get("port")
            
            if not selenium_port:
                logger.warning(f"No selenium port in response, but profile started successfully")
                # Profile đã start nhưng không có port, trả về success = True
                return True, {
                    "status": "started",
                    "selenium_port": None,
                    "profile_id": profile_id
                }

            logger.info(f"Profile started successfully on port: {selenium_port}")
            return True, {
                "status": "started",
                "selenium_port": selenium_port,
                "profile_id": profile_id
            }

        except Exception as e:
            logger.error(f"Error starting profile: {str(e)}")
            return False, {"error": f"Error starting profile: {str(e)}"}

    def get_profiles(self, folder_id: Optional[str] = None) -> Tuple[bool, Dict]:
        """
        Get list of profiles in folder
        
        Args:
            folder_id: Optional folder ID to filter
            
        Returns:
            (success, result with profiles list)
        """
        try:
            search_data = {
                "search_text": "",
                "limit": 100,
                "offset": 0
            }
            
            if folder_id:
                search_data['folder_id'] = folder_id
            
            response = requests.post(
                f"{self.api_url}/profile/search",
                json=search_data,
                headers=self.get_headers()
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get profiles: {response.status_code}")
                return False, {"error": f"Failed to get profiles: {response.status_code}"}
            
            result = response.json()
            profiles = result.get("data", {}).get("profiles", [])
            
            return True, {"profiles": profiles}
            
        except Exception as e:
            logger.error(f"Error getting profiles: {str(e)}")
            return False, {"error": f"Error getting profiles: {str(e)}"}
    
    def find_profile_by_name(self, name: str, folder_id: Optional[str] = None) -> Optional[str]:
        """
        Find profile by name
        
        Returns:
            profile_id if found, None otherwise
        """
        success, result = self.get_profiles(folder_id)
        if not success:
            return None
        
        for profile in result.get("profiles", []):
            if profile.get("name") == name:
                return profile.get("id")
        
        return None
    
    def delete_profile(self, profile_id: str) -> Tuple[bool, Dict]:
        """
        Delete a profile
        
        Args:
            profile_id: The profile ID to delete
            
        Returns:
            (success, result)
        """
        try:
            url = f"{self.api_url}/profile/remove"
            data = {
                "ids": [profile_id],
                "permanently": False  # Xóa vào trash, không xóa vĩnh viễn
            }
            
            response = requests.post(
                url,
                json=data,
                headers=self.get_headers()
            )
            
            if response.status_code not in [200, 201]:
                logger.error(f"Failed to delete profile: {response.status_code} - {response.text}")
                return False, {"error": f"Failed to delete profile: {response.status_code}"}
            
            logger.info(f"Profile {profile_id} deleted successfully")
            return True, {"status": "deleted", "profile_id": profile_id}
            
        except Exception as e:
            logger.error(f"Error deleting profile: {str(e)}")
            return False, {"error": f"Error deleting profile: {str(e)}"}
    
    def verify_proxy(self, automation_port: int) -> Tuple[bool, Dict]:
        """
        Verify the proxy is working by making a request to an IP check service
        
        Args:
            automation_port: The automation port from start_profile
            
        Returns:
            (success, result)
        """
        try:
            verify_url = "https://api.ipify.org?format=json"
            
            response = requests.get(
                verify_url,
                proxies={
                    "http": f"http://127.0.0.1:{automation_port}",
                    "https": f"http://127.0.0.1:{automation_port}"
                }
            )

            if response.status_code != 200:
                return False, {"error": "Failed to verify proxy"}

            ip_data = response.json()
            logger.info(f"Proxy verification successful. IP: {ip_data.get('ip')}")
            return True, {"ip": ip_data.get("ip")}
            
        except Exception as e:
            logger.error(f"Error verifying proxy: {str(e)}")
            return False, {"error": f"Error verifying proxy: {str(e)}"}
