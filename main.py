import logging
from proxy_handler import NineProxyHandler
from multilogin import MultiLoginHandler
import subprocess
import time
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def count_chrome_windows():
    """Count number of Chrome windows"""
    applescript = '''
    tell application "Google Chrome"
        count windows
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', applescript], 
                              capture_output=True, text=True, timeout=5)
        return int(result.stdout.strip())
    except:
        return 0

def wait_for_new_browser_window(initial_count, timeout=60):
    """Wait for a new browser window (Multilogin profile) to open"""
    logger.info(f"Waiting for Multilogin browser to open (up to {timeout}s)...")
    logger.info("Please START the profile in Multilogin app now!")
    
    for i in range(timeout):
        current_count = count_chrome_windows()
        if current_count > initial_count:
            logger.info(f"✓ New browser window detected! (Windows: {current_count})")
            time.sleep(3)  # Wait for full initialization
            return True
        time.sleep(1)
        if i % 10 == 0 and i > 0:
            logger.info(f"Still waiting... ({i}s elapsed)")
    
    logger.error("No new browser window detected")
    return False

def execute_js_in_chrome(js_code):
    """Execute JavaScript in Multilogin browser (last window)"""
    js_escaped = js_code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
    
    applescript = f'''
    tell application "Google Chrome"
        set windowCount to count windows
        tell active tab of window windowCount
            execute javascript "{js_escaped}"
        end tell
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', applescript], 
                          capture_output=True, text=True, timeout=5)
    return result

def open_new_tab_in_last_window(url):
    """Mở tab mới trong window cuối cùng (Multilogin browser)"""
    # Try Chromium first (Multilogin uses Chromium)
    applescript = f'''
    tell application "Chromium"
        activate
        set windowCount to count windows
        if windowCount > 0 then
            tell window windowCount
                set URL of active tab to "{url}"
            end tell
        end if
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', applescript], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logger.info(f"✓ Opened URL in Chromium browser: {url}")
            return
    except:
        pass
    
    # Fallback to Chrome if Chromium fails
    applescript = f'''
    tell application "Google Chrome"
        activate
        set windowCount to count windows
        if windowCount > 0 then
            tell window windowCount
                set URL of active tab to "{url}"
            end tell
        end if
    end tell
    '''
    subprocess.run(['osascript', '-e', applescript])
    logger.info(f"✓ Opened URL in Chrome browser: {url}")

def wait_for_element(selector, timeout=10):
    """Wait for element to exist"""
    js = f"document.querySelector('{selector}') !== null"
    
    for i in range(timeout):
        try:
            result = execute_js_in_chrome(js)
            if 'true' in result.stdout.lower():
                return True
        except:
            pass
        time.sleep(1)
    
    return False

def click_element(selector, wait_time=1):
    """Click element by CSS selector"""
    js = f"document.querySelector('{selector}').click()"
    execute_js_in_chrome(js)
    logger.info(f"✓ Clicked: {selector}")
    time.sleep(wait_time)

def type_text(selector, text, human_like=True):
    """Type text into element"""
    if human_like:
        for char in text:
            escaped_char = char.replace("'", "\\'").replace('"', '\\"')
            js = f'''
            var el = document.querySelector('{selector}');
            el.value += '{escaped_char}';
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            '''
            try:
                execute_js_in_chrome(js)
                time.sleep(0.1)
            except:
                pass
    else:
        escaped_text = text.replace("'", "\\'").replace('"', '\\"')
        js = f'''
        var el = document.querySelector('{selector}');
        el.value = '{escaped_text}';
        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
        '''
        execute_js_in_chrome(js)
    
    logger.info(f"✓ Typed into: {selector}")
    time.sleep(0.5)

def run_gameseal_automation():
    """Run GameSeal login automation"""
    try:
        logger.info("\n" + "=" * 60)
        logger.info("Starting GameSeal automation...")
        logger.info("=" * 60)
        
        # Step 1: Navigate to gameseal.com
        logger.info("\nStep 1: Navigating to gameseal.com...")
        open_new_tab_in_last_window("https://gameseal.com/")
        time.sleep(6)  # Wait for page to fully load
        
        # Step 2: Click account icon
        logger.info("\nStep 2: Clicking account icon...")
        if not wait_for_element('svg.icon-layout-account', timeout=15):
            logger.error("Account icon not found - page may not have loaded")
            return False
        time.sleep(1)  # Small delay before click
        click_element('svg.icon-layout-account', wait_time=2)
        
        # Step 3: Click REGISTER
        logger.info("\nStep 3: Clicking REGISTER...")
        if not wait_for_element('a[href="/account/register"].register-link', timeout=5):
            logger.error("Register link not found")
            return False
        click_element('a[href="/account/register"].register-link', wait_time=2)
        
        # Step 4: Click Login link
        logger.info("\nStep 4: Clicking Login link...")
        if not wait_for_element('a.card-subtitle-link[href="/account/login"]', timeout=5):
            logger.error("Login link not found")
            return False
        click_element('a.card-subtitle-link[href="/account/login"]', wait_time=2)
        
        # Step 5: Fill email
        logger.info("\nStep 5: Filling email...")
        if not wait_for_element('#loginMail', timeout=5):
            logger.error("Email field not found")
            return False
        type_text('#loginMail', 'catalinaart14_01582@outlook.com', human_like=True)
        
        # Step 6: Fill password
        logger.info("\nStep 6: Filling password...")
        type_text('#loginPassword', 'Abc@12345', human_like=True)
        
        # Step 7: Click continue
        logger.info("\nStep 7: Clicking CONTINUE button...")
        click_element('.login-submit button.btn-primary', wait_time=3)
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Login automation completed!")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"Automation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    proxy_handler = NineProxyHandler()
    multilogin_handler = MultiLoginHandler()
    
    # Step 1: Login to Multilogin
    logger.info("Step 1: Logging in to Multilogin...")
    success, login_result = multilogin_handler.login()
    
    if not success:
        logger.error(f"Failed to login to Multilogin: {login_result.get('error')}")
        return False
    
    logger.info("✓ Logged in successfully")
        
    # Step 2: Get proxy
    logger.info("Step 2: Getting proxy...")
    success, proxy_result = proxy_handler.get_next_proxy()
    
    if not success:
        logger.error(f"Failed to get proxy: {proxy_result.get('error')}")
        return False
        
    logger.info(f"Got proxy: {proxy_result['host']}:{proxy_result['port']}")
    
    # Step 3: Validate proxy with Multilogin
    logger.info("Step 3: Validating proxy...")
    success, validate_result = multilogin_handler.validate_proxy(proxy_result)
    
    if not success:
        logger.warning(f"Proxy validation warning: {validate_result.get('error')}")
        logger.info("Continuing anyway...")
    
    # Step 4: Check existing profile or create new
    logger.info("Step 4: Checking for existing profile...")
    profile_name = f"AutoBuy_Port_{proxy_result['port']}"
    profile_id = multilogin_handler.find_profile_by_name(profile_name)
    
    if profile_id:
        logger.info(f"✓ Reusing existing profile: {profile_name} (ID: {profile_id})")
    else:
        logger.info("Creating new Multilogin profile...")
        success, profile_result = multilogin_handler.create_profile(
            proxy_result, 
            profile_name=profile_name
        )
        
        if not success:
            logger.error(f"Failed to create profile: {profile_result.get('error')}")
            return False
            
        profile_id = profile_result["profile_id"]
        logger.info(f"✓ Created new profile: {profile_name} (ID: {profile_id})")
    
    # Step 5: Auto-start profile using Multilogin API
    logger.info("\nStep 5: Starting Multilogin profile...")
    
    # Try API method first
    success, start_result = multilogin_handler.start_profile(profile_id)
    
    if success and start_result.get("selenium_port"):
        logger.info(f"✓ Profile started via API on port {start_result['selenium_port']}")
        # Wait a bit for browser to fully initialize
        time.sleep(3)
    else:
        # Check if error is "already running"
        error_msg = start_result.get("error", "")
        if "ALREADY_RUNNING" in error_msg or "already running" in error_msg.lower():
            logger.info("✓ Profile is already running, continuing...")
            time.sleep(2)
        else:
            logger.warning(f"Could not start profile via API: {error_msg}")
            logger.info("Assuming profile is already open or will be opened manually...")
            time.sleep(5)
    
    # Step 6: Open GameSeal in new tab
    logger.info("\nStep 6: Opening GameSeal.com...")
    open_new_tab_in_last_window("https://gameseal.com/")
    time.sleep(3)
    
    logger.info("=" * 60)
    logger.info("✓ SUCCESS! Automation completed")
    logger.info(f"Profile: {profile_name}")
    logger.info(f"Proxy: {proxy_result['host']}:{proxy_result['port']}")
    logger.info("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)