'''
An initial fully sync implementation of camera communication
'''

import serial
from py.helpers.myloggers import getLogger
from py.constants import goArmConsts as CONST
LOG = getLogger(__name__)

def get_port_by_hwid(hwid):
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if hwid in port.hwid:
            return port.device
    return

class GoCam:
    def __init__(self):
        port = get_port_by_hwid('USB VID:PID=1209:ABD1')
        self.sp = serial.Serial(port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, xonxoff=False,
                           rtscts=False, stopbits=serial.STOPBITS_ONE, timeout=2, dsrdtr=True)
        self.sp.setDTR(True)
        self._arm = None
        self._last_command_from_cam = ''
        self._last_command_to_cam = ''

    def _send(self, b):
        self.sp.write(b)
        self.sp.flush()

    def respond(self, body):
        LOG.info("Response: {}={}".format(self._last_command_from_cam, body))
        self._send(Message.raw(CONST.msg_t_RESPONSE, body, self._last_command_from_cam))

    def request(self, command, body=''):
        LOG.info("Request: {} {}".format(command, body))
        self._send(Message.raw(CONST.msg_t_REQUEST, body, command))
        self._last_command_to_cam = command
        return self.message

    @property
    def message(self):
        m = self.sp.readline().decode().rstrip()

        if m:
            message = Message(m)
            LOG.info("Message from cam: {}".format(m))
            if message.type == CONST.msg_t_REQUEST:
                self._last_command_from_cam = m
                if message.cmd not in CONST.com_ACTIONS:
                    self.respond(CONST.msg_UNKNOWN)
                    return
            elif message.type == CONST.msg_t_RESPONSE and message.body in (CONST.msg_UNKNOWN, CONST.msg_NOT_IMPLEMENTED):
                return
            return message
        return

    # framebuffer (current image)
    @property
    def FB(self):
        return

    def disconnect(self):
        self.request(CONST.com_Disconnect)
        self.sp.close()

    @property
    def arm(self):
        return self._arm

    @arm.setter
    def arm(self, arm):
        self._arm = arm

    def snap(self):
        try:
            if self.arm:
                self.arm.set_position(self.arm.cam_position)
            return self.request(CONST.com_Snap)
        except Exception as e:
            LOG.error("Oops, failure during taking a snapshot: {}".format(e))


class Message:
    type = 0
    cmd = ''
    body = ''

    def __init__(self, msg):
        if msg:
            if msg[0] == '$':
                self.type = CONST.msg_t_RESPONSE
                self.cmd = msg[1:].split('=')[0]
                self.body = msg[1:].split('=')[1]
            else:
                self.type = CONST.msg_t_REQUEST
                self.cmd = msg.split(' ')[0]
                self.body = ' '.join(msg.split(' ')[1:])

    @staticmethod
    def raw(type, body='', cmd='') -> bytes:
        if type == CONST.msg_t_RESPONSE:
            return '${}={}'.format(cmd, body).encode()
        else:
            if body:
                return "{} {}".format(cmd, body).encode()
            else:
                return "{}".format(cmd).encode()
