import time

from adafruit_datetime import datetime

from config import CONFIG


class Chime:
    """
    Tracks clock time to provide clock chimes at the hour
    for only the designated time periods.
    """

    START_HOURS = CONFIG.CLOCK_CHIME_START_HOURS
    END_HOURS = CONFIG.CLOCK_CHIME_END_HOURS

    def __init__(self):
        self.__last_hour = -1

    @staticmethod
    def __current_hour():
        dt = datetime.now()
        return int(datetime.now().hour)

    @staticmethod
    def __chimes(hour):
        return hour if hour <= 12 else hour - 12

    def __valid_hours(self, hour):
        return self.START_HOURS <= hour <= self.END_HOURS

    def __hour_changed(self):
        hour = self.__current_hour()
        if self.__last_hour < 0:
            self.__last_hour = hour
        elif self.__last_hour != hour:
            self.__last_hour = hour
            return True

    @staticmethod
    def __time_synced():
        # Check in case NTP sync failed through Wi-Fi
        # Without NTP time will reset to chip year epoch before 2022
        return int(datetime.now().year) >= 2022

    def get_chimes(self):
        hour = self.__current_hour()
        if self.__time_synced() and self.__hour_changed() and self.__valid_hours(hour):
            return self.__chimes(hour)

    def play_chimes(self):
        now = datetime.now()
        print(f"{now.hour}:{now.minute}:{now.second} {self.__current_hour()}")
        count = self.get_chimes()
        if count:
            print(f"Play {count} chimes ...")


if __name__ == "__main__":
    chime = Chime()
    while True:
        chime.play_chimes()
        time.sleep(60)
