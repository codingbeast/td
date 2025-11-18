# In your core/utilities.py
import psutil
import time
from mycolorlogger.mylogger import log

logger = log.logger

def monitor_system():
    while True:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        if cpu > 90 or memory > 90:
            # Send alert
            pass
        time.sleep(60)


