from py.helpers.board import Board
from py.helpers.stones import Stones
from py.helpers.myloggers import getLogger
import uarm
from time import sleep
LOG = getLogger(__name__)


class GoArm:
    safe_position = [101, -7, 45]
    retry_allowed = 1

    def __init__(self, conffile=r'C:\work\goArm\experiments\goArm\env\env.yaml'):
        self.board = Board(conffile=conffile)
        self.stones = Stones(conffile=conffile)
        self.max_height = max(self.board.max_height, self.stones.max_height) + 20
        self.arm = uarm.SwiftAPI(filters={'hwid': 'USB VID:PID=0403:6001'}, callback_thread_pool_size=1)
        self.arm.waiting_ready()
        LOG.info("Arm fully initialised")

    def _vertex_to_real(self, vertex):
        if type(vertex) is list:
            if len(vertex) == 2:
                return self.board.get_real_vertex(vertex)
            elif len(vertex) == 3:
                return vertex
            else:
                return
        else:
            # this is GTP notation most likely, to be implemented
            return

    def above(self, vertex):
        return [vertex[0], vertex[1], self.max_height]

    def _run_arm_command(self, command, *args, **kwargs):
        attempts = 0
        while attempts < self.retry_allowed:
            attempts += 1
            r = command(*args, wait=True, **kwargs)
            if r == "OK":
                LOG.debug("Command {} succeeded, args = {}{}".format(command.__name__, args, kwargs))
                return True  # log success
            else:
                LOG.error("Command {} failed, args = {}{}".format(command.__name__, args, kwargs))
                self._safe_stop()
                raise Exception("Emergency stop!")

    def set_position(self, vertex):
        vertex = self._vertex_to_real(vertex)
        return self._run_arm_command(self.arm.set_position, x=vertex[0], y=vertex[1], z=vertex[2])

    def set_pump(self, on=True):
        res = self._run_arm_command(self.arm.set_pump, on=on)
        # need to allow some time to free up suction cup
        sleep(1)
        return res

    def _safe_stop(self):
        LOG.warn("Safe stop invoked. Moving to safe position")
        self.set_position(self.safe_position)

    def _move_stone(self, a, b):
        def pick_or_drop_stone(vertex, pick=True):
            self.set_position(self.above(vertex))
            self.set_position(vertex)
            self.set_pump(on=pick)
            self.set_position(self.above(vertex))
        pick_or_drop_stone(a, pick=True)
        pick_or_drop_stone(b, pick=False)
        return True

    def make_move(self, colour, vertex, to_position=False):
        '''
        A call to move stone from bowl to vertex
        :param colour: stone colour
        :param vertex: vertex as logical [i, j], GTP ('a1') or real [x, y, z]
        :param to_position: bool. Return to safe position after move completed.
        :return:
        '''
        res = self._move_stone(self.stones.get_next_stone(colour), self._vertex_to_real(vertex))
        if res:
            self.stones.move_done(colour)
        if to_position:
            self.set_position(self.safe_position)
        return res

    def remove_stone(self, vertex, to_position=False):
        res = self._move_stone(self._vertex_to_real(vertex), self.board.drop_stones)
        if to_position:
            self.set_position(self.safe_position)
        return res

    def put_stones(self, vertices):
        '''
        This method is to put a whole diagram to the empty board, doesn't respect sequence
        :param vertices: {black: [vertex1, vertex2], white: [vertex1, vertex2]}
        :return:
        '''
        for colour in vertices:
            for vertex in vertices[colour]:
                self.make_move(colour, vertex)
        self.set_position(self.safe_position)

    def play_sequence(self, sequence):
        #[{'action': 'put_stone', 'vertex': [], 'colour': 'black'}, {'action': 'remove_stone', 'vertex': []}]
        for action in sequence:
            if action.get('action') in ['put_stone', 'put']:
                self.make_move(colour=action.get('colour'), vertex=action.get('vertex'))
            if action.get('action') in ['remove_stone', 'capture_stone', 'capture', 'remove']:
                self.remove_stone(vertex=action.get('vertex'))
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
        myArm._move_stone(a, b)
        myArm._move_stone(b, a)

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
