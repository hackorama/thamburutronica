class CONFIG:  # pylint: disable=too-few-public-methods
    """
    Common configuration used across modules
    """

    PROJECT_NAME = "Thamburutronica"
    VERSION = "0.2.0"

    MCU = "Pi PICO W"
    MCU_SUPPORTS_WIFI = True
    MCU_CHIP_EPOCH_YEAR = 2020  # Chip epoch 2020-01-01T00:00:00
    MCU_MEMORY_CONSTRAINED = True  # True for aggressive memory collection

    AUDIO_AMP_MONO = True  # Enable only Left channel
    AUDIO_AMP_SHUTDOWN_ON_SLEEP = True
    AUDIO_BUFFER_SIZE_BYTES = 1024  # Valid values 8-1024, 0 for internal default buffer
    AUDIO_GAIN_DEFAULT_DB = 16
    AUDIO_GAIN_MAX_DB = 30
    AUDIO_GAIN_STEP_DB = 2
    AUDIO_QUIESCENT_VALUE = 0  # 0, 1x 32768, 2x 65535 Audio output value when no signal
    AUDIO_BEEP_FILE = "beep.wav"
    AUDIO_MIXER_ENABLED = True
    AUDIO_MIXER_GAIN_ENABLED = False
    AUDIO_MIXER_VOICE_COUNT = 1
    AUDIO_MIXER_DEFAULT_CHANNEL = 0

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
    CHIME_ON_LED_COLOR = (0, 200, 0)  # green
    CHIME_OFF_LED_COLOR = (200, 0, 0)  # red

    NTP_TZ_OFFSET_ENV = "TZ_OFFSET"
    NTP_TIMEOUT_SECS = 30  # Default 10
    NTP_MAX_RETRIES = 3

    FLAIR_ENABLED = False
    FLAIR_ANIMATION_SPEED = 3

    SLEEP_ON_INACTIVITY_FOR_SECS = 60 * 3
    SLEEP_LED_COLOR = (0, 0, 0)

    WIFI_MAX_RETRIES = 6
    WIFI_SYSTEM_RESTART_ON_ERROR = False
    WIFI_SYSTEM_RESTART_WAIT_SECS = 3
    WIFI_SSID_ENV = "WIFI_SSID"
    WIFI_PASSWORD_ENV = "WIFI_PASSWORD"
    APP_API_SERVER_ENV = "APP_API_SERVER"

    SD_MOUNT = "/sd"
    TOUCH_BUTTON_COUNT = 12
    EVENT_LOOP_SECS = 0.2
    PERIODIC_MEMORY_SWEEP_SECS = 60 * 5

    MODE_LED_COLOR = [
        (22, 159, 255),  # Touch mode, radiant blue
        (200, 0, 200),  # Tap mode, magenta
        (255, 164, 0),  # Tap custom mode, bright orange
    ]

    RICKROLL_AUDIO_FILE = "rickroll.wav"

    PLAY_LIST_BY_MODE = [
        #
        # Audio files for each mode as list for each chord
        # This is 3 modes each with 4 files for the 4 chords
        #
        ["panchamam.wav", "sarana.wav", "anusarana.wav", "manthram.wav"],  # Touch mode
        ["panchamam.wav", "sarana.wav", "anusarana.wav", "manthram.wav"],  # Tap mode
        ["epic.wav", "oriental.wav", "guitar.wav", "birds.wav"],  # Tap custom mode
    ]

    CHIME_SPECIAL_DAYS = {
        #
        # Key  : MONTH-DAY
        # Value: list of audio
        #
        # The list of audio that will be cycled through as hourly chime
        # If a single audio is provided then it will be repeated as hourly chime
        #
        "1-1": ["als.wav"],
        "7-4": ["hbd.wav"],
        "12-25": ["aiam.wav", "dth.wav", "hth.wav", "jttw.wav", "oct.wav", "sn.wav"],
        "12-31": ["als.wav"],
    }
