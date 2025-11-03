#!/usr/bin/env python3
"""
Auto Loop Script - Chạy outlook_registration.py liên tục cho đến hết data
"""
import subprocess
import time
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def read_current_index():
    """Đọc index hiện tại"""
    index_file = "data/data_mail/current_index.txt"
    try:
        with open(index_file, 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def count_mail_sets():
    """Đếm số lượng mail sets"""
    mail_file = "data/data_mail/data_mail.txt"
    try:
        with open(mail_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        # Mỗi set có 4 dòng
        return len(lines) // 4
    except:
        return 0

def main():
    logger.info("="*70)
    logger.info("AUTO LOOP - CONTINUOUS REGISTRATION")
    logger.info("="*70)
    
    total_sets = count_mail_sets()
    logger.info(f"Total mail sets available: {total_sets}")
    
    if total_sets == 0:
        logger.error("No mail data found!")
        return
    
    while True:
        current_index = read_current_index()
        
        # Check nếu đã hết data
        if current_index >= total_sets:
            logger.info("\n" + "="*70)
            logger.info("✅ ALL MAIL SETS COMPLETED!")
            logger.info("="*70)
            logger.info(f"Processed {total_sets} mail sets successfully.")
            break
        
        logger.info("\n" + "="*70)
        logger.info(f"PROCESSING MAIL SET {current_index + 1}/{total_sets}")
        logger.info("="*70)
        
        # Chạy outlook_registration.py
        try:
            result = subprocess.run(
                ["python", "outlook_registration.py"],
                cwd=os.getcwd(),
                capture_output=False,
                text=True
            )
            
            # Đợi 5 giây trước khi chạy lại
            logger.info("\nWaiting 5 seconds before next run...")
            time.sleep(5)
            
        except KeyboardInterrupt:
            logger.info("\n⚠️  Interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error running script: {str(e)}")
            logger.info("Waiting 10 seconds before retry...")
            time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Stopped by user")
