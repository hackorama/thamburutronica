import time

from chime import Chime
from config import CONFIG
from flair import Flair
from play import Play

# only for testing not deployed on device disable pylint
# pylint: disable-all
# pylint: skip-file

play_conf = Play()


def get_audio_file(page, click):
    return CONFIG.PLAY_LIST_BY_MODE[page][click]


def get_rickroll_audio_file():
    return CONFIG.RICKROLL_AUDIO_FILE


def get_led(page):
    return play_conf.page_led(page)


EXPECTED_ACTIONS = [
    [{"STOP": None}, {"LED": (0, 0, 0)}],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 0)}],
    [],
    [{"STOP": None}, {"LED": (0, 0, 0)}],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 1)}],
    [],
    [{"STOP": None}, {"LED": (0, 0, 0)}],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 1)}],
    [],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 0)}],
    [{"STOP": None}, {"LED": (0, 0, 0)}],
    [],
    [],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 2)}],
    [],
    [{"STOP": None}, {"LED": (0, 0, 0)}],
    [{"STOP": None}, {"BEEP": None}, {"LED": play_conf.page_led(1)}],
    [{"LED": play_conf.page_led(1)}, {"PLAY": get_audio_file(1, 2)}],
    [],
    [{"STOP": None}, {"BEEP": None}, {"LED": play_conf.page_led(2)}],
    [{"LED": play_conf.page_led(2)}, {"PLAY": get_audio_file(2, 0)}],
    [{"LED": play_conf.page_led(2)}, {"PLAY": get_audio_file(2, 1)}],
    [{"LED": play_conf.page_led(2)}, {"PLAY": get_audio_file(2, 2)}],
    [{"LED": play_conf.page_led(2)}, {"PLAY": get_audio_file(2, 3)}],
    [],
    [{"STOP": None}, {"BEEP": None}, {"LED": play_conf.page_led(0)}],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 1)}],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 2)}],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 3)}],
    [{"STOP": None}, {"LED": (0, 0, 0)}],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 2)}],
    [
        {"GAIN": [CONFIG.AUDIO_GAIN_DEFAULT_DB + CONFIG.AUDIO_GAIN_STEP_DB]},
        {"BEEP": None},
    ],
    [{"GAIN": [CONFIG.AUDIO_GAIN_DEFAULT_DB]}, {"BEEP": None}],
    [
        {"GAIN": [CONFIG.AUDIO_GAIN_DEFAULT_DB + CONFIG.AUDIO_GAIN_STEP_DB]},
        {"BEEP": None},
    ],
    [],
    [{"GAIN": [CONFIG.AUDIO_GAIN_DEFAULT_DB]}, {"BEEP": None}],
    [],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 0)}],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 1)}],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 2)}],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 3)}],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 0)}],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 1)}],
    [{"STOP": None}, {"BEEP": None}, {"LED": play_conf.page_led(1)}],
    [],
    [{"STOP": None}, {"BEEP": None}, {"LED": play_conf.page_led(2)}],
    [{"LED": play_conf.page_led(2)}, {"PLAY": get_audio_file(2, 0)}],
    [{"LED": play_conf.page_led(2)}, {"PLAY": get_audio_file(2, 1)}],
    [{"LED": play_conf.page_led(2)}, {"PLAY": get_rickroll_audio_file()}],
    [{"LED": play_conf.page_led(2)}, {"PLAY": get_audio_file(2, 3)}],
    [{"LED": play_conf.page_led(2)}, {"PLAY": get_audio_file(2, 0)}],
    [{"LED": play_conf.page_led(2)}, {"PLAY": get_audio_file(2, 1)}],
    [{"LED": play_conf.page_led(2)}, {"PLAY": get_audio_file(2, 2)}],
    [{"LED": play_conf.page_led(2)}, {"PLAY": get_audio_file(2, 3)}],
    [{"LED": play_conf.page_led(2)}, {"PLAY": get_rickroll_audio_file()}],
    [{"LED": play_conf.page_led(2)}, {"PLAY": get_audio_file(2, 1)}],
    [],
    [{"STOP": None}, {"BEEP": None}, {"LED": play_conf.page_led(0)}],
    [],
    [],
    [],
    [{"STOP": None}, {"BEEP": None}, {"LED": play_conf.page_led(1)}],
    [{"LED": play_conf.page_led(1)}, {"PLAY": get_audio_file(1, 0)}],
    [{"STOP": None}, {"BEEP": None}, {"LED": play_conf.page_led(2)}],
    [],
    [],
    [],
    [],
    [],
    [{"STOP": None}, {"BEEP": None}, {"LED": play_conf.page_led(0)}],
    [{"LED": play_conf.page_led(0)}, {"PLAY": get_audio_file(0, 0)}],
    [{"STOP": None}, {"BEEP": None}, {"LED": play_conf.page_led(1)}],
    [],
    [
        {"GAIN": [CONFIG.AUDIO_GAIN_DEFAULT_DB + CONFIG.AUDIO_GAIN_STEP_DB]},
        {"BEEP": None},
    ],
    [],
    [],
    [{"GAIN": [CONFIG.AUDIO_GAIN_DEFAULT_DB]}, {"BEEP": None}],
    [],
    [],
    [
        {"GAIN": [CONFIG.AUDIO_GAIN_DEFAULT_DB - CONFIG.AUDIO_GAIN_STEP_DB]},
        {"BEEP": None},
    ],
    [],
    [{"LED": play_conf.page_led(1)}, {"PLAY": get_audio_file(1, 0)}],
    [],
    [],
    [{"STOP": None}, {"LED": (0, 0, 0)}],
    [],
    [],
    [],
    [{"LED": play_conf.page_led(1)}, {"PLAY": get_audio_file(1, 0)}],
    [],
    [],
    [{"STOP": None}, {"BEEP": None}, {"LED": play_conf.page_led(2)}],
    [{"LED": play_conf.page_led(2)}, {"PLAY": get_audio_file(2, 0)}],
]


def test_action(play, touches, actions):
    action = play.process_clicks(touches)
    actions.append(action)


def test():
    play = Play(debug=True, trace=True)

    audio_files = play.get_play_files()
    chime_files = play.get_chime_files()
    files = play.get_files()
    print(", ".join(audio_files))
    print(", ".join(chime_files))
    print(", ".join(files))
    assert len(audio_files) == 15  # 3 * 4 chords + 1 beep + 1 rickroll + 1 chimes
    assert len(files) >= 15
    assert len(files) == len(audio_files) + len(chime_files)

    actual_actions = []
    play.debug_click_status_info()

    # test play clicks

    # 0

    test_action(play, [], actual_actions)

    test_action(
        play, [True, False, False, False, False, False, False, False], actual_actions
    )
    test_action(play, [True], actual_actions)

    test_action(play, [], actual_actions)

    test_action(play, [False, True], actual_actions)
    test_action(play, [False, True], actual_actions)

    test_action(play, [], actual_actions)

    test_action(play, [False, True], actual_actions)
    test_action(play, [False, True], actual_actions)
    test_action(play, [True], actual_actions)

    # 10

    test_action(play, [], actual_actions)
    test_action(play, [], actual_actions)
    test_action(play, [], actual_actions)
    test_action(play, [False, False, True], actual_actions)
    test_action(play, [False, False, True], actual_actions)
    test_action(play, [], actual_actions)
    test_action(play, [False, False, False, False, True], actual_actions)
    test_action(play, [False, False, True], actual_actions)
    test_action(play, [], actual_actions)

    # test page control clicks

    test_action(play, [True, True, True, True], actual_actions)

    # 20

    test_action(play, [True], actual_actions)
    test_action(play, [False, True], actual_actions)
    test_action(play, [False, False, True], actual_actions)
    test_action(play, [False, False, False, True], actual_actions)
    test_action(play, [False, False, False, True], actual_actions)
    test_action(play, [True, True, True, True], actual_actions)
    test_action(play, [False, True], actual_actions)
    test_action(play, [False, False, True], actual_actions)
    test_action(play, [False, False, False, True], actual_actions)
    test_action(play, [], actual_actions)

    # 30

    test_action(play, [False, False, True, True, True], actual_actions)

    # test gain control clicks

    test_action(
        play, [False, False, False, False, False, False, False, True], actual_actions
    )
    test_action(
        play,
        [False, False, False, False, False, False, False, False, True],
        actual_actions,
    )
    test_action(
        play, [False, False, False, False, False, False, False, True], actual_actions
    )
    test_action(play, [False, False, False, False, False, True], actual_actions)
    test_action(
        play,
        [False, False, False, False, False, False, False, False, True],
        actual_actions,
    )
    test_action(
        play,
        [False, False, False, False, False, True, False, False, True],
        actual_actions,
    )

    # test momentary page play clicks

    test_action(play, [True], actual_actions)
    test_action(play, [False, True], actual_actions)
    test_action(play, [False, False, True], actual_actions)

    # 40

    test_action(play, [False, False, False, True], actual_actions)
    test_action(play, [True], actual_actions)
    test_action(play, [False, True], actual_actions)

    # test play clicks with rick roll page

    test_action(play, [False, False, False, False, True], actual_actions)
    test_action(play, [], actual_actions)
    test_action(play, [False, False, False, False, True], actual_actions)

    test_action(play, [True], actual_actions)
    test_action(play, [False, True], actual_actions)
    test_action(play, [False, False, True], actual_actions)
    test_action(play, [False, False, False, True], actual_actions)

    # 50

    test_action(play, [True], actual_actions)
    test_action(play, [False, True], actual_actions)
    test_action(play, [False, False, True], actual_actions)
    test_action(play, [False, False, False, True], actual_actions)
    test_action(play, [True], actual_actions)
    test_action(play, [False, True], actual_actions)

    # test page control clicks are momentary

    test_action(play, [], actual_actions)
    test_action(play, [False, False, False, False, True], actual_actions)
    test_action(play, [False, False, False, False, True], actual_actions)
    test_action(play, [False, False, False, False, True], actual_actions)

    # 60

    test_action(play, [], actual_actions)
    test_action(play, [False, False, False, False, True], actual_actions)
    test_action(play, [True], actual_actions)
    test_action(play, [False, False, False, False, True], actual_actions)
    test_action(play, [True, True, True, True], actual_actions)
    test_action(play, [True, True, True, True], actual_actions)
    test_action(play, [True, True, True, True], actual_actions)
    test_action(play, [False, False, False, False, True], actual_actions)
    test_action(play, [], actual_actions)
    test_action(play, [True, True, True, True], actual_actions)

    # 70

    test_action(play, [True], actual_actions)
    test_action(play, [True, True, True, True], actual_actions)

    # test gain control clicks are momentary

    test_action(play, [], actual_actions)
    test_action(
        play, [False, False, False, False, False, False, False, True], actual_actions
    )
    test_action(
        play, [False, False, False, False, False, False, False, True], actual_actions
    )
    test_action(play, [], actual_actions)
    test_action(
        play,
        [False, False, False, False, False, False, False, False, True],
        actual_actions,
    )
    test_action(play, [False, False, False, False, False, False, True], actual_actions)
    test_action(play, [], actual_actions)
    test_action(
        play,
        [False, False, False, False, False, False, False, False, True],
        actual_actions,
    )

    # 80

    # test click again stops in non-momentary mode
    test_action(play, [], actual_actions)
    test_action(play, [True], actual_actions)
    test_action(play, [], actual_actions)
    test_action(play, [], actual_actions)
    test_action(play, [True], actual_actions)
    test_action(play, [True], actual_actions)
    test_action(play, [True], actual_actions)
    test_action(play, [], actual_actions)
    test_action(play, [True], actual_actions)
    test_action(play, [True], actual_actions)
    test_action(play, [True], actual_actions)
    test_action(play, [False, False, False, False, True], actual_actions)
    test_action(play, [True], actual_actions)

    play.debug_click_status_info()

    for i, action in enumerate(actual_actions):
        print(f"{i} {action} == {EXPECTED_ACTIONS[i]}")
        assert action == EXPECTED_ACTIONS[i]

    actions = play.process_clicks([False, False, False, False, True])
    for action in actions:
        if play.is_play(action):
            print(f"PLAY {play.get_params(action)}")
        elif play.is_stop(action):
            print("STOP")
        elif play.is_beep(action):
            print(f"BEEP {play.get_params(action)}")
        elif play.is_led(action):
            print(f"LED {play.get_params(action)}")
        elif play.is_gain(action):
            print(f"GAIN {play.get_params(action)}")


def test_sleep():
    print("Test sleep/wake actions ...")
    print("Wait for few minutes to finish")
    play = Play(debug=True, trace=True)

    play.debug_click_status_info()

    CONFIG.SLEEP_ON_INACTIVITY_FOR_SECS = 60
    sleep_threshold = CONFIG.SLEEP_ON_INACTIVITY_FOR_SECS
    start = time.monotonic()
    duration = 0

    touches = []

    action = play.process_clicks(touches)
    assert action == [{"STOP": None}, {"LED": (0, 0, 0)}]

    play.chime_on = True
    # before sleep, chime actions will not have wake/sleep
    chime_actions = play.get_chime_actions(3)
    assert len(chime_actions) == 2
    assert play.is_led(chime_actions[0])
    assert play.is_play(chime_actions[1])

    print("While audio playing do no sleep even when idle (no actions)")

    while duration < sleep_threshold:
        action = play.process_clicks(touches, True)  # audio is playing
        duration = time.monotonic() - start
        print(f"{int(duration)} {action}")
        assert action == []
        time.sleep(10)

    print("While audio not playing, sleep after idle (no actions) time")

    play = Play(debug=True, trace=True)
    action = play.process_clicks(touches)
    assert action == [{"STOP": None}, {"LED": (0, 0, 0)}]

    start = time.monotonic()
    duration = 0

    while duration < sleep_threshold:
        action = play.process_clicks(touches)
        duration = time.monotonic() - start
        print(f"{int(duration)} {action}")
        if duration >= sleep_threshold:
            assert action == [{"LED": (0, 0, 0)}, {"SLEEP": None}]
        else:
            assert action == []
        time.sleep(10)

    print("While sleeping wake up on any action")

    action = play.process_clicks(touches)
    duration = time.monotonic() - start
    print(f"{int(duration)} {action}")
    assert action == []

    action = play.process_clicks(touches)
    duration = time.monotonic() - start
    print(f"{int(duration)} {action}")
    assert action == []

    touches = [True]
    action = play.process_clicks(touches)
    duration = time.monotonic() - start
    print(f"{int(duration)} {action}")
    assert action == [
        {"WAKE": None},
        {"LED": get_led(0)},
        {"LED": get_led(0)},
        {"PLAY": get_audio_file(0, 0)},
    ]


def flair_action(flair, actions, r, g, b, audio, level, speed):
    action = flair.process(r, g, b, audio, level, speed)
    actions.append(action)
    print(action)
    return action


def test_flair():
    print("Test flair actions ...")
    flair = Flair()
    actions = []
    print("Flair test")
    print("Audio not playing ")
    action = flair_action(flair, actions, 200, 0, 0, False, 0, 20)
    assert action == {}
    action = flair_action(flair, actions, 200, 0, 0, False, 0, 20)
    assert action == {}
    action = flair_action(flair, actions, 200, 0, 0, False, 0, 20)
    assert action == {}
    print("Audio playing ")
    for i in range(20):
        flair_action(flair, actions, 200, 0, 0, True, 0, 20)
    print("Audio not playing ")
    action = flair_action(flair, actions, 200, 0, 0, False, 0, 20)
    assert action == {"LED": (200, 0, 0)}
    action = flair_action(flair, actions, 200, 0, 0, False, 0, 20)
    assert action == {}
    action = flair_action(flair, actions, 200, 0, 0, False, 0, 20)
    assert action == {}
    print("Audio playing ")
    action = flair_action(flair, actions, 200, 0, 0, True, 0, 20)
    assert action == {"LED": (220, 0, 0)}
    action = flair_action(flair, actions, 200, 0, 0, True, 0, 20)
    assert action == {"LED": (240, 0, 0)}
    action = flair_action(flair, actions, 200, 0, 0, True, 0, 20)
    assert action == {"LED": (255, 0, 0)}


def test_chimes():
    print("Test chime actions ...")

    play = Play()
    play.chime_on = True
    actions = play.get_chime_actions(3)
    print(actions)
    assert len(actions) == 2
    assert play.is_led(actions[0])
    assert play.is_play(actions[1])

    play.sleeping = True
    actions = play.get_chime_actions(3)
    print(actions)
    assert len(actions) == 3
    assert play.is_wake(actions[0])
    assert play.is_led(actions[1])
    assert play.is_play(actions[2])
    play.sleeping = False

    # turn off chimes
    actions = play.process_clicks(
        [False, False, False, False, False, False, False, False, False, True],
    )
    assert actions == [{"BEEP": None}, {"LED": CONFIG.CHIME_OFF_LED_COLOR}]
    chime_actions = play.get_chime_actions(3)
    assert len(chime_actions) == 0
    # turn on chimes
    actions = play.process_clicks(
        [False, False, False, False, False, False, False, False, False, True],
    )
    assert actions == [{"BEEP": None}, {"LED": CONFIG.CHIME_ON_LED_COLOR}]
    chime_actions = play.get_chime_actions(3)
    assert len(chime_actions) == 2

    print("Test chime special day audio")

    chime = Chime()
    today = chime.current_day()
    if today in CONFIG.CHIME_SPECIAL_DAYS:
        CONFIG.CHIME_SPECIAL_DAYS.pop(today)
    assert chime.get_chime_audio_file() == CONFIG.CHIME_AUDIO_FILE
    CONFIG.CHIME_SPECIAL_DAYS[today] = ["1", "2", "3"]
    assert chime.get_chime_audio_file() == "1"
    assert chime.get_chime_audio_file() == "2"
    assert chime.get_chime_audio_file() == "3"
    assert chime.get_chime_audio_file() == "1"


if __name__ == "__main__":
    test()
    test_flair()
    test_chimes()
    test_sleep()
