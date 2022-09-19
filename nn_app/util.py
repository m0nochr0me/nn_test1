"""
Recommendation Robot
Util
"""


class UserInput:
    """
    Auxiliary Class to get user input for development purposes
    """
    def __init__(self):
        self._ready = False
        self.warm_up()

    def warm_up(self):
        self._ready = True

    def shut_down(self):
        self._ready = False

    def get_raw_input(self):
        return input(':> ').strip()
