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

def count_card_sets():
    """Đếm số lượng card sets"""
    card_file = "data/data_ci/data_ci.txt"
    try:
        with open(card_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        # Mỗi dòng là 1 card
        return len(lines)
    except:
        return 0

def main():
    logger.info("="*70)
    logger.info("AUTO LOOP - CONTINUOUS REGISTRATION")
    logger.info("="*70)
    
    total_mail_sets = count_mail_sets()
    total_card_sets = count_card_sets()
    
    logger.info(f"Total mail sets available: {total_mail_sets}")
    logger.info(f"Total card sets available: {total_card_sets}")
    
    # Số phiên chạy = min(mail, card)
    total_runs = min(total_mail_sets, total_card_sets)
    
    if total_runs == 0:
        logger.error("No data found! Need both mail and card data.")
        return
    
    logger.info(f"Will run {total_runs} sessions (limited by {'mail' if total_mail_sets < total_card_sets else 'card'} data)")
    
    if total_mail_sets == 0:
        logger.error("No mail data found!")
        return
    
    if total_card_sets == 0:
        logger.error("No card data found!")
        return
    
    while True:
        current_index = read_current_index()
        
        # Check nếu đã hết data (mail hoặc card)
        if current_index >= total_runs:
            logger.info("\n" + "="*70)
            logger.info("✅ ALL SESSIONS COMPLETED!")
            logger.info("="*70)
            logger.info(f"Processed {total_runs} sessions successfully.")
            logger.info(f"Mail data: {current_index}/{total_mail_sets}")
            logger.info(f"Card data: {current_index}/{total_card_sets}")
            break
        
        logger.info("\n" + "="*70)
        logger.info(f"PROCESSING SESSION {current_index + 1}/{total_runs}")
        logger.info(f"Mail: {current_index + 1}/{total_mail_sets} | Card: {current_index + 1}/{total_card_sets}")
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
