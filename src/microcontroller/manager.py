import gc
import time

try:
    from typing import Any, Dict, List, Optional
except ImportError:
    pass  # No typing on device deploy

from chime import Chime
from config import CONFIG
from flair import Flair
from pico import Pico
from play import Play


class Manager:  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Implements the event loop checks and orchestrates interaction between modules

    Manager polls for events from MCU module Pi Pico W:
      - Touch and click inputs from MCU
      - Web clicks from Wi-Fi
      - Clock chimes from time tracking
      - Visual effect flair checks
    Manager passes EVENTS to Play module to process into ACTIONS:
      - Play module process these EVENTS and get corresponding MCU ACTIONS
        - Play audio, Change audio gain, Activate LED, Sleep/Wake device etc.
      - Manager then calls the MCU implementation (Pico) to execute the ACTIONS

    EVENTS: Events with params (booleans, numbers) from MCU and web app
    ACTIONS: Enumerated events mapped to MCU module method calls
    """

    def __init__(self) -> None:
        self.web: Optional[Any] = None  # Web is lazy imported later so mark it Any type
        self.time_tracker = time.monotonic()

        self.memory_sweep()

        self.play = Play()

        self.memory_sweep()

        self.pico = Pico()

        self.memory_sweep()

        self.pico.set_led_rgb(CONFIG.STARTUP_LED)

        self.flair = Flair()
        self.chime = Chime()

        self.memory_sweep()

        web_status = self.__init_check_wifi()

        self.memory_sweep()

        storage_status = self.pico.check_storage(self.play.get_files())

        self.memory_sweep()

        self.__report_system_status(web_status, storage_status)

    def __report_system_status(
        self, web_status: Optional[bool], storage_status: bool
    ) -> None:
        if storage_status and web_status:
            # Both storage and wi-fi ok
            self.pico.set_led_rgb(CONFIG.STARTUP_READY_LED)
            self.pico.beep()
            print("Device ready")
            time.sleep(1)
        else:
            if not storage_status and not web_status:
                # Both storage and w-fi failed
                self.pico.set_led_rgb(CONFIG.STARTUP_STORAGE_AND_WIFI_FAIL_LED)
                print("ERROR: Device not ready, no SD card and no Wi-Fi")
            elif not storage_status:
                # Only storage failed
                self.pico.set_led_rgb(CONFIG.STARTUP_STORAGE_FAIL_LED)
                print("ERROR: Device not ready, no SD card")
            elif web_status is None:
                # Unhandled exception during wi-fi, handled exception will set led
                self.pico.set_led_rgb(CONFIG.STARTUP_WIFI_UNKNOWN_FAIL_LED)
                print("ERROR: Device not ready, no Wi-Fi")
            print("Wait ...")
            time.sleep(3)

        self.memory_sweep()

    def __init_check_wifi(self) -> Optional[bool]:
        # Routes defined in Web will get initialised during get_web_instance import
        # and could fail without wi-fi
        try:
            return self.__init_wifi()
        except Exception as error:
            print(f"ERROR: Failed in wi-fi with error: {error}")
        return None

    def __init_wifi(self) -> bool:
        result = True
        if not CONFIG.MCU_SUPPORTS_WIFI:
            print("WARNING: Board do not support Wi-Fi")
            return result
        # Memory constrain, late import  only if board has wi-fi support
        from web import get_web_instance  # pylint: disable=import-outside-toplevel

        try:
            self.web = get_web_instance()
        except Exception as error:  # pylint: disable=broad-except
            print(f"ERROR: Wi-Fi setup failed with error {error}")

        if self.web and self.web.connected:
            if not self.web.sync_time(max_retries=CONFIG.NTP_MAX_RETRIES):
                result = False
                print("ERROR: Wi-Fi NTP sync failed")
                self.pico.set_led_rgb(CONFIG.STARTUP_WIFI_NTP_FAIL_LED)
        else:
            result = False
            print("ERROR: Wi-Fi connection or server failed")
            self.pico.set_led_rgb(CONFIG.STARTUP_WIFI_FAIL_LED)
        return result

    def __process_clicks(self) -> List[Dict[str, Any]]:
        return self.play.process_clicks(
            self.pico.get_touches(), self.pico.audio_playing()
        )

    def __process_web_click(
        self, actions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if not CONFIG.MCU_SUPPORTS_WIFI:
            return actions
        if not self.web or not self.web.connected:
            return actions
        if not self.web.device_registered:
            self.web.register_device()
        self.web.server.poll()  # TODO FIXME Wrap in a method call
        # TODO Consider clearing existing actions for web click
        web_actions = self.play.process_web_click(self.web.get_click())
        if web_actions:  # extend list of action
            actions.extend(web_actions)
        return actions

    def __process_flairs(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not CONFIG.FLAIR_ENABLED:
            return actions
        r, g, b = self.pico.get_led()
        flair_action = self.flair.process(r, g, b, self.pico.audio_playing())
        if flair_action:  # Append single action
            actions.append(flair_action)
        return actions

    def __process_chimes(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chimes = self.chime.get_chimes()
        # TODO Consider clearing existing actions for chimes
        if chimes:  # Extend list of actions
            actions.extend(
                self.play.get_chime_actions(chimes, self.chime.get_chime_audio_file())
            )
        return actions

    def process(self) -> None:
        actions = self.__process_chimes(
            self.__process_flairs(self.__process_web_click(self.__process_clicks()))
        )
        for action in actions:
            if self.play.is_play(action):
                print(f"PLAY {self.play.get_params(action)}")
                self.pico.play(self.play.get_params(action))
            elif self.play.is_stop(action):
                print("STOP")
                self.pico.stop()
            elif self.play.is_beep(action):
                print(f"BEEP {self.play.get_params(action)}")
                self.pico.beep()
            elif self.play.is_led(action):
                params = self.play.get_params(action)
                print(f"LED {params}")
                self.pico.set_led_rgb(params)
            elif self.play.is_gain(action):
                params = self.play.get_params(action)
                print(f"GAIN {params}")
                gain = params[0]
                self.pico.set_gain(gain)
            elif self.play.is_sleep(action):
                print("SLEEP")
                self.pico.sleep()
            elif self.play.is_wake(action):
                print("WAKE")
                self.pico.wake()
        self.__safe_memory_sweep(actions)

    @staticmethod
    def memory_sweep() -> None:
        # On a memory restricted MCU like Pi Pico call the garbage collector early and often
        # Refer: https://learn.adafruit.com/Memory-saving-tips-for-CircuitPython
        if CONFIG.MCU_MEMORY_CONSTRAINED:
            print("Memory sweep ...")
            gc.collect()

    def __safe_memory_sweep(self, actions: List[Dict[str, Any]]) -> None:
        periodic_sweep = False
        if time.monotonic() - self.time_tracker > CONFIG.PERIODIC_MEMORY_SWEEP_SECS:
            self.time_tracker = time.monotonic()
            periodic_sweep = True

        if (actions or periodic_sweep) and not self.pico.audio_playing():
            self.memory_sweep()
