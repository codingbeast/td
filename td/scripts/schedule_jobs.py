from crontab import CronTab
import os
from pathlib import Path

def schedule_strategy(strategy_name, action, schedule):
    cron = CronTab(user=True)
    command = f"python {Path(__file__).parent}/run_strategy.py --strategy {strategy_name} --action {action}"
    job = cron.new(command=command)
    job.setall(schedule)
    cron.write()

# Example: Schedule GOLDBEES buy at 8 AM on weekdays
schedule_strategy("goldbees", "buy", "0 8 * * 1-5")

# Example: Schedule CPSE sell at 3:30 PM on weekdays
schedule_strategy("cpse", "sell", "30 15 * * 1-5")