import time

from config import CONFIG
from manager import Manager


def run():
    print(f"{CONFIG.PROJECT_NAME} {CONFIG.VERSION}")
    manager = Manager()
    print(f"Starting event loop at tick rate {CONFIG.EVENT_LOOP_SECS} secs")
    time_tracker = 0
    while True:
        try:
            if time.monotonic() - time_tracker > CONFIG.EVENT_LOOP_SECS:
                time_tracker = time.monotonic()
                manager.process()
        except KeyboardInterrupt:
            print(f"Exiting event loop and shutting down {CONFIG.PROJECT_NAME}")
            break


run()
