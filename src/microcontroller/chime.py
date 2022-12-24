from adafruit_datetime import datetime

from config import CONFIG


class Chime:  # pylint: disable=too-few-public-methods
    """
    Tracks clock time to provide clock chimes at the hour
    for only the designated time periods.
    """

    START_HOURS = CONFIG.CHIME_START_HOURS
    END_HOURS = CONFIG.CHIME_END_HOURS

    def __init__(self):
        self.__last_hour = -1

    @staticmethod
    def __current_hour():
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
        return False

    @staticmethod
    def __time_synced():
        # if time sync failed time will reset to chip epoch
        return int(datetime.now().year) > CONFIG.MCU_CHIP_EPOCH_YEAR

    def get_chimes(self):
        hour = self.__current_hour()
        if self.__time_synced() and self.__hour_changed() and self.__valid_hours(hour):
            return self.__chimes(hour)
        return None
