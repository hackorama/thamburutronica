import gc

from chime import Chime
from config import CONFIG
from flair import Flair
from pico import Pico
from play import Play


class Manager:
    """
    Implement the event loop checks and orchestrate interaction between modules

    Manager polls for events from MCU module Pico:
      - Touch and click inputs from MCU
      - Web clicks from Wi-Fi
      - Clock chimes from time tracking
      - Visual effect flair checks
    Manager passes events to Play module to process into actions:
      - Play module process these events and get corresponding MCU actions
      - Play audio, Change audio gain, Activate LED, Sleep/Wake device etc.

    Events: Basic booleans and numbers from MCU clicks
    Actions: Enumerated and mapped to MCU module method calls
    """

    def __init__(self):

        gc.collect()

        self.play = Play()

        gc.collect()

        self.pico = Pico()

        gc.collect()

        self.flair = Flair()
        self.chime = Chime()

        gc.collect()

        self.web = None
        if CONFIG.MCU_SUPPORTS_WIFI:
            from web import get_web_instance  # save memory, late init

            self.web = get_web_instance()

        gc.collect()

        self.pico.check_storage(self.play.get_files())
        self.pico.set_led(
            CONFIG.STARTUP_LED_R, CONFIG.STARTUP_LED_G, CONFIG.STARTUP_LED_B
        )

        if not CONFIG.RESTRICT_MEMORY:
            self.diag()

        gc.collect()

    def __process_clicks(self):
        return self.play.process_clicks(self.pico.get_touches(), self.pico.get_clicks())

    def __process_web_click(self, actions):
        if not CONFIG.MCU_SUPPORTS_WIFI:
            return actions
        if not self.web or not self.web.connected:
            return actions
        if not self.web.device_registered:
            self.web.register_device()
        self.web.server.poll()  # TODO FIXME method call
        # TODO Consider clearing existing actions for web click
        web_action = self.play.process_web_click(self.web.get_click())
        if web_action:  # append single action
            actions.append(web_action)
        return actions

    def __process_flairs(self, actions):
        r, g, b = self.pico.get_led()
        flair_action = self.flair.process(r, g, b, self.pico.audio_playing())
        if flair_action:  # append single action
            actions.append(flair_action)
        return actions

    def __process_chimes(self, actions):
        chimes = self.chime.get_chimes()
        # TODO Consider clearing existing actions for chimes
        if chimes:  # extend list of actions
            actions.extend(self.play.get_chime_actions(chimes))
        return actions

    def process(self):
        actions = self.__process_chimes(
            self.__process_flairs(self.__process_web_click(self.__process_clicks()))
        )
        for action in actions:
            if self.play.is_play(action):
                print(f"PLAY {self.play.get_params(action)}")
                self.pico.play(self.play.get_params(action))
            if self.play.is_blocking_play(action):
                params = self.play.get_params(action)
                print(f"BLOCKING PLAY {params}")
                file = params[0]
                channel = params[1]
                count = params[2]
                self.pico.play(file, channel=channel, count=count)
            elif self.play.is_stop(action):
                print("STOP")
                self.pico.stop()
            elif self.play.is_beep(action):
                print(f"BEEP {self.play.get_params(action)}")
                self.pico.beep(tone_freq=self.play.get_params(action))
            elif self.play.is_led(action):
                params = self.play.get_params(action)
                print(f"LED {params}")
                r = params[0]
                g = params[1]
                b = params[2]
                self.pico.set_led(r, g, b)
            elif self.play.is_gain(action):
                params = self.play.get_params(action)
                print(f"GAIN {params}")
                gain = params[0]
                channel = None
                if len(params) > 1:
                    channel = params[1]
                self.pico.set_gain(gain, channel)
            elif self.play.is_sleep(action):
                print(f"SLEEP")
                self.pico.sleep()
                pass
            elif self.play.is_wake(action):
                print(f"WAKE")
                self.pico.wake()
        if len(actions):
            gc.collect()

    def diag(self):
        result = self.pico.diag()
        for k, v in sorted(result.items()):
            print(f"{k}: {v}")
