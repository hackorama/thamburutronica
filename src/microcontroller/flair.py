from config import CONFIG


class Flair:
    """
    Non-functional cosmetic light effects
    """

    DEFAULT = "DEFAULT"
    LED = "LED"

    def __init__(self):
        self.led_restore_r = None
        self.led_restore_g = None
        self.led_restore_b = None

        self.animated_r = None
        self.animated_g = None
        self.animated_b = None

        self.animation_speed = CONFIG.FLAIR_ANIMATION_SPEED

    def __led_animated(self):
        return self.led_restore_r is not None

    def __reset_restore_led(self, speed):
        self.led_restore_r = None
        self.led_restore_g = None
        self.led_restore_b = None

        self.animated_r = None
        self.animated_g = None
        self.animation_speed = speed

    def __set_restore_led(self, r, g, b, speed):
        self.led_restore_r = r
        self.led_restore_g = g
        self.led_restore_b = b
        self.animated_r = r
        self.animated_g = g
        self.animated_b = b
        self.animation_speed = speed

    def __breath_effect(self):
        if self.animated_r != 0:
            self.animated_r += self.animation_speed
            if self.animated_r >= 255:
                self.animated_r = 255
                self.animation_speed = -abs(self.animation_speed)
            elif self.animated_r <= 0:
                self.animated_r = 1
                self.animation_speed = abs(self.animation_speed)
        if self.animated_g != 0:
            self.animated_g += self.animation_speed
            if self.animated_g >= 255:
                self.animated_g = 255
                self.animation_speed = -abs(self.animation_speed)
            if self.animated_g <= 0:
                self.animated_g = 1
                self.animation_speed = abs(self.animation_speed)
                self.animated_g += self.animation_speed
        if self.animated_b != 0:
            self.animated_b += self.animation_speed
            if self.animated_b >= 255:
                self.animated_b = 255
                self.animation_speed = -abs(self.animation_speed)
            if self.animated_b <= 0:
                self.animated_b = 1
                self.animation_speed = abs(self.animation_speed)

    def process(self, led_r, led_g, led_b, audio_playing, audio_level=0, speed=20):
        if audio_playing:
            if not self.__led_animated():
                self.__set_restore_led(led_r, led_g, led_b, speed)
            self.__breath_effect()
            return {self.LED: (self.animated_r, self.animated_g, self.animated_b)}
        else:
            if self.__led_animated():
                action = {
                    self.LED: (
                        self.led_restore_r,
                        self.led_restore_g,
                        self.led_restore_b,
                    )
                }
                self.__reset_restore_led(speed)
                return action
        return {}
