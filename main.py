import subprocess
import time
from datetime import datetime
import traceback

if __name__ == '__main__':
    try:
        result = subprocess.run(['python', 'main_predict.py'], capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        result.check_returncode()
    except subprocess.CalledProcessError as e:
        print(e.stderr)
    minute_10_run = datetime.today()
    sleep_time = 60
    while True:
        now_day = datetime.today()
        time_difference = now_day - minute_10_run
        if time_difference.total_seconds() > 600:
            try:
                result = subprocess.run(['python', 'main_predict.py'], capture_output=True, text=True, encoding='utf-8')
                print(result.stdout)
                result.check_returncode()
            except subprocess.CalledProcessError as e:
                print(e.stderr)
            minute_10_run = datetime.today()
            time.sleep(sleep_time)
        else:
            time.sleep(sleep_time)