#!/usr/bin/env python3
"""
Simple Workflow: 
1. Bạn mở profile thủ công trong Multilogin
2. Script sẽ tự động tìm browser và chạy automation
"""
import logging
import sys
import time
from gameseal_auto_login import GameSealAutoLogin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 70)
    logger.info("SIMPLE AUTO LOGIN WORKFLOW")
    logger.info("=" * 70)
    logger.info("\nĐảm bảo Multilogin profile đã được start và browser đang mở...")
    logger.info("Đợi 3 giây...")
    time.sleep(3)
    
    EMAIL = "jacki2egthome@outlook.sg"
    PASSWORD = "Abc@12345"
    
    logger.info("\nĐang tìm browser...")
    automation = GameSealAutoLogin(email=EMAIL, password=PASSWORD, debug_port=None)
    
    if not automation.connect_to_browser():
        logger.error("\n❌ Không tìm thấy browser!")
        logger.info("Hãy đảm bảo:")
        logger.info("- Multilogin profile đã được start")
        logger.info("- Browser đang mở")
        return False
    
    logger.info("\n✓ Đã kết nối với browser!")
    logger.info("\nBắt đầu automation...")
    
    success = automation.run_login_workflow()
    
    if success:
        logger.info("\n" + "=" * 70)
        logger.info("✅ SUCCESS! Auto login completed")
        logger.info("=" * 70)
    else:
        logger.error("\n❌ FAILED! Auto login failed")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
