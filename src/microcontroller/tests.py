import time

from config import CONFIG
from flair import Flair
from play import Play

EXPECTED_ACTIONS = [
    [{"STOP": None}],
    [{"PLAY": "panchamam.mp3"}],
    [],
    [{"STOP": None}],
    [{"PLAY": "sarana.mp3"}],
    [],
    [{"STOP": None}],
    [{"PLAY": "sarana.mp3"}],
    [],
    [{"PLAY": "panchamam.mp3"}],
    [{"STOP": None}],
    [],
    [],
    [{"PLAY": "anusarana.mp3"}],
    [],
    [{"STOP": None}],
    [{"STOP": None}, {"BEEP": 262}, {"LED": (0, 0, 200)}],
    [{"PLAY": "anusarana.mp3"}],
    [],
    [{"STOP": None}, {"BEEP": 262}, {"LED": (200, 0, 0)}],
    [{"PLAY": "spring.mp3"}],
    [{"PLAY": "summer.mp3"}],
    [{"PLAY": "autumn.mp3"}],
    [{"PLAY": "winter.mp3"}],
    [],
    [{"STOP": None}, {"BEEP": 262}, {"LED": (0, 200, 0)}],
    [{"PLAY": "sarana.mp3"}],
    [{"PLAY": "anusarana.mp3"}],
    [{"PLAY": "manthram.mp3"}],
    [{"STOP": None}],
    [{"PLAY": "anusarana.mp3"}],
    [{"GAIN": [18]}, {"BEEP": 262}],
    [{"GAIN": [16]}, {"BEEP": 262}],
    [{"GAIN": [18]}, {"BEEP": 262}],
    [],
    [{"GAIN": [16]}, {"BEEP": 262}],
    [],
    [{"PLAY": "panchamam.mp3"}],
    [{"PLAY": "sarana.mp3"}],
    [{"PLAY": "anusarana.mp3"}],
    [{"PLAY": "manthram.mp3"}],
    [{"PLAY": "panchamam.mp3"}],
    [{"PLAY": "sarana.mp3"}],
    [{"STOP": None}, {"BEEP": 262}, {"LED": (0, 0, 200)}],
    [],
    [{"STOP": None}, {"BEEP": 262}, {"LED": (200, 0, 0)}],
    [{"PLAY": "spring.mp3"}],
    [{"PLAY": "summer.mp3"}],
    [{"PLAY": "rickroll.mp3"}],
    [{"PLAY": "winter.mp3"}],
    [{"PLAY": "spring.mp3"}],
    [{"PLAY": "summer.mp3"}],
    [{"PLAY": "autumn.mp3"}],
    [{"PLAY": "winter.mp3"}],
    [{"PLAY": "rickroll.mp3"}],
    [{"PLAY": "summer.mp3"}],
    [],
    [{"STOP": None}, {"BEEP": 262}, {"LED": (0, 200, 0)}],
    [],
    [],
    [],
    [{"STOP": None}, {"BEEP": 262}, {"LED": (0, 0, 200)}],
    [{"PLAY": "panchamam.mp3"}],
    [{"STOP": None}, {"BEEP": 262}, {"LED": (200, 0, 0)}],
    [],
    [],
    [],
    [],
    [],
    [{"STOP": None}, {"BEEP": 262}, {"LED": (0, 200, 0)}],
    [{"PLAY": "panchamam.mp3"}],
    [{"STOP": None}, {"BEEP": 262}, {"LED": (0, 0, 200)}],
    [],
    [{"GAIN": [18]}, {"BEEP": 262}],
    [],
    [],
    [{"GAIN": [16]}, {"BEEP": 262}],
    [],
    [],
    [{"GAIN": [14]}, {"BEEP": 262}],
    [],
    [{"PLAY": "panchamam.mp3"}],
    [],
    [],
    [{"STOP": None}],
    [],
    [],
    [],
    [{"PLAY": "panchamam.mp3"}],
    [],
    [],
    [{"STOP": None}, {"BEEP": 262}, {"LED": (200, 0, 0)}],
    [{"PLAY": "spring.mp3"}],
]


def test_action(play, touches, actions):
    action = play.process_clicks(touches, [False, False, False])
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

    actions = play.process_clicks(
        [False, False, False, False, True], [False, False, False]
    )
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

    action = play.process_clicks(touches, [False, False, False])
    assert action == [{"STOP": None}]

    # before sleep, chime actions will not have wake/sleep
    assert CONFIG.CHIME_MODE == CONFIG.CHIME_MODE_SIMPLE
    chime_actions = play.get_chime_actions(3)
    assert len(chime_actions) == 1
    assert play.is_play(chime_actions[0])

    while duration < sleep_threshold:
        action = play.process_clicks(touches, [False, False, False])
        duration = time.monotonic() - start
        print(f"{int(duration)} {action}")
        if duration >= sleep_threshold:
            assert action == [{"LED": (0, 0, 0)}, {"SLEEP": None}]
        else:
            assert action == []
        time.sleep(10)

    # while sleeping, chime action will have wake/sleep
    chime_actions = play.get_chime_actions(3)
    assert len(chime_actions) == 3
    assert play.is_wake(chime_actions[0])
    assert play.is_play(chime_actions[1])
    assert play.is_sleep(chime_actions[2])

    action = play.process_clicks(touches, [False, False, False])
    duration = time.monotonic() - start
    print(f"{int(duration)} {action}")
    assert action == []

    action = play.process_clicks(touches, [False, False, False])
    duration = time.monotonic() - start
    print(f"{int(duration)} {action}")
    assert action == []

    touches = [True]
    action = play.process_clicks(touches, [False, False, False])
    duration = time.monotonic() - start
    print(f"{int(duration)} {action}")
    assert action == [{"WAKE": None}, {"PLAY": "panchamam.mp3"}, {"LED": (0, 200, 0)}]


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

    saved_chime_mode = CONFIG.CHIME_MODE

    play = Play()
    actions = play.get_chime_actions(3)
    assert len(actions) == 1
    assert play.is_play(actions[0])

    CONFIG.CHIME_MODE = CONFIG.CHIME_MODE_MIXER
    actions = play.get_chime_actions(9)
    assert play.is_gain(actions[0])
    assert play.is_play(actions[1])
    assert play.is_blocking_play(actions[2])
    assert play.is_gain(actions[3])
    params = play.get_params(actions[1])
    assert params == CONFIG.CHIME_AMBIENT_AUDIO
    params = play.get_params(actions[2])
    assert params[0] == CONFIG.CHIME_BELL_AUDIO
    assert params[1] == CONFIG.CHIME_BELL_AUDIO_CHANNEL
    assert params[2] == 9

    chime_actions = play.get_chime_actions(3)
    assert len(chime_actions) == 4
    # turn off chimes
    actions = play.process_clicks(
        [False, False, False, False, False, False, False, False, False, True],
        [False, False, False],
    )
    assert actions == [{"BEEP": None}, {"BEEP": None}]
    chime_actions = play.get_chime_actions(3)
    assert len(chime_actions) == 0
    # turn on chimes
    actions = play.process_clicks(
        [False, False, False, False, False, False, False, False, False, True],
        [False, False, False],
    )
    assert actions == [{"BEEP": None}]
    chime_actions = play.get_chime_actions(3)
    assert len(chime_actions) == 4

    CONFIG.CHIME_MODE = saved_chime_mode  # restore mode after tests


if __name__ == "__main__":
    test()
    test_flair()
    test_chimes()
    test_sleep()
