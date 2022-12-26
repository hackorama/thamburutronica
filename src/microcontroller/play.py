import time

from config import CONFIG


class Play:  # pylint: disable=too-many-instance-attributes
    """
    TODO FIXME too-many-instance-attributes : move attributes to common config.CONFIG

    Pure python class with music player control logic, no MCU specific imports

    All MCU specific implementation will be in a separate MCU module like Pico for Pi Pico

    This module will get events from the MCU module and process it
    including some state tracking across the event loop ticks
    and generate the required MCU actions for each event loop tick.

    These actions are then send to MCU implementation module like Pico
    to be realised.
    """

    PLAY = "PLAY"
    STOP = "STOP"
    BEEP = "BEEP"
    LED = "LED"
    GAIN = "GAIN"
    SLEEP = "SLEEP"
    WAKE = "WAKE"

    def __init__(self, debug=False, trace=False):

        self.__page_current = 0
        self.page_size = len(CONFIG.PLAY_LIST_BY_MODE[0])
        # pages that need key continuously pressed to play, otherwise single click starts playing
        self.momentary_click_mode_pages = [0]

        # play buttons by default are 0 to page_size buttons
        # page flip must be a button that is not play button
        self.page_flip_button = 4

        self.debug = debug
        self.trace = trace

        self.audio_gain_default = CONFIG.AUDIO_GAIN_DEFAULT_DB
        self.audio_gain_current = self.audio_gain_default
        self.audio_gain_min = 0
        self.audio_gain_max = CONFIG.AUDIO_GAIN_MAX_DB
        self.audio_gain_step = CONFIG.AUDIO_GAIN_STEP_DB

        self.audio_up_button = 7
        self.audio_down_button = 8

        self.chime_mode_button = 9
        self.chime_on = CONFIG.CHIME_ON

        self.max_buttons = CONFIG.TOUCH_BUTTON_COUNT  # max buttons supported by board
        self.last_button_click = -1
        self.last_play_button_click = -1

        # map by order the physical button clicks to touch button click
        self.clicks_to_touches_map = [
            self.page_flip_button,
            self.audio_up_button,
            self.audio_down_button,
        ]

        self.rickroll_page = 2
        self.rickroll_counter = 0
        self.rickroll_frequency = 6

        self.web_play_page = 1

        self.sleeping = False
        self.last_activity_at_secs = time.monotonic()

        self.valid_config = self.__assert_configuration()

    def __assert_configuration(self):
        # control buttons are unique
        assert (
            len({self.page_flip_button, self.audio_up_button, self.audio_down_button})
            == 3
        )
        # control buttons cannot be the initial play buttons
        assert self.page_flip_button >= self.page_size
        assert self.audio_up_button >= self.page_size
        assert self.audio_down_button >= self.page_size
        # control buttons are valid
        assert self.page_flip_button < self.max_buttons
        assert self.audio_up_button < self.max_buttons
        assert self.audio_down_button < self.max_buttons
        # all pages should have same songs count
        for page_list in CONFIG.PLAY_LIST_BY_MODE:
            assert self.page_size == len(page_list)
        # valid page for momentary click mode
        for page_number in self.momentary_click_mode_pages:
            assert page_number < self.page_size
        # led color list should match page count
        assert len(CONFIG.PLAY_LIST_BY_MODE) == len(CONFIG.MODE_LED_COLOR)
        # rickroll page is valid
        assert self.rickroll_page < self.page_size

        return True

    def __all_play_buttons_clicked(self, current_clicks):
        return (
            len(current_clicks) == self.page_size
            and max(current_clicks) <= self.page_size
        )

    def __only_page_flip_button_clicked(self, current_clicks):
        return len(current_clicks) == 1 and self.page_flip_button in current_clicks

    def __valid_play_click(self, click):
        return click is not None and click <= len(CONFIG.PLAY_LIST_BY_MODE)

    def __valid_control_click(self, clicks):
        return (
            self.__volume_up_clicked(clicks)
            or self.__volume_up_clicked(clicks)
            or self.__only_page_flip_button_clicked(clicks)
        )

    def __current_click_is_same_as_last_click(self, current_click):
        return self.last_button_click == current_click

    def __current_click_is_not_same_as_last_click(self, current_click):
        return not self.__current_click_is_same_as_last_click(current_click)

    def __current_click_is_same_as_last_play_click(self, current_click):
        return self.last_play_button_click == current_click

    def __volume_up_clicked(self, current_clicks):
        return self.audio_up_button in current_clicks

    def __volume_down_clicked(self, current_clicks):
        return self.audio_down_button in current_clicks

    def __momentary_click_page(self):
        return self.__page_current in self.momentary_click_mode_pages

    def __regular_click_page(self):
        return not self.__momentary_click_page()

    def __page_flip(self):
        if self.__page_current == len(CONFIG.PLAY_LIST_BY_MODE) - 1:
            self.__page_current = 0
        else:
            self.__page_current += 1

    def __page_clicked(self, current_clicks, current_button_click):
        # all play buttons clicked is same as a page flip button click
        if self.__all_play_buttons_clicked(
            current_clicks
        ) or self.__only_page_flip_button_clicked(current_clicks):
            if self.__current_click_is_not_same_as_last_click(current_button_click):
                self.__page_flip()
                return True
        return False

    def __volume_clicked(self, current_clicks, current_click):
        if self.__current_click_is_same_as_last_click(current_click):
            return False
        if self.__volume_up_clicked(current_clicks) and self.__volume_down_clicked(
            current_clicks
        ):
            self.audio_gain_current = self.audio_gain_default
        elif self.__volume_up_clicked(current_clicks):
            self.audio_gain_current += self.audio_gain_step
        elif self.__volume_down_clicked(current_clicks):
            self.audio_gain_current -= self.audio_gain_step

        # correct for step overflow
        if self.audio_gain_current > self.audio_gain_max:
            self.audio_gain_current = self.audio_gain_max
        if self.audio_gain_current < self.audio_gain_min:
            self.audio_gain_current = self.audio_gain_min

        if self.__volume_up_clicked(current_clicks) or self.__volume_down_clicked(
            current_clicks
        ):
            return True
        return False

    def __chime_mode_clicked(self, current_click):
        return current_click == self.chime_mode_button

    def __rickroll(self):
        if self.__page_current != self.rickroll_page:
            return False
        if self.rickroll_counter == self.rickroll_frequency:
            self.rickroll_counter = 1
            return True
        self.rickroll_counter += 1
        return False

    def __play_clicked(self, current_button_click):
        if self.__valid_play_click(
            current_button_click
        ) and self.__current_click_is_not_same_as_last_click(current_button_click):
            return True
        return False

    def __momentary_stop_click(self, current_button_click):
        return (
            self.__momentary_click_page()
            and not self.__valid_play_click(current_button_click)
            and self.__valid_play_click(self.last_button_click)
        )

    def __stop_click(self, current_button_click):
        return (
            self.__regular_click_page()
            and self.__valid_play_click(current_button_click)
            and self.__current_click_is_same_as_last_play_click(current_button_click)
            and self.__current_click_is_not_same_as_last_click(current_button_click)
        )

    def __stop_clicked(self, current_button_click):
        return self.__stop_click(current_button_click) or self.__momentary_stop_click(
            current_button_click
        )

    def __reset_last_play_button_click(self):
        self.last_play_button_click = -1

    @property
    def page_current(self):
        return self.__page_current

    @page_current.setter
    def page_current(self, page):
        if 0 <= page < self.page_size:
            self.__page_current = page
        else:
            raise ValueError(
                f"Invalid page '{page}', must be between 0 and {self.page_size}"
            )

    def __ready_to_sleep(self):
        return (
            time.monotonic() - self.last_activity_at_secs
            > CONFIG.SLEEP_ON_INACTIVITY_FOR_SECS
        )

    def __going_to_sleep(self, actions):
        sleep = not actions and not self.sleeping and self.__ready_to_sleep()
        if sleep:
            self.sleeping = True
        return sleep

    def __waking_up(self, actions):
        if actions:
            self.last_activity_at_secs = time.monotonic()
        woke = actions and self.sleeping
        if woke:
            self.sleeping = False
        return woke

    def page_led(self, page=None):
        if page and 0 < page < len(CONFIG.MODE_LED_COLOR):
            return CONFIG.MODE_LED_COLOR[page]
        return CONFIG.MODE_LED_COLOR[self.__page_current]

    # TODO Modularise using a state machine approach
    def process_clicks(
        self, touches
    ):  # pylint: disable=too-many-branches, too-many-statements

        assert len(touches) <= self.max_buttons  # TODO FIXME change to == check

        current_button_clicks = []
        current_button_click = None
        for i, touch in enumerate(touches):
            if touch:
                current_button_clicks.append(i)

        if current_button_clicks:
            # for multi clicks we pick first one ignore others unless
            current_button_click = current_button_clicks[0]
            # check for all buttons which is an alias for page control click
            if self.__all_play_buttons_clicked(current_button_clicks):
                current_button_click = self.page_flip_button
            if self.__volume_up_clicked(current_button_clicks):
                current_button_click = self.audio_up_button
            if self.__volume_down_clicked(current_button_clicks):
                current_button_click = self.audio_down_button

        actions = []
        # control buttons have preference over play buttons so check them first
        if self.__volume_clicked(current_button_clicks, current_button_click):
            actions.append({self.GAIN: [self.audio_gain_current]})
            actions.append({self.BEEP: None})
        elif self.__page_clicked(current_button_clicks, current_button_click):
            actions.append({self.STOP: None})
            actions.append({self.BEEP: None})
            actions.append({self.LED: CONFIG.MODE_LED_COLOR[self.__page_current]})
        elif self.__chime_mode_clicked(current_button_click):
            actions.append({self.BEEP: None})
            if self.chime_on:
                self.chime_on = False
                actions.append({self.LED: CONFIG.CHIME_OFF_LED_COLOR})
            else:
                self.chime_on = True
                actions.append({self.LED: CONFIG.CHIME_ON_LED_COLOR})
        elif self.__stop_clicked(current_button_click):
            actions.append({self.STOP: None})
            actions.append({self.LED: CONFIG.SLEEP_LED_COLOR})
            self.__reset_last_play_button_click()
        elif self.__play_clicked(current_button_click):  # do not restart
            play_song = CONFIG.PLAY_LIST_BY_MODE[self.__page_current][
                current_button_click
            ]
            if self.__rickroll():
                play_song = CONFIG.RICKROLL_AUDIO_FILE
            # Default static led when flair mode is disabled
            actions.append({self.LED: CONFIG.MODE_LED_COLOR[self.__page_current]})
            actions.append({self.PLAY: play_song})
            self.last_play_button_click = current_button_click

        if self.__going_to_sleep(actions):
            actions.append({self.LED: CONFIG.SLEEP_LED_COLOR})
            actions.append({self.SLEEP: None})
        elif self.__waking_up(actions):
            # TODO: Optimise: skip LED restore action if there is already an LED action
            # Insert in front and not append since wake up actions should be before other actions
            actions.insert(0, {self.LED: CONFIG.MODE_LED_COLOR[self.__page_current]})
            actions.insert(0, {self.WAKE: None})  # wake up should be first action

        if self.__valid_control_click(current_button_clicks):
            self.__reset_last_play_button_click()

        self.last_button_click = current_button_click

        self.__debug(current_button_clicks, actions)

        return actions

    @staticmethod
    def __is_action(action, action_type):
        return next(iter(action)) == action_type

    def is_play(self, action):
        return self.__is_action(action, self.PLAY)

    def is_stop(self, action):
        return self.__is_action(action, self.STOP)

    def is_beep(self, action):
        return self.__is_action(action, self.BEEP)

    def is_led(self, action):
        return self.__is_action(action, self.LED)

    def is_gain(self, action):
        return self.__is_action(action, self.GAIN)

    def is_sleep(self, action):
        return self.__is_action(action, self.SLEEP)

    def is_wake(self, action):
        return self.__is_action(action, self.WAKE)

    @staticmethod
    def get_params(action):
        return list(action.values())[0]

    def get_files(self):
        return sum(
            CONFIG.PLAY_LIST_BY_MODE,
            [CONFIG.RICKROLL_AUDIO_FILE, CONFIG.CHIME_AUDIO_FILE],
        )

    def get_chime_actions(self, chimes, audio_file=CONFIG.CHIME_AUDIO_FILE):
        actions = []
        if not self.chime_on:
            return actions
        print(f"Playing {chimes} x {audio_file} chimes")
        actions = [
            {self.LED: CONFIG.CHIME_LED},
            {self.PLAY: audio_file},
        ]
        if self.__waking_up(actions):  # if sleeping wake up before chime actions
            actions.insert(0, {self.WAKE: None})  # first action
        return actions

    def process_web_click(self, web_click):
        # web click is not zero indexed, zero is used for stop play
        actions = {}
        if web_click == 0:
            actions = [{self.STOP: None}, {self.LED: CONFIG.SLEEP_LED_COLOR}]
        elif web_click is not None and self.__valid_play_click(web_click - 1):
            play_song = CONFIG.PLAY_LIST_BY_MODE[self.web_play_page][web_click - 1]
            # Default static led when flair mode is disabled
            actions = [
                {self.LED: CONFIG.MODE_LED_COLOR[self.web_play_page]},
                {self.PLAY: play_song},
            ]
        return actions

    def __debug(self, current_clicks, result):
        if not self.debug:
            return
        if self.trace:
            print(
                f"{self.__debug_click_status(current_clicks)} {self.__page_current} {result}"
            )
        elif result:
            print(
                f"{self.__debug_click_status(current_clicks)} {self.__page_current} {result}"
            )

    @staticmethod
    def debug_click_status_info():
        print()
        print(
            "----=__==___ X [] - PLAY, = CONTROL, _ UNUSED, | CLICKED, X PAGE, [] ACTIONS"
        )
        print()

    def __debug_click_status(self, clicks):
        click_status = ["_"] * self.max_buttons
        for i in range(len(CONFIG.PLAY_LIST_BY_MODE[0])):
            click_status[i] = "-"
        click_status[self.page_flip_button] = "="
        click_status[self.audio_up_button] = "="
        click_status[self.audio_down_button] = "="
        for click in clicks:
            click_status[click] = "|"
        return "".join(click_status)
