class CONFIG:  # pylint: disable=too-few-public-methods
    """
    Common configuration used across modules
    """

    PROJECT_NAME = "Thamburutronica"
    VERSION = "0.2.0"

    MCU = "Pi PICO W"
    MCU_SUPPORTS_WIFI = True
    MCU_CHIP_EPOCH_YEAR = 2020  # chip epoch 2020-01-01T00:00:00
    MCU_MEMORY_CONSTRAINED = True  # True for aggressive memory collection

    AUDIO_BUFFER_SIZE_BYTES = 1024  # valid values 8-1024, 0 for internal default buffer
    AUDIO_GAIN_DEFAULT_DB = 4
    AUDIO_GAIN_MAX_DB = 30
    AUDIO_GAIN_STEP_DB = 2
    AUDIO_BEEP_FILE = "beep.wav"

    STARTUP_LED = (200, 200, 200)  # white
    STARTUP_WIFI_FAIL_LED = (255, 0, 0)  # red
    STARTUP_WIFI_NTP_FAIL_LED = (255, 127, 0)  # orange
    STARTUP_STORAGE_FAIL_LED = (200, 200, 0)  # yellow
    STARTUP_STORAGE_AND_WIFI_FAIL_LED = (75, 0, 130)  # indigo
    STARTUP_WIFI_UNKNOWN_FAIL_LED = (0, 255, 255)  # cyan
    STARTUP_READY_LED = (0, 255, 0)  # green

    CHIME_ON = True
    CHIME_START_HOURS = 9  # 9 AM
    CHIME_END_HOURS = 22  # 10 PM
    CHIME_AUDIO_FILE = "chime-ambient.wav"
    CHIME_LED = (227, 200, 0)  # yellow

    WIFI_SSID_ENV = "WIFI_SSID"
    WIFI_PASSWORD_ENV = "WIFI_PASSWORD"
    APP_API_SERVER_ENV = "APP_API_SERVER"

    NTP_TZ_OFFSET_ENV = "TZ_OFFSET"
    NTP_TIMEOUT_SECS = 30  # Default 10
    NTP_MAX_RETRIES = 3

    FLAIR_ENABLED = False
    FLAIR_ANIMATION_SPEED = 3

    SLEEP_ON_INACTIVITY_FOR_SECS = 60
    TOUCH_BUTTON_COUNT = 12
    EVENT_LOOP_SECS = 0.2
    SD_MOUNT = "/sd"
