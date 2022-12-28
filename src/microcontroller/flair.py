from typing import Any, Dict, Optional

from config import CONFIG


class Flair:  # pylint: disable=too-few-public-methods
    """
    Non-functional cosmetic light effects
    """

    DEFAULT = "DEFAULT"
    LED = "LED"

    def __init__(self) -> None:
        self.led_restore_r: Optional[int] = None
        self.led_restore_g: Optional[int] = None
        self.led_restore_b: Optional[int] = None

        self.animated_r: Optional[int] = None
        self.animated_g: Optional[int] = None
        self.animated_b: Optional[int] = None

        self.animation_speed = CONFIG.FLAIR_ANIMATION_SPEED

    def __led_animated(self) -> bool:
        return self.led_restore_r is not None

    def __reset_restore_led(self, speed: int) -> None:
        self.led_restore_r = None
        self.led_restore_g = None
        self.led_restore_b = None

        self.animated_r = None
        self.animated_g = None
        self.animated_b = None
        self.animation_speed = speed

    def __set_restore_led(
        self, r: Optional[int], g: Optional[int], b: Optional[int], speed: int
    ) -> None:
        self.led_restore_r = r
        self.led_restore_g = g
        self.led_restore_b = b
        self.animated_r = r
        self.animated_g = g
        self.animated_b = b
        self.animation_speed = speed

    def __level_effect(self, level: int = 0) -> None:
        print(f"Audio level {level}")  # TODO Implement LED level effect

    def __breath_effect(self) -> None:
        if self.animated_r and self.animated_r != 0:
            self.animated_r += self.animation_speed
            if self.animated_r >= 255:
                self.animated_r = 255
                self.animation_speed = -abs(self.animation_speed)
            elif self.animated_r <= 0:
                self.animated_r = 1
                self.animation_speed = abs(self.animation_speed)
        if self.animated_g and self.animated_g != 0:
            self.animated_g += self.animation_speed
            if self.animated_g >= 255:
                self.animated_g = 255
                self.animation_speed = -abs(self.animation_speed)
            if self.animated_g <= 0:
                self.animated_g = 1
                self.animation_speed = abs(self.animation_speed)
                self.animated_g += self.animation_speed
        if self.animated_b and self.animated_b != 0:
            self.animated_b += self.animation_speed
            if self.animated_b >= 255:
                self.animated_b = 255
                self.animation_speed = -abs(self.animation_speed)
            if self.animated_b <= 0:
                self.animated_b = 1
                self.animation_speed = abs(self.animation_speed)

    def process(  # pylint: disable=too-many-arguments
        self,
        led_r: int,
        led_g: int,
        led_b: int,
        audio_playing: bool,
        audio_level: int = 0,
        speed: int = 20,
    ) -> Dict[Any, Any]:
        if audio_playing:
            if not self.__led_animated():
                self.__set_restore_led(led_r, led_g, led_b, speed)
            if audio_level:
                self.__level_effect(audio_level)
            else:
                self.__breath_effect()
            return {self.LED: (self.animated_r, self.animated_g, self.animated_b)}

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
