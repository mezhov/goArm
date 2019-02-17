from py.helpers.board import Board
from py.helpers.stones import Stones
from py.helpers.myloggers import getLogger
from py.helpers import uarm
from time import sleep
LOG = getLogger(__name__)


class GoArm:
    safe_position = [101, -7, 45]
    retry_allowed = 1

    def __init__(self):
        self.board = Board(conffile=r'C:\work\goArm\experiments\goArm\env\env.yaml')
        self.stones = Stones(conffile=r'C:\work\goArm\experiments\goArm\env\env.yaml')
        self.max_height = max(self.board.max_height, self.stones.max_height) + 20
        self.arm = uarm.SwiftAPI(filters={'hwid': 'USB VID:PID=0403:6001'}, callback_thread_pool_size=1)
        self.arm.waiting_ready()
        LOG.info("Arm fully initialised")

    def above(self, vertex):
        return [vertex[0], vertex[1], self.max_height]

    def _run_arm_command(self, command, *args, **kwargs):
        attempts = 0
        while attempts < self.retry_allowed:
            attempts += 1
            r = command(*args, **kwargs)
            if r == "OK":
                LOG.debug("Command {} succeeded, args = {}{}".format(command.__name__, args, kwargs))
                return True  # log success
            else:
                LOG.error("Command {} failed, args = {}{}".format(command.__name__, args, kwargs))
                self._safe_stop()
                raise Exception("Emergency stop!")

    def set_position(self, vertex):
        return self._run_arm_command(self.arm.set_position, x=vertex[0], y=vertex[1], z=vertex[2], wait=True)

    def set_pump(self, on=True):
        return self._run_arm_command(self.arm.set_pump, on=on)

    def _safe_stop(self):
        LOG.warn("Safe stop invoked. Moving to safe position")
        return self.set_position(self.safe_position)

    def move_stone(self, a, b):
        # moving stone from point a to point b
        # above stone > to stone > catch stone > above stone > above target > to target > drop stone > above target
        self.set_position(self.above(a))
        self.set_position(a)
        self.set_pump()
        sleep(1)
        self.set_position(self.above(a))
        self.set_position(self.above(b))
        self.set_position(b)
        self.set_pump(on=False)
        sleep(1)
        self.set_position(self.above(b))
        return True

    def make_move(self, colour, vertex, to_position=False):
        real_vertex = self.board.get_real_vertex(vertex)
        stone_vertex = self.stones.get_next_stone(colour)
        res = self.move_stone(stone_vertex, real_vertex)
        if res:
            self.stones.move_done(colour)
        if to_position:
            self.set_position(self.safe_position)
        return res

    def remove_stone(self, vertex, to_position=False):
        stone_vertex = self.board.get_real_vertex(vertex)
        outta_board = self.board.drop_stones
        res = self.move_stone(stone_vertex, outta_board)
        if to_position:
            self.set_position(self.safe_position)
        return res

    def put_stones(self, vertices):
        for colour in vertices:
            for vertex in vertices[colour]:
                self.make_move(colour, vertex)
        self.set_position(self.safe_position)

    def play_sequence(self, sequence):
        #[['put_stone', {'vertex': [], 'colour': 'black'}], ['remove_stone', {'vertex': []}]]
        for action in sequence:
            if action[0] == 'put_stone':
                self.make_move(colour=action[1]['colour'], vertex=action[1]['vertex'])
            if action[0] == 'remove_stone':
                self.remove_stone(vertex=action[1]['vertex'])
        self.set_position(self.safe_position)

if __name__ == "__main__":
    myArm = GoArm()
    myArm.set_position(myArm.safe_position)
    try:
        '''
        for v in [[1,1], [1,9], [7,7], [9,1], [5,5]]:
            myArm.set_position(myArm.above(myArm.board.get_real_vertex(v)))
            myArm.set_position(myArm.board.get_real_vertex(v))
            sleep(3)
            myArm.set_position(myArm.above(myArm.board.get_real_vertex(v)))
        '''
        a = myArm.board.get_real_vertex([1,1])
        b = myArm.board.get_real_vertex([3,3])
        myArm.move_stone(a,b)
        myArm.move_stone(b,a)

    finally:
        myArm.set_position(myArm.safe_position)



    '''
    cur_position = myArm.safe_position
    i = ''
    while i != 'q':
        print("Current position: {}".format(cur_position))
        i = input('Adjustment: ')
        a = i.split(',')
        new_position = [(float(a[i]) + cur_position[i]) for i in range(3)]
        print("New position: {}".format(new_position))
        i = input('Confirm?')
        if i.lower() == 'y':
            myArm.set_position(new_position)
            cur_position = new_position
    '''
