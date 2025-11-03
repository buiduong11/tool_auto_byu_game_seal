#!/usr/bin/env python3
"""
Test PyDoll với GameSeal - bypass reCAPTCHA v3
"""
import asyncio
import logging
from pydoll.browser import Chrome

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("="*70)
    logger.info("TEST: GameSeal Registration with PyDoll")
    logger.info("="*70)
    
    # Khởi tạo Chrome browser
    logger.info("Starting Chrome browser...")
    async with Chrome() as browser:
        tab = await browser.start()
        
        # Mở trang GameSeal register
        logger.info("Opening GameSeal register page...")
        await tab.go_to("https://gameseal.com/account/register")
        
        # Đợi page load
        await asyncio.sleep(3)
        
        # Điền form
        logger.info("\n[STEP 1] Filling registration form...")
        
        import random
        email = f"test_{random.randint(10000, 99999)}@outlook.com"
        password = "Abcdn@12345"
        
        # Điền form bằng JavaScript với đầy đủ events
        await tab.execute_script(f"""
            function setInputValue(input, value) {{
                // Focus
                input.focus();
                
                // Set value
                var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                nativeInputValueSetter.call(input, value);
                
                // Trigger events
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                input.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                
                // Blur
                input.blur();
            }}
            
            // Email
            var emailInput = document.querySelector('input[type="email"]');
            if (emailInput) {{
                setInputValue(emailInput, "{email}");
            }}
            
            // Wait a bit
            setTimeout(function() {{
                // Password 1
                var passwords = document.querySelectorAll('input[type="password"]');
                if (passwords.length >= 2) {{
                    setInputValue(passwords[0], "{password}");
                    
                    setTimeout(function() {{
                        // Password 2
                        setInputValue(passwords[1], "{password}");
                        
                        setTimeout(function() {{
                            // Checkbox
                            var checkbox = document.querySelector('input[type="checkbox"]');
                            if (checkbox && !checkbox.checked) {{
                                checkbox.click();
                            }}
                        }}, 500);
                    }}, 500);
                }}
            }}, 500);
        """)
        logger.info(f"✓ Form filling started: {email}")
        # Đợi JavaScript setTimeout hoàn thành (500 + 500 + 500 = 1500ms)
        await asyncio.sleep(3)
        logger.info("✓ Form filled and validated")
        
        # Click Continue button
        logger.info("\n[STEP 2] Clicking Continue button...")
        
        # Check button state
        button_info = await tab.execute_script("""
            var button = document.querySelector('button.btn-primary');
            if (button) {
                return {
                    disabled: button.disabled,
                    text: button.textContent.trim(),
                    classes: button.className
                };
            }
            return null;
        """)
        
        if isinstance(button_info, dict) and 'result' in button_info:
            button_data = button_info['result']['result']['value']
            logger.info(f"Button state: {button_data}")
        
        button = await tab.find(tag_name="button", class_name="btn-primary")
        
        if button:
            await button.click()
            logger.info("✓ Button clicked")
            
            # Đợi response
            logger.info("Waiting for response...")
            await asyncio.sleep(5)
            
            # Check URL
            result = await tab.execute_script("return window.location.href;")
            # Extract actual URL from result
            if isinstance(result, dict) and 'result' in result:
                current_url = result['result']['result']['value']
            else:
                current_url = result
                
            logger.info(f"Current URL: {current_url}")
            
            if current_url != "https://gameseal.com/account/register":
                logger.info(f"✅ SUCCESS! Redirected to: {current_url}")
            else:
                logger.warning("⚠️ Still at register page - reCAPTCHA may have blocked")
        else:
            logger.error("✗ Button not found!")
        
        # Keep browser open
        logger.info("\nBrowser will stay open for 30 seconds...")
        await asyncio.sleep(30)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted")
    except Exception as e:
        logger.error(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
