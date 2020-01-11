from py.helpers.board import Board
from py.helpers.stones import Stones
from py.helpers.myloggers import getLogger
import uarm
from time import sleep
import datetime
import os
LOG = getLogger(__name__)


class GoArm:
    safe_position = [120, 0, 70]
    cam_position = [220, 0, 195]
    retry_allowed = 1

    def __init__(self, conffile=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'env', 'env.yaml')):
        self.config_file = conffile
        self._read_env()
        self.arm = uarm.SwiftAPI(filters={'hwid': 'USB VID:PID=0403:6001'}, callback_thread_pool_size=1)
        self.arm.waiting_ready()
        self.set_position()
        self._cam = None
        LOG.info("Arm fully initialised")

    @property
    def cam(self):
        return self._cam

    @cam.setter
    def cam(self, cam):
        self._cam = cam

    def _read_env(self):
        self.board = Board(conffile=self.config_file)
        self.stones = Stones(conffile=self.config_file)
        self.max_height = max(self.board.max_height, self.stones.max_height) + 20

    def _vertex_to_real(self, vertex):
        if vertex is None:
            return self.safe_position
        elif type(vertex) is list:
            if len(vertex) == 2:
                return self.board.get_real_vertex(vertex)
            elif len(vertex) == 3:
                return vertex
            else:
                return
        else:
            # this is GTP notation most likely, to be implemented
            return

    def above(self, vertex=None, z=None):
        if vertex is None:
            vertex = self._get_current_position()
        return [vertex[0], vertex[1], vertex[2] + z if z else self.max_height]

    def _run_arm_command(self, command, *args, **kwargs):
        attempts = 0
        while attempts < self.retry_allowed:
            attempts += 1
            if 'wait' in kwargs.keys():
                wait = kwargs['wait']
                del(kwargs['wait'])
            else:
                wait = True

            if wait:
                r = command(*args, wait=True, **kwargs)
                if r == "OK":
                    self.last_time_moved = datetime.datetime.now()
                    LOG.debug("Command {} succeeded, args = {}{}".format(command.__name__, args, kwargs))
                    return True  # log success
                else:
                    LOG.error("Command {} failed with result {}, args = {}{}".format(command.__name__, r, args, kwargs))
                    self._safe_stop()
                    raise Exception("Emergency stop!")
            else:
                command(*args, wait=False, **kwargs)
                return True

    def set_position(self, vertex=None, wait=True):
        vertex = self._vertex_to_real(vertex)
        return self._run_arm_command(self.arm.set_position, x=vertex[0], y=vertex[1], z=vertex[2], speed=200, wait=wait)

    def set_pump(self, on=True):
        res = self._run_arm_command(self.arm.set_pump, on=on)
        # need to allow some time to free up suction cup
        if on is False:
            sleep(1)
        return res

    def _safe_stop(self):
        LOG.warn("Safe stop invoked. Moving to safe position")
        self.set_pump(on=False)
        self.set_position()

    def _capture_stone(self, vertex=None, above=4, use_limit_switch=True):
        '''
        A function to pick a stone from defined coordinates
        :param vertex: coordinates in real, current if no coord given
        :param above: Amount of mm above object to start adjusting. Adjustment range is always twice of above distance.
        :param use_limit_switch: Boolean to use adjusting or not.
        :return: True if stone captured
        '''

        STEP = 2  # mm

        res = False
        if vertex:
            self.set_position(self.above(vertex), wait=False)
            self.set_position(self.above(vertex, above))

        adj_limit = above*2 if use_limit_switch else 0
        i = 0
        while i <= adj_limit - STEP or adj_limit == 0:
            if adj_limit == 0 or self.arm.get_limit_switch():
                res = self.set_pump(on=True)
                break
            self.set_position(self.above(z=-STEP), wait=False)
            i += STEP

        if vertex:
            self.set_position(self.above(vertex), wait=False)
        return res

    def _release_stone(self, vertex=None):
        if vertex:
            self.set_position(self.above(vertex), wait=False)
            self.set_position(self.above(vertex, 5))
        self.set_pump(on=False)
        if vertex:
            self.set_position(self.above(vertex), wait=False)

    def _move_stone(self, a, b):
        self._capture_stone(a)
        self._release_stone(b)
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
            self.set_position()
        return res

    def remove_stone(self, vertex, to_position=False):
        res = self._move_stone(self._vertex_to_real(vertex), self.board.drop_stones)
        if to_position:
            self.set_position()
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
        self.set_position()

    def play_sequence(self, sequence):
        #[{'action': 'put_stone', 'vertex': [], 'colour': 'black'}, {'action': 'remove_stone', 'vertex': []}]
        for action in sequence:
            if action.get('action') in ['put_stone', 'put']:
                self.make_move(colour=action.get('colour'), vertex=action.get('vertex'))
            if action.get('action') in ['remove_stone', 'capture_stone', 'capture', 'remove']:
                self.remove_stone(vertex=action.get('vertex'))
        self.set_position()

    def disconnect(self):
        self.set_position()
        return self.arm.disconnect()

    def _get_current_position(self):
        return self.arm.get_position()

    def _calibrate(self):
        self.set_position()
        cur_position = self._get_current_position()
        i = ''
        while i != 'q':
            print("Current position: {}".format(self._get_current_position()))
            i = input('Adjustment: ')
            a = i.replace(' ', '').split(',')
            new_position = [(cur_position[i] + float(a[i])) for i in range(3)]
            print("New position: {}".format(new_position))
            i = input('Confirm?')
            if i == '' or i.lower() == 'y':
                self.set_position(new_position)
                cur_position = new_position

    def _refpoint(self):
        LOG.info(self.arm.set_servo_detach())
        input("Ready?")
        LOG.info(self.arm.send_cmd_sync('M2401'))
        LOG.info(self.arm.set_servo_attach())
        self.set_position()
        LOG.info("Moved to: {}".format())
        LOG.info("Self esteem coords: {}".format(self._get_current_position()))

    def stretch(self, timeout=5):
        '''
        Makes arm move a bit from time to time to attract attention
        :param timeout: int in minutes
        '''

        # TODO: yet to eb implemented
        pass

if __name__ == "__main__":
    myArm = GoArm()
    myArm.set_position()
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
        myArm.set_position()

    def get_bowl_vertex(a, b, c):
        '''
        b.c
        .x.
        x.x
        .x.
        a.x
        '''

        res = []
        col = 6
        for i in range(col):
            v = [round(a[j] + i*( (b[j] - a[j])/(col - 1) ), 1) for j in range(3)]
            res.append(v)

        for i in range(col):
            v = [round(res[i][j] + (c[j] - b[j]), 1) for j in range(3)]
            res.append(v)

        for i in range(col-1):
            v = [round((res[col+i+1][j] + res[i][j]) / 2, 1) for j in range(3)]
            res.append(v)
        return res
    '''
    r = get_bowl_vertex([120.75, -122.2, 29.2],[247.2, -120, 27.1],[247.2, -160.3, 27.2])
    for i in r:
        print("- {}".format(i))
    r = get_bowl_vertex([119.4, 164.7, 29.3],[248.1, 162.3, 28.5],[248, 121, 28.2])
    for i in r:
        print("- {}".format(i))
    '''
