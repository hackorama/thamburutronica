from adafruit_datetime import datetime

from config import CONFIG


class Chime:  # pylint: disable=too-few-public-methods
    """
    Tracks clock time to provide clock chimes at the hour
    for only the designated time periods.
    """

    def __init__(self):
        self.__last_hour = -1
        self.__special_track_count = 0

    @staticmethod
    def __current_hour():
        return int(datetime.now().hour)

    def current_day(self):
        return f"{int(datetime.now().month)}-{int(datetime.now().day)}"

    @staticmethod
    def __chimes(hour):
        return hour if hour <= 12 else hour - 12

    def __valid_hours(self, hour):
        return CONFIG.CHIME_START_HOURS <= hour <= CONFIG.CHIME_END_HOURS

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

    def get_chime_audio_file(self):
        day = self.current_day()
        special_audio_files = CONFIG.CHIME_SPECIAL_DAYS.get(day)
        if special_audio_files:
            selected = self.__special_track_count
            count = len(special_audio_files)
            self.__special_track_count = selected + 1 if selected < count - 1 else 0
            return special_audio_files[selected]

        return CONFIG.CHIME_AUDIO_FILE
