class Info_exception(Exception):
    def __init__(self, exc_msg: str) -> None:
        self.exc_msg = exc_msg
        super().__init__(self.exc_msg)
