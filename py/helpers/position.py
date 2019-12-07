class PositionHolder:
    def __init__(self, p=''):
        self._position = []

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new_position):
        # check for new moves
        # emit moves to UI if needed
        self._position = new_position

    def emit_move(self):
        pass
