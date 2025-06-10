import time
import schedule
from main import full_scan
# Define a function to run the scheduler
def run_scheduler(target_ip):
    print(f"Running immediate scan on {target_ip}...")
    schedule.every(2).days.do(full_scan)
    
    while True:
        schedule.run_pending()
        time.sleep(60)