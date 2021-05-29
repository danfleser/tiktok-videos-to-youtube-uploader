import os
import sched
import time
from datetime import datetime


s = sched.scheduler(time.time, time.sleep)
sleep_time = 60 * 60 * 25


def run(sc):
    print(f"Start Time = {datetime.now().strftime('%H:%M:%S')}")

    scrape_cmd = f"python download_process_upload.py"
    os.system(scrape_cmd)

    print(f"End Time = {datetime.now().strftime('%H:%M:%S')}")
    # do your stuff
    s.enter(sleep_time, 1, run, (sc,))


s.enter(0, 1, run, (s,))
s.run()
