import time

from config import CONFIG
from flair import Flair
from play import Play

# only for testing not deployed on device disable pylint
# pylint: disable-all
# pylint: skip-file

play_conf = Play()


def get_audio_file(page, click):
    return play_conf.play_list_pages[page][click]


def get_rickroll_audio_file():
    return play_conf.rickroll_song


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

    files = play.get_files()
    assert len(files) == 14  # 3 * 4 chords + 1 rickroll + 1 chimes
    print(", ".join(files))

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
    print("Wait for a minute to finish")
    play = Play(debug=True, trace=True)

    play.debug_click_status_info()

    sleep_threshold = 60  # play.sleep_on_no_activity_for_secs
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

    while duration < sleep_threshold:
        action = play.process_clicks(touches)
        duration = time.monotonic() - start
        print(f"{int(duration)} {action}")
        if duration >= sleep_threshold:
            assert action == [{"LED": (0, 0, 0)}, {"SLEEP": None}]
        else:
            assert action == []
        time.sleep(10)

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
    assert actions == [{"BEEP": None}, {"LED": play.chime_off_led_color}]
    chime_actions = play.get_chime_actions(3)
    assert len(chime_actions) == 0
    # turn on chimes
    actions = play.process_clicks(
        [False, False, False, False, False, False, False, False, False, True],
    )
    assert actions == [{"BEEP": None}, {"LED": play.chime_on_led_color}]
    chime_actions = play.get_chime_actions(3)
    assert len(chime_actions) == 2


if __name__ == "__main__":
    test()
    test_flair()
    test_chimes()
    test_sleep()
