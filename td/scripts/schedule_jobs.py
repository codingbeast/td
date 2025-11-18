"""schedule jobs for trading strategies"""
from pathlib import Path
import sys
from crontab import CronTab

def schedule_strategy(strategy_name, action, schedule):
    """_summary_

    Args:
        strategy_name (_type_): _description_
        action (_type_): _description_
        schedule (_type_): _description_
    """
    cron = CronTab(user=True)
    # Use the current Python executable and Path joining to build a robust
    # command. Quote paths/args to be safe for spaces and shell parsing.
    run_script = Path(__file__).parent / "run_strategy.py"
    command = (
        f'"{sys.executable}" "{str(run_script)}' + '"'
        f' --strategy "{strategy_name}" --action "{action}"'
    )
    job = cron.new(command=command)
    job.setall(schedule)
    cron.write()

# # Example: Schedule GOLDBEES buy at 8 AM on weekdays
# schedule_strategy("goldbees", "buy", "0 8 * * 1-5")

# # Example: Schedule CPSE sell at 3:30 PM on weekdays
# schedule_strategy("cpse", "sell", "30 15 * * 1-5")
