import time
import schedule
from main import full_scan
# Define a function to run the scheduler
def run_scheduler(target_ip):
    schedule.every(2).days.do(full_scan, target_ip=target_ip)
    
    while True:
        schedule.run_pending()
        time.sleep(60)