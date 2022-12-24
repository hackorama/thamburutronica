from adafruit_logging import LogRecord, StreamHandler


# https://learn.adafruit.com/a-logger-for-circuitpython/file-handler
class FileHandler(StreamHandler):
    def __init__(self, filename: str, mode: str = "a") -> None:
        # file closed later on stream closing
        # fmt: off
        super().__init__(open(filename, mode=mode, encoding="utf-8")) # pylint: disable=consider-using-with
        # fmt: on

    def close(self) -> None:
        self.stream.flush()
        self.stream.close()

    def format(self, record: LogRecord) -> str:
        return super().format(record) + "\r\n"

    def emit(self, record: LogRecord) -> None:
        self.stream.write(self.format(record))
